"""Automatic packaging and publishing (.github/workflows/release.yml).

The workflow publishes release v<VERSION> on a push to master when that
release does not exist yet, using scripts/release_notes.py for the notes.
These tests cover the parts that can be checked offline: the notes script,
and the workflow's guards against overwriting a release or publishing an
unvalidated or non-deterministic package."""
from pathlib import Path

from conftest import load_module

ROOT = Path(__file__).resolve().parent.parent
release_notes = load_module("release_notes", "release_notes.py")
WORKFLOW = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")

SAMPLE = """# Changelog

## v2.1.0 -- 2026-12-01

v2.1.0 PREPARED -- NOT PUBLISHED

### Added

- Something new.

## v2.0.0 -- 2026-11-08

v2.0.0 PUBLISHED

- Older entry.
"""


def test_current_version_has_release_notes():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    notes = release_notes.section(version, (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
    assert notes and notes.strip(), f"CHANGELOG.md has no section for v{version}"


def test_section_stops_at_next_version_and_drops_status_line():
    notes = release_notes.section("2.1.0", SAMPLE)
    assert "Something new." in notes
    assert "Older entry." not in notes
    assert "PREPARED" not in notes and "PUBLISHED" not in notes


def test_section_does_not_match_a_version_prefix():
    assert release_notes.section("2.1", SAMPLE) is None


def test_missing_version_fails_the_script():
    assert release_notes.main(["release_notes.py", "99.0.0"]) == 1


def test_workflow_publishes_from_master_and_tags():
    assert "branches:\n      - master" in WORKFLOW
    assert '- "v*"' in WORKFLOW
    assert "workflow_dispatch" in WORKFLOW


def test_workflow_never_overwrites_a_release():
    assert WORKFLOW.count('gh release view "${tag}"') >= 2
    assert "refusing to overwrite" in WORKFLOW
    assert "--clobber" not in WORKFLOW


def test_workflow_validates_tests_and_checks_determinism_before_publishing():
    publish = WORKFLOW.index("gh release create")
    for step in ["scripts/validate_suite.py", "pytest tests/", "release_notes.py",
                 "Packaging is not deterministic", "SHA256SUMS"]:
        assert step in WORKFLOW
        assert WORKFLOW.index(step) < publish, f"{step} must run before publishing"


def test_workflow_rejects_a_tag_that_does_not_match_version():
    assert "does not match VERSION" in WORKFLOW
