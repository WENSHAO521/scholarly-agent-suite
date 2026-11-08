# Release checklist

Releases are published automatically. On every push to `master`,
`.github/workflows/release.yml` checks whether release `v<VERSION>` exists;
if not, it validates, runs the tests, builds the runtime ZIP twice (they
must be byte-identical), and publishes the release with the ZIP,
`release-manifest.json`, `SHA256SUMS`, and the version's CHANGELOG section
as notes. An existing release is never overwritten.

So a release is: bump the version, write the CHANGELOG section, and merge.
Before merging a version bump, confirm the items below. This is the
concrete procedure behind rule 97 / rule 145.

## Layout

- [ ] `skills/` contains exactly one Skill, `skills/scholarly-agent/`, and the
      four modules live at `skills/scholarly-agent/modules/<name>/MODULE.md`
      with no `SKILL.md` or frontmatter of their own.
- [ ] `COMPONENTS.json` lists the four modules with their `merged_from`
      origin, and its `suite_version` matches `VERSION`.

## Validate

- [ ] `python scripts/validate_suite.py` passes with 0 failures.
- [ ] `pytest tests/` passes.
- [ ] The Skill is self-contained: modules, `protocols/`, `shared/`, and
      workflow recipes all resolve from inside `skills/scholarly-agent/` --
      verified by `tests/test_standalone_independence.py`.
- [ ] Every required workflow recipe (`scripts/workflow_manifest.
      REQUIRED_WORKFLOWS`) exists at the runtime-canonical path
      `skills/scholarly-agent/references/workflows/` -- never only at the
      repository-root `workflows/` mirror. `python scripts/
      sync_workflows.py --check` passes (also run as part of
      `validate_suite.py`); if it reports drift, regenerate with
      `python scripts/sync_workflows.py` and re-check, never hand-edit
      `workflows/` directly.
- [ ] `tests/test_workflow_packaging.py` and `tests/
      test_workflow_install_smoke.py` pass -- these are the packaging
      regression guard for the theory-paper.md runtime-visibility
      incident (a recipe present in the repo/tag but unreachable from an
      installed Skill's own runtime boundary).

## Package

- [ ] `python scripts/package_suite.py` builds
      `dist/scholarly-agent-suite-v<VERSION>.zip` with no `tests/`, `evals/`,
      `.github/`, dev scripts, or component `.git` metadata inside.
- [ ] `release-manifest.json` inside the ZIP lists the exact suite version,
      component versions, source commits, protocol versions, file count, and
      a SHA-256 checksum, with no private machine paths.
- [ ] Inspect the built ZIP directly (not just the source tree) and confirm
      `skills/scholarly-agent/references/workflows/theory-paper.md` (and
      every other required workflow recipe) is actually present inside it
      -- e.g. `unzip -l dist/scholarly-agent-suite-v<VERSION>.zip | grep
      references/workflows/`. Do not declare a release ready because the
      repository contains the file; the acceptance condition is the built
      artifact containing it.
- [ ] Re-running packaging from a clean checkout of the same commit produces
      a ZIP with the same SHA-256 (deterministic ordering/timestamps).

## Version consistency

- [ ] `VERSION` == `.codex-plugin/plugin.json` `version` ==
      `COMPONENTS.json` `suite_version` (the release tag is `v<VERSION>`).
- [ ] `CHANGELOG.md` has a `## v<VERSION> -- <date>` section;
      `python scripts/release_notes.py` prints it. The workflow refuses to
      publish without one.
- [ ] Merging a change *without* a version bump publishes nothing. Merging
      the first commit with a new `VERSION` publishes it -- bump only when
      the release is meant to go out.

## Publication state

- [ ] Report the release using exactly one of the two defined states:
      `v<VERSION> PREPARED -- NOT PUBLISHED` (merged or merging, workflow not
      yet green) or `v<VERSION> PUBLISHED` (the GitHub release exists).
      Local validation passing never by itself implies "PUBLISHED"
      (rule 152). The GitHub release is the record of publication.

## After release

- [ ] Since v2.0.0 module changes are made in this repository. The former
      component repositories are not synced from; archiving them is a
      separate, deliberate owner decision, not part of a release.
