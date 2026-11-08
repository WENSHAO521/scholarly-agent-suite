import unittest

from jfe.apc_oa import APCClassification, DIAMOND_OA, HYBRID_OA_OPTIONAL, MANDATORY_APC, UNKNOWN as APC_UNKNOWN
from jfe.fit_model import (
    EXCELLENT_FIT,
    FitResult,
    NOT_RECOMMENDED,
    PLAUSIBLE_FIT,
    STRETCH,
    STRONG_FIT as FIT_MODEL_STRONG_FIT,
    WEAK_FIT as FIT_MODEL_WEAK_FIT,
)
from jfe.indexing import IndexingAssessment, IndexingEntry
from jfe.integrity import IntegrityCheck, IntegrityScreen, VERIFIED, WARNING, CANNOT_VERIFY as INTEGRITY_CANNOT_VERIFY
from jfe.journal_evidence import JournalEvidence
from jfe.target_journal_profile import (
    MODERATE_FIT,
    NOT_ASSESSED,
    PROTOCOL,
    PROVENANCE_PROTOCOL,
    STRONG_FIT,
    TargetJournalProfileError,
    WEAK_FIT,
    build_target_journal_profile,
)

# The schema's full allowed key set (journal-profile.schema.json,
# additionalProperties: false) -- used to assert this producer never emits
# a key the canonical schema doesn't declare.
_ALLOWED_KEYS = {
    "protocol", "name", "issn", "scope_summary", "indexing",
    "apc_status", "oa_status", "fit_assessment", "freshness", "provenance",
}
_ALLOWED_PROVENANCE_KEYS = {
    "protocol", "sources", "retrieval_date", "verification_status", "conflict_notes",
}


def _evidence(**overrides):
    defaults = dict(
        display_name="Journal of Example Studies",
        issn_l="1234-5678",
        issn=["1234-5678"],
        publisher="Example University Press",
        homepage_url="https://example.org/jes",
        is_oa=True,
        is_in_doaj=True,
        apc_usd=0,
        works_count=500,
        cited_by_count=1000,
        first_publication_year=1990,
        last_publication_year=2026,
        topics=["sociology", "public administration"],
        source="openalex",
        checked_at="2026-09-09T12:00:00+00:00",
    )
    defaults.update(overrides)
    return JournalEvidence(**defaults)


class BuildTargetJournalProfileMinimalTests(unittest.TestCase):
    def test_minimal_envelope_shape(self):
        envelope = build_target_journal_profile(_evidence())
        self.assertEqual(envelope["protocol"], PROTOCOL)
        self.assertEqual(envelope["name"], "Journal of Example Studies")
        self.assertEqual(envelope["issn"], "1234-5678")
        self.assertIn(envelope["freshness"], ("current", "aging", "stale"))
        self.assertLessEqual(set(envelope.keys()), _ALLOWED_KEYS)

    def test_no_evidence_fit_apc_indexing_gives_not_assessed_and_omits_optional_fields(self):
        envelope = build_target_journal_profile(_evidence(topics=[]))
        self.assertEqual(envelope["fit_assessment"], NOT_ASSESSED)
        self.assertNotIn("apc_status", envelope)
        self.assertNotIn("oa_status", envelope)
        self.assertNotIn("indexing", envelope)
        self.assertNotIn("scope_summary", envelope)

    def test_missing_checked_at_rejected(self):
        with self.assertRaises(TargetJournalProfileError):
            build_target_journal_profile(_evidence(checked_at=None))

    def test_missing_display_name_rejected(self):
        with self.assertRaises(TargetJournalProfileError):
            build_target_journal_profile(_evidence(display_name=None))

    def test_provenance_identity_falls_back_to_homepage_then_name(self):
        envelope = build_target_journal_profile(_evidence(issn_l=None, issn=[]))
        self.assertEqual(envelope["provenance"]["sources"][0]["identity"], "https://example.org/jes")

        envelope2 = build_target_journal_profile(_evidence(issn_l=None, issn=[], homepage_url=None))
        self.assertEqual(envelope2["provenance"]["sources"][0]["identity"], "Journal of Example Studies")


class ScopeSummaryTests(unittest.TestCase):
    def test_topics_present_produce_index_labeled_scope_summary(self):
        envelope = build_target_journal_profile(_evidence())
        self.assertIn("sociology", envelope["scope_summary"])
        self.assertIn("OpenAlex", envelope["scope_summary"])
        self.assertIn("not the journal's own scope statement", envelope["scope_summary"])

    def test_no_topics_omits_scope_summary(self):
        envelope = build_target_journal_profile(_evidence(topics=[]))
        self.assertNotIn("scope_summary", envelope)


