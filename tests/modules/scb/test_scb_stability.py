import os
import sys
import unittest


from scb.stability import (
    INSUFFICIENT_SAMPLE,
    MOSTLY_STABLE,
    STABLE,
    UNSTABLE,
    bootstrap_sentence_median_length,
    run_stability_check,
    split_corpus,
)
from scb.text_normalize import normalize_text

# A "stable" synthetic corpus: every document has very similar sentence
# length, first-person usage, hedging, and citation density.
_STABLE_TEMPLATE = """Introduction
We argue that institutional design shapes outcomes (Smith, 2020). We find that this pattern holds across cases (Doe, 2019). We suggest this may explain variation in adoption (Lee, 2021).

Results
The data show a consistent effect across all specifications (Kim, 2018). We find this result is robust (Park, 2017).
"""

# An "unstable" synthetic corpus: half the documents are short/direct
# with no hedging or citations, half are long/hedged/citation-heavy —
# a split test should catch the resulting inconsistency.
_UNSTABLE_SHORT = "This works. That works too. Done."
_UNSTABLE_LONG = (
    "It may perhaps be suggested that, under a wide range of plausible and carefully qualified conditions, "
    "the institutional arrangement in question could conceivably be associated with a range of downstream "
    "outcomes that scholars have long debated in the literature (Smith, 2020; Doe, 2019; Lee, 2021; Kim, 2018). "
    "We suggest this may possibly hold, though further qualification seems warranted (Park, 2017; Chen, 2022)."
)


def _stable_docs(n):
    return [normalize_text(_STABLE_TEMPLATE) for _ in range(n)]


def _unstable_docs(n):
    docs = []
    for i in range(n):
        text = _UNSTABLE_SHORT if i % 2 == 0 else _UNSTABLE_LONG
        docs.append(normalize_text(text))
    return docs


class TestSplitCorpus(unittest.TestCase):
    def test_alternating_split_is_deterministic_and_balanced(self):
        docs = _stable_docs(10)
        a, b = split_corpus(docs)
        self.assertEqual(len(a), 5)
        self.assertEqual(len(b), 5)
        a2, b2 = split_corpus(docs)
        self.assertEqual(a, a2)


class TestRunStabilityCheck(unittest.TestCase):
    def test_insufficient_sample_below_minimum(self):
        report = run_stability_check(_stable_docs(4))
        self.assertEqual(report.status, INSUFFICIENT_SAMPLE)

    def test_stable_corpus_is_classified_stable_or_mostly_stable(self):
        report = run_stability_check(_stable_docs(20))
        self.assertIn(report.status, (STABLE, MOSTLY_STABLE))
        self.assertGreater(report.stable_feature_share, 0.5)

    def test_unstable_corpus_is_flagged(self):
        report = run_stability_check(_unstable_docs(20))
        self.assertIn(report.status, (UNSTABLE, MOSTLY_STABLE))

    def test_feature_results_report_both_values(self):
        report = run_stability_check(_stable_docs(20))
        for result in report.feature_results:
            self.assertIsNotNone(result.value_a)
            self.assertIsNotNone(result.value_b)


class TestBootstrap(unittest.TestCase):
    def test_bootstrap_runs_and_reports_spread(self):
        result = bootstrap_sentence_median_length(_stable_docs(15), iterations=50)
        self.assertEqual(result.iterations, 50)
        self.assertEqual(len(result.estimates), 50)
        self.assertGreaterEqual(result.max, result.min)

    def test_bootstrap_is_reproducible_with_fixed_seed(self):
        docs = _stable_docs(15)
        r1 = bootstrap_sentence_median_length(docs, iterations=30, seed=42)
        r2 = bootstrap_sentence_median_length(docs, iterations=30, seed=42)
        self.assertEqual(r1.estimates, r2.estimates)

    def test_empty_corpus(self):
        result = bootstrap_sentence_median_length([], iterations=10)
        self.assertEqual(result.iterations, 0)


if __name__ == "__main__":
    unittest.main()
