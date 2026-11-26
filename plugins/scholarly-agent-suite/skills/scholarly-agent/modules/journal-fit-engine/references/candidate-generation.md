# Candidate Generation

## Pipeline

```
broad discovery → candidate pool (10–30) → hard filters → deep-fit analysis → shortlist (3–8)
```

Do not evaluate thousands of journals in depth. Cast a reasonably wide net for
discovery, then narrow quickly with hard filters before spending effort on
deep-fit analysis.

## Candidate sources

- manuscript's own reference list (where its intellectual conversation is
  already published)
- journals publishing the closest recent literature (not just cited works —
  actively search for recent similar papers)
- disciplinary indexes and directories
- OpenAlex source graph or equivalent venue-linkage data
- author's own publication history (as a signal, not a constraint)
- related-paper venues (papers similar in question/method/theory/data, not
  just topic)
- user-provided target journals (always include and evaluate these even if
  they weren't independently discovered)

Do not rely on keyword search alone — this is one of the most common weak
patterns in journal recommendation and is explicitly disallowed. A journal
whose title merely contains a manuscript keyword is not evidence of fit.

## Reference-neighborhood analysis

A strong signal: where is the manuscript's intellectual conversation already
published? Inspect journals appearing among the manuscript's references,
closest related literature, cited theoretical foundations, and recent
competing studies.

Caution: avoid circularity — this signal should surface candidates, not be
the sole justification for recommending them. A manuscript that heavily cites
Journal X does not automatically belong in Journal X; verify independently
against Journal X's actual scope, article types, and recent corpus.

## Recent-neighbor matching

Identify papers similar to the manuscript in research question, method,
theory, data type, and contribution (not just topic), then inspect where
those papers were published. This is often stronger evidence than
title-keyword matching because it captures the actual scholarly conversation
rather than surface vocabulary.

## No keyword-only matching

Never justify a candidate purely because the journal's title or scope
contains a term that also appears in the manuscript. This produces
superficially plausible but substantively wrong recommendations (e.g. a
"Journal of AI Governance" that only publishes empirical policy studies is
not a fit for a doctrinal legal argument just because both mention "AI
governance").

## Journal similarity graph (future-compatible concept)

Conceptually: manuscript → closest papers → their venues → related venues.
Do not build a heavy graph database for this — treat it as a reasoning
pattern to apply manually/via retrieval, not infrastructure to construct.

## Corpus Builder reuse

If `scholarly-corpus-builder` is available, request specific missing
evidence (a journal profile, a recent sample, article-type distribution,
method profile) rather than re-deriving retrieval logic. Reuse cached
profiles when they are still `CURRENT` (see [journal-profile.md](journal-profile.md)).
See [integration.md](integration.md) for the request contract.
