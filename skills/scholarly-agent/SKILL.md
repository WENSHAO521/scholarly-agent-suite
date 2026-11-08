---
name: scholarly-agent
description: Evidence-first academic research and writing agent for any discipline. Use for scholarly work such as drafting or revising research articles, reviews, commentaries, theses, book chapters and monographs; building literature corpora and discipline, journal, historical or author-voice style profiles; finding and adapting to target journals; and planning how a multi-stage research task should be executed. Loads only the internal module(s) a request needs. Do not invoke for casual, marketing or administrative writing, or for a one-line factual question that needs no scholarly workflow.
---

# Scholarly Agent

One Skill for the whole scholarly workflow. It contains four internal
modules -- execution planning, research evidence, scholarly writing, and
publication strategy -- plus a dispatcher (this file) that decides which of
them a request actually needs, loads only those, hands data between them
through versioned protocols, and runs a final integrity gate.

Until v2.0.0 the four modules were separate Skills (`adaptive-model-router`,
`scholarly-corpus-builder`, `scholarly-voice-engine`, `journal-fit-engine`).
They keep those names as module names, so existing workflow recipes,
protocols, and evals still read correctly.

## Module map

| Module | Owns | Load `MODULE.md` when the request needs... |
|---|---|---|
| `modules/scholarly-voice-engine/MODULE.md` | Writing and argument | drafting, revising, restructuring, claim calibration, citation-integrity checks, author-voice calibration, long-form continuity |
| `modules/scholarly-corpus-builder/MODULE.md` | Research evidence | retrieving or verifying literature, building a corpus, or compiling a discipline / journal / historical / author-voice style profile |
| `modules/journal-fit-engine/MODULE.md` | Publication strategy | a manuscript profile, journal candidates, hard filters (scope, APC, open access, indexing), fit scoring, submission strategy, or a target journal's style context |
| `modules/adaptive-model-router/MODULE.md` | Execution planning | deciding model tier, reasoning effort, subagent delegation, validation depth, or escalation for a large or high-stakes task (only meaningful when the host can actually dispatch) |

Load a `MODULE.md` only when it is selected; never load all four "just in
case." Each module's `references/` files are loaded on demand from inside
that module, exactly as its `MODULE.md` directs. Paths in a `MODULE.md` are
relative to that module's own directory, and where a module's text says
"this Skill" or names another former Skill, read it as "this module" or the
sibling module of that name.

## Dispatch

Before loading anything, answer:

1. What is the requested final deliverable?
2. Which module capabilities are actually required to produce it?
3. Which artifacts (corpus profile, manuscript profile, journal profile,
   continuity state) already exist and are still fresh enough to reuse
   (`references/orchestration-state.md`)?
4. Which modules can be skipped entirely?

Then follow one of three paths:

- **No module.** A one-line factual or formatting question is answered
  directly. **Do not activate** a workflow for, e.g., "Fix this sentence"
  (a single obvious grammar fix), "What does APC mean?", "Format this DOI",
  or "Translate this title".
- **Single module.** The request sits inside one module's scope, e.g.
  "polish this paragraph" (voice), "build a journal style profile"
  (corpus), "find journals for this finished manuscript" (journal fit).
  Load that one `MODULE.md` and follow it. No workflow recipe, no
  orchestration state.
- **Multi-module workflow.** The deliverable genuinely needs two or more
  modules, e.g. "turn this idea into a paper and find journals." Pick a
  workflow recipe (below), keep compact orchestration state, and load each
  module only when its stage starts.

When unsure between paths, prefer the narrower one. Never run a fixed
Router -> Corpus -> Voice -> Journal-Fit pipeline for every request; see
`references/routing-matrix.md` for which intents need which modules.

## Workflow recipes

Workflow recipes ship inside this Skill so they resolve from its own
runtime boundary under every installation mode. Never resolve them via a
path that climbs out of this Skill directory; the repository-root
`workflows/` folder is only a generated documentation mirror.

Pick the closest matching recipe:
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
A recipe describes a stage order and default module set, not new logic.
Adapt it to what already exists (skip a stage whose artifact is available
and fresh) rather than following it mechanically.

A theory paper whose target journal is already selected combines
`references/workflows/theory-paper.md` with
`references/workflows/target-journal-adaptation.md`: run the theory-paper
stages (light-touch prior-theory evidence, then argument-architecture
writing), then target-journal-adaptation's stages against the
already-chosen journal. The journal-fit module performs adaptation only
(confirm/refresh the profile, produce style context), never a fresh
discovery/shortlist pass, since the venue is not in question.

## Resolving a workflow recipe file

Before ever reporting a workflow recipe as unavailable, actually inspect
this Skill's own installed `references/workflows/` directory.
`scripts/workflow_resolver.py`'s `resolve_workflow()` is the concrete
procedure and returns exactly one of:

- `RESOLVED` -- the file was found; proceed.
- `WORKFLOW_SOURCE_MISSING` -- the requested name is not a known workflow
  recipe. Safe to report immediately.
- `WORKFLOW_RUNTIME_MISSING` -- the recipe is real, `references/workflows/`
  was found and read, and the file is confirmed absent. Only this case may
  be reported as "the installed package is missing `<file>`."
- `WORKFLOW_UNRESOLVABLE` -- `references/workflows/` itself could not be
  located or read. Report a runtime-resolution problem, never a missing
  file.

## Handoffs between modules

Modules exchange data only through the versioned JSON Schemas in
`protocols/`, never through ad hoc prose summaries:

