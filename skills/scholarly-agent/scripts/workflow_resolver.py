"""Resolves a workflow recipe from scholarly-agent's own installed runtime,
and classifies exactly why a lookup failed instead of guessing.

This module exists because of a real incident: during an end-to-end
orchestration run, scholarly-agent reported "the installed package is
missing theory-paper.md" when in fact `theory-paper.md` existed on
`master`, existed in tag `v1.2.0`, was allowlisted by `package_suite.py`,
and was documented in this very SKILL.md. The runtime never actually
inspected the installed Skill's own files before making that claim -- it
inferred "missing" from a failed lookup at a path
(`../../workflows/theory-paper.md`) that only resolves when the whole
repository root happens to be visible next to `skills/`, which is not true
for a standalone install, a `.codex-plugin` load, or a release ZIP
extracted on its own.

`resolve_workflow()` never makes that mistake again because it distinguishes
three different failure conditions instead of collapsing them into one
"missing" message:

  WORKFLOW_SOURCE_MISSING  -- `name` is not one of the workflow recipes this
                               orchestrator actually knows about. This is a
                               real "does not exist" case -- safe to report
                               as such immediately, no runtime inspection
                               needed (there is nothing to inspect for).
  WORKFLOW_RUNTIME_MISSING -- `name` IS a recipe this orchestrator knows
                               about, the runtime workflow directory was
                               successfully found and read, and the specific
                               file is confirmed absent from it. This is the
                               only condition under which "the installed
                               package is missing <file>" is an honest
                               statement -- it is reported only after the
                               runtime has actually been inspected.
  WORKFLOW_UNRESOLVABLE    -- the runtime's own workflow directory could not
                               be located or read at all (wrong root passed,
                               directory absent, permission error). This is
                               a resolution/installation-visibility problem,
                               not proof that the file itself is missing --
                               report it as such, never as "missing
                               <file>".

`KNOWN_WORKFLOWS` is intentionally a plain literal list, not an import from
the Suite's dev-only `scripts/workflow_manifest.py`: this file ships inside
`skills/scholarly-agent/` and must keep working when scholarly-agent is
installed completely standalone, with no `scripts/` directory from the
Suite root anywhere nearby. `tests/test_workflow_packaging.py` in the Suite
dev repo asserts this list stays in sync with
`scripts/workflow_manifest.REQUIRED_WORKFLOWS` -- drift between the two is
a test failure, not a silent divergence.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

RESOLVED = "RESOLVED"
WORKFLOW_SOURCE_MISSING = "WORKFLOW_SOURCE_MISSING"
WORKFLOW_RUNTIME_MISSING = "WORKFLOW_RUNTIME_MISSING"
WORKFLOW_UNRESOLVABLE = "WORKFLOW_UNRESOLVABLE"

# Keep in sync with scripts/workflow_manifest.REQUIRED_WORKFLOWS.
KNOWN_WORKFLOWS = [
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
    "pre-submission-review.md",
]


@dataclass
class WorkflowResolution:
    status: str
    name: str
    detail: str
    path: Optional[Path] = None

    @property
    def ok(self) -> bool:
        return self.status == RESOLVED


def _normalize(name: str) -> str:
    return name if name.endswith(".md") else f"{name}.md"


def resolve_workflow(skill_root: Path, name: str) -> WorkflowResolution:
    """Resolve `name` (with or without the `.md` suffix) against the
    `references/workflows/` directory inside `skill_root` -- the root of an
    *installed* scholarly-agent Skill, whatever that turns out to be for
    the current install (full Suite checkout, standalone Skill directory,
    `.codex-plugin` load, or a release ZIP extracted on its own).

    Never returns a generic "missing" result: every non-RESOLVED outcome is
    one of the three classified statuses above, each carrying enough detail
    to tell a genuine packaging gap apart from a resolution failure that
    never actually inspected the runtime.
    """
    filename = _normalize(name)

    if filename not in KNOWN_WORKFLOWS:
        return WorkflowResolution(
            status=WORKFLOW_SOURCE_MISSING,
            name=filename,
            detail=f"{filename!r} is not a workflow recipe scholarly-agent knows about.",
        )

    workflows_dir = Path(skill_root) / "references" / "workflows"
    try:
        dir_exists = workflows_dir.is_dir()
    except OSError as exc:
        return WorkflowResolution(
            status=WORKFLOW_UNRESOLVABLE,
            name=filename,
            detail=(
                f"could not read {workflows_dir} to check for {filename!r}: {exc}. "
                "This is a runtime-resolution failure, not confirmation that the "
                "file is absent."
            ),
        )
    if not dir_exists:
        return WorkflowResolution(
            status=WORKFLOW_UNRESOLVABLE,
            name=filename,
            detail=(
                f"{workflows_dir} does not exist under this install root -- the "
                "installed runtime has not actually been inspected, so this must "
                "not be reported as the file being missing."
            ),
        )

    target = workflows_dir / filename
    try:
        found = target.is_file()
    except OSError as exc:
        return WorkflowResolution(
            status=WORKFLOW_UNRESOLVABLE,
            name=filename,
            detail=f"could not read {target}: {exc}.",
        )

    if found:
        return WorkflowResolution(status=RESOLVED, name=filename, detail=f"resolved at {target}", path=target)

    return WorkflowResolution(
        status=WORKFLOW_RUNTIME_MISSING,
        name=filename,
        detail=(
            f"{filename!r} is a declared workflow recipe, {workflows_dir} was "
            f"successfully inspected, and {filename!r} is confirmed absent from "
            "it -- a genuine packaging/installation gap."
        ),
    )
