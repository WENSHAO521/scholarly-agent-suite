# Source Adapters

Implementation reference for the six scholarly-API adapters plus the
local User File adapter in `scb/adapters/`. Each declares only the
capabilities it actually supports (`scb/adapters/base.py`,
`AdapterCapabilities`) — a host must not assume every adapter answers
every kind of lookup.

## Capability summary

| Adapter | search | lookup_by_doi | lookup_by_pmid | lookup_by_pmcid | lookup_by_arxiv | abstract | journal_metadata |
|---|---|---|---|---|---|---|---|
| OpenAlex (`openalex.py`) | ✓ | ✓ | | | | ✓ | ✓ |
| Crossref (`crossref.py`) | ✓ | ✓ | | | | | ✓ |
| PubMed (`pubmed.py`) | ✓ | | ✓ | | | ✓ | |
| PMC (`pmc.py`) | | ✓ | ✓ | ✓ | | | |
| arXiv (`arxiv.py`) | ✓ | | | | ✓ | ✓ | |
| DOAJ (`doaj.py`) | ✓ | ✓ | | | | | ✓ |

## Canonical record

Every adapter normalizes into `scb.records.CanonicalRecord` — see
`references/provenance-schema.md` for the field-level schema. Access
information is never asserted beyond what the source actually reports
(see `references/copyright-boundary.md` — "do not equate `is_oa=true`
with unrestricted reuse").

## Configuration (all optional; none hard-coded)

```text
OPENALEX_MAILTO, OPENALEX_API_KEY
CROSSREF_MAILTO
NCBI_TOOL, NCBI_EMAIL, NCBI_API_KEY   (used by both pubmed.py and pmc.py)
```

## PMC — a real, documented API change

As of August 2026, NCBI decommissioned the legacy per-article "PMC OA
Web Service" (`oa.fcgi`) in favor of bulk PMC Cloud Service (AWS S3)
datasets — confirmed live on 2026-09-09. `scb/adapters/pmc.py` was
redesigned around this: it now only performs PMID/PMCID/DOI
cross-reference resolution via the current NCBI ID Converter API, and
honestly reports `access.is_oa = None` rather than guessing at OA
status. OA/license resolution for PMC-hosted articles falls back to
OpenAlex locations or Crossref license data instead (see
`references/oa-resolution.md`). This is exactly the kind of drift
`references/refresh-policy.md`'s reproducibility caveat anticipates —
"external scholarly databases evolve" is not abstract.

## DOAJ — journal-level vs. article-level license

DOAJ's `bibjson.journal.license` describes the *journal's stated
policy*, not a verified per-article license. `scb/adapters/doaj.py`
never writes that into an article record's `access.reuse_license` —
see its module docstring and `parse_journal_license()`.

## Error handling

Every `lookup_by_*` method returns `None` on a not-found or
irrecoverable error rather than raising; `search()` propagates errors
so the caller (`scb/acquisition.py`) can record them as a per-adapter
failure without aborting the whole acquisition. See
`scb/http_client.py` for the shared timeout/retry/backoff engine and
`tests/test_failure_handling.py` for the offline fault-injection
coverage.

## User File adapter

`scb/adapters/user_files.py` is local-only — no network call, ever. It
extracts text from `.txt/.md/.html/.xml/.docx` using only the standard
library; `.pdf` requires an injected or host-native extractor (no OCR
is implemented — see `references/copyright-boundary.md`).
