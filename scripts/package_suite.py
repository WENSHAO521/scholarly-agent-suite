#!/usr/bin/env python3
"""Build the self-contained runtime distribution ZIP for scholarly-agent-suite.

Packages exactly the runtime allowlist from the spec (rule 81):

    scholarly-agent-suite/
      .codex-plugin/
      skills/
      protocols/
      shared/
      workflows/
      README.md
      LICENSE
      VERSION
      COMPONENTS.json

Explicitly excludes tests/, evals/, .github/, scripts/, dist/, .git, and any
__pycache__ (rule 83). The ZIP itself is built deterministically (sorted
entries, fixed per-entry timestamp, UTF-8 text normalized to LF, stored
uncompressed) so identical source content produces identical bytes across
builds/machines (rule 86), including across a Windows checkout (CRLF) and
Linux CI (LF) of the same commit, and across different zlib versions --
verified 2026-09-09 after finding two real cross-platform mismatches: one
synced component file with CRLF line endings, and DEFLATE compression not
being byte-identical across zlib builds even for identical input (the same
tradeoff adaptive-model-router's/scholarly-corpus-builder's/
journal-fit-engine's own packagers already made). The human-readable build
timestamp instead lives in release-manifest.json, written alongside the ZIP
(not inside it), so it never perturbs the ZIP's own checksum.

Usage: python scripts/package_suite.py
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = ROOT / "dist"

RUNTIME_ALLOWLIST = [
    ".codex-plugin",
    "skills",
    "protocols",
    "shared",
    "workflows",
    "README.md",
    "LICENSE",
    "VERSION",
    "COMPONENTS.json",
]

EXCLUDE_DIR_NAMES = {"__pycache__", ".git", "tests", "evals", "dist", ".github", "scripts"}
FIXED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def iter_runtime_files() -> list[Path]:
    files: list[Path] = []
    for entry in RUNTIME_ALLOWLIST:
        path = ROOT / entry
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            for sub in sorted(path.rglob("*")):
                if sub.is_dir():
                    continue
                if any(part in EXCLUDE_DIR_NAMES for part in sub.relative_to(ROOT).parts):
                    continue
                files.append(sub)
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def normalized_bytes(file_path: Path) -> bytes:
    """Decode as UTF-8 text with universal-newline translation (any of
    \\r\\n, \\r, \\n becomes \\n on read) and re-encode with LF, so the same
    committed content produces identical bytes regardless of the checking-
    out platform's line-ending conversion (Windows CRLF vs Linux LF).
    Every file in RUNTIME_ALLOWLIST is text (.md/.py/.json/.yaml/.svg/
    extensionless LICENSE-style files); this would need reconsidering if a
    genuinely binary file were ever added to the allowlist. Path.read_text()
    only gained a `newline` parameter in Python 3.13; open() supports it on
    every supported version, so this uses open() directly."""
    with open(file_path, "r", encoding="utf-8", newline=None) as handle:
        return handle.read().encode("utf-8")


def build_zip(files: list[Path], version: str) -> Path:
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"scholarly-agent-suite-v{version}.zip"
    root_prefix = "scholarly-agent-suite/"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
        for file_path in files:
            arcname = root_prefix + file_path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(arcname, date_time=FIXED_ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            zf.writestr(info, normalized_bytes(file_path))
    return zip_path


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def write_release_manifest(zip_path: Path, files: list[Path], version: str) -> Path:
    components = json.loads((ROOT / "COMPONENTS.json").read_text(encoding="utf-8"))
    manifest = {
        "suite_version": version,
        "components": components["components"],
        "protocol_versions": components.get("protocol_versions", []),
        "file_count": len(files),
        "files": [f"scholarly-agent-suite/{p.relative_to(ROOT).as_posix()}" for p in files],
        "build_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "zip_filename": zip_path.name,
        "zip_sha256": sha256_of(zip_path),
    }
    manifest_path = DIST_DIR / "release-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files = iter_runtime_files()
    if not files:
        print("No runtime files found -- aborting.")
        return 1
    zip_path = build_zip(files, version)
    manifest_path = write_release_manifest(zip_path, files, version)
    checksum = sha256_of(zip_path)
    print(f"Built {zip_path} ({len(files)} files)")
    print(f"SHA-256: {checksum}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
