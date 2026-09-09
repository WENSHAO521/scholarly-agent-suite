"""Real git-backed tests for scripts/check_component_drift.py -- builds
actual temporary git repositories and commits so each status path is
exercised against real git plumbing, not mocked."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from conftest import load_module

drift = load_module("check_component_drift", "check_component_drift.py")


def _run(args, cwd):
    subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True)


def _init_repo(path: Path) -> None:
    path.mkdir(parents=True)
    _run(["git", "init", "--quiet"], path)
    _run(["git", "config", "user.email", "test@example.com"], path)
    _run(["git", "config", "user.name", "Test"], path)


def _commit(path: Path, version: str, message: str) -> str:
    (path / "VERSION").write_text(version, encoding="utf-8")
    # A second file that changes every call, so a commit whose VERSION
    # content happens to repeat (e.g. an untagged follow-up commit with no
    # real version bump) still has something to actually commit.
    (path / "NOTES.txt").write_text(message, encoding="utf-8")
    _run(["git", "add", "VERSION", "NOTES.txt"], path)
    _run(["git", "commit", "--quiet", "-m", message], path)
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=path, capture_output=True, text=True, check=True)
    return proc.stdout.strip()


def _tag(path: Path, tag: str, ref: str = "HEAD") -> None:
    _run(["git", "tag", tag, ref], path)


class ComponentDriftTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name) / "component"
        _init_repo(self.repo)

    def _entry(self, ref: str, tag, version: str) -> dict:
        return {"name": "component", "repo_url": "https://example.invalid/component.git",
                "ref": ref, "tag": tag, "version": version, "include": ["SKILL.md"]}

    def test_current_when_pin_is_tip_and_tagged_and_version_matches(self):
        ref = _commit(self.repo, "1.0.0", "release")
        _tag(self.repo, "v1.0.0")
        entry = self._entry(ref, "v1.0.0", "1.0.0")
        result = drift.check_component(entry, overrides={"component": str(self.repo)}, fetch=False)
        self.assertEqual(result["status"], drift.CURRENT)

    def test_pin_unreachable_for_a_ref_not_in_the_repo(self):
        _commit(self.repo, "1.0.0", "release")
        entry = self._entry("0" * 40, "v1.0.0", "1.0.0")
        result = drift.check_component(entry, overrides={"component": str(self.repo)}, fetch=False)
        self.assertEqual(result["status"], drift.PIN_UNREACHABLE)

    def test_version_tag_mismatch_when_declared_tag_points_elsewhere(self):
        ref1 = _commit(self.repo, "1.0.0", "first")
        _tag(self.repo, "v1.0.0", ref1)
        ref2 = _commit(self.repo, "1.1.0", "second")
        _tag(self.repo, "v1.1.0", ref2)
        # Pin claims v1.0.0 points at ref2 (the v1.1.0 commit) -- it doesn't.
        entry = self._entry(ref2, "v1.0.0", "1.1.0")
        result = drift.check_component(entry, overrides={"component": str(self.repo)}, fetch=False)
        self.assertEqual(result["status"], drift.VERSION_TAG_MISMATCH)

    def test_source_version_mismatch_when_version_file_disagrees(self):
        ref = _commit(self.repo, "1.0.0", "release")
        _tag(self.repo, "v1.0.0")
        # component-sources.json claims 2.0.0, but VERSION at that ref says 1.0.0.
        entry = self._entry(ref, "v1.0.0", "2.0.0")
        result = drift.check_component(entry, overrides={"component": str(self.repo)}, fetch=False)
        self.assertEqual(result["status"], drift.SOURCE_VERSION_MISMATCH)

    def test_pin_not_tagged_when_ref_has_no_tag(self):
        ref = _commit(self.repo, "1.0.0", "release")
        entry = self._entry(ref, None, "1.0.0")
        result = drift.check_component(entry, overrides={"component": str(self.repo)}, fetch=False)
        self.assertEqual(result["status"], drift.PIN_NOT_TAGGED)

    def test_new_release_available_when_a_newer_tag_exists(self):
        ref1 = _commit(self.repo, "1.0.0", "first")
        _tag(self.repo, "v1.0.0", ref1)
        _commit(self.repo, "1.1.0", "second")
        _tag(self.repo, "v1.1.0")
        entry = self._entry(ref1, "v1.0.0", "1.0.0")
        result = drift.check_component(entry, overrides={"component": str(self.repo)}, fetch=False)
        self.assertEqual(result["status"], drift.NEW_RELEASE_AVAILABLE)

    def test_unreleased_commits_ahead_when_head_moved_past_the_tagged_pin(self):
        ref1 = _commit(self.repo, "1.0.0", "first")
        _tag(self.repo, "v1.0.0", ref1)
        _commit(self.repo, "1.0.0", "untagged follow-up commit")
        entry = self._entry(ref1, "v1.0.0", "1.0.0")
        result = drift.check_component(entry, overrides={"component": str(self.repo)}, fetch=False)
        self.assertEqual(result["status"], drift.UNRELEASED_COMMITS_AHEAD)

    def test_no_local_source_when_neither_override_nor_cache_exists(self):
        entry = self._entry("0" * 40, "v1.0.0", "1.0.0")
        result = drift.check_component(entry, overrides={}, fetch=False)
        self.assertEqual(result["status"], drift.NO_LOCAL_SOURCE)

    def test_never_writes_to_component_sources_or_components_json(self):
        """The detector must only detect and report -- never auto-repin."""
        sources_before = drift.SOURCES_FILE.read_bytes()
        ref = _commit(self.repo, "1.0.0", "release")
        _tag(self.repo, "v1.0.0")
        entry = self._entry(ref, "v1.0.0", "1.0.0")
        drift.check_component(entry, overrides={"component": str(self.repo)}, fetch=False)
        self.assertEqual(drift.SOURCES_FILE.read_bytes(), sources_before)


if __name__ == "__main__":
    unittest.main()
