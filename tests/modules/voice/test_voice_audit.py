import unittest

from scripts.voice.audit import (
    find_citation_dumps,
    find_repeated_sentences,
    flag_uniform_sentence_length,
    scan_generic_phrases,
    sentence_length_variation,
)


class GenericPhraseTests(unittest.TestCase):
    def test_flags_repeated_furthermore(self):
        text = "Furthermore, the results suggest a link. Furthermore, this indicates support."
        hits = scan_generic_phrases(text)
        self.assertIn(r"\bfurthermore\b", hits)
        self.assertEqual(hits[r"\bfurthermore\b"], 2)

    def test_clean_scholarly_text_is_not_flagged(self):
        text = (
            "The mechanism operates through a narrow channel. This explanation, "
            "however, leaves the timing puzzle unresolved."
        )
        self.assertEqual(scan_generic_phrases(text), {})


class SentenceVariationTests(unittest.TestCase):
    def test_uniform_length_is_flagged(self):
        text = (
            "The cat sat on the mat today. The dog ran to the park now. "
            "The bird flew over the tree there."
        )
        self.assertTrue(flag_uniform_sentence_length(text))

    def test_varied_length_is_not_flagged(self):
        text = (
            "It failed. The mechanism that was expected to govern this transition "
            "turned out, on closer inspection of the boundary cases, to depend on "
            "at least two additional factors the original model omitted entirely. "
            "Why?"
        )
        self.assertFalse(flag_uniform_sentence_length(text))

    def test_too_few_sentences_not_flagged(self):
        self.assertFalse(flag_uniform_sentence_length("One sentence only."))

    def test_variation_is_zero_for_single_sentence(self):
        self.assertEqual(sentence_length_variation("Only one sentence here."), 0.0)


class CitationDumpTests(unittest.TestCase):
    def test_five_citation_cluster_flagged(self):
        text = "This is well established (Smith 2019; Jones 2020; Lee 2021; Park 2018; Chen 2022) in the field."
        dumps = find_citation_dumps(text)
        self.assertEqual(len(dumps), 1)

    def test_two_citation_cluster_not_flagged(self):
        text = "This specific mechanism was first proposed (Smith 2019; Jones 2020)."
        self.assertEqual(find_citation_dumps(text), [])


class RepeatedSentenceTests(unittest.TestCase):
    def test_duplicate_sentence_flagged(self):
        text = (
            "The mechanism explains the observed pattern well. "
            "A separate point follows here. "
            "The mechanism explains the observed pattern well."
        )
        repeated = find_repeated_sentences(text)
        self.assertEqual(len(repeated), 1)

    def test_unique_sentences_not_flagged(self):
        text = "The mechanism explains the pattern. A different claim follows here."
        self.assertEqual(find_repeated_sentences(text), [])


if __name__ == "__main__":
    unittest.main()
