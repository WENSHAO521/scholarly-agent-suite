# Refresh Policy

## Corpus Selection Gate

Before retrieving new material, determine whether an existing cached profile
is sufficient. Possible states:

```text
CURRENT                 reuse the existing profile as-is
STALE                    reusable but should be refreshed soon or on request
INSUFFICIENT             existing profile too thin/narrow for the current need
NEW_TARGET                no existing profile for this target
USER_REQUESTED_REFRESH    user explicitly asked for a refresh
```

If `CURRENT`, reuse the existing profile — do not rebuild a journal corpus
every time the user writes another manuscript.

## Freshness defaults (policy defaults, not rigid requirements)

```text
Discipline corpus:                        12-24 months
Journal corpus:                            6-12 months
Fast-moving computing/AI journals/venues:  3-6 months (when current style
                                             materially matters)
Historical scholar corpus:                 no periodic refresh, unless better
                                             source material becomes available
Author corpus:                             refresh when new works are added or
                                             the user requests recalibration
```

## Time-window sampling

A journal profile usually emphasizes recent work — a common default is the
last 2-3 years — but adapt to publication volume, field stability, genre, and
user request. Historical trend studies may intentionally use longer windows.
Always record the sampling period actually used.

## Refresh decision

Before refreshing, compare:

```text
existing profile date
new publications available since then
journal redesign or editorial policy change
article-type changes
discipline evolution
user need
```

Possible outcomes:

```text
NO_REFRESH | PARTIAL_REFRESH | FULL_REFRESH
```

## Incremental refresh

Prefer incremental updates over full rebuilds. Example:

```text
existing journal corpus: 2024-2025
new refresh: add 2026 articles only
recompute the profile from the combined set
```

Do not redownload all prior sources unnecessarily.

## Refresh diff

When refreshing, surface what changed:

```text
stable features
changed features
newly observed features
removed assumptions
```

Example:

```text
2025 profile: limitations usually folded into the Discussion section
2026 refresh: a dedicated Limitations subsection is increasingly common
```

Do not overinterpret small changes as a trend.

## Profile staleness states

```text
CURRENT | AGING | STALE | INCOMPLETE
```

A journal profile may go stale due to editorial-policy changes, article-
architecture changes, elapsed time, or new article categories appearing.

## Deduplication (see also provenance-schema.md)

Deduplicate by DOI, persistent ID, normalized title, author/year, or
repository-publication equivalence. Do not count a preprint, an accepted
manuscript, and the version of record as three separate works.

## Versioning

Profiles should be versionable with simple, human-readable identifiers, e.g.:

```text
PAR-2026Q3
NatureMedicine-2026Q3
AuthorProfile-v3
```

No database is required — a manifest with a version id and timestamps is
sufficient.

## Cache metadata

```json
{
  "profile_id": "",
  "profile_type": "",
  "created_at": "",
  "updated_at": "",
  "sample_window": "",
  "source_count": 0,
  "source_hash": null,
  "status": "current"
}
```

## Suggested cache layout (conceptual)

```text
corpus_state/
  profiles/
  provenance/
  manifests/
```

This is conceptual unless the host provides artifact/file storage. Do not
write persistent user memory without authorization, and never fold a personal
author corpus into shared/global storage (see `author-profile.md` § Privacy).
