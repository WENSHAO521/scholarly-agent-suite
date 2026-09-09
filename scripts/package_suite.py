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
entries, fixed per-entry timestamp) so identical source content produces
identical bytes across builds/machines (rule 86); the human-readable build
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


def build_zip(files: list[Path], version: str) -> Path:
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"scholarly-agent-suite-v{version}.zip"
    root_prefix = "scholarly-agent-suite/"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for file_path in files:
            arcname = root_prefix + file_path.relative_to(ROOT).as_posix()
            info = zipfile.ZipInfo(arcname, date_time=FIXED_ZIP_TIMESTAMP)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, file_path.read_bytes())
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
