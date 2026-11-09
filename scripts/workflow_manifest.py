"""Single source of truth for the Suite's required workflow recipes.

Root cause this module fixes: `scholarly-agent`'s SKILL.md used to point at
`workflows/` one level *above* its own Skill directory
(`skills/scholarly-agent/../../workflows/`). That path only resolves when a
host happens to expose the whole repository root next to `skills/` -- it is
invisible the moment scholarly-agent is installed standalone, loaded via
`.codex-plugin/plugin.json`, extracted from the release ZIP into its own
directory, or served by a host that only exposes the declared `skills/`
tree. The files were never missing from the repository or from git tag
v1.2.0; they were only unreachable from *inside scholarly-agent's own
runtime boundary* under those installation modes -- a packaging/visibility
defect, not a content defect.

Canonical runtime location (this is what every installation mode must be
able to resolve, because it lives inside scholarly-agent's own Skill
directory):

    skills/scholarly-agent/references/workflows/<name>.md

`workflows/` at the repository root is an optional, generated
*documentation* mirror of the same files -- never hand-edited. It exists
only because README.md and external links have historically pointed at it;
`scripts/sync_workflows.py` regenerates it from the canonical source and
`--check`s that it has not drifted. There is exactly one manually-editable
copy of each workflow recipe: the one under
`skills/scholarly-agent/references/workflows/`.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# The one list every test, validator, and sync script imports -- adding or
# removing a required workflow recipe means editing this list and nothing
# else.
REQUIRED_WORKFLOWS = [
    "paper-from-idea.md",
    "paper-from-notes.md",
    "revise-manuscript.md",
    "journal-selection.md",
    "target-journal-adaptation.md",
    "literature-review.md",
    "theory-paper.md",
    "empirical-paper.md",
    "systematic-review.md",
    "nature-commentary.md",
    "book-project.md",
    "monograph-chapter.md",
    "author-voice-calibration.md",
    "corpus-profile-build.md",
    "peer-review-simulation.md",
]

CANONICAL_WORKFLOWS_DIR = ROOT / "skills" / "scholarly-agent" / "references" / "workflows"
MIRROR_WORKFLOWS_DIR = ROOT / "workflows"


def missing_from(directory: Path) -> list[str]:
    """Return the subset of REQUIRED_WORKFLOWS not present as a file in
    `directory`. An empty list means every required recipe is present."""
    return [name for name in REQUIRED_WORKFLOWS if not (directory / name).is_file()]
