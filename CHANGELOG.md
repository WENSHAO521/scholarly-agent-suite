# Changelog

All notable changes to the Scholarly Agent Suite are documented in this file.
Suite versioning follows `docs/development.md#suite-versioning` /
`skills/scholarly-agent/shared/protocol-versioning.md`. Since v2.0.0 modules
have no versions of their own; `COMPONENTS.json` records where each module
was merged from.

## v2.2.0 -- 2026-11-09

v2.2.0 PREPARED -- NOT PUBLISHED

**A sixth module for polishing prose in any language.** Installing and
invoking the Skill is unchanged; nothing existing was renamed.

### Added

- **`prose-polish-engine` module** (`modules/prose-polish-engine/`), with
  its own page (`MODULE.md`). It removes the "language watermark" of
  templated writing (潤色、去 AI 味): stock connectives, empty emphasis
  ("plays a crucial role", 「具有重要意義」), inflated vocabulary, formulaic
  openings and closings, stacked hedges, contrast templates,
  nominalizations, repeated sentence and paragraph openers, uniform
  sentence rhythm, reflexive three-item lists, and dash habits. Three
  levels (`light`, `standard`, `deep`); none changes claims, claim
  strength, evidence, citations, quotations, or defined terms, and
  argument-level problems are handed to the voice module as escalations.
- **Every language.** Phrase catalogs for English, Chinese (Traditional
  and Simplified), Japanese, Korean, Spanish, French, German, Portuguese,
  and Russian (173 patterns); language detection for any language by
  script and function words; structural checks and protected-item checks
  for every language, with a written procedure for languages without a
  catalog (`references/other-languages.md`). The author's language, script,
  and regional variety are kept; polishing never translates.
- **Runtime `ppe/`** (standard library): `ppe.diagnose` (findings, density,
  `pattern_load`), `ppe.invariants` (every citation, DOI, URL, number,
  quotation, and formula must survive unchanged; protected terms keep their
  exact form; hedge, negation, and length changes are flagged for review),
  `ppe.report`, and `python -m ppe diagnose|check`.
- **`POLISH_REPORT_V1`** protocol (`protocols/polish-report.schema.json`):
  load before and after, change log, findings kept on purpose, invariant
  result, and a fixed notice that pattern counts are not an authorship
  estimate. The dispatcher's quality gate treats `FAIL` as blocked.
- Integrity: the module improves the writing; it never scores text for AI
  authorship, never runs or loops against an AI-text detector, never adds
  noise, typos, invisible characters, or homoglyphs, and reminds authors
  that AI-use disclosure rules still apply (integrity rule 14).
- Evals (`evals/modules/prose-polish-engine/`), three orchestration
  fixtures, 47 tests (`tests/modules/ppe/`), and a sixth card in both
  architecture diagrams.

### Changed

- Routing: wording-only polishing goes to the polish module; the voice
  module keeps drafting, revising, and structural edits. The polish module
  can run once as the final language pass of a writing workflow.

## v2.1.0 -- 2026-11-09

v2.1.0 PREPARED -- NOT PUBLISHED

**A fifth module for pre-submission peer review, reference-manager import and
export, a platform-neutral model router, and fixes for problems the v2.0.0
merge left behind.** Installing and invoking the Skill is unchanged. Two
renames can affect scripts that read module files directly: two
journal-fit discipline files and the router's eval/record keys (see
Changed).

### Added

- **`peer-review-engine` module** (`modules/peer-review-engine/`), the first
  module built here rather than merged in. An editor desk-screens the
  manuscript, picks a panel of 2-3 reviewers with distinct lenses (methods,
  statistics, theory, literature, field, ethics-integrity, devil's advocate,
  generalist; defaults per article type and discipline), runs each reviewer
  as an isolated, read-only subagent when the host can dispatch (within the
  router's delegation caps) or sequentially in one model otherwise (and says
  so), then decides from the **upheld concerns**, not a vote count:
  unfixable fatal -> reject, fixable fatal -> reject-and-resubmit, major ->
  major revision, minor -> minor revision. The editor may be stricter with a
  reason, never more lenient without dismissing concerns explicitly.
  Reviewer disagreements are recorded, not hidden. Outputs a decision
  letter, a response matrix of numbered required changes, and one
  second-round check of the revision and response letter. Reports and letters read
  like a real journal's (no "simulation" wording in the body), followed by
  a submission-readiness verdict and one closing line saying the review was
  prepared by Scholarly Agent before submission, not by any journal; no
  acceptance probabilities, no impersonated named reviewers or editors, and a stop-and-warn rule for confidential manuscripts the user
  was sent as a reviewer. Runtime: `prv/` (panel, report validation,
  decision, response matrix, second round), standard library only.
- Protocols `REVIEW_REPORT_V1` (`protocols/review-report.schema.json`) and
  `EDITORIAL_DECISION_V1` (`protocols/editorial-decision.schema.json`).
- Workflow recipe `pre-submission-review` (review, optional revision and
  response letter by the voice module, one second round).
- **Reference-manager import and export** in the corpus module
  (`scb/bibliography.py`, `references/reference-managers.md`): BibTeX (with
  `@string` macros, `#` concatenation, LaTeX accents), RIS, and CSL-JSON, so
  Zotero, Mendeley, EndNote, and JabRef libraries can seed a corpus or serve
  as citation sources, and results can be exported back. Imported records are
  `NEEDS_CHECK` until an adapter lookup verifies them; malformed DOIs or
  years are left empty and listed as conflicts, never guessed. CLI:
  `scb.cli import-bib` / `export-bib`.
