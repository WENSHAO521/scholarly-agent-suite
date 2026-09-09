# Shared provenance policy

Defines what every `PROVENANCE_RECORD_V1` (see
`protocols/provenance.schema.json`) must capture, and how conflicts between
sources are handled. Applies to scholarly-corpus-builder and journal-fit-engine
directly; scholarly-voice-engine and scholarly-agent consume it but do not
originate it.

## Fields

- **Source identity** -- DOI, ISSN, canonical URL, or an explicit
  `user-supplied` marker. Never a bare title/author guess standing in for an
  identifier.
- **Verification status** -- one of `verified`, `unverified`,
  `partially-verified`, `conflicting`. A field pulled from a single
  unconfirmed source is `unverified`, not `verified`.
- **Retrieval date** -- the date the source was actually fetched/checked, used
  to compute `freshness` (`current` / `aging` / `stale`) downstream.
- **Field provenance** -- when a profile aggregates many sources, each
  contested field should be traceable to which source(s) produced it, not just
  the profile as a whole.
- **Profile provenance** -- a `SCHOLARLY_PROFILE_V1` or
  `TARGET_JOURNAL_PROFILE_V1` carries one summarized `provenance` block, but
  that summary must not overstate the weakest source it depends on.

## Conflict handling

When two sources disagree on a fact (e.g. two directories disagree on a
journal's OA status), do not silently pick one:

1. Record both values in `conflict_notes`.
2. Set `verification_status: conflicting`.
3. Prefer the source closer to the primary record (publisher/registry over a
   third-party aggregator) only as a *reported preference*, not as a silent
   overwrite -- the conflict stays visible.

## Minimal necessary use

- Retain only what downstream protocols need (metadata, measured features,
  provenance) -- not full-text copies of copyrighted material.
- Never bypass a paywall or access restriction to fill in a provenance field;
  mark it `access-restricted` instead (see `integrity-policy.md`).

## Cross-Skill obligation

Any Skill that receives a profile with `verification_status: conflicting` or
`freshness: stale` must preserve that flag in whatever it produces downstream
-- it may not "launder" a conflicting/stale field into a confidently-stated
one (rule 76, rule 79).
