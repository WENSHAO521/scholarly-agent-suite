"""Regression coverage for the generated Claude marketplace plugin."""
import json
import shutil
import zipfile
from pathlib import Path

import pytest

import package_suite
import sync_manifests

ROOT = Path(__file__).resolve().parent.parent


def test_marketplace_points_to_generated_plugin_and_metadata():
    market = sync_manifests.read_json(sync_manifests.MARKETPLACE)
    plugin = sync_manifests.read_json(sync_manifests.CLAUDE)
    entry = market["plugins"][0]
    assert entry["source"] == "./plugins/scholarly-agent-suite"
    for name in ("name", "version", "description", "author", "license"):
        assert entry[name] == plugin[name]
    assert plugin["version"] == (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    assert not (ROOT / ".claude-plugin" / "plugin.json").exists()


def test_generated_skill_matches_all_canonical_runtime_files():
    source = ROOT / sync_manifests.SKILL_PATH
    generated = ROOT / sync_manifests.CLAUDE_ROOT / sync_manifests.SKILL_PATH
    canonical = {
        path.relative_to(source)
        for path in source.rglob("*")
        if path.is_file()
        and not sync_manifests.RUNTIME_EXCLUDES.intersection(path.relative_to(source).parts)
        and path.relative_to(source).parts[0] != "agents"
    }
    actual = {path.relative_to(generated) for path in generated.rglob("*") if path.is_file()}
    assert actual == canonical
    for relative in canonical:
        assert (source / relative).read_text(encoding="utf-8") == (generated / relative).read_text(encoding="utf-8")


def test_claude_zip_contains_only_generated_runtime(tmp_path, monkeypatch):
    monkeypatch.setattr(package_suite, "DIST_DIR", tmp_path)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    archive, count = package_suite.build_claude_zip(version)
    prefix = sync_manifests.CLAUDE_ROOT + "/"
    expected = {
        "scholarly-agent-suite/" + name.removeprefix(prefix)
        for name in sync_manifests.generated_files()
        if name.startswith(prefix)
    }
    with zipfile.ZipFile(archive) as zf:
        assert zf.testzip() is None
        assert set(zf.namelist()) == expected
        assert len(zf.namelist()) == count <= 200
        assert json.loads(zf.read("scholarly-agent-suite/.claude-plugin/plugin.json"))["version"] == version
    first = archive.read_bytes()
    assert package_suite.build_claude_zip(version)[0].read_bytes() == first


def test_skill_zip_uses_platform_independent_path_order(tmp_path, monkeypatch):
    monkeypatch.setattr(package_suite, "DIST_DIR", tmp_path)
    files = package_suite.iter_skill_files()
    names = [path.relative_to(package_suite.SKILL_DIR).as_posix() for path in files]
    assert names == sorted(names)
    archive = package_suite.build_skill_zip(files, "9.8.7")
    with zipfile.ZipFile(archive) as zf:
        assert zf.namelist() == [f"scholarly-agent/{name}" for name in names]


def test_sync_recreates_runtime_and_preserves_source(tmp_path, monkeypatch):
    for name in ("VERSION", "COMPONENTS.json", "LICENSE", sync_manifests.CODEX):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    shutil.copytree(ROOT / sync_manifests.SKILL_PATH, tmp_path / sync_manifests.SKILL_PATH,
                    ignore=shutil.ignore_patterns("__pycache__"))
    monkeypatch.setattr(sync_manifests, "ROOT", tmp_path)
    (tmp_path / "VERSION").write_text("9.8.7\n", encoding="utf-8")
    sync_manifests.sync(check=False)
    generated = tmp_path / sync_manifests.CLAUDE_ROOT / sync_manifests.SKILL_PATH / "SKILL.md"
    source = tmp_path / sync_manifests.SKILL_PATH / "SKILL.md"
    original = source.read_bytes()
    generated.write_text("modified", encoding="utf-8")
    assert sync_manifests.sync(check=True)
    sync_manifests.sync(check=False)
    assert source.read_bytes() == original
    assert source.read_text(encoding="utf-8") == generated.read_text(encoding="utf-8")
    assert not sync_manifests.sync(check=True)
    assert sync_manifests.read_json(sync_manifests.MARKETPLACE)["plugins"][0]["source"] == sync_manifests.CLAUDE_SOURCE
    assert sync_manifests.read_json(sync_manifests.CLAUDE)["version"] == "9.8.7"


def test_unrecognized_runtime_file_cannot_be_silently_omitted(tmp_path, monkeypatch):
    skill = tmp_path / sync_manifests.SKILL_PATH
    (skill / "modules").mkdir(parents=True)
    (skill / "modules" / "resource.bin").write_bytes(b"future runtime")
    monkeypatch.setattr(sync_manifests, "ROOT", tmp_path)
    with pytest.raises(ValueError, match="Unsupported Claude runtime file type"):
        sync_manifests.claude_skill_files()
