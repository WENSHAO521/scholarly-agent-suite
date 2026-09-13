#!/usr/bin/env python3
"""Regenerate (or check) the top-level `workflows/` documentation mirror
from the runtime-canonical source at
`skills/scholarly-agent/references/workflows/` (scripts/workflow_manifest.py).

`workflows/` at the repository root is never hand-edited. It exists only as
a documentation convenience for anyone browsing the repo root or following
an old link; the one manually-editable copy of each recipe lives under
scholarly-agent's own Skill package so it resolves from inside that Skill's
runtime boundary under every installation mode (see workflow_manifest.py's
docstring for why that distinction matters).

Usage:
    python scripts/sync_workflows.py           # regenerate the mirror
    python scripts/sync_workflows.py --check   # report drift, write nothing

--check exits non-zero if the mirror is missing a required file, has a
stray extra file, or any file's content has drifted from the canonical
source -- this is the mechanism that makes two-copy drift a CI failure
instead of a silent inconsistency.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from workflow_manifest import CANONICAL_WORKFLOWS_DIR, MIRROR_WORKFLOWS_DIR, REQUIRED_WORKFLOWS  # noqa: E402


def check_drift(canonical_dir: Path = CANONICAL_WORKFLOWS_DIR,
                 mirror_dir: Path = MIRROR_WORKFLOWS_DIR) -> list[str]:
    """Return a list of human-readable drift problems; empty means the
    mirror exactly matches the canonical source for every required file."""
    problems: list[str] = []
    for name in REQUIRED_WORKFLOWS:
        canonical_file = canonical_dir / name
        mirror_file = mirror_dir / name
        if not canonical_file.is_file():
            problems.append(f"canonical source missing: {canonical_file}")
            continue
        if not mirror_file.is_file():
            problems.append(f"mirror missing: {mirror_file}")
            continue
        canonical_text = canonical_file.read_text(encoding="utf-8")
        mirror_text = mirror_file.read_text(encoding="utf-8")
        if canonical_text != mirror_text:
            problems.append(f"content drift: {mirror_file} does not match {canonical_file}")

    if mirror_dir.is_dir():
        known = set(REQUIRED_WORKFLOWS)
        for entry in sorted(mirror_dir.iterdir()):
            if entry.is_file() and entry.name not in known:
                problems.append(f"stray file in mirror (not in REQUIRED_WORKFLOWS): {entry}")

    return problems


def regenerate(canonical_dir: Path = CANONICAL_WORKFLOWS_DIR,
               mirror_dir: Path = MIRROR_WORKFLOWS_DIR) -> None:
    missing_source = [name for name in REQUIRED_WORKFLOWS if not (canonical_dir / name).is_file()]
    if missing_source:
        raise SystemExit(
            "Refusing to regenerate the mirror -- canonical source is missing "
            f"required file(s): {missing_source}"
        )
    mirror_dir.mkdir(parents=True, exist_ok=True)
    known = set(REQUIRED_WORKFLOWS)
    for entry in list(mirror_dir.iterdir()) if mirror_dir.is_dir() else []:
        if entry.is_file() and entry.name in known:
            entry.unlink()
    for name in REQUIRED_WORKFLOWS:
        (mirror_dir / name).write_text((canonical_dir / name).read_text(encoding="utf-8"), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="report drift only, write nothing")
    args = parser.parse_args()

    if args.check:
        problems = check_drift()
        if problems:
            print("Workflow mirror drift detected:", file=sys.stderr)
            for problem in problems:
                print(f"  - {problem}", file=sys.stderr)
            return 1
        print("workflows/ mirror matches skills/scholarly-agent/references/workflows/ exactly.")
        return 0

    regenerate()
    problems = check_drift()
    if problems:
        print("Regeneration completed but drift remains (unexpected):", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1
    print(f"Regenerated {MIRROR_WORKFLOWS_DIR} from {CANONICAL_WORKFLOWS_DIR}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