- **`scb.compiler.build_provenance_record_v1()`**, the first real producer of
  `PROVENANCE_RECORD_V1`, built from the records a profile came from:
  identity from DOI/PMID/arXiv/URL or an explicit user-supplied marker,
  verified only when an adapter verified it, and `conflicting` with notes
  when fields disagree or a source has no identifier. Previously the record
  was only ever hand-written in tests.
- **Platform mapping for the model router**
  (`references/routing-policy.md#platform-mapping`): how its Luna/Terra/Sol
  (standard tier) and Astra (expert tier) roles map onto OpenAI/Codex,
  Claude, Gemini, local, and single-model hosts.
- `shared/disciplines.md`: one discipline taxonomy (11 families) for every
  module.
- Tests: `test_e2e_provenance_handoff.py`, `test_disciplines.py`,
  `test_router_platform_neutral.py`, `test_markdown_links.py`,
  `tests/modules/prv/`, `tests/modules/scb/test_scb_bibliography.py`.
  Evals: `evals/modules/peer-review-engine/` and new dispatch cases for
  peer review and library import.

### Changed

- **adaptive-model-router is platform-neutral.** Its gates and budgets no
  longer say "GPT-5-family" and "GPT-6"; they use the standard tier and
  expert tier. Eval and record keys renamed accordingly: `gpt6` ->
  `expert_dispatch`, `gpt5_attempt` -> `standard_tier_attempt`,
  `gpt6_reason` -> `expert_reason`, and `gpt6_*` task-state counters ->
  `expert_*`.
- **Discipline files unified.** journal-fit-engine's `management.md` and
  `mathematics.md` renamed to `business-management.md` and
  `mathematics-formal.md` to match the voice module, and its arts section
  moved out of `humanities.md` into its own `arts-design.md`. Both modules
  now have the same 11 files.
- Architecture diagram and flowchart redrawn with five modules, plus
  Traditional Chinese versions (`assets/*.zh-TW.svg`) used by
  `README.zh-TW.md`; README
  (English and Traditional Chinese), `docs/development.md`, routing matrix,
  capability boundaries, plugin manifest, and `agents/openai.yaml` updated.
- `COMPONENTS.json` allows a native module (`"origin": {"native": true,
  "added_in": ...}`) alongside merged ones.

### Fixed

- Dead links left by the v2.0.0 move: the router's references pointed at
  `../SKILL.md` (now `../MODULE.md`) and a `THIRD_PARTY_NOTICES.md` that was
  never merged; module files throughout still said "see `SKILL.md`" for
  their own instructions.
- `scb.cli validate` called a `scripts/validate_skill.py` that no longer
  exists; the subcommand is removed. Module docs that pointed at that script
  or at a module README now point at the Suite's validator and tests.
- `scb.__version__` read a per-module `VERSION` file removed by the merge, so
  every corpus build manifest recorded builder version `0.0.0`; it now reads
  the Suite `VERSION`.
- CHANGELOG: v2.0.0 marked PUBLISHED; v1.2.1 noted as never released on its
  own.

## v2.0.0 -- 2026-11-08

v2.0.0 PUBLISHED

**The four specialist Skills are merged into one Skill.** The Suite now
ships a single Skill, `scholarly-agent`, with the former specialists as
on-demand internal modules. This is a breaking change for anyone who
installed or invoked a specialist Skill by name (`$scholarly-voice-engine`,
etc.): those names no longer register as Skills.

### Changed

- `skills/adaptive-model-router/`, `skills/scholarly-corpus-builder/`,
  `skills/scholarly-voice-engine/`, `skills/journal-fit-engine/` moved to
  `skills/scholarly-agent/modules/<name>/`. Each `SKILL.md` became a
  frontmatter-free `MODULE.md` with a header stating its scope and that its
  paths are module-relative. Per-module `agents/openai.yaml` files were
  folded into the one `skills/scholarly-agent/agents/openai.yaml`. Module
  content is otherwise unchanged from the merged releases (router v0.3.0,
  corpus v0.9.2, voice v1.1.0, journal fit v0.4.0) apart from the two
  handoff fixes below.
- `protocols/` and `shared/` moved inside the Skill
  (`skills/scholarly-agent/protocols/`, `skills/scholarly-agent/shared/`),
  so everything the Skill needs resolves from its own directory under every
  install mode -- the same lesson as the v1.2.1 workflow-recipe fix.
- `SKILL.md` rewritten as a dispatcher: a module map, three dispatch paths
  (no module / single module / multi-module workflow recipe), a protocol
  handoff table, module boundaries, and the existing workflow, state,
  constraint, and quality-gate rules. The description now covers every
  module's domain instead of only "two or more specialists."
- `COMPONENTS.json` now lists one `skill` and four `modules`, each with a
  `merged_from` record (repository, release, commit). Suite version 2.0.0.
- `shared/capability-boundaries.md` and `shared/integrity-policy.md` updated
  for modules inside one Skill; the boundaries themselves are unchanged.
- `validate_suite.py`, `package_suite.py`, and the tests now enforce the
  single-Skill layout: exactly one Skill under `skills/`, no `SKILL.md` or
  frontmatter inside modules, and every module/protocol/shared reference
  resolving inside the Skill.
- README (English and Traditional Chinese) rewritten for the single-Skill
  design, with a new architecture diagram
  (`assets/scholarly-agent-architecture.svg`, replacing
  `suite-architecture-diagram.svg`) and an updated orchestration flowchart.
  `docs/development.md` rewritten for the in-tree development model.

### Fixed

