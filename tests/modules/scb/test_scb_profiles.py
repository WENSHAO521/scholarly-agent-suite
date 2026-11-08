import os
import sys
import unittest


from scb.profiles.author import build_author_profile
from scb.profiles.book import build_book_profile
from scb.profiles.discipline import build_discipline_profile
from scb.profiles.historical import build_historical_profile
from scb.profiles.journal import build_journal_profile
from scb.text_normalize import normalize_text

SAMPLE_TEXT = """Introduction
This paper studies institutional mechanisms in policy diffusion (Smith, 2020). We argue that coercive pressure causes convergence.

Methods
We use archival data from twelve countries.

Results
The data show a strong effect of coercive pressure on adoption timing (Doe, 2019).

Limitations
This study is limited by its focus on a single policy domain.
"""


def _docs(n):
    return [normalize_text(SAMPLE_TEXT) for _ in range(n)]


class TestJournalProfile(unittest.TestCase):
    def test_schema_shape(self):
        profile = build_journal_profile(_docs(6), journal="Journal X", issn=["1234-5678"], sample_window="2024-2026")
        self.assertEqual(profile["journal"], "Journal X")
        self.assertEqual(profile["sample_size"], 6)
        self.assertIn("prose", profile)
        self.assertIn("citations", profile)
        self.assertIn("sections", profile)

    def test_limitations_flagged_when_absent(self):
        no_limits = normalize_text("Introduction\nJust an intro with no limitations section at all.")
        profile = build_journal_profile([no_limits] * 3, journal="Journal Y")
        self.assertTrue(len(profile["limitations"]) >= 1)


class TestDisciplineProfile(unittest.TestCase):
    def test_schema_shape(self):
        profile = build_discipline_profile(_docs(6), discipline="Sociology", subdiscipline="Political Sociology")
        self.assertEqual(profile["discipline"], "Sociology")
        self.assertIn("claim_conventions", profile)
        self.assertIn("methods_visibility", profile)


class TestHistoricalProfile(unittest.TestCase):
    def test_schema_shape_and_no_verbatim_text_stored(self):
        profile = build_historical_profile(_docs(3), scholar="Test Scholar", source_status="likely")
        self.assertEqual(profile["scholar"], "Test Scholar")
        self.assertIn("argument_architecture", profile)
        # Verify no raw sentence/paragraph text leaked into the profile.
        profile_str = str(profile)
        self.assertNotIn("coercive pressure causes convergence", profile_str)

    def test_unverified_status_triggers_caution(self):
        profile = build_historical_profile(_docs(3), scholar="X", source_status="unknown")
        self.assertTrue(any("unverified" in c for c in profile["modern_use_cautions"]))


class TestAuthorProfile(unittest.TestCase):
    def test_schema_shape_and_default_do_not_preserve(self):
        profile = build_author_profile(_docs(5), source_scope="5 uploaded articles")
        self.assertEqual(profile["profile_type"], "author")
        self.assertEqual(profile["source_count"], 5)
        self.assertIn("citation errors", profile["do_not_preserve"])

    def test_custom_do_not_preserve_overrides_default(self):
        profile = build_author_profile(_docs(2), do_not_preserve=["overlong intros"])
        self.assertEqual(profile["do_not_preserve"], ["overlong intros"])


class TestBookProfile(unittest.TestCase):
    def test_schema_shape(self):
        profile = build_book_profile(_docs(4), title="Test Book")
        self.assertEqual(profile["profile_type"], "book")
        self.assertEqual(profile["chapters_sampled"], 4)
        self.assertIn("chapter_length", profile)
        self.assertIn("median_words", profile["chapter_length"])


if __name__ == "__main__":
    unittest.main()
