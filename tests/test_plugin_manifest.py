"""Acceptance criteria: Plugin (spec section 135)."""
import json
from pathlib import Path

import sync_manifests

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


def test_platform_manifests_share_brand_version_and_skill_root():
    expected = sync_manifests.expected_manifests()
    for path, manifest in expected.items():
        assert sync_manifests.read_json(path) == manifest, path
    marketplace = expected[sync_manifests.MARKETPLACE]["plugins"][0]
    codex_source = expected[sync_manifests.CODEX_MARKETPLACE]["plugins"][0]["source"]
    assert (ROOT / marketplace["source"]).resolve() == (ROOT / codex_source["path"]).resolve() == ROOT
    assert marketplace["version"] == load_manifest()["version"]


def test_version_is_regenerated_without_editing_any_manifest(tmp_path, monkeypatch):
    for path in ("VERSION", "COMPONENTS.json", sync_manifests.CODEX):
        dest = tmp_path / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes((ROOT / path).read_bytes())
    (tmp_path / "VERSION").write_text("9.8.7\n", encoding="utf-8")
    monkeypatch.setattr(sync_manifests, "ROOT", tmp_path)
    generated = sync_manifests.expected_manifests()
    assert generated[sync_manifests.CODEX]["version"] == "9.8.7"
    assert generated[sync_manifests.CLAUDE]["version"] == "9.8.7"
    assert generated[sync_manifests.MARKETPLACE]["plugins"][0]["version"] == "9.8.7"
    assert generated["COMPONENTS.json"]["suite_version"] == "9.8.7"