- **SCHOLARLY_PROFILE_V1 handoff (corpus -> voice).**
  `scb.compiler.compile_scholarly_profile_v1()` never produced a
  schema-valid `SCHOLARLY_PROFILE_V1`: no required `provenance` record,
  `provenance_summary`/`known_biases`/`sample_size_label` fields the schema
  forbids, a confidence value (`medium`) outside the schema enum, and
  scb-internal stability labels. Added
  `compile_scholarly_profile_protocol_v1()`, which requires a real
  `PROVENANCE_RECORD_V1`, takes the weakest measured-feature confidence
  (never overstating), maps `MOSTLY_STABLE` to `unstable` with the reason
  recorded in `biases`, and validates against the shared schema. The old
  function is kept unchanged for existing callers.
- **MANUSCRIPT_PROFILE_V1 handoff (envelope -> journal fit).** A
  schema-valid envelope was rejected by `jfe`'s
  `ManuscriptProfile.from_dict()` (unknown `protocol` field, `contribution`
  vs `central_contribution`, string vs list `methods`, a different
  article-type vocabulary). Added
  `jfe.manuscript_profile.from_manuscript_profile_v1()`.
- New `tests/test_e2e_module_handoffs.py` drives both handoffs with real
  module code, including the real journal-fit model.

### Added

- **Module tests and evals merged in.** 469 unit tests from the former
  component repositories now live in `tests/modules/{scb,jfe,voice}/` (file
  names prefixed by module to avoid collisions; fixtures included), and 377
  eval cases in `evals/modules/<module>/`. `tests/conftest.py` puts the
  module engines on `sys.path`. Not merged: each former repository's tests
  of its own `package_runtime.py` / `validate_skill.py`, which do not exist
  here. The router module has evals only; it never had unit tests.
