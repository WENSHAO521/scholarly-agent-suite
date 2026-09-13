---
name: scholarly-agent
description: Coordinate multi-stage academic workflows across research evidence, scholarly writing, model routing, and publication strategy. Use for substantive end-to-end scholarly tasks that require two or more specialist academic Skills; do not invoke for a simple one-step academic edit that one specialist Skill can handle directly.
---

# Scholarly Agent

The orchestrator for the Scholarly Agent Suite. It does not do research,
writing, routing, or journal-fit work itself -- it decides which of those are
actually needed for a given request, invokes the smallest sufficient set,
and assembles their outputs into one deliverable.

Not a project-management tool, a memory system, or a fifth way to do what the
specialists already do. If a task needs only one specialist, that specialist
should handle it directly -- this Skill exists for the tasks that genuinely
span more than one.

## Ecosystem position

```
Scholarly Agent             -> workflow orchestration (this Skill)
Adaptive Model Router       -> how to execute the task
Scholarly Corpus Builder    -> what scholarly evidence/journal profiles to acquire
Scholarly Voice Engine      -> how the manuscript is argued and written
Journal Fit Engine          -> where the manuscript should be submitted
```

## Responsibility boundary (see shared/capability-boundaries.md)

Responsible for: task decomposition, workflow selection, component
coordination, shared-state handoff, result assembly, and the final
integrity/completeness gate before declaring a workflow done.

Not responsible for: model routing, corpus acquisition logic, academic prose
rules, or journal ranking logic -- those stay inside their owning specialist.
Never duplicate a specialist's internal policy here; if a decision needs
domain judgment (is this evidence sufficient? is this claim overstated?
does this journal fit?), delegate it to the specialist that owns it.

## When to activate

Activate only for a genuinely multi-stage scholarly deliverable -- something
that needs two or more of the four specialists working together toward one
final output. See `references/routing-matrix.md` for the full decision table.

**Do activate** for requests like:
- "Help me turn this idea into a paper and find journals."
- "Improve this manuscript and tell me where to submit it."
- "Help me build and write a research monograph."

**Do not activate** for a one-step task a single specialist already covers:
- "Fix this sentence." / "Polish this paragraph." -> scholarly-voice-engine
- "What does APC mean?" / "Format this DOI." -> answer directly, no Skill
- "Find journals for this finished manuscript." (no further writing wanted)
  -> journal-fit-engine (with scholarly-corpus-builder as its own dependency)
- "Translate this title." -> answer directly

When unsure, prefer the narrower specialist. Reserve activation for tasks
where skipping coordination would force the user to manually chain Skills
themselves (rule 54, rule 56).

## Minimal orchestration rule

Before invoking anything, answer:

1. What is the requested final deliverable?
2. Which specialist capabilities are actually required to produce it?
3. Which relevant artifacts (corpus profile, manuscript profile, journal
   profile, continuity state) already exist and are still fresh enough to
   reuse (`references/orchestration-state.md`)?
4. Which components can be skipped entirely?

Then invoke only the required specialists, in the order the selected
workflow recipe under `references/workflows/` specifies. Never run a fixed
Router -> Corpus -> Voice -> Journal-Fit pipeline "because it's installed" --
see rule 19 and `references/routing-matrix.md`.

## Workflow recipes

Workflow recipes are orchestration resources **owned by scholarly-agent**,
not independent Skills of their own -- they ship inside this Skill's own
package specifically so they resolve from inside its runtime boundary under
every installation mode (full Suite, standalone scholarly-agent install,
`.codex-plugin` load, release ZIP, or a host that only exposes the declared
`skills/` tree). Never resolve them via a parent-directory path
(`../../workflows/` or similar) -- that only happens to work when the whole
repository root is visible next to `skills/`, which is not guaranteed and is
exactly the class of bug that once made this orchestrator wrongly report a
recipe as "missing" when it was only unreachable from where it was looking.

Pick the closest matching recipe from `references/workflows/`:
`references/workflows/paper-from-idea.md`,
`references/workflows/paper-from-notes.md`,
`references/workflows/revise-manuscript.md`,
`references/workflows/journal-selection.md`,
`references/workflows/target-journal-adaptation.md`,
`references/workflows/literature-review.md`,
`references/workflows/theory-paper.md`,
`references/workflows/empirical-paper.md`,
`references/workflows/systematic-review.md`,
`references/workflows/nature-commentary.md`,
`references/workflows/book-project.md`,
`references/workflows/monograph-chapter.md`,
`references/workflows/author-voice-calibration.md`,
`references/workflows/corpus-profile-build.md`.
These are recipes, not Skills -- they describe a stage order and default
component set, not new logic. Adapt the recipe to what already exists (skip
a stage whose artifact is already available and fresh) rather than
following it mechanically.

