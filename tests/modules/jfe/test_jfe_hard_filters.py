import unittest

from jfe.apc_oa import MANDATORY_APC
from jfe.hard_filters import (
    CANNOT_VERIFY, FAIL, PASS,
    apply_all, check_inactive, check_no_apc_constraint, eliminated,
)
from jfe.journal_evidence import JournalEvidence
from jfe.manuscript_profile import ManuscriptProfile


class InactiveFilterTests(unittest.TestCase):
    def test_recently_active_passes(self):
        result = check_inactive(JournalEvidence(last_publication_year=2026), current_year=2026)
        self.assertEqual(result.result, PASS)

    def test_long_inactive_fails(self):
        result = check_inactive(JournalEvidence(last_publication_year=2018), current_year=2026)
        self.assertEqual(result.result, FAIL)

    def test_no_data_cannot_verify(self):
        result = check_inactive(JournalEvidence(last_publication_year=None), current_year=2026)
        self.assertEqual(result.result, CANNOT_VERIFY)

    def test_boundary_just_under_threshold_passes(self):
        result = check_inactive(JournalEvidence(last_publication_year=2023), current_year=2026)
        self.assertEqual(result.result, PASS)


class NoApcConstraintFilterTests(unittest.TestCase):
    def test_no_constraint_stated_passes(self):
        manuscript = ManuscriptProfile()
        result = check_no_apc_constraint(manuscript, MANDATORY_APC)
        self.assertEqual(result.result, PASS)

    def test_constraint_stated_and_mandatory_apc_fails(self):
        manuscript = ManuscriptProfile(constraints={"no_mandatory_apc": True})
        result = check_no_apc_constraint(manuscript, MANDATORY_APC)
        self.assertEqual(result.result, FAIL)

    def test_constraint_stated_and_no_mandatory_apc_passes(self):
        manuscript = ManuscriptProfile(constraints={"no_mandatory_apc": True})
        result = check_no_apc_constraint(manuscript, "DIAMOND_OA")
        self.assertEqual(result.result, PASS)


class EliminationTests(unittest.TestCase):
    def test_cannot_verify_alone_does_not_eliminate(self):
        manuscript = ManuscriptProfile()
        evidence = JournalEvidence(last_publication_year=2026)
        results = apply_all(manuscript, evidence, "UNKNOWN", current_year=2026)
        # language + article_type are always CANNOT_VERIFY in this
        # implementation; that alone must never eliminate a candidate.
        self.assertFalse(eliminated(results))

    def test_actual_fail_eliminates(self):
        manuscript = ManuscriptProfile()
        evidence = JournalEvidence(last_publication_year=2015)
        results = apply_all(manuscript, evidence, "UNKNOWN", current_year=2026)
        self.assertTrue(eliminated(results))


if __name__ == "__main__":
    unittest.main()
