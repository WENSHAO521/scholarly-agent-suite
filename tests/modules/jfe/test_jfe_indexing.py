import unittest

from jfe.indexing import (
    CANNOT_VERIFY,
    OFFICIALLY_VERIFIED,
    UNCHECKABLE_INDEXES,
    UNCHECKABLE_METRICS,
    assess_indexing,
)
from jfe.journal_evidence import JournalEvidence


class AssessIndexingTests(unittest.TestCase):
    def test_doaj_true_is_officially_verified(self):
        evidence = JournalEvidence(display_name="X", is_in_doaj=True)
        result = assess_indexing(evidence).as_dict()
        self.assertEqual(result["DOAJ"]["state"], OFFICIALLY_VERIFIED)
        self.assertTrue(result["DOAJ"]["value"])

    def test_doaj_false_is_still_officially_verified_a_definite_fact(self):
        evidence = JournalEvidence(display_name="X", is_in_doaj=False)
        result = assess_indexing(evidence).as_dict()
        self.assertEqual(result["DOAJ"]["state"], OFFICIALLY_VERIFIED)
        self.assertFalse(result["DOAJ"]["value"])

    def test_doaj_unknown_is_cannot_verify(self):
        evidence = JournalEvidence(display_name="X", is_in_doaj=None)
        result = assess_indexing(evidence).as_dict()
        self.assertEqual(result["DOAJ"]["state"], CANNOT_VERIFY)

    def test_scopus_and_wos_are_always_cannot_verify(self):
        """No claim about a paid/authenticated index is ever fabricated
        from a free adapter, no matter what the evidence otherwise
        contains."""
        evidence = JournalEvidence(display_name="X", is_in_doaj=True, apc_usd=0, is_oa=True)
        result = assess_indexing(evidence).as_dict()
        for name in ("Scopus", "Web of Science", "SCIE", "SSCI"):
            self.assertEqual(result[name]["state"], CANNOT_VERIFY)
            self.assertIsNone(result[name]["value"])

    def test_no_quartile_is_ever_returned_without_year_and_category_context(self):
        """A quartile is meaningless without naming its ranking system,
        category, and year (references/indexing-metrics.md) -- this module
        never has that context, so it must never populate a value."""
        evidence = JournalEvidence(display_name="X")
        result = assess_indexing(evidence).as_dict()
        for name in ("JCR quartile", "CiteScore quartile"):
            self.assertEqual(result[name]["state"], CANNOT_VERIFY)
            self.assertIsNone(result[name]["value"])

    def test_all_uncheckable_names_appear_exactly_once(self):
        evidence = JournalEvidence(display_name="X")
        result = assess_indexing(evidence).as_dict()
        for name in (*UNCHECKABLE_INDEXES, *UNCHECKABLE_METRICS):
            self.assertIn(name, result)


if __name__ == "__main__":
    unittest.main()
