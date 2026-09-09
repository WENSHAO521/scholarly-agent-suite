"""Acceptance criteria: Packaging (spec sections 82-86, 144)."""
import json
import zipfile
from pathlib import Path

from conftest import load_module

ROOT = Path(__file__).resolve().parent.parent
package_suite = load_module("package_suite", "package_suite.py")

EXCLUDED_TOP_LEVEL = {"tests", "evals", ".github", "scripts", "dist", ".git"}


def test_runtime_allowlist_excludes_dev_only_directories():
    files = package_suite.iter_runtime_files()
    rel_parts_first = {f.relative_to(ROOT).parts[0] for f in files}
    assert not (rel_parts_first & EXCLUDED_TOP_LEVEL), rel_parts_first & EXCLUDED_TOP_LEVEL


def test_runtime_allowlist_excludes_pycache():
    files = package_suite.iter_runtime_files()
    assert not any("__pycache__" in f.parts for f in files)


def test_runtime_allowlist_includes_all_skill_md():
    files = package_suite.iter_runtime_files()
    rel = {f.relative_to(ROOT).as_posix() for f in files}
    for name in [
        "scholarly-agent", "adaptive-model-router", "scholarly-corpus-builder",
        "scholarly-voice-engine", "journal-fit-engine",
    ]:
        assert f"skills/{name}/SKILL.md" in rel


def test_package_builds_valid_zip_with_single_root(tmp_path, monkeypatch):
    monkeypatch.setattr(package_suite, "DIST_DIR", tmp_path)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files = package_suite.iter_runtime_files()
    zip_path = package_suite.build_zip(files, version)
    assert zip_path.exists()
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        assert all(n.startswith("scholarly-agent-suite/") for n in names)
        assert zf.testzip() is None  # no corrupt entries


def test_package_is_byte_deterministic_across_two_builds(tmp_path, monkeypatch):
    monkeypatch.setattr(package_suite, "DIST_DIR", tmp_path)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files = package_suite.iter_runtime_files()
    zip1 = package_suite.build_zip(files, version)
    hash1 = package_suite.sha256_of(zip1)
    zip1.unlink()
    zip2 = package_suite.build_zip(files, version)
    hash2 = package_suite.sha256_of(zip2)
    assert hash1 == hash2


def test_zip_entries_never_contain_carriage_returns(tmp_path, monkeypatch):
    """Regression guard for a real bug (found 2026-09-09): package_suite.py
    used to write file_path.read_bytes() directly, so a component file
    checked out with CRLF line endings (as scholarly-corpus-builder's own
    scb/manifest.py was, on a Windows checkout) produced a ZIP whose bytes
    differed from the same commit packaged on Linux CI (LF checkout) --
    silently breaking the "identical bytes across builds/machines" claim
    this module's own docstring makes. normalized_bytes() now decodes with
    universal-newline translation and re-encodes as LF; assert that
    directly rather than only checking two same-machine builds match,
    which passed even with the bug present."""
    monkeypatch.setattr(package_suite, "DIST_DIR", tmp_path)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files = package_suite.iter_runtime_files()
    zip_path = package_suite.build_zip(files, version)
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            data = zf.read(info)
            assert b"\r" not in data, f"{info.filename} contains a carriage return -- CRLF leaked into the ZIP"


def test_zip_uses_stored_not_deflated_compression(tmp_path, monkeypatch):
    """Regression guard for a real bug (found 2026-09-09): ZIP_DEFLATED
    compression is not guaranteed byte-identical across zlib versions/
    builds even for identical input, so a Windows-local build (with the
    CRLF fix already applied) still didn't match the Linux-CI-published
    v1.0.0 ZIP until compression was switched to ZIP_STORED -- the same
    tradeoff adaptive-model-router/scholarly-corpus-builder/
    journal-fit-engine's own packagers already made for the same reason."""
    monkeypatch.setattr(package_suite, "DIST_DIR", tmp_path)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files = package_suite.iter_runtime_files()
    zip_path = package_suite.build_zip(files, version)
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            assert info.compress_type == zipfile.ZIP_STORED, info.filename


def test_release_manifest_has_no_private_machine_paths(tmp_path, monkeypatch):
    monkeypatch.setattr(package_suite, "DIST_DIR", tmp_path)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files = package_suite.iter_runtime_files()
    zip_path = package_suite.build_zip(files, version)
    manifest_path = package_suite.write_release_manifest(zip_path, files, version)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_text = json.dumps(manifest)
    assert str(ROOT) not in manifest_text
    assert "C:\\" not in manifest_text
    assert manifest["zip_sha256"]
    assert manifest["file_count"] == len(files)
    for name in [
        "scholarly-agent", "adaptive-model-router", "scholarly-corpus-builder",
        "scholarly-voice-engine", "journal-fit-engine",
    ]:
        assert name in manifest["components"]