- **POSI as a journal-fit evidence source** (`jfe/posi.py`). Reads an
  immutable POSI snapshot (from a local directory, or downloaded from
  data.posi.panorama-sg.com with GitHub release assets as fallback, verified
  against the snapshot's SHA256SUMS and cached). Exact ISSN or title lookup
  only; ambiguous titles return no match. Reports POSI's Citation Quartile
  only with its POSI category, metric year, and methodology version, never
  as a JCR/SJR/CiteScore quartile; treats only `official` ranking status as
  verified; cites the snapshot with every result; adds a conflict-of-interest
  disclosure for journals published by POSI's operator, Panorama Scholarly
  Group. `indexing.assess_indexing(..., posi=)` adds a "POSI" entry,
  `apply_to_evidence()` fills missing OA/DOAJ/APC fields without
  overwriting, and `jfe.cli posi-lookup` exposes it. Rules documented in the
  module's `references/indexing-metrics.md`. 32 tests against a fixture cut
  from real snapshot 2026-11-08.

- **Automatic packaging and publishing.** `.github/workflows/release.yml`
  now runs on every push to `master` (and on `v*` tags and manual dispatch):
  if release `v<VERSION>` does not exist, it validates, tests, builds the
  runtime ZIP twice and requires identical SHA-256, and publishes the release
  with the ZIP, `release-manifest.json`, `SHA256SUMS`, and the CHANGELOG
  section as notes (new `scripts/release_notes.py`). It never overwrites an
  existing release and rejects a tag that does not match `VERSION`. Tested in
  `tests/test_release_automation.py`.
- **New "how it works" flowchart** (`assets/orchestration-flowchart.svg`),
  redrawn for the single-Skill dispatcher: three dispatch paths, the
  multi-module workflow stages, the six-check quality gate with one repair
  pass, and the three outcomes.

### Removed

- `scripts/sync_components.py`, `scripts/component-sources.json`,
  `scripts/check_component_drift.py`, `.github/workflows/component-drift.yml`,
  and `tests/test_component_drift.py`. Modules are developed in this
  repository now; there is nothing to sync or drift from.

### Not changed

- The former component repositories were not modified, archived, or
  deleted. Whether to archive them is a separate owner decision.

## v1.2.1 -- 2026-09-13

v1.2.1 PREPARED -- NOT PUBLISHED

(Never published as its own release: its fix shipped inside v2.0.0.)

**Workflow packaging/runtime-visibility fix.** During an end-to-end
theoretical-paper orchestration run, scholarly-agent reported that the
installed package was missing `theory-paper.md`. That diagnosis was wrong
in the specific way that matters: `workflows/theory-paper.md` existed on
`master`, existed in tag `v1.2.0`, was already included by
`package_suite.py`'s `RUNTIME_ALLOWLIST`, and was already documented in
`skills/scholarly-agent/SKILL.md`. The real defect was architectural, not a
missing file: `scholarly-agent`'s only path to any workflow recipe was
`workflows/` *one level above its own Skill directory*
(`skills/scholarly-agent/../../workflows/`), which only resolves when the
whole repository root happens to be visible next to `skills/` -- not
guaranteed for a standalone scholarly-agent install, a `.codex-plugin`
load, a release ZIP extracted on its own, or a host that only exposes the
declared `skills/` tree. The orchestrator also never actually inspected an
installed runtime before reporting "missing," so a resolution failure and a
genuine packaging gap were indistinguishable.

### Added

- **Runtime-canonical workflow location**:
  `skills/scholarly-agent/references/workflows/` now holds all fourteen
  workflow recipes as scholarly-agent's own bundled content -- it resolves
  from inside this Skill's own runtime boundary under every installation
  mode. `SKILL.md` now references every recipe by its in-package path
  (`references/workflows/<name>.md`); no reference to a parent-directory
  `workflows/` path remains.
- `scripts/workflow_manifest.py` -- the single `REQUIRED_WORKFLOWS` source
  of truth every test, `validate_suite.py`, and `sync_workflows.py` import,
  replacing four independently-maintained copies of the same 14-item list.
- `scripts/sync_workflows.py` -- regenerates (or `--check`s) the
  repository-root `workflows/` directory as a generated documentation
  mirror of the canonical copy above. `workflows/` is never hand-edited
  again; there is exactly one manually-editable copy of each recipe.
  `validate_suite.py` now fails if the mirror drifts from the canonical
  source.
- `skills/scholarly-agent/scripts/workflow_resolver.py` -- resolves a
  workflow recipe from an installed scholarly-agent runtime and classifies
  a failed lookup as one of `WORKFLOW_SOURCE_MISSING` (not a real recipe),
  `WORKFLOW_RUNTIME_MISSING` (a real recipe, the runtime directory was
  actually inspected, and the file is confirmed absent -- the only case
  that may honestly be reported as "the installed package is missing
  `<file>`"), or `WORKFLOW_UNRESOLVABLE` (the runtime directory itself
  could not be located/read -- a resolution problem, never proof of
  absence). Documented in `SKILL.md`'s new "Resolving a workflow recipe
  file" section and `references/routing-matrix.md`'s new "Workflow-
  resolution error taxonomy" section.
- `references/workflows/theory-paper.md` gained a "Voice Engine emphasis"
  section (construct definition, theoretical mechanism, proposition
  architecture, causal/conceptual chain, boundary conditions, rival
  explanations, theoretical contribution, falsifiability where applicable)
  and a "Combining with target-journal-adaptation" section for the case
  where a theory paper's target journal is already selected: corpus stays
  a light-touch prior-theory sweep even with the adaptation stage added,
  and journal-fit-engine performs adaptation only, never a fresh discovery
  pass.
- `evals/orchestration-cases.jsonl`: `theory-target-001` -- "Develop a
  theoretical paper for an already-selected target journal," exercising
  the combined `theory-paper` + `target-journal-adaptation` recipe with the
  expected minimum specialist set (`scholarly-corpus-builder`,
  `scholarly-voice-engine`, `journal-fit-engine`; the Adaptive Model Router
  remains an optional execution layer). `tests/test_evals.py` asserts this
  fixture's specialist set and combined-recipe framing directly.
- Packaging regression tests (`tests/test_workflow_packaging.py`): every
  required workflow recipe proven present in (1) the source runtime
  boundary, (2) `package_suite.iter_runtime_files()`, (3) the built release
  ZIP, (4) `release-manifest.json`, and (5) a standalone-copied
  scholarly-agent package -- plus a negative test proving a genuinely
  missing recipe is actually caught, and a drift guard between
  `workflow_resolver.py`'s embedded recipe list and the shared manifest.
- Install/runtime smoke test (`tests/test_workflow_install_smoke.py`):
  builds the filesystem layout an installed scholarly-agent Skill actually
  receives (no repository root, no top-level `workflows/`, no `shared/` or
  `protocols/`) and resolves `SKILL.md`, the workflow index, and
  `theory-paper.md` / `empirical-paper.md` / `target-journal-adaptation.md`
  from inside it; includes a test that fails if a recipe is reachable only
  via the repository-root mirror and not from the installed runtime, and a
  test proving `WORKFLOW_UNRESOLVABLE` (not a false "missing") is reported
  when the runtime directory itself is absent.
- `tests/test_standalone_independence.py`: a new
  `test_scholarly_agent_all_internal_references_resolve_within_own_directory`
  check -- scholarly-agent's own `references/workflows/*.md` and
  `scripts/*.py` links in `SKILL.md` must resolve inside its own directory,
  the same completeness guarantee specialists already had.

### Changed

- **scholarly-corpus-builder re-pinned to v0.9.2** (`844735f`, was v0.9.1
  `ec80236`). v0.9.2 is a packaging-reproducibility patch in the component
  repository only (CRLF/LF normalization and cross-platform ZIP metadata
  in its own `package_runtime.py`); no `scb/` code, schema, API, or
  `SKILL.md` changed, so the synced `skills/scholarly-corpus-builder/` tree
  is byte-identical and only `scripts/component-sources.json` and
  `COMPONENTS.json` move. `check_component_drift.py --fetch` now reports
  all four components `CURRENT`.
- **README rewritten as a user-facing introduction**: what the Suite does,
  a "what you can ask it" table mapping each request to its workflow recipe
  and the specialists that recipe actually uses, the five Skills, how
  orchestration works, install, and integrity guarantees. Maintainer
  material (versioning, development model, drift detection, standalone
  compatibility, testing, runtime package, limitations) moved verbatim to
  `docs/development.md`, plus a new "Suite versioning" section that
  `shared/protocol-versioning.md` already linked to but which never
  existed. Added a Traditional Chinese introduction, `README.zh-TW.md`.
  `docs/` and `README.zh-TW.md` are repository documentation, not part of
  the runtime package.

- `skills/scholarly-agent/SKILL.md`: "Workflow recipes" section rewritten
  to state plainly that workflow recipes are orchestration resources owned
  by scholarly-agent, not independent Skills, and to reference every recipe
  by its in-package path.
- `scripts/package_suite.py`, `scripts/validate_suite.py`,
  `tests/test_workflows.py`: now import `REQUIRED_WORKFLOWS` from
  `scripts/workflow_manifest.py` instead of maintaining separate copies of
  the same list.
- `README.md`, `RELEASE_CHECKLIST.md`: document the new canonical location,
  the generated `workflows/` mirror and its drift check, and the new
  regression/smoke tests. `RELEASE_CHECKLIST.md` adds an explicit "inspect
  the built ZIP directly" step for `references/workflows/theory-paper.md`.

### Known limitations

- The repository-root `workflows/` mirror is retained for anyone browsing
  the repo directly or following an existing link to it; it is generated
  and drift-checked, never a second source of truth, but it does mean two
  physical copies of each file still exist on disk (by design, not by
  oversight -- see `scripts/sync_workflows.py`).
- `skills/scholarly-agent/scripts/workflow_resolver.py` embeds its own
  literal `KNOWN_WORKFLOWS` list rather than importing
  `scripts/workflow_manifest.py`, because it must keep working when
  scholarly-agent is installed completely standalone with no Suite
  `scripts/` directory nearby. A dedicated test keeps the two lists in
  sync; nothing prevents a future edit to one without the other except that
  test.
- This release does not change any component pin (`adaptive-model-router`
  `0.3.0`, `scholarly-corpus-builder` `0.9.1`, `scholarly-voice-engine`
  `1.1.0`, `journal-fit-engine` `0.4.0` all unchanged) -- it is a
  Suite-internal packaging/documentation/orchestration fix only.

## v1.2.0 -- 2026-09-09

v1.2.0 PUBLISHED

**Protocol Closure Phase**: `TARGET_JOURNAL_PROFILE_V1` moves from a
schema-validated producer with no consumer (`PARTIAL`, as of v1.1.1) to a
real producer -> consumer handoff. `journal-fit-engine`'s
`jfe.target_journal_profile.build_target_journal_profile()` (unchanged --
already shipped in v0.4.0/v1.1.1) is not touched by this release; the new
work is entirely a downstream consumer inside this Suite, plus the tests
that prove the handoff is real.

### Added

- `skills/scholarly-agent/scripts/target_journal_adapter.py` --
  scholarly-agent's first real code (not just orchestration prose)
  consuming a component protocol directly. Validates an incoming
  `TARGET_JOURNAL_PROFILE_V1` envelope, applies a hard compatibility gate
  against the manuscript's own stated hard constraints (`no_mandatory_apc`,
  `requires_indexing`) and returns `SELECTED` / `REJECTED` /
  `NEEDS_VERIFICATION` with reasons, limitations, and the profile's
  `PROVENANCE_RECORD_V1` preserved unchanged. An unresolved fact (unknown
  `apc_status`, an unconfirmed requested index) is always
  `NEEDS_VERIFICATION`, never a guessed pass or fail; a confirmed mismatch
  is `REJECTED` and a stale profile never softens an existing `REJECTED`
  back to selectable. `journal_style_context_seed()` hands a `SELECTED`
  profile's identity/freshness/provenance forward toward a
  `JOURNAL_STYLE_CONTEXT_V1` build -- deliberately excluding
  `fit_assessment`/`apc_status`/`oa_status`/`indexing`, which answer "is
  this a plausible target?", not "how should this manuscript be written?" --
  and refuses outright to seed one from a `REJECTED` selection.
