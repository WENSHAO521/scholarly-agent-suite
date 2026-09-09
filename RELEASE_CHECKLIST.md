# Release checklist

Before tagging a Suite release (e.g. `v1.0.0`), confirm every item below.
This is the concrete procedure behind rule 97 / rule 145.

## Pin and sync

- [ ] Every component's `ref` in `scripts/component-sources.json` is a commit
      SHA (never a branch name).
- [ ] `python scripts/sync_components.py` runs clean (exit 0) from a fresh
      checkout.
- [ ] `COMPONENTS.json` versions and `source_commit` values match what was
      just synced.

## Validate

- [ ] `python scripts/validate_suite.py` passes with 0 failures.
- [ ] `pytest tests/` passes.
- [ ] Each bundled component still installs and runs standalone (outside
      `skills/`, with no `../shared` or `../protocols` reference) --
      verified by `tests/test_standalone_independence.py`.

## Package

- [ ] `python scripts/package_suite.py` builds
      `dist/scholarly-agent-suite-v<VERSION>.zip` with no `tests/`, `evals/`,
      `.github/`, dev scripts, or component `.git` metadata inside.
- [ ] `release-manifest.json` inside the ZIP lists the exact suite version,
      component versions, source commits, protocol versions, file count, and
      a SHA-256 checksum, with no private machine paths.
- [ ] Re-running packaging from a clean checkout of the same commit produces
      a ZIP with the same SHA-256 (deterministic ordering/timestamps).

## Version consistency

- [ ] `VERSION` == `.codex-plugin/plugin.json` `version` == the git tag being
      created (without the `v` prefix, e.g. `VERSION` = `1.0.0`, tag =
      `v1.0.0`).
- [ ] `CHANGELOG.md` has an entry for this version.
- [ ] The tag does not already exist -- never overwrite an existing tag.

## Publication state

- [ ] Report the release using exactly one of the two defined states:
      `v<VERSION> PREPARED -- NOT PUBLISHED` or `v<VERSION> PUBLISHED`. Local
      validation passing never by itself implies "PUBLISHED" (rule 152).

## After release

- [ ] Component repositories remain independently maintained and are not
      deleted, archived, or deprecated because of this release (rule 88-89).
