# Development, release, and maintenance

This page is for maintainers and contributors. If you just want to use the
Scholarly Agent, start with the [README](../README.md).

Contents:

- [Layout](#layout)
- [Suite versioning](#suite-versioning)
- [Development model](#development-model)
- [Testing](#testing)
- [Runtime package](#runtime-package)
- [Limitations](#limitations)
- [History: the v1 multi-Skill suite](#history-the-v1-multi-skill-suite)

## Layout

Since v2.0.0 the repository ships exactly one Skill:

```
skills/scholarly-agent/
  SKILL.md                  dispatcher: the only file with Skill frontmatter
  agents/openai.yaml        optional cross-runtime descriptor
  references/               routing matrix, orchestration state, 15 workflow recipes
  scripts/                  workflow_resolver.py, target_journal_adapter.py
  modules/
    adaptive-model-router/     MODULE.md, references/
    scholarly-corpus-builder/  MODULE.md, references/, scb/  (scb/bibliography.py: BibTeX/RIS/CSL-JSON)
    scholarly-voice-engine/    MODULE.md, references/, disciplines/, assets/, scripts/voice/
    journal-fit-engine/        MODULE.md, references/, disciplines/, jfe/
    peer-review-engine/        MODULE.md, references/, prv/  (native, v2.1.0)
  protocols/                12 JSON Schemas (*_V1)
  shared/                   integrity, provenance, terminology, versioning, boundaries,
                            disciplines (the one discipline taxonomy)
```

Rules that keep this layout honest (all checked by `validate_suite.py` and
`tests/`):

- Only `skills/scholarly-agent/SKILL.md` carries frontmatter. A `SKILL.md`
  anywhere else under `skills/` would register a second, competing Skill.
- Every runtime dependency resolves from inside `skills/scholarly-agent/`.
  Nothing at the repository root (`workflows/`, `docs/`, `assets/`) is
  needed at runtime; `workflows/` is a generated mirror of
  `skills/scholarly-agent/references/workflows/` (`scripts/sync_workflows.py`).
- Paths inside a `MODULE.md` are relative to that module's directory.
- Modules exchange data only through `protocols/`; module boundaries are
  defined in `shared/capability-boundaries.md`.

## Suite versioning

The Suite follows semantic versioning on its own `VERSION`
(== `.codex-plugin/plugin.json` `version` == `COMPONENTS.json`
`suite_version` == the release tag without `v`). Modules no longer carry
independent versions; a module change is a Suite change. A breaking change to
any shared protocol in `skills/scholarly-agent/protocols/` requires a new
major protocol version and a Suite major version (see
`skills/scholarly-agent/shared/protocol-versioning.md`). Every release is
reported as exactly one of `v<VERSION> PREPARED -- NOT PUBLISHED` or
`v<VERSION> PUBLISHED`; see `RELEASE_CHECKLIST.md`.

Publishing is automatic (`.github/workflows/release.yml`): every push to
`master` publishes release `v<VERSION>` if it does not exist yet, after
validation, tests, and a two-build determinism check, with
`scripts/release_notes.py` extracting the CHANGELOG section as release
notes. Pushes that do not change `VERSION` publish nothing; a hand-pushed
`v*` tag must match `VERSION`; an existing release is never overwritten.

## Development model

All modules are developed in this repository. `COMPONENTS.json` records,
per module, either the upstream repository, release, and commit it was
merged from (`merged_from`, the four v2.0.0 modules), or
`"origin": {"native": true, "added_in": "<version>"}` for a module created
here (`peer-review-engine`).

Adding a module: create `modules/<name>/MODULE.md` with the standard header
(no frontmatter) and a `> Scope:` line, add it to the module map and the
handoff table in `SKILL.md`, to `agents/openai.yaml`, `COMPONENTS.json`,
`shared/capability-boundaries.md`, `references/routing-matrix.md`, the module
lists in `scripts/validate_suite.py`, the tests that enumerate modules, and
the CI package sanity step. Per-discipline guidance files follow
`shared/disciplines.md`. There is no sync step and
no drift check any more; the former `scripts/sync_components.py`,
`scripts/component-sources.json`, `scripts/check_component_drift.py`, and the
weekly drift workflow were removed in v2.0.0.

Python engines are imported by putting the module directory on `sys.path`
(`import scb`, `import jfe`, `import prv`). The voice module's engine lives under a
directory named `scripts/`, which collides with the dispatcher's own
`scripts/`; tests load those files by path with
`tests/conftest.py:load_module_at()`.

## Testing

```bash
pip install pytest jsonschema
python scripts/validate_suite.py   # layout, manifest, protocols, workflows
pytest tests/
```

- `tests/test_components.py`, `test_standalone_independence.py`,
  `test_plugin_manifest.py` -- one Skill, five modules, no stray
  frontmatter, everything resolvable inside the Skill.
- `tests/test_orchestration_triggers.py`, `test_capability_boundaries.py`,
  `evals/` -- trigger boundary, the three dispatch paths, negative examples,
  and dispatcher scope creep.
- `tests/test_protocols.py` -- schema validity and cross-schema
  compatibility.
- `tests/test_e2e_protocol_handoff.py` -- real producer code into real
  consumer code for `JOURNAL_STYLE_CONTEXT_V1` (journal fit -> voice) and
  `TARGET_JOURNAL_PROFILE_V1` (journal fit -> dispatcher gate).
- `tests/test_e2e_module_handoffs.py` -- real handoffs for
  `SCHOLARLY_PROFILE_V1` (corpus -> voice) and `MANUSCRIPT_PROFILE_V1`
  (envelope -> journal fit), both added in v2.0.0 after the merge exposed
  that neither producer/consumer pair actually conformed to the shared
  schema.
- `tests/test_e2e_provenance_handoff.py` -- `PROVENANCE_RECORD_V1` built by
  `scb.compiler.build_provenance_record_v1()` from real records (including a
  BibTeX import), through `SCHOLARLY_PROFILE_V1` into a voice request.
- `tests/test_disciplines.py` -- both discipline directories match
  `shared/disciplines.md`.
- `tests/test_router_platform_neutral.py` -- no provider model generations
  in the router policy; router eval fixtures follow the records contract.
- `tests/test_markdown_links.py` -- every relative Markdown link resolves.
- `tests/modules/prv/` -- peer-review panel, report validation, decision
  rules, response matrix, second round; `tests/modules/scb/test_scb_bibliography.py`
  -- BibTeX/RIS/CSL-JSON import and export.
- `tests/modules/scb/`, `tests/modules/jfe/`, `tests/modules/voice/` -- each
  module's own unit tests, merged from its former repository in v2.0.0
  (fixtures included). Tests of the former repositories' own packaging and
  `validate_skill.py` scripts were not merged, since those scripts are not
  part of this repository. `tests/modules/jfe/test_jfe_posi.py` covers the
  POSI evidence source against a fixture cut from a real POSI snapshot.
- `evals/modules/<module>/` -- each module's own eval cases, merged from its
  former repository; `tests/test_evals.py` checks they parse.
- `tests/test_release_automation.py` -- release-notes extraction and the
  release workflow's guards (no overwrite, validate and test first,
  deterministic package).
- `tests/test_workflow_packaging.py`, `test_workflow_install_smoke.py`,
  `test_packaging.py`, `test_diagrams.py` -- release ZIP contents,
  determinism, and installed-Skill layout.

CI (`.github/workflows/validate.yml`) runs validation and tests across
Python 3.10-3.13; the deterministic packaging build runs once, on the
Python 3.11 job.

## Runtime package

`scripts/package_suite.py` builds a self-contained runtime ZIP
(`dist/scholarly-agent-suite-v<version>.zip`) containing only
`.codex-plugin/`, `skills/` (the one Skill, including its modules,
protocols, and shared policy), `workflows/`, `README.md`, `LICENSE`,
`VERSION`, and `COMPONENTS.json`. It excludes `tests/`, `evals/`,
`.github/`, `docs/`, `assets/`, and development scripts, and writes a
`release-manifest.json` with the suite version, module provenance, protocol
versions, file list, and a SHA-256 checksum. The ZIP is byte-deterministic:
sorted entries, a fixed timestamp, LF-normalized text, `ZIP_STORED`, and a
pinned `create_system`.

## Limitations

- No protocol version adapters yet (only `V1` of each protocol exists).
- `scb.compiler.compile_scholarly_profile_v1()` (the pre-schema shape) is
  kept for existing callers; new code should use
  `compile_scholarly_profile_protocol_v1()`.
- `VOICE_CONTEXT_V1`, `VOICE_REQUEST_V1`, and `VOICE_OUTPUT_V1` have schema
  round-trip coverage only.
- Peer-review evals (`evals/modules/peer-review-engine/`) describe expected
  behavior; like the other module evals they are not run against a live
  model here. `prv/` tests cover the deterministic rules only.
- `scb.__version__` (recorded as the builder version in corpus build
  manifests) is the Suite `VERSION`; in a plain-Skill install without that
  file it falls back to `0.0.0`.
- Live evidence retrieval (current journal metrics, APC policy) depends on
  the host's network and tool access at runtime; the Skill adds no
  connectors.
- POSI lookups need a downloaded snapshot (`jfe.cli posi-lookup
  --cache-dir`, about 13 MB) or network access; there is no live per-journal
  POSI API.

## History: the v1 multi-Skill suite

Up to v1.2.1 the Suite bundled five separate Skills: the
`scholarly-agent` orchestrator plus four specialist Skills synced from their
own repositories at pinned commits, with a weekly drift report. v2.0.0
merged the four specialists into `scholarly-agent` as modules, moved
`protocols/` and `shared/` inside the Skill, and made this repository the
only place modules are developed. See `CHANGELOG.md` for details.
