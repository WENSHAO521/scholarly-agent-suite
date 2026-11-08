import unittest

from jfe.fit_dimensions import (
    CANNOT_VERIFY,
    MATCH,
    MISMATCH,
    NOT_APPLICABLE,
    apc_constraint_fit,
    article_type_fit,
    assess_all,
    audience_fit,
    indexing_evidence_fit,
    method_fit,
    oa_model_fit,
    requirement_compatibility_fit,
    scope_fit,
    topic_fit,
)
from jfe.journal_evidence import JournalEvidence
from jfe.manuscript_profile import ManuscriptProfile


class UnstatedFieldsAreNotApplicableTests(unittest.TestCase):
    """A dimension the manuscript itself never asked about is NOT_APPLICABLE,
    not CANNOT_VERIFY -- there is nothing to verify against."""

    def test_article_type_not_applicable_when_unstated(self):
        self.assertEqual(article_type_fit(ManuscriptProfile()).result, NOT_APPLICABLE)

    def test_method_not_applicable_when_unstated(self):
        self.assertEqual(method_fit(ManuscriptProfile()).result, NOT_APPLICABLE)

    def test_audience_not_applicable_when_unstated(self):
        self.assertEqual(audience_fit(ManuscriptProfile()).result, NOT_APPLICABLE)

    def test_apc_constraint_not_applicable_when_unstated(self):
        result = apc_constraint_fit(ManuscriptProfile(), JournalEvidence())
        self.assertEqual(result.result, NOT_APPLICABLE)

    def test_oa_model_not_applicable_when_unstated(self):
        result = oa_model_fit(ManuscriptProfile(), JournalEvidence())
        self.assertEqual(result.result, NOT_APPLICABLE)

    def test_indexing_not_applicable_when_unstated(self):
        result = indexing_evidence_fit(ManuscriptProfile(), JournalEvidence())
        self.assertEqual(result.result, NOT_APPLICABLE)


class StatedButUnverifiableFieldsAreCannotVerifyTests(unittest.TestCase):
    def test_article_type_cannot_verify_when_stated_but_no_index_data(self):
        manuscript = ManuscriptProfile(article_type="original-research")
        self.assertEqual(article_type_fit(manuscript).result, CANNOT_VERIFY)

    def test_indexing_cannot_verify_for_a_paid_index_request(self):
        manuscript = ManuscriptProfile(constraints={"requires_indexing": ["Scopus"]})
        result = indexing_evidence_fit(manuscript, JournalEvidence())
        self.assertEqual(result.result, CANNOT_VERIFY)


class ApcAndOaConstraintTests(unittest.TestCase):
    def test_mandatory_apc_violates_no_apc_constraint(self):
        manuscript = ManuscriptProfile(constraints={"no_mandatory_apc": True})
        evidence = JournalEvidence(is_oa=True, apc_usd=2000)
        self.assertEqual(apc_constraint_fit(manuscript, evidence).result, MISMATCH)

    def test_diamond_oa_satisfies_no_apc_constraint(self):
        manuscript = ManuscriptProfile(constraints={"no_mandatory_apc": True})
        evidence = JournalEvidence(is_oa=True, apc_usd=0)
        self.assertEqual(apc_constraint_fit(manuscript, evidence).result, MATCH)

    def test_requires_oa_true_matches_oa_journal(self):
        manuscript = ManuscriptProfile(constraints={"requires_oa": True})
        evidence = JournalEvidence(is_oa=True)
        self.assertEqual(oa_model_fit(manuscript, evidence).result, MATCH)

    def test_requires_oa_true_mismatches_subscription_journal(self):
        manuscript = ManuscriptProfile(constraints={"requires_oa": True})
        evidence = JournalEvidence(is_oa=False)
        self.assertEqual(oa_model_fit(manuscript, evidence).result, MISMATCH)


class RequirementCompatibilityTests(unittest.TestCase):
    def test_no_official_requirements_is_cannot_verify(self):
        manuscript = ManuscriptProfile(word_count=5000)
        self.assertEqual(requirement_compatibility_fit(manuscript, None).result, CANNOT_VERIFY)

    def test_within_word_limit_is_match(self):
        manuscript = ManuscriptProfile(word_count=5000)
        result = requirement_compatibility_fit(manuscript, {"word_limit": 8000})
        self.assertEqual(result.result, MATCH)

    def test_over_word_limit_is_mismatch(self):
        manuscript = ManuscriptProfile(word_count=9000)
        result = requirement_compatibility_fit(manuscript, {"word_limit": 8000})
        self.assertEqual(result.result, MISMATCH)


class TopicAndScopeFitTests(unittest.TestCase):
    def test_strong_overlap_is_match(self):
        manuscript = ManuscriptProfile(topic="policy diffusion states local government")
        evidence = JournalEvidence(topics=["Public Policy and Administration Research",
                                            "Local Government Finance and Decentralization"])
        self.assertEqual(topic_fit(manuscript, evidence).result, MATCH)

    def test_no_topic_data_is_cannot_verify(self):
        manuscript = ManuscriptProfile(topic="policy diffusion")
        evidence = JournalEvidence(topics=[])
        self.assertEqual(topic_fit(manuscript, evidence).result, CANNOT_VERIFY)

    def test_scope_fit_uses_discipline_not_full_keyword_bag(self):
        manuscript = ManuscriptProfile(discipline="public administration",
                                        research_question="an unrelated quantum entanglement question")
        evidence = JournalEvidence(topics=["Public Administration"])
        self.assertEqual(scope_fit(manuscript, evidence).result, MATCH)


class AssessAllTests(unittest.TestCase):
    def test_returns_eleven_dimensions_never_a_float(self):
        manuscript = ManuscriptProfile(discipline="sociology")
        evidence = JournalEvidence(topics=["Sociology"])
        results = assess_all(manuscript, evidence)
        self.assertEqual(len(results), 11)
        for r in results:
            self.assertIsInstance(r.result, str)
            self.assertNotIsInstance(r.result, float)


if __name__ == "__main__":
    unittest.main()
