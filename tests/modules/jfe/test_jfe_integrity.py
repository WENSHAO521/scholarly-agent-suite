import unittest

from jfe.integrity import CANNOT_VERIFY, VERIFIED, WARNING, screen
from jfe.journal_evidence import JournalEvidence


class IntegrityScreenTests(unittest.TestCase):
    def test_single_source_evidence_cannot_reach_verified_overall(self):
        """Cross-source identity consistency is genuinely unverifiable from
        one index alone -- 'complete-looking' single-source evidence must
        stay CANNOT_VERIFY overall, never get rounded up to VERIFIED."""
        evidence = JournalEvidence(
            display_name="X", issn_l="1234-5678", issn=["1234-5678"], publisher="Example Press",
            is_oa=True, apc_usd=0, last_publication_year=2026,
        )
        result = screen(evidence, current_year=2026)
        self.assertEqual(result.overall, CANNOT_VERIFY)

    def test_two_agreeing_healthy_sources_yield_verified_overall(self):
        primary = JournalEvidence(
            display_name="X", issn_l="1234-5678", issn=["1234-5678"], publisher="Example Press",
            is_oa=True, apc_usd=0, last_publication_year=2026, source="openalex",
        )
        secondary = JournalEvidence(
            display_name="X", issn=["1234-5678"], publisher="Example Press", source="crossref",
        )
        result = screen(primary, secondary=secondary, current_year=2026)
        self.assertEqual(result.overall, VERIFIED)

    def test_missing_publisher_and_issn_yields_warning(self):
        evidence = JournalEvidence(display_name="X", last_publication_year=2026)
        result = screen(evidence, current_year=2026)
        self.assertEqual(result.overall, WARNING)

    def test_oa_with_no_apc_figure_is_a_transparency_warning(self):
        evidence = JournalEvidence(display_name="X", issn_l="1234-5678", publisher="Example Press",
                                    is_oa=True, apc_usd=None, last_publication_year=2026)
        result = screen(evidence, current_year=2026)
        apc_check = next(c for c in result.checks if c.name == "apc_transparency")
        self.assertEqual(apc_check.result, WARNING)

    def test_no_secondary_source_is_cannot_verify_not_verified(self):
        evidence = JournalEvidence(display_name="X", issn_l="1234-5678", publisher="Example Press",
                                    is_oa=True, apc_usd=0, last_publication_year=2026)
        result = screen(evidence, current_year=2026)
        cross_check = next(c for c in result.checks if c.name == "cross_source_consistency")
        self.assertEqual(cross_check.result, CANNOT_VERIFY)

    def test_conflicting_issn_between_sources_is_a_warning(self):
        primary = JournalEvidence(display_name="X", issn=["1111-1111"], publisher="Example Press", source="openalex")
        secondary = JournalEvidence(display_name="X", issn=["2222-2222"], publisher="Example Press", source="crossref")
        result = screen(primary, secondary=secondary, current_year=2026)
        cross_check = next(c for c in result.checks if c.name == "cross_source_consistency")
        self.assertEqual(cross_check.result, WARNING)

    def test_agreeing_sources_yield_verified_cross_source_check(self):
        primary = JournalEvidence(display_name="X", issn=["1111-1111"], publisher="Example Press", source="openalex")
        secondary = JournalEvidence(display_name="X", issn=["1111-1111"], publisher="Example Press", source="crossref")
        result = screen(primary, secondary=secondary, current_year=2026)
        cross_check = next(c for c in result.checks if c.name == "cross_source_consistency")
        self.assertEqual(cross_check.result, VERIFIED)

    def test_overall_state_is_never_outside_the_three_defined_states(self):
        evidence = JournalEvidence(display_name="X")
        result = screen(evidence)
        self.assertIn(result.overall, (VERIFIED, WARNING, CANNOT_VERIFY))


if __name__ == "__main__":
    unittest.main()
