# Corpus Policy

Cross-cutting policy that applies to every corpus type.

## Corpus purpose declaration

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

## Sampling ranges (heuristics, not statistical guarantees)

```text
Journal profile:        20-50 articles
Discipline profile:     40-100 representative works
Historical scholar:      selected representative works (quality over count)
Personal author profile: ideally 5-20 substantive works
```

Avoid overrepresenting one special issue, one prolific author, one laboratory,
or one article genre. Sample by year, article type, subfield, methods, topic,
issue, and author diversity.

## Corpus sufficiency

More papers do not automatically improve a profile. Judge sufficiency by:

```text
genre diversity
feature stability (do new sources change the high-level features?)
source quality
temporal coverage
disciplinary coverage
```

## Stop rule

```text
Stop retrieval when:
  the requested profile is sufficiently supported
  AND additional sources show diminishing feature changes
  AND minimum genre/source diversity is achieved
```

Prefer 20 verified representative sources over 500 noisy or unverified
documents.

## Corpus build record

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

## Small-corpus honesty

```text
n < 5    -> label profile "illustrative"
n 5-19   -> label profile "limited"
n >= 20  -> normal confidence labeling applies (still not "definitive")
```

## Bias tracking

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

## Multilingual corpora

Metadata and text may be gathered in English, Chinese, German, French,
Japanese, Korean, Spanish, and other languages, but style metrics do not
transfer directly across languages. Record a `language` field per source and
do not merge multilingual sentence-level statistics into one number.

### Translation boundary

Translated text should not be used to infer the original author's exact
sentence style. For translated sources record `original_language`,
`analysis_language`, and `translation_status`. Use translated text mainly for
argument architecture and concept structure, not fine-grained sentence-style
inference.

## Book-writing corpus

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

## Corpus comparison mode

Support comparisons such as Journal A vs. Journal B, 1990s vs. 2020s
conventions, or historical scholar vs. contemporary field norm. Return:

```text
shared traits
differences
potential adaptation points
features that should not be changed
```

## Manifest

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

## No automatic quality judgment

Do not infer "better journal = better prose" or "high-impact = superior
scholarship." This skill is descriptive of writing architecture, not
evaluative of research quality or venue prestige.