class FitAssessmentMappingTests(unittest.TestCase):
    def _fit(self, label, hard_eliminated=False):
        return FitResult(label=label, topic_overlap_terms=[], explanation="x", hard_eliminated=hard_eliminated)

    def test_excellent_and_strong_map_to_schema_strong(self):
        for label in (EXCELLENT_FIT, FIT_MODEL_STRONG_FIT):
            envelope = build_target_journal_profile(_evidence(), fit_result=self._fit(label))
            self.assertEqual(envelope["fit_assessment"], STRONG_FIT)

    def test_plausible_maps_to_moderate(self):
        envelope = build_target_journal_profile(_evidence(), fit_result=self._fit(PLAUSIBLE_FIT))
        self.assertEqual(envelope["fit_assessment"], MODERATE_FIT)

    def test_stretch_weak_and_not_recommended_map_to_weak(self):
        for label in (STRETCH, FIT_MODEL_WEAK_FIT, NOT_RECOMMENDED):
            envelope = build_target_journal_profile(_evidence(), fit_result=self._fit(label))
            self.assertEqual(envelope["fit_assessment"], WEAK_FIT)

    def test_hard_eliminated_maps_to_weak_not_not_assessed(self):
        fit = self._fit(NOT_RECOMMENDED, hard_eliminated=True)
        envelope = build_target_journal_profile(_evidence(), fit_result=fit)
        self.assertEqual(envelope["fit_assessment"], WEAK_FIT)

    def test_no_topic_data_and_not_hard_eliminated_is_not_assessed_not_weak(self):
        """Regression: fit_model.compute_fit's own label conflates 'no topic
        data' with NOT_RECOMMENDED (score defaults to 0.0). The producer must
        not repeat that -- 'could not assess' and 'assessed as poor' differ."""
        fit = self._fit(NOT_RECOMMENDED, hard_eliminated=False)
        envelope = build_target_journal_profile(_evidence(topics=[]), fit_result=fit)
        self.assertEqual(envelope["fit_assessment"], NOT_ASSESSED)

    def test_no_fit_result_at_all_is_not_assessed(self):
        envelope = build_target_journal_profile(_evidence(), fit_result=None)
        self.assertEqual(envelope["fit_assessment"], NOT_ASSESSED)


class ApcOaMappingTests(unittest.TestCase):
    def test_mandatory_apc_maps_to_apc_required_fully_oa(self):
        apc = APCClassification(MANDATORY_APC, 2000, True, True, "note")
        envelope = build_target_journal_profile(_evidence(), apc_classification=apc)
        self.assertEqual(envelope["apc_status"], "apc-required")
        self.assertEqual(envelope["oa_status"], "fully-oa")

    def test_diamond_oa_maps_to_no_apc_fully_oa(self):
        apc = APCClassification(DIAMOND_OA, None, True, True, "note")
        envelope = build_target_journal_profile(_evidence(), apc_classification=apc)
        self.assertEqual(envelope["apc_status"], "no-apc")
        self.assertEqual(envelope["oa_status"], "fully-oa")

    def test_hybrid_optional_maps_to_no_apc_hybrid_never_fully_oa(self):
        """A hybrid-optional fee must never be represented as fully-oa (no
        mandatory fee is not the same as fully open) or as apc-required (the
        default publication path has no mandatory fee)."""
        apc = APCClassification(HYBRID_OA_OPTIONAL, 1500, False, False, "note")
        envelope = build_target_journal_profile(_evidence(), apc_classification=apc)
        self.assertEqual(envelope["apc_status"], "no-apc")
        self.assertEqual(envelope["oa_status"], "hybrid")

    def test_unknown_maps_to_unknown_unknown(self):
        apc = APCClassification(APC_UNKNOWN, None, None, None, "note")
        envelope = build_target_journal_profile(_evidence(), apc_classification=apc)
        self.assertEqual(envelope["apc_status"], "unknown")
        self.assertEqual(envelope["oa_status"], "unknown")

    def test_no_apc_classification_omits_both_fields(self):
        envelope = build_target_journal_profile(_evidence(), apc_classification=None)
        self.assertNotIn("apc_status", envelope)
        self.assertNotIn("oa_status", envelope)


class IndexingListTests(unittest.TestCase):
    def test_only_officially_verified_truthy_entries_included(self):
        assessment = IndexingAssessment(entries=[
            IndexingEntry("DOAJ", "officially_verified", True, "openalex", "current", "note"),
            IndexingEntry("Scopus", "cannot_verify", None, None, None, "note"),
            IndexingEntry("JCR quartile", "cannot_verify", None, None, None, "note"),
        ])
        envelope = build_target_journal_profile(_evidence(), indexing_assessment=assessment)
        self.assertEqual(envelope["indexing"], ["DOAJ"])
        self.assertNotIn("Scopus", envelope["indexing"])
        self.assertNotIn("JCR quartile", envelope["indexing"])

    def test_doaj_false_value_excluded_even_if_officially_verified(self):
        assessment = IndexingAssessment(entries=[
            IndexingEntry("DOAJ", "officially_verified", False, "openalex", "current", "note"),
        ])
        envelope = build_target_journal_profile(_evidence(), indexing_assessment=assessment)
        self.assertNotIn("indexing", envelope)

    def test_no_indexing_assessment_omits_field(self):
        envelope = build_target_journal_profile(_evidence(), indexing_assessment=None)
        self.assertNotIn("indexing", envelope)