- `tests/test_target_journal_adapter.py` -- 19 unit tests covering protocol
  validation and the full hard-gate truth table (APC mismatch, unknown APC,
  unconfirmed indexing, stale-plus-checked-constraint, an unrequested
  constraint never being invented, and the style-context seed's
  contamination guard).
- `tests/test_e2e_protocol_handoff.py`: `TestE2E07`-`TestE2E12` -- a second
  real cross-Skill integration alongside the existing
  `JOURNAL_STYLE_CONTEXT_V1` handoff (`TestE2E03`-`TestE2E06`). These drive
  journal-fit-engine's actual `fit_model`/`apc_oa`/`indexing`/`integrity`
  pipeline over real `JournalEvidence`/`ManuscriptProfile` objects into the
  real producer, then into the new consumer, and (for a `SELECTED` result)
  on into the existing `JOURNAL_STYLE_CONTEXT_V1` handoff -- nothing here
  is mocked or hand-built at the protocol boundary. Cases covered: a
  strong, APC-compatible, DOAJ-confirmed target (`SELECTED`, seeds a valid
  style context); a real mandatory-APC mismatch (`REJECTED`, seed refused);
  an unverifiable paid-index requirement (`NEEDS_VERIFICATION`, never a
  fabricated pass); stale evidence with a checked hard constraint
  (`NEEDS_VERIFICATION`); provenance surviving the full producer ->
  consumer -> style-context round trip (source identity, retrieval date);
  and a structural regression guard that fit/APC/OA/indexing vocabulary
  never leaks into `official_requirements`/`observed_patterns`.
