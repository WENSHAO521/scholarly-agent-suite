"""Acceptance criteria: Plugin (spec section 135)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_manifest():
    return json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))


def test_manifest_is_valid_json():
    load_manifest()  # raises on parse failure


def test_manifest_required_fields():
    manifest = load_manifest()
    for field in ("name", "version", "description", "author"):
        assert field in manifest, f"plugin.json missing required field '{field}'"
    for field in ("name", "email", "url"):
        assert field in manifest["author"], f"plugin.json author missing '{field}'"


def test_manifest_name_and_skills_path():
    manifest = load_manifest()
    assert manifest["name"] == "scholarly-agent-suite"
    assert manifest["skills"] == "./skills/"
    assert (ROOT / "skills").is_dir()


def test_manifest_no_unsupported_top_level_fields():
    # Fields confirmed against the upstream plugin-json-spec.md as of this
    # release: name, version, description, author, homepage, repository,
    # license, keywords, skills, hooks, mcpServers, apps, interface.
    allowed = {
        "name", "version", "description", "author", "homepage", "repository",
        "license", "keywords", "skills", "hooks", "mcpServers", "apps", "interface",
    }
    manifest = load_manifest()
    unexpected = set(manifest.keys()) - allowed
    assert not unexpected, f"plugin.json has unsupported top-level fields: {unexpected}"


def test_manifest_version_matches_version_file():
    manifest = load_manifest()
    suite_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert manifest["version"] == suite_version


def test_single_skill_present():
    skills = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
    assert skills == ["scholarly-agent"]
    assert (ROOT / "skills" / "scholarly-agent" / "SKILL.md").exists()
