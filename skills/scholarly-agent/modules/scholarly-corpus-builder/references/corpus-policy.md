# Corpus policy

Sections (each starts at an `<a id>` anchor; read only the one the task needs): [corpus-policy](#corpus-policy), [copyright-boundary](#copyright-boundary), [source-hierarchy](#source-hierarchy), [refresh-policy](#refresh-policy).

<a id="corpus-policy"></a>

## Corpus Policy

Cross-cutting policy that applies to every corpus type.

### Corpus purpose declaration

Every corpus records a `purpose`, one of:

```text
disciplinary_style | journal_style | historical_voice | author_voice
argument_structure | book_style | literature_evidence
```

Never silently reuse a style corpus (built to learn *how* something is
written) as a scientific evidence base (used to support a research claim).
These are different products even when the underlying papers overlap. A
style corpus for a journal is not vetted for evidentiary reliability, and an
evidence corpus is not sampled for stylistic representativeness.

### Sampling ranges (heuristics, not statistical guarantees)

```text
Journal profile:        20-50 articles
Discipline profile:     40-100 representative works
Historical scholar:      selected representative works (quality over count)
Personal author profile: ideally 5-20 substantive works
```

Avoid overrepresenting one special issue, one prolific author, one laboratory,
or one article genre. Sample by year, article type, subfield, methods, topic,
issue, and author diversity.

### Corpus sufficiency

More papers do not automatically improve a profile. Judge sufficiency by:

```text
genre diversity
feature stability (do new sources change the high-level features?)
source quality
temporal coverage
disciplinary coverage
```

### Stop rule

```text
Stop retrieval when:
  the requested profile is sufficiently supported
  AND additional sources show diminishing feature changes
  AND minimum genre/source diversity is achieved
```

Prefer 20 verified representative sources over 500 noisy or unverified
documents.

### Corpus build record

Track honestly and report when asked:

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

Never claim a source count that was not actually retrieved or processed.

### Small-corpus honesty

```text
n < 5    -> label profile "illustrative"
n 5-19   -> label profile "limited"
n >= 20  -> normal confidence labeling applies (still not "definitive")
```

### Bias tracking

Record when material:

```text
OA bias
English-language bias
recent-publication bias
special-issue bias
methodological bias
author-concentration bias
repository-availability bias
```

### Multilingual corpora

Metadata and text may be gathered in English, Chinese, German, French,
Japanese, Korean, Spanish, and other languages, but style metrics do not
transfer directly across languages. Record a `language` field per source and
do not merge multilingual sentence-level statistics into one number.

#### Translation boundary

Translated text should not be used to infer the original author's exact
sentence style. For translated sources record `original_language`,
`analysis_language`, and `translation_status`. Use translated text mainly for
argument architecture and concept structure, not fine-grained sentence-style
inference.

### Book-writing corpus

Relevant lawful sources: public-domain monographs, user-authorized book
chapters, open-access scholarly books, publisher previews when legally
usable. Derived features differ from journal-article features:

```text
chapter length
chapter-opening strategy
concept recurrence
cross-chapter transitions
citation distribution
narrative density
argument progression
```

Do not treat book prose as simply "enlarged journal prose" — assess it on its
own terms.

### Corpus comparison mode

Support comparisons such as Journal A vs. Journal B, 1990s vs. 2020s
conventions, or historical scholar vs. contemporary field norm. Return:

```text
shared traits
differences
potential adaptation points
features that should not be changed
```

### Manifest

Every corpus should have a manifest recording:

```text
corpus type
purpose
target
sample period
source count
included source types
selection criteria
exclusion criteria
known limitations
```

This is what makes a profile reproducible and auditable later.

### No automatic quality judgment

Do not infer "better journal = better prose" or "high-impact = superior
scholarship." This skill is descriptive of writing architecture, not
evaluative of research quality or venue prestige.

<a id="copyright-boundary"></a>

## Copyright Boundary

This file states the hard rules. They are not defaults to be optimized away
under time pressure or user insistence — they are the floor.

1. **Derive features, don't reproduce text.** The product of this skill is a
   structured profile (sentence rhythm, argument architecture, section
   layout), not a copy of the source. Quotations, when used at all, must be
   short and clearly justified by the analytical point being made.
2. **Use only lawful access paths.** Tier 1 (user-authorized), Tier 2–3
   (open metadata/abstracts), Tier 4 (genuinely open-access full text), and
   Tier 5 (verified or reasonably believed public domain).
3. **Never bypass paywalls, login walls, or bot/anti-scraping protections.**
   If a source sits behind one and no lawful open version exists, stop at
   metadata or abstract level and record `access_status: access_restricted`.
4. **Do not use leaked databases, unauthorized mirrors, or shadow libraries**
   to acquire books or articles, even when they are "commonly available."
5. **Do not store unnecessary full text.** If full text was used transiently
   to extract features, persistent storage should retain the provenance
   record and derived features — not the full text — unless the user has
   separately authorized retaining their own material (Tier 1).
6. **Do not build characteristic-phrase imitation libraries.** Never compile
   a bank of an author's or journal's distinctive sentences/phrases intended
   for direct reuse. Feature extraction stays at the level of patterns
   ("claim-first paragraphs," "mechanism-centered examples"), not verbatim
   text.
7. **Do not create living-author imitation systems.** A profile of a living,
   contemporary scholar's public work may describe high-level argument and
   structural tendencies, but must not become a signature-sentence generator
   or a template for passing off writing as theirs.
8. **Retain provenance for everything used.** Every source that contributed to
   a profile must have a provenance record (`sources.md#provenance-schema`), even if
   only metadata was used.
9. **Do not fabricate licensing.** If a license is unknown, record
   `license: null`. Free access does not imply a permissive license (e.g. do
   not infer `CC BY` from mere availability).
10. **Public domain is not global.** Status varies by jurisdiction and can
    depend on author death date, publication date, and renewal history. Use
    `public_domain_status: verified / likely / unknown` rather than a blanket
    assertion, and prefer conservative wording when unverified.

### What to do when access is unavailable

```text
record metadata
mark full_text_status = unavailable
continue with lawful evidence (abstract, headings, prior profile)
```

Do not treat an access failure as a task failure — the profile can usually
still be built, just with a lower confidence rating and a recorded limitation.

### Refusal pattern

If a user explicitly asks to bypass a paywall, scrape protected content, pull
from a leaked/shadow database, or build a phrase-imitation library for a living
author, decline that specific action, explain the lawful alternative (Tier 1–4
sources, feature-level profiling), and proceed with what is actually
obtainable.

<a id="source-hierarchy"></a>

## Source Hierarchy

Prefer sources in this order. Only move down a tier when the tier above cannot
answer the analytical question at hand.

### Tier 1 — User-provided or explicitly authorized material

- Uploaded papers or books
- Author manuscript files
- Personal publication archive
- Institutionally authorized corpus

This is the preferred, and normally required, source for personal author
profiling (see `profiles.md#author-profile` § Authorization boundary). Do not substitute
publicly retrieved papers for this tier merely because a name matches.

### Tier 2 — Open metadata

- Crossref, OpenAlex, PubMed metadata, other bibliographic indexes
- Repository and publisher metadata

Metadata alone is usually sufficient for: title analysis, year distributions,
journal sampling, author disambiguation, DOI verification, venue
identification. **Do not retrieve full text when metadata solves the task.**

### Tier 3 — Open abstracts

Use when lawfully accessible. Abstracts support: argument framing, contribution
language, claim calibration, abstract architecture, field terminology.

### Tier 4 — Open-access full text

Prioritize, in order of preference:

1. Public repositories and institutional repositories
2. PMC or similar lawful archives
3. Preprint servers
4. Author manuscripts
5. Clearly open-licensed publisher versions

Verify access status when practical before use. Never bypass a paywall or bot
protection to reach a version that would otherwise sit behind Tier 4's lawful
boundary.

### Tier 5 — Public-domain historical works

Valuable for historical voice profiles. For each work record: edition, source,
publication date, and public-domain status when known (see
`profiles.md#historical-profile` and `corpus-policy.md#copyright-boundary` for jurisdiction caveats —
public-domain status is not global and must not be assumed).

### Retrieval minimization decision sequence

```text
What feature is needed?
  -> Can metadata answer it?          -> use Tier 2, stop
  -> Can the abstract answer it?      -> use Tier 3, stop
  -> Can section headings answer it?  -> use structural metadata, stop
  -> Is open full text materially necessary? -> use Tier 4, minimally
```

Only escalate a tier when doing so would change the analytical result — not
because more text is available.

### Escalation is never permission to bypass access

Escalating from Tier 3 to Tier 4 means "look for a lawful open-access copy," not
"retrieve the paywalled version by any means." If no lawful Tier 4 copy exists,
stop at Tier 3, record `access_status: access_restricted`, and continue the
profile with abstract-level evidence.

<a id="refresh-policy"></a>

## Refresh Policy

### Corpus Selection Gate

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

### Freshness defaults (policy defaults, not rigid requirements)

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

### Time-window sampling

A journal profile usually emphasizes recent work — a common default is the
last 2-3 years — but adapt to publication volume, field stability, genre, and
user request. Historical trend studies may intentionally use longer windows.
Always record the sampling period actually used.

### Refresh decision

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

### Incremental refresh

Prefer incremental updates over full rebuilds. Example:

```text
existing journal corpus: 2024-2025
new refresh: add 2026 articles only
recompute the profile from the combined set
```

Do not redownload all prior sources unnecessarily.

### Refresh diff

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

### Profile staleness states

```text
CURRENT | AGING | STALE | INCOMPLETE
```

A journal profile may go stale due to editorial-policy changes, article-
architecture changes, elapsed time, or new article categories appearing.

### Deduplication (see also sources.md#provenance-schema)

Deduplicate by DOI, persistent ID, normalized title, author/year, or
repository-publication equivalence. Do not count a preprint, an accepted
manuscript, and the version of record as three separate works.

### Versioning

Profiles should be versionable with simple, human-readable identifiers, e.g.:

```text
PAR-2026Q3
NatureMedicine-2026Q3
AuthorProfile-v3
```

No database is required — a manifest with a version id and timestamps is
sufficient.

### Cache metadata

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

### Suggested cache layout (conceptual)

```text
corpus_state/
  profiles/
  provenance/
  manifests/
```

This is conceptual unless the host provides artifact/file storage. Do not
write persistent user memory without authorization, and never fold a personal
author corpus into shared/global storage (see `profiles.md#author-profile` § Privacy).