- `workflows/target-journal-adaptation.md` -- documents the now-real Stage
  1 (`journal-fit-engine: confirm/refresh target journal profile` ->
  `scholarly-agent`'s hard compatibility gate) ahead of the existing
  style-context/voice-adaptation stages.
- `skills/scholarly-agent/references/orchestration-state.md` -- documents
  the `SELECTED` / `REJECTED` / `NEEDS_VERIFICATION` target-journal
  selection state tied to `artifacts.journal_profile_id`, and that only
  `SELECTED` proceeds automatically to the style-context stage.
- `tests/conftest.py`: `load_module_at()` -- loads a component script from
  an arbitrary path under a unique module name, registered in
  `sys.modules` before execution. Needed because
  `skills/scholarly-agent/scripts/` and `skills/scholarly-voice-engine/scripts/`
  are both directories literally named `scripts`; a plain
  `sys.path.insert` + `import scripts...` collides the moment both
  component directories are on `sys.path` in the same process (exactly
  what `test_e2e_protocol_handoff.py` now does), since Python caches
  `scripts` as one global module name regardless of which directory it
  first resolved from.

### Changed

- `tests/test_protocols.py`'s existing producer-to-schema check for
  `TARGET_JOURNAL_PROFILE_V1` no longer claims "no consumer exists yet" --
  updated to point at the new E2E coverage above; the check itself is
  unchanged and kept as a fast, independent defense-in-depth test.

### Known limitations

- The hard compatibility gate only checks the two hard-constraint keys
  documented above (`no_mandatory_apc`, `requires_indexing`); it does not
  widen itself to check a constraint the caller did not actually state, and
  it does not re-derive fit, indexing, APC, or a quartile -- those remain
  journal-fit-engine's job entirely.
- `journal_style_context_seed()` supplies only identity, freshness, and
  provenance; `official_requirements`/`observed_patterns` for the
  eventual `JOURNAL_STYLE_CONTEXT_V1` still have to come from their own
  real sources (a host LLM's guideline fetch, scholarly-corpus-builder) --
  this consumer does not and must not invent either.
- `PROVENANCE_RECORD_V1` itself stays `PARTIAL`, not `FULL`: this release
  proves a real producer (journal-fit-engine) feeding a real consumer that
  preserves it unchanged through two protocol handoffs, but there is still
  no independent canonical provenance handoff test that exercises
  `PROVENANCE_RECORD_V1` on its own terms, separately from riding inside
  `TARGET_JOURNAL_PROFILE_V1`/`JOURNAL_STYLE_CONTEXT_V1`.
- Unchanged from v1.1.1 below: `scholarly-corpus-builder` stays pinned at
  `v0.9.1` (its `v0.9.2` release is packaging-only, byte-identical runtime
  source); `adaptive-model-router` (`0.3.0`), `scholarly-voice-engine`
  (`1.1.0`), `journal-fit-engine` (`0.4.0`, untouched by this release)
  unchanged.

## v1.1.1 -- 2026-09-09

v1.1.1 PUBLISHED

A component-pin refresh, not a Suite runtime/protocol/workflow change:
`journal-fit-engine` bumped `0.3.0` -> `0.4.0` (adds a
`TARGET_JOURNAL_PROFILE_V1` producer -- see that repository's own
CHANGELOG), and this pin update is real new runtime capability actually
landing in `skills/journal-fit-engine/jfe/`, unlike a standalone
component's packaging-only patch (`scholarly-corpus-builder` v0.9.2,
released the same day, stays pinned at `v0.9.1` here on purpose -- its
runtime source content is byte-identical to `v0.9.1`, confirmed by diffing
both tags' `scb/`/`SKILL.md`/`agents/`/`references/`/`LICENSE`; nothing a
Suite re-pin would actually change).

### Changed

- `journal-fit-engine` pinned at `0.4.0` (`scripts/component-sources.json`,
  `COMPONENTS.json`), re-synced from the published tag via
  `scripts/sync_components.py` against the public `repo_url` (not a local
  working copy).
- `adaptive-model-router` (`0.3.0`), `scholarly-corpus-builder` (`0.9.1`),
  `scholarly-voice-engine` (`1.1.0`) unchanged.

### Known limitations

Unchanged from v1.1.0 below.

## v1.1.0 -- 2026-09-09

v1.1.0 PUBLISHED

Every component release below was pushed to its public remote, validated
by real remote CI (including this Suite's Python 3.10-3.13 matrix), and
published as a GitHub Release before this Suite tag was pushed -- see
rule 152: local validation passing never by itself implies "PUBLISHED".

The 1.1 line closes the `JOURNAL_STYLE_CONTEXT_V1` producer/consumer loop
(the one cross-Skill protocol handoff that was still schema-only through
v1.0.3), adds component drift detection, replaces routing-only "E2E"
coverage with a real cross-repo protocol-handoff integration test, and
moves CI to a Python 3.10-3.13 compatibility matrix.

### Added

- **`JOURNAL_STYLE_CONTEXT_V1` closed end to end.** `journal-fit-engine`
  v0.3.0 adds `jfe.style_context` (the producer: builds and validates the
  envelope, structurally rejects official/observed-pattern cross-
  contamination, never derives either bucket from its own index evidence)
  plus an 11-dimension fit model, an integrity screen, and an indexing
  evidence assessor. `scholarly-voice-engine` v1.1.0 adds
  `scripts/voice/journal_context` (the consumer: `official_requirements`
  becomes a `hard_requirements` block, never confidence-gated;
  `observed_patterns` feeds the existing author→discipline→journal→
  historical precedence resolution as the "journal" layer, gated by
  `freshness`). See `workflows/target-journal-adaptation.md`'s new
  "Implementation" section.
- `tests/test_e2e_protocol_handoff.py` — imports both components' *actual
  code* from the synced `skills/` tree and drives a real handoff: official
  requirement survives, observed pattern survives and correctly outranks a
  lower-precedence layer at `current` freshness, a `stale` (or absent)
  freshness correctly yields instead, limitations survive, and corpus-
  derived evidence never lands in `official_requirements` (or vice versa)
  after a full round trip. This is the first Suite-level test that
  exercises a real protocol handoff rather than only an orchestration-
  routing decision or a standalone schema round-trip.
- `scripts/check_component_drift.py` + `.github/workflows/
  component-drift.yml` (weekly + `workflow_dispatch`) — reports each
  component's pin state (`CURRENT` / `UNRELEASED_COMMITS_AHEAD` /
  `NEW_RELEASE_AVAILABLE` / `PIN_NOT_TAGGED` / `PIN_UNREACHABLE` /
  `VERSION_TAG_MISMATCH` / `SOURCE_VERSION_MISMATCH` / `NO_LOCAL_SOURCE`).
  Detect-and-report only: never edits `component-sources.json` or
  `COMPONENTS.json`, never re-pins, never releases. Only a broken pin
  fails the scheduled workflow; a newer available release is informational.
  9 new tests build real temporary git repositories to exercise every
  status path.
- `protocols/journal-style-context.schema.json` gained optional
  `journal_identifiers`, `article_type`, `evidence`, `limitations`, and
  `generated_at` fields (all backward compatible -- `freshness` and the
  original two required fields are unchanged) to match what the new
  producer/consumer actually read and write.
- `.github/workflows/validate.yml` now runs a `compatibility` matrix job
  (Python 3.10, 3.11, 3.12, 3.13: `validate_suite.py` + `pytest`) ahead of
  a single canonical `package` job (Python 3.11 only) that does the
  deterministic-packaging build and artifact upload -- packaging
  correctness doesn't vary by interpreter version, so it isn't rebuilt
  four times over.

### Fixed

- **Real, pre-existing packaging gap**: `component-sources.json`'s include
  allowlist for `scholarly-voice-engine` never listed anything under
  `scripts/`, so that component's actual runtime Python package
  (`scripts/voice/`: `profile_merge`, `continuity`, `audit`,
  `profile_schema`) was silently absent from every packaged Suite release
  through v1.0.3, despite CHANGELOG entries in that component describing
  code (e.g. `CONTINUITY_STATE_V1` serialization) as shipped. Fixed at the
  sync step (`component-sources.json` now names `scripts/__init__.py` and
  `scripts/voice` precisely, not that component's dev-only
  `validate_skill.py`/`package_runtime.py`) and at the packager
  (`package_suite.py`'s `EXCLUDE_DIR_NAMES` used to blanket-exclude any
  path component literally named `scripts` anywhere in the tree, which
  would have silently stripped the fix back out even after the include
  list was corrected). Two new regression tests in `tests/
  test_packaging.py` assert the runtime package is present and the
  dev-only scripts are not.

### Changed

- `scholarly-corpus-builder` pinned at `0.9.1` (documentation/evidence
  patch on `0.9.0` -- cross-disciplinary live-acquisition demonstrations
  extended from one discipline to five, and a stale eval-fixture count in
  its README corrected; no `scb/` code or schema change).
- `scholarly-voice-engine` pinned at `1.1.0`, `journal-fit-engine` pinned
  at `0.3.0` (see above).
- `adaptive-model-router` remains pinned at `0.3.0` -- unchanged, no real
  issue to fix this round, so its version was not bumped just for
  uniformity.

### Known limitations

- Only `JOURNAL_STYLE_CONTEXT_V1` has a real cross-repo protocol-handoff
  test (`test_e2e_protocol_handoff.py`); the other nine protocols in
  `protocols/` still have schema-validity and (for several) standalone
  round-trip coverage, but not this same depth of producer-code-into-
  consumer-code integration testing yet.
- `check_component_drift.py` depends on locally reachable git history
  (an override or a `.cache/components/` clone) -- it does not query
  GitHub's API directly, so a component with neither present locally
  reports `NO_LOCAL_SOURCE`, not a live check.
- Only two of `protocols/`'s ten protocols were `FULL` at this release
  (`JOURNAL_STYLE_CONTEXT_V1`: real cross-repository producer-into-
  consumer E2E; `CONTINUITY_STATE_V1`: a self-contained serialization
  round trip, not a cross-repo handoff -- the two are FULL by different
  routes). `TARGET_JOURNAL_PROFILE_V1` and `PROVENANCE_RECORD_V1` were
  `DECLARED_ONLY` (schema only, no producer or consumer code) as of this
  tag; see v1.1.1 above for `TARGET_JOURNAL_PROFILE_V1`'s producer.

## v1.0.3 -- 2026-09-09

v1.0.3 PUBLISHED

### Fixed

- Even after the v1.0.1 CRLF/`ZIP_STORED` fix, a fresh Windows-local
  rebuild of the published `v1.0.2` content still did not match the
  Linux-CI-published `v1.0.2` ZIP byte-for-byte. Root cause:
  `zipfile.ZipInfo` defaults `create_system` to the platform running the
  build script (`0`=Windows, `3`=Unix/Linux) unless explicitly pinned, so
  identical file content still produced different ZIP container bytes
  depending on which OS built it. Fixed by pinning `create_system = 3` on
  every entry. **Verified directly, not just asserted**: a fresh local
  Windows rebuild of this exact commit now produces
  `4a27739d0a80cdf52c4db72c6930a86488d73b39cec7b0307da74311f85da65e` --
  byte-identical to the already-published Linux-CI-built `v1.0.2` ZIP. A
  new regression test pins this directly. `v1.0.1` and `v1.0.2` stay
  published as-is per the never-overwrite rule.
- This closes the "byte-identical across builds/machines" claim for
  real, after two prior patches (v1.0.1, v1.0.2) each fixed one real bug
  in it but left another undiscovered. Confirmed this time by actually
  diffing CI-published bytes against a fresh local build rather than
  only checking two same-machine builds agree with each other.

## v1.0.2 -- 2026-09-09

v1.0.2 PUBLISHED

### Fixed

- The published `v1.0.1` release itself shipped with `COMPONENTS.json`'s
  `suite_version` still reading `"1.0.0"` -- `VERSION` was bumped to
  `1.0.1` in that same commit, but `scripts/sync_components.py` was not
  re-run afterward to regenerate `COMPONENTS.json`, and
  `validate_suite.py` only checked that `suite_version` was *present*,
  never that its *value* matched `VERSION`. Discovered by comparing a
  fresh local rebuild's SHA-256 against the CI-published artifact (the
  same reproducibility check that had just caught the v1.0.0 packaging
  bug) and finding they still differed. Fixed by: (1) regenerating
  `COMPONENTS.json` correctly before this release, in the right order
  (bump `VERSION` first, then run `sync_components.py`, then commit
  both together); (2) adding the missing value check to
  `validate_suite.py` (`COMPONENTS.json suite_version matches VERSION
  file`); (3) a regression test in `tests/test_components.py`. `v1.0.1`
  stays published as-is per the never-overwrite rule -- its component
  pins and packaged content were otherwise correct, only its own
  `suite_version` field was one release behind.

