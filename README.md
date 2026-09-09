# Scholarly Agent Suite

A modular cross-disciplinary academic AI agent suite for research execution,
scholarly corpus construction, academic writing, author voice calibration,
and evidence-backed publication strategy.

This is **not** an AI paper generator, an automatic publication machine, or a
journal-acceptance predictor. It is an integration, coordination, and
distribution layer over four independently maintained specialist Skills, plus
one small orchestrator.

## Why a Suite

Each capability below already works as a standalone Skill. The Suite does not
replace them or merge them into one giant Skill -- it packages them together,
gives them a shared vocabulary and shared data contracts, and adds a thin
orchestrator so a genuinely multi-stage scholarly task (e.g. "turn this idea
into a paper and find a journal") does not require the user to manually chain
four separate Skills. The design principle is: **integrate, do not collapse.**

## Architecture

```
User
 |
 v
Scholarly Agent (orchestration)
 |
 +-- Adaptive Model Router      (execution intelligence)
 +-- Scholarly Corpus Builder   (research intelligence)
 +-- Scholarly Voice Engine     (writing intelligence)
 +-- Journal Fit Engine         (publication intelligence)

Shared:
 protocols/   -- data contracts between Skills
 shared/      -- integrity, provenance, terminology, capability boundaries
 workflows/   -- stage-order recipes (not Skills)
```

Each specialist Skill keeps its own trigger boundary, responsibility, tests,
references, and version. See `shared/capability-boundaries.md` for exactly
what each one is (and is not) responsible for.

## Components

| Skill | Role | Packaged version |
|---|---|---|
| [scholarly-agent](skills/scholarly-agent/SKILL.md) | Workflow orchestration | see `COMPONENTS.json` |
| [adaptive-model-router](skills/adaptive-model-router/SKILL.md) | Execution intelligence | see `COMPONENTS.json` |
| [scholarly-corpus-builder](skills/scholarly-corpus-builder/SKILL.md) | Research & evidence intelligence | see `COMPONENTS.json` |
| [scholarly-voice-engine](skills/scholarly-voice-engine/SKILL.md) | Writing & argument intelligence | see `COMPONENTS.json` |
| [journal-fit-engine](skills/journal-fit-engine/SKILL.md) | Publication intelligence | see `COMPONENTS.json` |

`COMPONENTS.json` records the *exact* version and source commit of each
bundled component for this Suite release -- it is the single source of truth,
not this table (versions here would go stale; the JSON file will not).

## Quick start

### Option A -- Suite Plugin (recommended)

Install the whole Suite once via `.codex-plugin/plugin.json`. All five Skills
become available, plus shared workflow recipes and protocols.

### Option B -- Individual Skill

Every component Skill remains independently installable and fully functional
on its own (see "Standalone compatibility" below). Use this for a minimal
install, active component development, or if you only need one capability
(e.g. only `scholarly-voice-engine`).

## Typical workflows

See `workflows/` for the full set of recipes (paper from an idea, revising an
existing manuscript, journal selection, target-journal adaptation, literature
review, systematic review, commentary writing, a full book project, a single
monograph chapter, and author voice calibration). These are recipes the
`scholarly-agent` Skill follows, not additional Skills.

`scholarly-agent` does **not** run all four specialists for every request --
see its `references/routing-matrix.md` for which intents need which
specialists, and its SKILL.md for when it should not activate at all (e.g. a
one-sentence paragraph polish stays with `scholarly-voice-engine` alone).

## Shared protocols

Ten JSON Schemas under `protocols/` define the data contracts specialists use
to hand work to each other (`EXECUTION_POLICY_V1`, `SCHOLARLY_PROFILE_V1`,
`VOICE_REQUEST_V1`, `VOICE_CONTEXT_V1`, `VOICE_OUTPUT_V1`,
`MANUSCRIPT_PROFILE_V1`, `TARGET_JOURNAL_PROFILE_V1`,
`JOURNAL_STYLE_CONTEXT_V1`, `CONTINUITY_STATE_V1`, `PROVENANCE_RECORD_V1`).
See `shared/protocol-versioning.md` for how these evolve without breaking
existing consumers.

## Integrity policy

`shared/integrity-policy.md` is non-negotiable across every bundled Skill: no
fabricated citations, DOIs, quotations, journal metrics, corpus counts, or
acceptance probabilities; no paywall bypass or shadow libraries; no direct
living-author imitation; no AI-detector-evasion objective. The orchestrator's
final quality gate (`skills/scholarly-agent/references/orchestration-state.md`)
enforces that a specialist's unresolved integrity flag is never silently
dropped on the way to a "complete" result.

## Component versioning

Component Skills are **not** forced to share the Suite's version number. A
valid release can (and does) bundle `scholarly-corpus-builder` at `0.9.0`
alongside `scholarly-voice-engine` at `1.0.0` -- see `COMPONENTS.json` for the
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
was pinned for this release.

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
  and negative), and packaging tests.
- `evals/` -- end-to-end orchestration fixtures (component selection,
  negative triggers, cross-disciplinary and multilingual scenarios).
- Component-level correctness (adapters, analytics, validators) is owned by
  each component's own repository and its own `tests/`/`evals/` -- this Suite
  does not duplicate them.

Run `python scripts/validate_suite.py` for the acceptance-criteria checker,
and `pytest tests/` for the full test suite.

## Runtime package

`scripts/package_suite.py` builds a self-contained runtime ZIP
(`dist/scholarly-agent-suite-v<version>.zip`) containing only what an
end-user install needs -- `.codex-plugin/`, `skills/`, `protocols/`,
`shared/`, `workflows/`, `README.md`, `LICENSE`, `VERSION`, and
`COMPONENTS.json`. It excludes `tests/`, `evals/`, `.github/`, development
scripts, and any component `.git` metadata, and writes a
`release-manifest.json` with the exact packaged versions, source commits,
protocol versions, file list, and a SHA-256 checksum.

## Limitations

- No dependency resolver: component version compatibility is a declared
  range (`COMPONENTS.json`), not an enforced constraint.
- No protocol version adapters yet (only `V1` of each protocol exists);
  a future breaking change requires a new major protocol version and, likely,
  a Suite major version.
- Live/network-dependent evidence retrieval (current journal metrics, current
  APC policy) depends entirely on each component's own tool access at
  runtime; the Suite adds no additional connectors in v1.0.0 (see rule 60,
  "optional future connectors").
- Suite-level end-to-end evals exercise orchestration/routing decisions, not
  the full correctness of each specialist's domain logic.

## Roadmap

Future components (e.g. `peer-review-engine`, `systematic-review-engine`,
`grant-writing-engine`) are only added once each has a distinct trigger
boundary, substantial independent policy, and standalone usability (rule
131-133) -- not merely because a feature could be split out.
