# Provenance Schema

Every source that contributes to a profile — even metadata-only — needs a
compact provenance record.

## Record schema

```json
{
  "source_id": "",
  "title": "",
  "authors": [],
  "year": null,
  "venue": null,
  "doi": null,
  "persistent_id": null,
  "source_url": null,
  "source_type": "metadata",
  "access_status": "open",
  "license": null,
  "full_text_used": false,
  "checked_at": null,
  "corpus_role": "",
  "verification": "verified"
}
```

`source_type` (one of):

```text
metadata | abstract | open_full_text | public_domain | user_supplied | author_manuscript
```

`access_status` (one of): `open | access_restricted | not_found | unknown`

## Verification states

```text
VERIFIED           persistent identifier (DOI/ISBN/persistent_id) checked
PARTIALLY_VERIFIED  title/venue/year found but identifier unverified
NEEDS_CHECK         plausible but not yet confirmed; do not use for high-confidence claims
REJECTED             could not be confirmed, or evidence contradicts the claimed source
```

A plausible-sounding title and author is **not** automatically `VERIFIED`.
Verify persistent identifiers when available before assigning `VERIFIED`.

## Never fabricate

Do not invent or guess: DOI, ISSN, publication year, author list, or license.
If any of these is unknown, record it as `null` rather than a best guess, and
lower `verification` accordingly.

## Deduplication

Deduplicate by, in order of reliability:

```text
DOI
persistent ID
normalized title
author + year
repository-publication equivalence (a repository copy of a published article)
```

Do not count a preprint, an accepted manuscript, and the version of record as
three independent works when they are versions of the same study — resolve to
one `source_id` and record versions under it (see § Version resolution).

## Version resolution

When multiple versions of the same work exist, record which were seen:

```text
preprint
accepted_manuscript
version_of_record
repository_copy
```

Prefer the version of record for bibliographic identity (title, venue, year,
DOI). Prefer a lawfully open version (preprint, accepted manuscript, repository
copy) for full-text feature analysis when the version of record is not openly
accessible. Note in `corpus_role` which version was actually used for feature
extraction.

## Build record

Track retrieval funnel counts honestly — do not claim a source count that was
not actually processed:

```json
{
  "requested_sources": 40,
  "retrieval_attempts": 45,
  "retrieved": 38,
  "usable": 32,
  "rejected": 6,
  "full_text_used": 15,
  "abstract_only": 12,
  "metadata_only": 5
}
```
