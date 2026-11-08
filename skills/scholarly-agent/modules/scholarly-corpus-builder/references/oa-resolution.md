# Open Access Resolution

Implementation reference for `scb/oa_resolver.py`. Input: a
`CanonicalRecord` (already possibly enriched by multiple adapters via
`scb/dedup.py`'s merge). Output: an `AccessResolution` naming the best
currently-known lawful access state.

## States, most to least actionable

```text
STRUCTURED_FULLTEXT_AVAILABLE   e.g. JATS/XML pointer
OA_PDF_AVAILABLE
OA_FULLTEXT_AVAILABLE
OA_LANDING_PAGE                  OA claimed but no direct text pointer
ABSTRACT_AVAILABLE
ACCESS_RESTRICTED                confirmed closed, no abstract either
LICENSE_UNKNOWN                  no OA signal at all, but a title exists
METADATA_ONLY
RESOLUTION_FAILED                no usable bibliographic data at all
```

`resolve_access()` stops at the first state whose evidence requirement
is met — it never probes a hidden publisher URL and never fabricates a
URL that wasn't actually present on the record (tested explicitly in
`tests/test_oa_resolver.py`).

## Retrieval depth

`scb/retrieval_depth.py` maps an `AccessResolution` (plus whether an
abstract is present) onto `LEVEL_0_METADATA` .. `LEVEL_3_FULLTEXT`.
`scb/acquisition.py` uses `meets_requested_depth()` to filter candidates
to the *minimum* level the caller actually asked for — a caller who
only needs `LEVEL_0_METADATA` should not be rejecting records just
because their full-text access happens to be restricted (see
`scb/manifest.py`'s `usable` semantics: "usable" means "met the
requested depth," not a fixed abstract-or-better bar).

## Known limitation

Since NCBI decommissioned PMC's per-article OA lookup (see
`references/source-adapters.md`), OA status for PMC-hosted articles
depends on OpenAlex's `best_oa_location`/`locations` or Crossref's
`license` field being present on the same canonical record — if
neither adapter contributed that data, the resolver will honestly
report `LICENSE_UNKNOWN` or `METADATA_ONLY` rather than assume PMC
availability implies open access.
