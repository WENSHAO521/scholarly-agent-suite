import unittest

from jfe.apc_oa import (
    DIAMOND_OA, HYBRID_OA_OPTIONAL, MANDATORY_APC, UNKNOWN,
    classify, violates_no_apc_constraint,
)
from jfe.journal_evidence import JournalEvidence


def evidence(**kwargs) -> JournalEvidence:
    return JournalEvidence(**kwargs)


class ClassifyTests(unittest.TestCase):
    def test_oa_with_no_apc_is_diamond(self):
        result = classify(evidence(is_oa=True, apc_usd=None))
        self.assertEqual(result.state, DIAMOND_OA)

    def test_oa_with_zero_apc_is_diamond(self):
        result = classify(evidence(is_oa=True, apc_usd=0))
        self.assertEqual(result.state, DIAMOND_OA)

    def test_oa_with_apc_is_mandatory(self):
        result = classify(evidence(is_oa=True, apc_usd=4029))
        self.assertEqual(result.state, MANDATORY_APC)

    def test_subscription_with_apc_is_hybrid_optional(self):
        result = classify(evidence(is_oa=False, apc_usd=3000))
        self.assertEqual(result.state, HYBRID_OA_OPTIONAL)

    def test_subscription_with_no_apc_is_unknown_not_free(self):
        # A subscription journal with no recorded hybrid fee isn't
        # confidently classifiable from this alone -- must not silently
        # become DIAMOND_OA (it isn't OA at all).
        result = classify(evidence(is_oa=False, apc_usd=None))
        self.assertEqual(result.state, UNKNOWN)

    def test_unresolved_oa_status_is_unknown(self):
        result = classify(evidence(is_oa=None, apc_usd=None))
        self.assertEqual(result.state, UNKNOWN)


class NoApcConstraintTests(unittest.TestCase):
    def test_mandatory_apc_violates_constraint(self):
        result = classify(evidence(is_oa=True, apc_usd=4029))
        self.assertTrue(violates_no_apc_constraint(result))

    def test_hybrid_optional_does_not_violate_constraint(self):
        result = classify(evidence(is_oa=False, apc_usd=3000))
        self.assertFalse(violates_no_apc_constraint(result))

    def test_diamond_oa_does_not_violate_constraint(self):
        result = classify(evidence(is_oa=True, apc_usd=None))
        self.assertFalse(violates_no_apc_constraint(result))

    def test_unknown_does_not_violate_constraint(self):
        # Absence of evidence is not evidence of a mandatory fee.
        result = classify(evidence(is_oa=None, apc_usd=None))
        self.assertFalse(violates_no_apc_constraint(result))


if __name__ == "__main__":
    unittest.main()
