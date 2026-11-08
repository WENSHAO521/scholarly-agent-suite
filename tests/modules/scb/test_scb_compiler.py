import os
import sys
import unittest


from scb.compiler import (
    MANDATORY,
    OBSERVED,
    PROTOCOL_JOURNAL_STYLE_CONTEXT_V1,
    PROTOCOL_SCHOLARLY_PROFILE_V1,
    PROTOCOL_VOICE_CONTEXT_V1,
    RECOMMENDED,
    compile_journal_style_context_v1,
    compile_scholarly_profile_v1,
    compile_voice_context_v1,
)
from scb.profiles.author import build_author_profile
from scb.profiles.journal import build_journal_profile
from scb.text_normalize import normalize_text

SAMPLE_TEXT = """Introduction
This paper studies institutional mechanisms (Smith, 2020). We contribute to the literature by showing this pattern holds broadly.

Methods
We use archival data.
"""


def _docs(n):
    return [normalize_text(SAMPLE_TEXT) for _ in range(n)]


class TestCompileScholarlyProfileV1(unittest.TestCase):
    def test_protocol_tag_and_shape(self):
        author = build_author_profile(_docs(6))
        compiled = compile_scholarly_profile_v1("author", "Test Author", author)
        self.assertEqual(compiled["protocol"], PROTOCOL_SCHOLARLY_PROFILE_V1)
        self.assertIn("measured_features", compiled)
        self.assertIn("inferred_features", compiled)
        self.assertEqual(compiled["stability"], "not_evaluated")


class TestCompileVoiceContextV1(unittest.TestCase):
    def test_do_not_preserve_becomes_mandatory(self):
        author = build_author_profile(_docs(6), do_not_preserve=["overlong intros"])
        compiled = compile_voice_context_v1(author_profile=author)
        self.assertEqual(compiled["protocol"], PROTOCOL_VOICE_CONTEXT_V1)
        mandatory_statements = [c for c in compiled["voice_constraints"] if c["status"] == MANDATORY]
        self.assertTrue(any("overlong intros" in c["text"] for c in mandatory_statements))

    def test_journal_observation_is_never_mandatory(self):
        journal = build_journal_profile(_docs(6), journal="Journal X")
        compiled = compile_voice_context_v1(journal_profile=journal)
        journal_statements = [c for c in compiled["voice_constraints"] if "journal." in c["basis"]]
        self.assertTrue(journal_statements)
        self.assertTrue(all(c["status"] == OBSERVED for c in journal_statements))

    def test_voice_precedence_order(self):
        compiled = compile_voice_context_v1()
        self.assertEqual(compiled["voice_precedence"][0], "author")


class TestCompileJournalStyleContextV1(unittest.TestCase):
    def test_official_requirements_kept_separate_from_observed(self):
        journal = build_journal_profile(_docs(6), journal="Journal X")
        compiled = compile_journal_style_context_v1(journal, official_requirements={"word_limit": 8000})
        self.assertEqual(compiled["protocol"], PROTOCOL_JOURNAL_STYLE_CONTEXT_V1)
        self.assertEqual(compiled["official_requirements"]["word_limit"], 8000)
        self.assertIn("observed_style_profile", compiled)
        self.assertIsNot(compiled["official_requirements"], compiled["observed_style_profile"])


if __name__ == "__main__":
    unittest.main()
