# Reference managers: import and export

Users often already have a curated library in Zotero, Mendeley, EndNote,
JabRef, or Paperpile. Import it instead of re-searching for works the user
has already chosen, and export results back so they land in the user's own
tool. Runtime: `scb/bibliography.py` (standard library only, no network).

## Formats

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

## What imported records are, and are not

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
  text. Retrieval depth and copyright rules (`references/oa-resolution.md`,
  `references/copyright-boundary.md`) apply exactly as for searched records.
  A PDF the user attaches is handled by the user-file adapter, not here.

## Uses

1. **Seed list for a corpus.** Treat the library as Tier 1 user-supplied
   candidates (`references/source-hierarchy.md`): dedup against search
   results (`scb.dedup`), verify, then sample as usual. Say in the build
   record that the corpus was seeded from the user's library, because a
   personal library is a biased sample of a field.
2. **Citation source for writing.** The voice module cites only verified
   records. Hand it the verified subset; list the rest as "in your library
   but not yet verified."
3. **Author profile.** A library of the user's own publications identifies
   which works to request as Tier 1 text for an author-voice profile
   (`references/author-profile.md`). It does not replace authorization.
4. **Export back.** After a build or a literature review, export the
   selected, verified records in the user's format so they can import them
   into their manager. Citation keys from the original import are kept;
   generated keys follow `familyYEARfirstword` with `a`, `b`, ... suffixes on
   collision.

## Known limits

- BibTeX: common LaTeX accents and escapes are converted; arbitrary macros
  and math are passed through as text. `@string` macros and `#`
  concatenation are supported; `crossref` inheritance is not.
- RIS has no family/given structure for institutional authors; a corporate
  author exported to RIS comes back split at the last space (its display
  name is unchanged).
- Notes, attachments, tags-as-collections, and annotations are not imported.