class ProvenanceTests(unittest.TestCase):
    def test_default_verification_status_is_unverified(self):
        envelope = build_target_journal_profile(_evidence())
        prov = envelope["provenance"]
        self.assertEqual(prov["protocol"], PROVENANCE_PROTOCOL)
        self.assertEqual(prov["verification_status"], "unverified")
        self.assertNotIn("conflict_notes", prov)
        self.assertLessEqual(set(prov.keys()), _ALLOWED_PROVENANCE_KEYS)

    def test_retrieval_date_is_date_only_not_full_timestamp(self):
        envelope = build_target_journal_profile(_evidence(checked_at="2026-09-09T12:34:56+00:00"))
        self.assertEqual(envelope["provenance"]["retrieval_date"], "2026-09-09")

    def test_cross_source_verified_sets_provenance_verified(self):
        screen = IntegrityScreen(
            checks=[IntegrityCheck("cross_source_consistency", VERIFIED, "agree")],
            overall=VERIFIED,
        )
        envelope = build_target_journal_profile(_evidence(), integrity=screen)
        self.assertEqual(envelope["provenance"]["verification_status"], "verified")

    def test_cross_source_conflict_sets_provenance_conflicting_with_notes(self):
        screen = IntegrityScreen(
            checks=[IntegrityCheck("cross_source_consistency", WARNING, "publisher differs")],
            overall=WARNING,
        )
        envelope = build_target_journal_profile(_evidence(), integrity=screen)
        self.assertEqual(envelope["provenance"]["verification_status"], "conflicting")
        self.assertEqual(envelope["provenance"]["conflict_notes"], ["publisher differs"])

    def test_cross_source_cannot_verify_stays_unverified(self):
        screen = IntegrityScreen(
            checks=[IntegrityCheck("cross_source_consistency", INTEGRITY_CANNOT_VERIFY, "only one source")],
            overall=INTEGRITY_CANNOT_VERIFY,
        )
        envelope = build_target_journal_profile(_evidence(), integrity=screen)
        self.assertEqual(envelope["provenance"]["verification_status"], "unverified")

    def test_source_entry_records_which_index(self):
        envelope = build_target_journal_profile(_evidence(source="crossref"))
        self.assertEqual(envelope["provenance"]["sources"][0]["index"], "crossref")


class NoFabricationTests(unittest.TestCase):
    def test_no_numeric_acceptance_probability_anywhere(self):
        apc = APCClassification(MANDATORY_APC, 2000, True, True, "note")
        fit = FitResult(EXCELLENT_FIT, ["x"], "explanation", False)
        indexing = IndexingAssessment(entries=[
            IndexingEntry("DOAJ", "officially_verified", True, "openalex", "current", "note"),
        ])
        envelope = build_target_journal_profile(
            _evidence(), fit_result=fit, apc_classification=apc, indexing_assessment=indexing,
        )
        import json
        blob = json.dumps(envelope)
        self.assertNotIn("acceptance_probability", blob)
        self.assertNotIn("acceptance_likelihood", blob)
        self.assertEqual(envelope["fit_assessment"], STRONG_FIT)
        self.assertIsInstance(envelope["fit_assessment"], str)

    def test_envelope_never_has_keys_outside_the_canonical_schema(self):
        apc = APCClassification(MANDATORY_APC, 2000, True, True, "note")
        fit = FitResult(EXCELLENT_FIT, ["x"], "explanation", False)
        indexing = IndexingAssessment(entries=[
            IndexingEntry("DOAJ", "officially_verified", True, "openalex", "current", "note"),
        ])
        screen = IntegrityScreen(
            checks=[IntegrityCheck("cross_source_consistency", WARNING, "conflict")], overall=WARNING,
        )
        envelope = build_target_journal_profile(
            _evidence(), fit_result=fit, apc_classification=apc,
            indexing_assessment=indexing, integrity=screen,
        )
        self.assertLessEqual(set(envelope.keys()), _ALLOWED_KEYS)
        self.assertLessEqual(set(envelope["provenance"].keys()), _ALLOWED_PROVENANCE_KEYS)


if __name__ == "__main__":
    unittest.main()
