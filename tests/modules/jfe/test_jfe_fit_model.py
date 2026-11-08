import unittest

from jfe.fit_model import (
    EXCELLENT_FIT, NOT_RECOMMENDED, PLAUSIBLE_FIT, WEAK_FIT,
    compute_fit,
)
from jfe.journal_evidence import JournalEvidence
from jfe.manuscript_profile import ManuscriptProfile


class ComputeFitTests(unittest.TestCase):
    def test_hard_eliminated_is_always_not_recommended(self):
        manuscript = ManuscriptProfile(discipline="public administration", topic="policy diffusion")
        evidence = JournalEvidence(topics=["Public Policy and Administration Research"])
        result = compute_fit(manuscript, evidence, hard_eliminated=True)
        self.assertEqual(result.label, NOT_RECOMMENDED)
        self.assertTrue(result.hard_eliminated)

    def test_strong_topic_overlap_yields_high_label(self):
        manuscript = ManuscriptProfile(discipline="public administration", topic="policy diffusion states")
        evidence = JournalEvidence(topics=["Public Policy and Administration Research",
                                            "Local Government Finance and Decentralization"])
        result = compute_fit(manuscript, evidence, hard_eliminated=False)
        self.assertIn(result.label, (EXCELLENT_FIT, "STRONG FIT"))
        self.assertTrue(result.topic_overlap_terms)

    def test_no_overlap_yields_low_label(self):
        manuscript = ManuscriptProfile(discipline="quantum physics", topic="entanglement")
        evidence = JournalEvidence(topics=["Public Policy and Administration Research"])
        result = compute_fit(manuscript, evidence, hard_eliminated=False)
        self.assertIn(result.label, (WEAK_FIT, NOT_RECOMMENDED, PLAUSIBLE_FIT))
        self.assertEqual(result.topic_overlap_terms, [])

    def test_no_journal_topic_data_is_honest_not_fabricated(self):
        manuscript = ManuscriptProfile(discipline="public administration")
        evidence = JournalEvidence(topics=[])
        result = compute_fit(manuscript, evidence, hard_eliminated=False)
        self.assertIn("no topic data", result.explanation.lower())

    def test_stopwords_do_not_count_as_topic_overlap(self):
        # Regression: "and" appears in both a plausible manuscript topic
        # phrase and a real OpenAlex topic name ("Policy and Administration
        # Research") -- it must never be reported as matched evidence.
        manuscript = ManuscriptProfile(topic="quantum physics and entanglement")
        evidence = JournalEvidence(topics=["Public Policy and Administration Research"])
        result = compute_fit(manuscript, evidence, hard_eliminated=False)
        self.assertNotIn("and", result.topic_overlap_terms)

    def test_never_returns_a_numeric_score_field(self):
        manuscript = ManuscriptProfile(discipline="x")
        evidence = JournalEvidence(topics=["y"])
        result = compute_fit(manuscript, evidence, hard_eliminated=False)
        for field_name in vars(result):
            value = getattr(result, field_name)
            if field_name != "hard_eliminated":
                self.assertNotIsInstance(value, float, f"{field_name} leaked a raw float to the result")


if __name__ == "__main__":
    unittest.main()
