import os
import sys
import unittest


from scb.comparison import author_vs_journal_adaptation, compare_profiles, synthesize_composite_voice
from scb.profiles.author import build_author_profile
from scb.profiles.journal import build_journal_profile
from scb.text_normalize import normalize_text

SHORT_TEXT = """Introduction
This works. That works too. Short sentences here.

Methods
We did a thing.
"""

LONG_TEXT = """Introduction
This is a considerably longer and more elaborately qualified sentence that continues on at some length in order to make a nuanced point about institutional design and its downstream consequences for policy adoption across many different national contexts.

Methods
We used an elaborate multi-stage archival and interview-based research design across twelve distinct national contexts.
"""


class TestCompareProfiles(unittest.TestCase):
    def test_identical_profiles_share_everything_comparable(self):
        docs = [normalize_text(SHORT_TEXT) for _ in range(6)]
        profile_a = build_author_profile(docs)
        profile_b = build_author_profile(docs)
        comparison = compare_profiles(profile_a, profile_b)
        self.assertIn("sentence_style.median_length", comparison.shared_traits)

    def test_materially_different_profiles_flagged(self):
        short_docs = [normalize_text(SHORT_TEXT) for _ in range(6)]
        long_docs = [normalize_text(LONG_TEXT) for _ in range(6)]
        profile_a = build_author_profile(short_docs)
        profile_b = build_author_profile(long_docs)
        comparison = compare_profiles(profile_a, profile_b, "short", "long")
        feature_names = [d["feature"] for d in comparison.differences]
        self.assertIn("sentence_style.median_length", feature_names)


class TestAuthorVsJournalAdaptation(unittest.TestCase):
    def test_never_recommends_imitating_journal_phrasing(self):
        author = build_author_profile([normalize_text(LONG_TEXT) for _ in range(6)])
        journal = build_journal_profile([normalize_text(SHORT_TEXT) for _ in range(6)], journal="Journal X")
        result = author_vs_journal_adaptation(author, journal)
        combined = " ".join(result.adaptation_implications).lower()
        self.assertNotIn("imitate", combined)
        self.assertNotIn("copy the journal", combined)

    def test_preserves_author_substantive_voice_in_do_not_change(self):
        author = build_author_profile([normalize_text(LONG_TEXT) for _ in range(6)])
        journal = build_journal_profile([normalize_text(SHORT_TEXT) for _ in range(6)], journal="Journal X")
        result = author_vs_journal_adaptation(author, journal)
        self.assertIn("author's substantive argumentative voice", result.do_not_change)


class TestSynthesizeCompositeVoice(unittest.TestCase):
    def test_precedence_reflects_present_layers_only(self):
        author = build_author_profile([normalize_text(SHORT_TEXT) for _ in range(6)])
        result = synthesize_composite_voice(author_profile=author)
        self.assertEqual(result["precedence"], ["author"])

    def test_conflict_recorded_between_author_and_journal(self):
        author = build_author_profile([normalize_text(LONG_TEXT) for _ in range(6)])
        journal = build_journal_profile([normalize_text(SHORT_TEXT) for _ in range(6)], journal="Journal X")
        result = synthesize_composite_voice(author_profile=author, journal_profile=journal)
        self.assertTrue(len(result["conflicts"]) >= 1)
        self.assertEqual(result["conflicts"][0]["resolution"], "preserve author voice; adapt only the surface-level differences listed")


if __name__ == "__main__":
    unittest.main()