A theory paper whose target journal is already selected combines
`references/workflows/theory-paper.md` with
`references/workflows/target-journal-adaptation.md`: run the theory-paper
stages (light-touch prior-theory evidence, then argument-architecture
writing), then target-journal-adaptation's stages against the
already-chosen journal -- journal-fit-engine performs adaptation only
(confirm/refresh the profile, produce style context), never a fresh
discovery/shortlist pass, since the venue is not in question.

## Resolving a workflow recipe file

Before ever reporting a workflow recipe as unavailable, actually inspect
this Skill's own installed `references/workflows/` directory --
`scripts/workflow_resolver.py`'s `resolve_workflow()` is the concrete
procedure and returns exactly one of:

- `RESOLVED` -- the file was found; proceed.
- `WORKFLOW_SOURCE_MISSING` -- the requested name is not a workflow recipe
  this orchestrator knows about at all. Safe to report immediately.
- `WORKFLOW_RUNTIME_MISSING` -- the recipe is a real, known one, this
  Skill's own `references/workflows/` directory was actually found and
  read, and the specific file is confirmed absent from it. Only this case
  may be reported as "the installed package is missing `<file>`" --
  because only this case actually inspected the runtime and confirmed it.
- `WORKFLOW_UNRESOLVABLE` -- `references/workflows/` itself could not be
  located or read under the given install root. Report this as a
  runtime-resolution / installation-visibility problem, never as the file
  being missing -- repository/tag metadata saying the workflow exists is
  not overridden by a lookup that never successfully inspected the
  runtime.

## State, reuse, and freshness

Keep only compact, task-local state (`references/orchestration-state.md`
gives the exact shape) -- goal, completed stages, active stage, artifact
references, open issues, limitations. This is not a long-term memory system
(rule 46, rule 130).

Reuse existing artifacts by logical id (`corpus_profile_id`,
`manuscript_profile_id`, `journal_profile_id`, `continuity_state_id`) rather
than rebuilding them, unless a component reports the artifact `stale` and the
current request depends on the stale part (rule 47-49).

## Constraint propagation

Carry the user's hard constraints (e.g. "SSCI only," "no APC," a word limit,
a citation style, a deadline) through every stage without silently dropping
them. Store them as `hard_constraints` vs. `soft_preferences`
(`references/orchestration-state.md`). If hard constraints leave no viable
outcome, report that plainly and suggest the smallest relaxation -- never
silently violate one to produce an answer (rule 111-112).

## Failure propagation and the final quality gate

A specialist's limitation, `PARTIAL` result, or unresolved integrity flag
must survive into the assembled output -- never launder it into an
unqualified "complete" (rule 73, rule 76). Before marking a workflow
`COMPLETE`, check `references/orchestration-state.md`'s gate: deliverable
exists, evidence verified or limitations declared, argument integrity
passed, citations not fabricated, journal claims current where required,
and component outputs used compatible protocol versions (rule 106). If any
check fails, report `COMPLETE_WITH_LIMITATIONS` or a blocked state instead.

Bound repair loops: one main adaptation cycle plus at most one targeted
repair pass. Never cycle a manuscript between two specialists indefinitely
(rule 107).

## Explicit invocation

Advanced users may still explicitly invoke a specialist directly
(`$scholarly-corpus-builder`, `$scholarly-voice-engine`,
`$journal-fit-engine`, `$adaptive-model-router`, `$scholarly-agent`) where the
host supports it -- this Skill does not intercept or require passing through
those explicit calls.

## Reference index

- `references/routing-matrix.md` -- which specialists a given intent needs,
  and the shared error taxonomy (including the workflow-resolution codes).
- `references/orchestration-state.md` -- state shape, freshness handling,
  and the final-quality gate.
- `references/workflows/` -- the fourteen workflow recipes themselves (see
  "Workflow recipes" above); the runtime-canonical copy, resolvable from
  inside this Skill's own package under every installation mode.
- `scripts/workflow_resolver.py` -- resolves a workflow recipe from this
  Skill's own installed runtime and classifies a failed lookup as
  `WORKFLOW_SOURCE_MISSING` / `WORKFLOW_RUNTIME_MISSING` /
  `WORKFLOW_UNRESOLVABLE` (see "Resolving a workflow recipe file" above).
- `scripts/target_journal_adapter.py` -- the hard compatibility gate for
  `TARGET_JOURNAL_PROFILE_V1` (see
  `references/workflows/target-journal-adaptation.md`).