| Protocol | Schema | Typical producer -> consumer |
|---|---|---|
| `EXECUTION_POLICY_V1` | `protocols/execution-policy.schema.json` | router -> dispatcher (bounds each stage) |
| `SCHOLARLY_PROFILE_V1` | `protocols/scholarly-profile.schema.json` | corpus -> voice, journal fit |
| `VOICE_REQUEST_V1` | `protocols/voice-request.schema.json` | dispatcher -> voice |
| `VOICE_CONTEXT_V1` | `protocols/voice-context.schema.json` | dispatcher -> voice |
| `VOICE_OUTPUT_V1` | `protocols/voice-output.schema.json` | voice -> dispatcher |
| `MANUSCRIPT_PROFILE_V1` | `protocols/manuscript-profile.schema.json` | voice or user -> journal fit |
| `TARGET_JOURNAL_PROFILE_V1` | `protocols/journal-profile.schema.json` | journal fit -> dispatcher gate |
| `JOURNAL_STYLE_CONTEXT_V1` | `protocols/journal-style-context.schema.json` | journal fit (or corpus observed patterns) -> voice |
| `CONTINUITY_STATE_V1` | `protocols/continuity-state.schema.json` | voice <-> voice (long-form) |
| `PROVENANCE_RECORD_V1` | `protocols/provenance.schema.json` | embedded in profiles, journal contexts, continuity state |

A producer emitting a protocol version the consumer does not recognize is a
`PROTOCOL_MISMATCH`; report it, never guess around it
(`shared/protocol-versioning.md`). `scripts/target_journal_adapter.py` is
the hard compatibility gate for `TARGET_JOURNAL_PROFILE_V1` (see
`references/workflows/target-journal-adaptation.md`).

## Module boundaries

The merge put the modules in one Skill; it did not merge their
responsibilities. `shared/capability-boundaries.md` is the single source of
truth for who may decide what. In short: the router never sets corpus
policy, the corpus module never recommends journals, the voice module never
routes models, the journal-fit module never fabricates current metrics, and
this dispatcher never re-implements a module's domain rules -- it delegates
the decision to the module that owns it.

## State, reuse, and freshness

For multi-module workflows only, keep compact, task-local state
(`references/orchestration-state.md` gives the exact shape): goal,
completed stages, active stage, artifact references, open issues,
limitations. This is not a long-term memory system.

Reuse existing artifacts by logical id (`corpus_profile_id`,
`manuscript_profile_id`, `journal_profile_id`, `continuity_state_id`) rather
than rebuilding them, unless a module reports the artifact `stale` and the
current request depends on the stale part.

## Constraint propagation

Carry the user's hard constraints (e.g. "SSCI only," "no APC," a word limit,
a citation style, a deadline) through every stage without silently dropping
them. Store them as `hard_constraints` vs. `soft_preferences`
(`references/orchestration-state.md`). If hard constraints leave no viable
outcome, report that plainly and suggest the smallest relaxation -- never
silently violate one to produce an answer.

## Failure propagation and the final quality gate

A module's limitation, `PARTIAL` result, or unresolved integrity flag must
survive into the assembled output -- never launder it into an unqualified
"complete." Before marking a workflow `COMPLETE`, check
`references/orchestration-state.md`'s gate: deliverable exists, evidence
verified or limitations declared, argument integrity passed, citations not
fabricated, journal claims current where required, and module outputs used
compatible protocol versions. If any check fails, report
`COMPLETE_WITH_LIMITATIONS` or a blocked state instead.

Bound repair loops: one main adaptation cycle plus at most one targeted
repair pass. Never cycle a manuscript between two modules indefinitely.

## Integrity

`shared/integrity-policy.md` applies to every module and is
non-negotiable: no fabricated citations, DOIs, quotations, journal metrics,
corpus counts, or acceptance probabilities; no paywall bypass or shadow
libraries; no imitation of a living author's voice; no AI-detector evasion
as a goal. Provenance rules are in `shared/provenance-policy.md` and
shared vocabulary in `shared/terminology.md`.

## Runtime code

Some modules ship optional, tested Python engines. Each is importable by
putting its module directory on `sys.path`:

- `modules/scholarly-corpus-builder/scb/` -- source adapters, OA
  resolution, deduplication, style analytics, profile compilation
  (`import scb`).
- `modules/journal-fit-engine/jfe/` -- manuscript profiling, hard filters,
  fit model, POSI snapshot lookup (`jfe/posi.py`), `TARGET_JOURNAL_PROFILE_V1`
  and `JOURNAL_STYLE_CONTEXT_V1` producers (`import jfe`).
- `modules/scholarly-voice-engine/scripts/voice/` -- profile merge,
  continuity ledger, prose audit, journal-context consumer
  (`import scripts.voice`; load it separately from this Skill's own
  `scripts/` to avoid a package-name clash).

## Reference index

- `references/routing-matrix.md` -- which modules a given intent needs, and
  the shared error taxonomy (including the workflow-resolution codes).
- `references/orchestration-state.md` -- state shape, freshness handling,
  and the final quality gate.
- `references/workflows/` -- the fourteen workflow recipes.
- `scripts/workflow_resolver.py` -- resolves a workflow recipe and
  classifies a failed lookup.
- `scripts/target_journal_adapter.py` -- hard compatibility gate for
  `TARGET_JOURNAL_PROFILE_V1`.
- `shared/capability-boundaries.md`, `shared/integrity-policy.md`,
  `shared/provenance-policy.md`, `shared/protocol-versioning.md`,
  `shared/terminology.md` -- cross-module policy.
