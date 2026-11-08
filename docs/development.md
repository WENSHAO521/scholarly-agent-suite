# Development, release, and maintenance

This page is for maintainers and contributors. If you just want to use the
Suite, start with the [README](../README.md).

Contents:

- [Suite versioning](#suite-versioning)
- [Component versioning](#component-versioning)
- [Development model](#development-model)
- [Component drift detection](#component-drift-detection)
- [Standalone compatibility](#standalone-compatibility)
- [Testing](#testing)
- [Runtime package](#runtime-package)
- [Limitations](#limitations)

## Suite versioning

The Suite follows semantic versioning on its own `VERSION`
(== `.codex-plugin/plugin.json` `version` == the release tag without `v`).
A breaking change to any shared protocol in `protocols/` requires a new major
protocol version and, in practice, a Suite major version (see
`shared/protocol-versioning.md`). Re-pinning a component to a new patch or
minor release that stays inside the declared `compatibility` range is a
Suite patch or minor release. Every release is reported as exactly one of
`v<VERSION> PREPARED -- NOT PUBLISHED` or `v<VERSION> PUBLISHED`; see
`RELEASE_CHECKLIST.md`.

## Component versioning

Component Skills are **not** forced to share the Suite's version number. A
valid release can (and does) bundle `scholarly-corpus-builder` at `0.9.1`
alongside `scholarly-voice-engine` at `1.1.0` -- see `COMPONENTS.json` for the
exact versions and `compatibility` for the declared-compatible ranges. This is
a declaration, not a dependency resolver: the Suite does not automatically
install or upgrade components.

## Development model

```
component repository
  -> component release/tag
    -> scripts/sync_components.py (pinned commit, never a floating branch)
      -> skills/<component>/
        -> suite integration tests
          -> suite release
```

Component repositories (`adaptive-model-router`, `scholarly-corpus-builder`,
`scholarly-voice-engine`, `journal-fit-engine`) remain the canonical
development sources and are never deleted or deprecated because this Suite
exists. `scripts/component-sources.json` records exactly which commit of each
was pinned for this release, using only public `repo_url` + pinned commit sha
(and a `tag` when that commit has a real published tag) -- it contains no
machine-specific paths and syncs correctly on a clean machine with only
network access to each `repo_url`.

`sync_components.py` clones/fetches each `repo_url` into a local bare cache
under `.cache/components/` (gitignored) and exports the exact pinned commit
from there; `--offline` skips the clone/fetch and requires the commit to
already be cached, for reproducible builds without network access. A
contributor iterating on a component locally can add a gitignored
`scripts/component-sources.local.json` with a `repo_path` override per
component to sync from a local working copy instead of the network -- the
pinned `ref` must still be reachable from that local copy; it is a faster
source of the same bytes, not a way to sync a different revision.

## Component drift detection

`python scripts/check_component_drift.py` compares what's pinned in
`scripts/component-sources.json` against each component repository's actual
current state (its own tags, its own default-branch tip) and reports one of:
`CURRENT`, `UNRELEASED_COMMITS_AHEAD`, `NEW_RELEASE_AVAILABLE`,
`PIN_NOT_TAGGED`, `PIN_UNREACHABLE`, `VERSION_TAG_MISMATCH`,
`SOURCE_VERSION_MISMATCH`, or `NO_LOCAL_SOURCE`. It only detects and
reports -- it never edits `component-sources.json` or `COMPONENTS.json`,
never re-pins, and never triggers a release; bumping a pin is always a
deliberate maintainer action driven by `RELEASE_CHECKLIST.md`. A weekly
`.github/workflows/component-drift.yml` run surfaces drift as an
informational report; only a genuinely broken pin (`PIN_UNREACHABLE`,
`VERSION_TAG_MISMATCH`, `SOURCE_VERSION_MISMATCH`) fails that workflow.

**A newer component HEAD does not automatically mean the Suite is
outdated.** The Suite pins published, integration-tested source states
(see "Development model" above) -- `NEW_RELEASE_AVAILABLE` or
`UNRELEASED_COMMITS_AHEAD` on a component is a prompt to evaluate whether
picking that up is worth a new sync + integration test pass, not a
standing failure.

## Standalone compatibility

Every bundled Skill still works if installed by itself, outside this Suite --
none of them has a hard runtime dependency on a `../shared/*` or
`../protocols/*` file living next to it. Suite-level shared policy and
protocols standardize and supplement the family; they never become an
unavailable hard dependency for a standalone install (rule 42). Each
specialist keeps a compact copy of the integrity rules relevant to its own
domain directly inside its own `SKILL.md`.

## Testing

- `tests/` -- suite-level tests: plugin manifest, component presence/
  frontmatter/uniqueness, protocol schema validity and cross-schema
  compatibility, workflow references, orchestration trigger tests (positive
  and negative), packaging tests, and component-drift-detector tests.
- `tests/test_e2e_protocol_handoff.py` -- true cross-Skill integration tests
  that import each component's *actual code* from the synced `skills/` tree
  (not a mock, not a routing-only check) and exercise a real protocol
  handoff end to end. Two handoffs are covered: `journal-fit-engine`'s
  `JOURNAL_STYLE_CONTEXT_V1` producer feeding `scholarly-voice-engine`'s
  consumer (official requirements, observed patterns, freshness, and
  limitations all survive the full round trip, and corpus-derived evidence
  can never land in an official-requirement field or vice versa); and
  `journal-fit-engine`'s `TARGET_JOURNAL_PROFILE_V1` producer feeding
  `scholarly-agent`'s hard-compatibility-gate consumer
  (`skills/scholarly-agent/scripts/target_journal_adapter.py`) -- a
  confirmed APC mismatch is `REJECTED`, an unverifiable paid-index
  requirement is `NEEDS_VERIFICATION` rather than a guessed pass/fail,
  stale evidence with a checked hard constraint is `NEEDS_VERIFICATION`,
  provenance survives the full handoff, and fit/APC/OA/indexing vocabulary
  never leaks into the eventual `JOURNAL_STYLE_CONTEXT_V1`'s
  `official_requirements`/`observed_patterns`.
- `evals/` -- end-to-end orchestration fixtures (component selection,
  negative triggers, cross-disciplinary and multilingual scenarios),
  including a combined `theory-paper` + `target-journal-adaptation` routing
  fixture for "develop a theoretical paper for an already-selected target
  journal."
- `tests/test_workflow_packaging.py` -- proves every required workflow
  recipe (`scripts/workflow_manifest.REQUIRED_WORKFLOWS`, the single source
  of truth) is present in the source runtime boundary, in
  `package_suite.iter_runtime_files()`, in the built release ZIP, in
  `release-manifest.json`, and in a standalone-copied scholarly-agent
  package -- plus a negative test proving a genuinely missing recipe is
  actually caught.
- `tests/test_workflow_install_smoke.py` -- builds the filesystem layout an
  *installed* scholarly-agent Skill actually receives (not the repository
  root) and resolves `SKILL.md`, the workflow index, and specific recipes
  (`theory-paper.md`, `empirical-paper.md`,
  `target-journal-adaptation.md`) from inside it; fails if a recipe is only
  reachable via the repository root's `workflows/` mirror.
- Component-level correctness (adapters, analytics, validators) is owned by
  each component's own repository and its own `tests/`/`evals/` -- this Suite
  does not duplicate them.

Run `python scripts/validate_suite.py` for the acceptance-criteria checker,
and `pytest tests/` for the full test suite. CI (`.github/workflows/
validate.yml`) runs validation and tests across a Python 3.10-3.13
compatibility matrix; the deterministic packaging build itself runs once,
on the canonical Python 3.11 job, since packaging correctness doesn't vary
by interpreter version and rebuilding it four times over would just be
wasted CI time.

## Runtime package

`scripts/package_suite.py` builds a self-contained runtime ZIP
(`dist/scholarly-agent-suite-v<version>.zip`) containing only what an
end-user install needs -- `.codex-plugin/`, `skills/`, `protocols/`,
`shared/`, `workflows/`, `README.md`, `LICENSE`, `VERSION`, and
`COMPONENTS.json`. It excludes `tests/`, `evals/`, `.github/`, development
scripts, and any component `.git` metadata, and writes a
`release-manifest.json` with the exact packaged versions, source commits,
protocol versions, file list, and a SHA-256 checksum.

Every workflow recipe scholarly-agent needs ships inside `skills/` (at
`skills/scholarly-agent/references/workflows/`), so it is present in this
ZIP under every consumption pattern -- the whole ZIP, `skills/` copied out
on its own, or scholarly-agent extracted standalone. `tests/
test_workflow_packaging.py` and `tests/test_workflow_install_smoke.py`
assert this directly against the built ZIP, `release-manifest.json`, and a
simulated installed-Skill-only filesystem layout, not just against the
repository's source tree.

## Limitations

- No dependency resolver: component version compatibility is a declared
  range (`COMPONENTS.json`), not an enforced constraint.
- No protocol version adapters yet (only `V1` of each protocol exists);
  a future breaking change requires a new major protocol version and, likely,
  a Suite major version.
- Live/network-dependent evidence retrieval (current journal metrics, current
  APC policy) depends entirely on each component's own tool access at
  runtime; the Suite adds no additional connectors (see rule 60, "optional
  future connectors").
- Suite-level end-to-end evals (`evals/`) exercise orchestration/routing
  decisions, not the full correctness of each specialist's domain logic.
  `tests/test_e2e_protocol_handoff.py` goes one level deeper for the
  `JOURNAL_STYLE_CONTEXT_V1` and `TARGET_JOURNAL_PROFILE_V1` handoffs
  specifically (real producer code into real consumer code, not
  routing-only), but that coverage does not yet extend to every protocol in
  `protocols/` -- `PROVENANCE_RECORD_V1` in particular stays `PARTIAL`
  (preserved unchanged by both of the above, but with no independent
  canonical provenance-handoff test of its own), and `SCHOLARLY_PROFILE_V1`
  / `VOICE_CONTEXT_V1` / `MANUSCRIPT_PROFILE_V1` / `VOICE_REQUEST_V1` /
  `VOICE_OUTPUT_V1` remain schema-only round-trip coverage rather than a
  real cross-Skill handoff test.
- `check_component_drift.py` requires each component's git history to be
  locally reachable (a local override or a `.cache/components/` clone); it
  is not itself a network service and does not run against GitHub's API.
