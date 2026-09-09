# Shared protocol versioning

Rules for evolving the protocols in `protocols/`, which are the main glue
between specialist Skills.

## Rule

- An **additive, optional** change (a new optional field, a new enum value
  that old consumers can ignore) stays on the **same protocol major version**
  (e.g. `SCHOLARLY_PROFILE_V1` gains an optional field and remains
  `SCHOLARLY_PROFILE_V1`).
- A **breaking semantic change** (removing/renaming a required field,
  changing a field's meaning or type, making an optional field required)
  requires a **new protocol major version** (`SCHOLARLY_PROFILE_V2`).

Inter-Skill contracts are not casually broken. A component bump that would
require a breaking protocol change is a Suite MAJOR event (see
`README.md#suite-versioning`), not a patch.

## Stability in practice

- Every schema in `protocols/*.schema.json` declares its logical id via
  `title` (e.g. `"title": "SCHOLARLY_PROFILE_V1"`) -- that string, not the
  filename, is the stable identifier referenced by SKILL.md files and other
  schemas.
- `additionalProperties: false` is deliberate: it makes an accidental
  breaking change (a producer emitting an undocumented shape) fail suite
  contract tests immediately instead of silently drifting.

## Adapters

`protocols/` does not currently ship any `V1 -> V2` converter. Rule 80
deliberately forbids building speculative converters before a V2 actually
exists. If a future release introduces one, `shared/protocol-versioning.md`
is the place to document the supported conversion paths and their
limitations.

## Mismatch handling

If a consumer receives a protocol object whose `protocol` field names a
version it does not recognize, it must not guess a mapping. It reports a
`PROTOCOL_MISMATCH` error (see `shared/error-taxonomy` list in
`skills/scholarly-agent/references/routing-matrix.md`) rather than silently
coercing the shape (rule 79).
