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
workflow recipe under `workflows/` specifies. Never run a fixed
Router -> Corpus -> Voice -> Journal-Fit pipeline "because it's installed" --
see rule 19 and `references/routing-matrix.md`.

## Workflow recipes

Pick the closest matching recipe from `workflows/` (`paper-from-idea.md`,
`paper-from-notes.md`, `revise-manuscript.md`, `journal-selection.md`,
`target-journal-adaptation.md`, `literature-review.md`, `theory-paper.md`,
`empirical-paper.md`, `systematic-review.md`, `nature-commentary.md`,
`book-project.md`, `monograph-chapter.md`, `author-voice-calibration.md`,
`corpus-profile-build.md`). These are recipes, not Skills -- they describe a
stage order and default component set, not new logic. Adapt the recipe to
what already exists (skip a stage whose artifact is already available and
fresh) rather than following it mechanically.

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

- `references/routing-matrix.md` -- which specialists a given intent needs.
- `references/orchestration-state.md` -- state shape, freshness handling,
  the final-quality gate, and the shared error taxonomy.
