#!/usr/bin/env python3
"""Print the CHANGELOG.md section for one version, as GitHub release notes.

Usage: python scripts/release_notes.py [VERSION]   (default: the VERSION file)

Exits 1 if CHANGELOG.md has no `## v<VERSION>` section, so the release
workflow refuses to publish a version that was never written up. The
section's publication-status line (`... PREPARED -- NOT PUBLISHED` /
`... PUBLISHED`) is dropped: the GitHub release itself is the record of
publication.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
_STATUS_RE = re.compile(r"^v\d+(\.\d+)*\s+(PREPARED -- NOT PUBLISHED|PUBLISHED)\s*$")


def section(version: str, changelog: str) -> str | None:
    lines = changelog.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(rf"^## v{re.escape(version)}(\s|$)", line):
            start = i
            break
    if start is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        if lines[j].startswith("## v"):
            end = j
            break
    body = [l for l in lines[start + 1:end] if not _STATUS_RE.match(l.strip())]
    return "\n".join(body).strip() + "\n"


def main(argv: list[str]) -> int:
    version = argv[1] if len(argv) > 1 else (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    notes = section(version, (ROOT / "CHANGELOG.md").read_text(encoding="utf-8"))
    if not notes or not notes.strip():
        print(f"CHANGELOG.md has no section for v{version}", file=sys.stderr)
        return 1
    sys.stdout.write(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