## v1.0.1 -- 2026-09-09

v1.0.1 PUBLISHED

### Fixed

- `scripts/package_suite.py` claimed the built ZIP was "byte-identical
  across builds/machines" but only same-machine rebuilds were ever
  actually tested. Publishing v1.0.0 exposed two real bugs: (1) it read
  `file_path.read_bytes()` directly, so a synced component file checked
  out with CRLF line endings (a Windows checkout of
  `scholarly-corpus-builder`'s own `scb/manifest.py`) produced different
  bytes than the same commit packaged on Linux CI; (2) `ZIP_DEFLATED`
  compression is not guaranteed byte-identical across zlib versions/
  builds even for identical input. Fixed by normalizing every packaged
  file to UTF-8/LF on read and switching to `ZIP_STORED` (uncompressed) --
  the same tradeoff `adaptive-model-router`'s, `scholarly-corpus-builder`'s,
  and `journal-fit-engine`'s own packagers already made for the same
  reason. Two new regression tests assert directly on the fixed
  properties (no `\r` in any packaged entry; `ZIP_STORED` compression),
  not only that two same-machine builds match, which passed even with
  both bugs present.
- The already-published `v1.0.0` GitHub Release is left as-is (never
  overwrite a published tag/release) -- its file *contents* were correct;
  only the cross-platform-reproducibility guarantee was overstated. This
  is documented here rather than silently fixed with no record.

## v1.0.0 -- 2026-09-09

v1.0.0 PUBLISHED

Initial integration/distribution release.

### Added

- Plugin manifest (`.codex-plugin/plugin.json`) bundling five Skills.
- New `scholarly-agent` orchestrator Skill: narrow multi-stage trigger,
  minimal-component selection, routing matrix, workflow-state model, and a
  final integrity/completeness quality gate.
- Reproducible, commit-pinned component sync
  (`scripts/sync_components.py` + `scripts/component-sources.json`) for
  `adaptive-model-router` (v0.2.0), `scholarly-corpus-builder` (v0.9.0),
  `scholarly-voice-engine` (v1.0.0), and `journal-fit-engine` (v0.1.0).
- Ten shared protocol schemas (`protocols/`) covering execution policy,
  scholarly profiles, voice request/context/output, manuscript profiles,
  journal profiles and style context, continuity state, and provenance.
- Five shared cross-Skill policy documents (`shared/`): integrity,
  provenance, terminology, protocol versioning, capability boundaries.
- Fourteen workflow recipes (`workflows/`) covering paper-from-idea through
  paper-from-notes, revision, journal selection, target-journal adaptation,
  literature/systematic review, theory/empirical papers, commentary writing,
  book projects, monograph chapters, author-voice calibration, and
  standalone corpus-profile building.
- Suite-level test suite (`tests/`) and offline validator
  (`scripts/validate_suite.py`) covering plugin manifest validity, component
  presence/frontmatter/uniqueness, protocol schema structure, workflow
  references, and orchestration trigger behavior (positive and negative).
- Suite-level end-to-end orchestration eval fixtures (`evals/`).
- Deterministic runtime packaging (`scripts/package_suite.py`) producing
  `dist/scholarly-agent-suite-v1.0.0.zip` plus a `release-manifest.json`
  with SHA-256 checksum, packaged component versions, and source commits.
- CI (`.github/workflows/validate.yml`) running the validator, tests, and a
  packaging dry run on every push/PR.

### Changed

- Synced `adaptive-model-router` from its published `v0.3.0` release
  (commit `de79826`, was the unpublished `v0.2.0` working state at commit
  `3c441a7`). See that repository's own CHANGELOG for the budget
  controller, task state, stop rule, and escalation reason codes it adds.
- Synced `scholarly-voice-engine` to `v1.0.2` (commit `859aa75`, was
  `v1.0.0` at commit `0a020b9`): a compatibility audit (`v1.0.1`) that
  fixed a real `SCHOLARLY_PROFILE_V1` confidence-vocabulary mismatch
  (`medium` vs. the correct `moderate`) and added optional
  `VOICE_REQUEST_V1`/`VOICE_OUTPUT_V1` adapters, then (`v1.0.2`)
  implemented `CONTINUITY_STATE_V1` serialization for
  `ContinuityLedger`. `JOURNAL_STYLE_CONTEXT_V1` remains an open
  compatibility gap -- see that repository's CHANGELOG.
- Synced `journal-fit-engine` to its published `v0.2.0` release (commit
  `35bca33`, was `v0.1.0` at commit `f0729e0`): first working code
  (`jfe/`) for live journal-evidence lookup, APC/OA classification, hard
  filters, and a topic-overlap fit dimension -- previously the entire
  engine was prose only. `jfe` added to this Suite's `include` allowlist
  for the component (178 packaged files, was 170). See that repository's
  CHANGELOG for what's live-verified vs. still not implemented; this is
  not a 1.0 release.

### Fixed

- Removed machine-specific absolute local paths (`repo_path`) from the
  committed `scripts/component-sources.json`; it now records only public
  `repo_url` + pinned commit sha (+ an optional real tag), and syncs
  correctly on a clean machine with only network access.
- Rewrote `scripts/sync_components.py` to clone/fetch each component's
  `repo_url` into a local bare cache (`.cache/components/`, gitignored) and
  export the pinned commit from there, with an `--offline` mode for
  reproducible builds without network access. A gitignored
  `scripts/component-sources.local.json` optionally overrides a component
  with a contributor's local working-copy path for faster iteration; it must
  still contain the pinned commit.

### Notes

- No dependency resolver: `COMPONENTS.json` `compatibility` ranges are a
  declaration this release was tested against, not an enforced constraint.
- Only `V1` of each protocol exists in this release; no version adapters are
  implemented (none are needed yet).
