# Shared capability boundaries

Each specialist Skill owns a distinct responsibility. This table is the single
source of truth for "who is not allowed to do this" -- when in doubt about
whether a Skill should perform an action, check here before extending its
scope.

## Boundaries

- **adaptive-model-router does not write corpus policy.** It may say "this
  stage needs current external evidence" but never dictates which sources
  scholarly-corpus-builder should query or how it dedups/samples.
- **scholarly-corpus-builder does not recommend journals.** It supplies
  journal *evidence* (`SCHOLARLY_PROFILE_V1`, profile_type=journal /
  `JOURNAL_STYLE_CONTEXT_V1` observed_patterns) -- ranking and fit judgment
  belong to journal-fit-engine alone.
- **scholarly-voice-engine does not route models.** It consumes an
  `EXECUTION_POLICY_V1` if one is supplied but never selects a model, decides
  delegation, or overrides adaptive-model-router's execution decisions.
- **journal-fit-engine does not fabricate current metrics.** If current
  evidence (APC, indexing, acceptance policy) cannot be verified, it reports
  `unknown`/`NOT_ASSESSED` rather than reusing a stale or estimated value as if
  current (rule 74, rule 105).
- **scholarly-agent does not duplicate specialist logic.** It decomposes
  tasks, selects the minimal specialist set, and assembles results -- it does
  not itself perform routing, corpus acquisition, prose writing, or journal
  ranking (rule 3, rule 156).

## Why this matters

A Suite is only worth building if "integrate, do not collapse" (the Suite's
core design principle) is enforced structurally, not just stated. If any
component starts reimplementing another's responsibility, the family
degrades back into one monolithic Skill with extra files around it -- exactly
what rule 155 forbids.

## Enforcement in practice

- `scholarly-agent`'s routing matrix (`skills/scholarly-agent/references/routing-matrix.md`)
  is written entirely in terms of *which specialist* handles a need, never
  "how" -- the how stays inside that specialist's own SKILL.md.
- Suite-level tests (`tests/test_capability_boundaries.py`) grep each
  bundled `SKILL.md` for language that would indicate scope creep (e.g. the
  orchestrator's SKILL.md directly prescribing citation-formatting rules)
  and fail the build if found.
