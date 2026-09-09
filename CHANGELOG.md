# Changelog

All notable changes to the Scholarly Agent Suite are documented in this file.
Suite versioning follows `README.md#component-versioning` /
`shared/protocol-versioning.md`; component versions are tracked separately in
`COMPONENTS.json`.

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
