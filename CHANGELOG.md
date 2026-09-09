# Changelog

All notable changes to the Scholarly Agent Suite are documented in this file.
Suite versioning follows `README.md#component-versioning` /
`shared/protocol-versioning.md`; component versions are tracked separately in
`COMPONENTS.json`.

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
