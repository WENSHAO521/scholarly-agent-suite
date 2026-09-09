# Changelog

All notable changes to the Scholarly Agent Suite are documented in this file.
Suite versioning follows `README.md#component-versioning` /
`shared/protocol-versioning.md`; component versions are tracked separately in
`COMPONENTS.json`.

## v1.0.0 -- 2026-09-09

v1.0.0 PREPARED -- NOT PUBLISHED

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

### Notes

- No dependency resolver: `COMPONENTS.json` `compatibility` ranges are a
  declaration this release was tested against, not an enforced constraint.
- Only `V1` of each protocol exists in this release; no version adapters are
  implemented (none are needed yet).
