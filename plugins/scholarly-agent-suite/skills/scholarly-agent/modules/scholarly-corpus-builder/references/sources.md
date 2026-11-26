# Sources, open access, reference managers, and provenance

Sections (each starts at an `<a id>` anchor; read only the one the task needs): [source-adapters](#source-adapters), [oa-resolution](#oa-resolution), [reference-managers](#reference-managers), [provenance-schema](#provenance-schema).

<a id="source-adapters"></a>

## Source Adapters

Implementation reference for the six scholarly-API adapters plus the
local User File adapter in `scb/adapters/`. Each declares only the
capabilities it actually supports (`scb/adapters/base.py`,
`AdapterCapabilities`) — a host must not assume every adapter answers
every kind of lookup.

### Capability summary

| Adapter | search | lookup_by_doi | lookup_by_pmid | lookup_by_pmcid | lookup_by_arxiv | abstract | journal_metadata |
|---|---|---|---|---|---|---|---|
| OpenAlex (`openalex.py`) | ✓ | ✓ | | | | ✓ | ✓ |
| Crossref (`crossref.py`) | ✓ | ✓ | | | | | ✓ |
| PubMed (`pubmed.py`) | ✓ | | ✓ | | | ✓ | |
| PMC (`pmc.py`) | | ✓ | ✓ | ✓ | | | |
| arXiv (`arxiv.py`) | ✓ | | | | ✓ | ✓ | |
| DOAJ (`doaj.py`) | ✓ | ✓ | | | | | ✓ |

### Canonical record

Every adapter normalizes into `scb.records.CanonicalRecord` — see
`references/sources.md#provenance-schema` for the field-level schema. Access
information is never asserted beyond what the source actually reports
(see `references/corpus-policy.md#copyright-boundary` — "do not equate `is_oa=true`
with unrestricted reuse").

### Configuration (all optional; none hard-coded)

```text
OPENALEX_MAILTO, OPENALEX_API_KEY
CROSSREF_MAILTO
NCBI_TOOL, NCBI_EMAIL, NCBI_API_KEY   (used by both pubmed.py and pmc.py)
```

### PMC — a real, documented API change

As of August 2026, NCBI decommissioned the legacy per-article "PMC OA
Web Service" (`oa.fcgi`) in favor of bulk PMC Cloud Service (AWS S3)
datasets — confirmed live on 2026-09-09. `scb/adapters/pmc.py` was
redesigned around this: it now only performs PMID/PMCID/DOI
cross-reference resolution via the current NCBI ID Converter API, and
honestly reports `access.is_oa = None` rather than guessing at OA
status. OA/license resolution for PMC-hosted articles falls back to
OpenAlex locations or Crossref license data instead (see
`references/sources.md#oa-resolution`). This is exactly the kind of drift
`references/corpus-policy.md#refresh-policy`'s reproducibility caveat anticipates —
"external scholarly databases evolve" is not abstract.

### DOAJ — journal-level vs. article-level license

DOAJ's `bibjson.journal.license` describes the *journal's stated
policy*, not a verified per-article license. `scb/adapters/doaj.py`
never writes that into an article record's `access.reuse_license` —
see its module docstring and `parse_journal_license()`.

### Error handling

Every `lookup_by_*` method returns `None` on a not-found or
irrecoverable error rather than raising; `search()` propagates errors
so the caller (`scb/acquisition.py`) can record them as a per-adapter
failure without aborting the whole acquisition. See
`scb/http_client.py` for the shared timeout/retry/backoff engine and
`tests/test_failure_handling.py` for the offline fault-injection
coverage.

### User File adapter

`scb/adapters/user_files.py` is local-only — no network call, ever. It
extracts text from `.txt/.md/.html/.xml/.docx` using only the standard
library; `.pdf` requires an injected or host-native extractor (no OCR
is implemented — see `references/corpus-policy.md#copyright-boundary`).

<a id="oa-resolution"></a>

## Open Access Resolution

Implementation reference for `scb/oa_resolver.py`. Input: a
`CanonicalRecord` (already possibly enriched by multiple adapters via
`scb/dedup.py`'s merge). Output: an `AccessResolution` naming the best
currently-known lawful access state.

### States, most to least actionable

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

### Retrieval depth

`scb/retrieval_depth.py` maps an `AccessResolution` (plus whether an
abstract is present) onto `LEVEL_0_METADATA` .. `LEVEL_3_FULLTEXT`.
`scb/acquisition.py` uses `meets_requested_depth()` to filter candidates
to the *minimum* level the caller actually asked for — a caller who
only needs `LEVEL_0_METADATA` should not be rejecting records just
because their full-text access happens to be restricted (see
`scb/manifest.py`'s `usable` semantics: "usable" means "met the
requested depth," not a fixed abstract-or-better bar).

### Known limitation

Since NCBI decommissioned PMC's per-article OA lookup (see
`references/sources.md#source-adapters`), OA status for PMC-hosted articles
depends on OpenAlex's `best_oa_location`/`locations` or Crossref's
`license` field being present on the same canonical record — if
neither adapter contributed that data, the resolver will honestly
report `LICENSE_UNKNOWN` or `METADATA_ONLY` rather than assume PMC
availability implies open access.

<a id="reference-managers"></a>

## Reference managers: import and export

Users often already have a curated library in Zotero, Mendeley, EndNote,
JabRef, or Paperpile. Import it instead of re-searching for works the user
has already chosen, and export results back so they land in the user's own
tool. Runtime: `scb/bibliography.py` (standard library only, no network).

### Formats

| Format | Typical source | Extension |
|---|---|---|
| BibTeX / BibLaTeX | Zotero, JabRef, Overleaf, Google Scholar, Better BibTeX | `.bib` |
| RIS | EndNote, Mendeley, Zotero, Web of Science, Scopus, most publisher sites | `.ris` |
| CSL-JSON | Zotero ("CSL JSON" export), Better BibTeX, pandoc/citeproc | `.json` |

Zotero has no separate format: export the collection as any of the three.
CSL-JSON keeps the most structure (separate family/given names, full dates).

```text
python -m scb.cli import-bib library.bib            # -> canonical records (JSON)
python -m scb.cli import-bib export.txt --format ris
python -m scb.cli import-bib library.json | python -m scb.cli export-bib --format bibtex
```

In code: `load_bibliography(path)`, `parse_bibtex/parse_ris/parse_csl_json(text)`,
and `export_bibliography(records, "bibtex" | "ris" | "csl-json")`.

### What imported records are, and are not

- **User-supplied metadata, state `NEEDS_CHECK`.** Each record carries a
  `user_bibliography` provenance entry. Library entries are often
  hand-typed, auto-scraped, or out of date (preprint metadata for a
  published article, a missing issue number). Before a record supports a
  material claim or is cited in a manuscript, verify it with an adapter
  lookup by DOI/PMID (Crossref, OpenAlex, PubMed) and keep the adapter's
  provenance alongside, per `shared/provenance-policy.md`.
- **Never repaired by guessing.** A malformed DOI or unparseable year is
  left empty and listed in `record.conflicts` for the user or a lookup to
  resolve.
- **Metadata only.** Importing a library does not grant access to full
  text. Retrieval depth and copyright rules (`references/sources.md#oa-resolution`,
  `references/corpus-policy.md#copyright-boundary`) apply exactly as for searched records.
  A PDF the user attaches is handled by the user-file adapter, not here.

### Uses

1. **Seed list for a corpus.** Treat the library as Tier 1 user-supplied
   candidates (`references/corpus-policy.md#source-hierarchy`): dedup against search
   results (`scb.dedup`), verify, then sample as usual. Say in the build
   record that the corpus was seeded from the user's library, because a
   personal library is a biased sample of a field.
2. **Citation source for writing.** The voice module cites only verified
   records. Hand it the verified subset; list the rest as "in your library
   but not yet verified."
3. **Author profile.** A library of the user's own publications identifies
   which works to request as Tier 1 text for an author-voice profile
   (`references/profiles.md#author-profile`). It does not replace authorization.
4. **Export back.** After a build or a literature review, export the
   selected, verified records in the user's format so they can import them
   into their manager. Citation keys from the original import are kept;
   generated keys follow `familyYEARfirstword` with `a`, `b`, ... suffixes on
   collision.

### Known limits

- BibTeX: common LaTeX accents and escapes are converted; arbitrary macros
  and math are passed through as text. `@string` macros and `#`
  concatenation are supported; `crossref` inheritance is not.
- RIS has no family/given structure for institutional authors; a corporate
  author exported to RIS comes back split at the last space (its display
  name is unchanged).
- Notes, attachments, tags-as-collections, and annotations are not imported.

<a id="provenance-schema"></a>

## Provenance Schema

Every source that contributes to a profile — even metadata-only — needs a
compact provenance record.

### Record schema

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

### Verification states

```text
VERIFIED           persistent identifier (DOI/ISBN/persistent_id) checked
PARTIALLY_VERIFIED  title/venue/year found but identifier unverified
NEEDS_CHECK         plausible but not yet confirmed; do not use for high-confidence claims
REJECTED             could not be confirmed, or evidence contradicts the claimed source
```

A plausible-sounding title and author is **not** automatically `VERIFIED`.
Verify persistent identifiers when available before assigning `VERIFIED`.

### Never fabricate

Do not invent or guess: DOI, ISSN, publication year, author list, or license.
If any of these is unknown, record it as `null` rather than a best guess, and
lower `verification` accordingly.

### Deduplication

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

### Version resolution

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

### Build record

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
