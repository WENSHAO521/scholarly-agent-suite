# Shared capability boundaries

Since v2.0.0 the four specialists are modules of the single `scholarly-agent`
Skill (`modules/<name>/MODULE.md`), but each module still owns a distinct
responsibility. This page is the single source of truth for "who is not
allowed to do this" -- when in doubt about whether a module should perform an
action, check here before extending its scope.

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
- **The scholarly-agent dispatcher (`SKILL.md`) does not duplicate module
  logic.** It decomposes tasks, selects the minimal module set, and
  assembles results -- it does not itself perform routing, corpus
  acquisition, prose writing, or journal ranking (rule 3, rule 156).

## Why this matters

Merging the specialists into one Skill removed the cost of installing,
versioning, and syncing five packages; it did not license one module to
absorb another's job. If a module starts reimplementing a sibling's
responsibility, the Skill degrades into one undifferentiated prompt -- the
failure mode the module split exists to prevent. Boundaries are now enforced
inside one package instead of between packages.

## Enforcement in practice

- The routing matrix (`references/routing-matrix.md`) is written entirely in
  terms of *which module* handles a need, never "how" -- the how stays inside
  that module's own `MODULE.md`.
- Modules exchange data only through the versioned schemas in `protocols/`.
  `tests/test_e2e_protocol_handoff.py` and `tests/test_e2e_module_handoffs.py`
  run real producer code into real consumer code across modules.
- Suite-level tests (`tests/test_capability_boundaries.py`) grep the
  dispatcher's `SKILL.md` for language that would indicate scope creep (e.g.
  directly prescribing citation-formatting rules or naming specific models)
  and fail the build if found.
