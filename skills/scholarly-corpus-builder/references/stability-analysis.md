# Corpus Stability Analysis

Implementation reference for `scb/stability.py`. A profile should not
be trusted merely because a corpus exists — this module actually runs
a comparison, it does not assume stability.

## Split-corpus test

`run_stability_check(documents)`:

1. Below 10 documents: `INSUFFICIENT_SAMPLE` — no test is run.
2. Otherwise, `split_corpus()` deterministically alternates documents
   into two halves (reproducible without a seed — no randomness needed
   for a simple alternating split).
3. A `StyleProfile` is built for each half (`scb/profile_schema.py`).
4. Five numeric features are compared (sentence/paragraph length,
   first-person rate, hedge rate, citation density) using a **35%
   relative-difference tolerance** — an explicit, documented threshold,
   not a fitted statistical model.
5. `stable_feature_share >= 0.8` → `STABLE`; `>= 0.5` → `MOSTLY_STABLE`;
   otherwise `UNSTABLE`.

`STABLE` means the two halves of *this* corpus agree with each other —
it is a statement about internal consistency, not external validation
against ground truth, and not a claim that the corpus is representative
of the wider discipline/journal/author it was sampled from.

## Bootstrap resampling

`bootstrap_sentence_median_length(documents, iterations, seed)`
resamples documents with replacement (Python's stdlib `random`, no
third-party statistics package — PART XXV: "do not turn this into a
complex statistical package") and recomputes the sentence-length
median each time, reporting the spread (mean/stdev/min/max) across
resamples. Deterministic given a fixed seed — verified reproducible in
`tests/test_stability.py`.

## What this does not do

- No cross-disciplinary, human-QA'd validation of whether "stable"
  profiles actually match expert judgment (see the benchmark-honesty
  fixtures in `evals/production-hardening.jsonl`).
- No confidence interval or p-value — the module reports a descriptive
  spread, not an inferential statistic, deliberately avoiding false
  precision (see `references/style-feature-schema.md`).
