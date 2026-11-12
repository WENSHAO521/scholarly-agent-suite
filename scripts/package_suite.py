#!/usr/bin/env python3
"""Build the self-contained runtime distribution ZIP for scholarly-agent-suite.

Packages exactly the runtime allowlist from the spec (rule 81):

    scholarly-agent-suite/
      .codex-plugin/
      skills/            (the single scholarly-agent Skill, including its
                          modules/, protocols/ and shared/)
      workflows/
      README.md
      LICENSE
      VERSION
      COMPONENTS.json

`skills/` is what makes this deterministic regardless of installation mode:
every workflow recipe scholarly-agent needs lives at
`skills/scholarly-agent/references/workflows/` -- inside its own Skill
package -- so it ships correctly whether this ZIP is used whole, a host
extracts only `skills/`, or scholarly-agent is later re-packaged standalone.
Top-level `workflows/` (also in this allowlist) is a generated
*documentation* mirror of the same files, not a second runtime source --
`scripts/sync_workflows.py --check` (wired into `validate_suite.py`) fails
the build if it ever drifts from the canonical copy under `skills/`.

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

It also builds a second ZIP, `dist/scholarly-agent-skill-v<version>.zip`,
for uploading the Skill directly in claude.ai's Skills settings. That upload rejects archives with more than 200
files ("Zip contains too many files (maximum 200)"), so this ZIP holds only
the Skill folder itself (`scholarly-agent/SKILL.md` at its top) minus
descriptors other runtimes use (`agents/`). Both ZIPs are checked against
MAX_UPLOAD_FILES and the build fails rather than producing an archive the
upload would refuse.

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
    "workflows",
    "README.md",
    "LICENSE",
    "VERSION",
    "COMPONENTS.json",
]

EXCLUDE_DIR_NAMES = {"__pycache__", ".git", "tests", "evals", "dist", ".github"}
# "scripts" was previously in this set as a blanket exclusion, on the
# (until now correct) assumption that no component ever needs a directory
# literally named "scripts" in its packaged runtime tree -- the Suite's own
# dev-only scripts/ isn't walked at all (it's not in RUNTIME_ALLOWLIST).
# scholarly-voice-engine's runtime package legitimately lives under
# scripts/voice/ (see component-sources.json's include list, which already
# excludes that component's own dev-only scripts/validate_skill.py and
# scripts/package_runtime.py at the sync step) -- a blanket "scripts" match
# on any path component would silently strip that runtime package back out
# here regardless of what sync_components.json chose to include, so this
# exclusion is now handled precisely at the sync step's include allowlist
# instead of by directory name here.
FIXED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)

# claude.ai's Skill upload refuses a ZIP with more than 200 files. Keep
# both archives under it so either one uploads.
MAX_UPLOAD_FILES = 200
SKILL_DIR = ROOT / "skills" / "scholarly-agent"
# Paths (relative to SKILL_DIR) left out of the claude.ai Skill ZIP: the
# cross-runtime descriptor is read by other hosts, never by claude.ai.
SKILL_ZIP_EXCLUDE_PREFIXES = ("agents/",)


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


def iter_skill_files() -> list[Path]:
    """Files for the claude.ai Skill ZIP: the Skill folder only."""
    files: list[Path] = []
    for sub in sorted(SKILL_DIR.rglob("*")):
        if sub.is_dir():
            continue
        rel = sub.relative_to(SKILL_DIR)
        if any(part in EXCLUDE_DIR_NAMES for part in rel.parts):
            continue
        if rel.as_posix().startswith(SKILL_ZIP_EXCLUDE_PREFIXES):
            continue
        files.append(sub)
    return sorted(files, key=lambda p: p.relative_to(SKILL_DIR).as_posix())


def check_upload_limit(files: list[Path], label: str) -> None:
    if len(files) > MAX_UPLOAD_FILES:
        raise SystemExit(
            f"{label} would contain {len(files)} files; claude.ai Skill upload "
            f"accepts at most {MAX_UPLOAD_FILES}. Consolidate files before releasing."
        )


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
    _write_zip(zip_path, [("scholarly-agent-suite/" + f.relative_to(ROOT).as_posix(), f) for f in files])
    return zip_path


def build_skill_zip(files: list[Path], version: str) -> Path:
    """The claude.ai upload ZIP: `scholarly-agent/SKILL.md` and the rest of
    the Skill folder, nothing else."""
    DIST_DIR.mkdir(exist_ok=True)
    zip_path = DIST_DIR / f"scholarly-agent-skill-v{version}.zip"
    _write_zip(zip_path, [("scholarly-agent/" + f.relative_to(SKILL_DIR).as_posix(), f) for f in files])
    return zip_path


def _write_zip(zip_path: Path, entries: list[tuple[str, Path]]) -> None:
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_STORED) as zf:
        for arcname, file_path in entries:
            info = zipfile.ZipInfo(arcname, date_time=FIXED_ZIP_TIMESTAMP)
            # ZipInfo defaults create_system to the platform running this
            # script (0=Windows, 3=Unix) unless pinned -- fix it so the
            # same commit produces the same bytes on Windows and Linux CI.
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = 0o644 << 16
            zf.writestr(info, normalized_bytes(file_path))


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def write_release_manifest(
    zip_path: Path, files: list[Path], version: str, skill_zip_path: Path | None = None,
    skill_files: list[Path] | None = None,
) -> Path:
    components = json.loads((ROOT / "COMPONENTS.json").read_text(encoding="utf-8"))
    manifest = {
        "suite_version": version,
        "skill": components["skill"],
        "modules": components["modules"],
        "protocol_versions": components.get("protocol_versions", []),
        "file_count": len(files),
        "files": [f"scholarly-agent-suite/{p.relative_to(ROOT).as_posix()}" for p in files],
        "build_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "zip_filename": zip_path.name,
        "zip_sha256": sha256_of(zip_path),
    }
    if skill_zip_path is not None:
        manifest["skill_zip"] = {
            "filename": skill_zip_path.name,
            "purpose": "claude.ai Skill upload (at most 200 files)",
            "file_count": len(skill_files or []),
            "sha256": sha256_of(skill_zip_path),
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
    skill_files = iter_skill_files()
    check_upload_limit(files, "Suite ZIP")
    check_upload_limit(skill_files, "Skill ZIP")
    zip_path = build_zip(files, version)
    skill_zip_path = build_skill_zip(skill_files, version)
    manifest_path = write_release_manifest(zip_path, files, version, skill_zip_path, skill_files)
    print(f"Built {zip_path} ({len(files)} files)")
    print(f"SHA-256: {sha256_of(zip_path)}")
    print(f"Built {skill_zip_path} ({len(skill_files)} files; upload this one in claude.ai)")
    print(f"SHA-256: {sha256_of(skill_zip_path)}")
    print(f"Manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
