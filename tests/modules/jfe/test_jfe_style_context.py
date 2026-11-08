import datetime
import unittest

from jfe.journal_evidence import JournalEvidence
from jfe.style_context import (
    PROTOCOL,
    StyleContextError,
    build_journal_style_context,
    compute_freshness,
    from_journal_evidence,
    journal_identifiers_from_evidence,
)


class BuildJournalStyleContextTests(unittest.TestCase):
    def test_minimal_envelope_matches_protocol_shape(self):
        envelope = build_journal_style_context("Journal of Example Studies")
        self.assertEqual(envelope["protocol"], PROTOCOL)
        self.assertEqual(envelope["journal_name"], "Journal of Example Studies")
        self.assertEqual(envelope["official_requirements"], {})
        self.assertEqual(envelope["observed_patterns"], {})
        self.assertEqual(envelope["freshness"], "current")

    def test_missing_official_requirements_produces_a_limitation(self):
        envelope = build_journal_style_context("X", observed_patterns={"mean_paragraph_length": 120})
        self.assertTrue(any("official_requirements" in note for note in envelope["limitations"]))

    def test_missing_observed_patterns_produces_a_limitation(self):
        envelope = build_journal_style_context("X", official_requirements={"word_limit": 8000})
        self.assertTrue(any("observed_patterns" in note for note in envelope["limitations"]))

    def test_stale_freshness_produces_a_limitation(self):
        envelope = build_journal_style_context(
            "X", official_requirements={"word_limit": 8000},
            observed_patterns={"mean_paragraph_length": 120}, freshness="stale",
        )
        self.assertTrue(any("stale" in note for note in envelope["limitations"]))

    def test_invalid_freshness_rejected(self):
        with self.assertRaises(StyleContextError):
            build_journal_style_context("X", freshness="fresh")

    def test_empty_journal_name_rejected(self):
        with self.assertRaises(StyleContextError):
            build_journal_style_context("")

    def test_observed_pattern_leaking_an_official_only_key_is_rejected(self):
        """Regression: a corpus-derived observation must never be labeled a
        stated author-guideline rule (SKILL.md's Evidence discipline)."""
        with self.assertRaises(StyleContextError):
            build_journal_style_context(
                "X", observed_patterns={"word_limit": 8000, "mean_paragraph_length": 120},
            )

    def test_official_requirement_leaking_an_observed_only_key_is_rejected(self):
        """Regression: descriptive corpus evidence must never be presented
        as an official, mandatory requirement."""
        with self.assertRaises(StyleContextError):
            build_journal_style_context(
                "X", official_requirements={"word_limit": 8000, "mean_paragraph_length": 120},
            )

    def test_optional_fields_only_present_when_supplied(self):
        envelope = build_journal_style_context("X")
        for field in ("journal_identifiers", "article_type", "evidence", "generated_at"):
            self.assertNotIn(field, envelope)


class ComputeFreshnessTests(unittest.TestCase):
    def test_missing_checked_at_is_stale_not_silently_current(self):
        self.assertEqual(compute_freshness(None), "stale")

    def test_unparseable_checked_at_is_stale(self):
        self.assertEqual(compute_freshness("not-a-date"), "stale")

    def test_recent_timestamp_is_current(self):
        now = datetime.datetime(2026, 9, 9, tzinfo=datetime.timezone.utc)
        checked_at = (now - datetime.timedelta(days=10)).isoformat()
        self.assertEqual(compute_freshness(checked_at, now=now), "current")

    def test_eight_month_old_timestamp_is_aging(self):
        now = datetime.datetime(2026, 9, 9, tzinfo=datetime.timezone.utc)
        checked_at = (now - datetime.timedelta(days=240)).isoformat()
        self.assertEqual(compute_freshness(checked_at, now=now), "aging")

    def test_two_year_old_timestamp_is_stale(self):
        now = datetime.datetime(2026, 9, 9, tzinfo=datetime.timezone.utc)
        checked_at = (now - datetime.timedelta(days=730)).isoformat()
        self.assertEqual(compute_freshness(checked_at, now=now), "stale")


class FromJournalEvidenceTests(unittest.TestCase):
    def test_never_derives_official_requirements_from_index_evidence(self):
        """Index evidence (OpenAlex/Crossref) is a bibliographic index, not
        an author-guideline source -- this must stay empty unless the
        caller explicitly supplies it."""
        evidence = JournalEvidence(display_name="X", apc_usd=2000, is_oa=True,
                                    checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        envelope = from_journal_evidence(evidence)
        self.assertEqual(envelope["official_requirements"], {})

    def test_never_derives_observed_patterns_from_index_evidence(self):
        evidence = JournalEvidence(display_name="X", works_count=500, topics=["Sociology"],
                                    checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        envelope = from_journal_evidence(evidence)
        self.assertEqual(envelope["observed_patterns"], {})

    def test_journal_identifiers_derived_from_evidence(self):
        evidence = JournalEvidence(display_name="X", issn_l="1234-5678", issn=["1234-5678"],
                                    publisher="Example Press",
                                    checked_at=datetime.datetime.now(datetime.timezone.utc).isoformat())
        envelope = from_journal_evidence(evidence)
        self.assertEqual(envelope["journal_identifiers"], journal_identifiers_from_evidence(evidence))

    def test_missing_checked_at_yields_stale_freshness(self):
        evidence = JournalEvidence(display_name="X", checked_at=None)
        envelope = from_journal_evidence(evidence)
        self.assertEqual(envelope["freshness"], "stale")


if __name__ == "__main__":
    unittest.main()
