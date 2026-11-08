import os
import sys
import unittest


from scb.analytics.citations import compute_citation_metrics, find_citations
from scb.analytics.lexical import compute_lexical_metrics
from scb.analytics.paragraph import compute_paragraph_metrics
from scb.analytics.sentence import compute_sentence_metrics, split_sentences


class TestSplitSentences(unittest.TestCase):
    def test_basic_split(self):
        text = "This is one sentence. This is another one. And a third."
        sentences = split_sentences(text)
        self.assertEqual(len(sentences), 3)

    def test_abbreviations_do_not_cause_false_split(self):
        text = "We studied several cases, e.g. institutions and firms. Results varied."
        sentences = split_sentences(text)
        self.assertEqual(len(sentences), 2)

    def test_empty_text(self):
        self.assertEqual(split_sentences(""), [])
        self.assertEqual(split_sentences("   "), [])


class TestSentenceMetrics(unittest.TestCase):
    def test_metrics_on_varied_lengths(self):
        text = "Short one. " + ("This is a considerably longer sentence with many words in it to push length up. " * 1)
        metrics = compute_sentence_metrics(text)
        self.assertEqual(metrics.sentence_count, 2)
        self.assertGreater(metrics.word_count, 5)

    def test_empty_text_returns_zeroed_metrics(self):
        metrics = compute_sentence_metrics("")
        self.assertEqual(metrics.sentence_count, 0)
        self.assertEqual(metrics.median_length, 0.0)

    def test_short_and_long_share_sum_to_at_most_one(self):
        text = "One two three. " * 5 + " ".join(["word"] * 35) + "."
        metrics = compute_sentence_metrics(text)
        self.assertLessEqual(metrics.short_sentence_share + metrics.long_sentence_share, 1.0)


class TestParagraphMetrics(unittest.TestCase):
    def test_basic_metrics(self):
        paragraphs = ["One two three four five.", "One two three four five six seven eight nine ten."]
        metrics = compute_paragraph_metrics(paragraphs)
        self.assertEqual(metrics.paragraph_count, 2)
        self.assertGreater(metrics.median_length_words, 0)

    def test_empty_list(self):
        metrics = compute_paragraph_metrics([])
        self.assertEqual(metrics.paragraph_count, 0)

    def test_blank_paragraphs_excluded(self):
        metrics = compute_paragraph_metrics(["Real paragraph here.", "   ", ""])
        self.assertEqual(metrics.paragraph_count, 1)


class TestLexicalMetrics(unittest.TestCase):
    def test_first_person_detected(self):
        metrics = compute_lexical_metrics("We argue that our data show this clearly. I agree.")
        self.assertGreater(metrics.first_person_rate_per_1000, 0)

    def test_hedge_words_detected(self):
        metrics = compute_lexical_metrics("The results may suggest a possible relationship, though this seems unlikely.")
        self.assertGreater(metrics.hedge_rate_per_1000, 0)

    def test_empty_text_returns_zeroed_metrics(self):
        metrics = compute_lexical_metrics("")
        self.assertEqual(metrics.word_count, 0)
        self.assertEqual(metrics.unique_word_ratio, 0.0)

    def test_unique_word_ratio_in_range(self):
        metrics = compute_lexical_metrics("the the the the cat sat on the mat")
        self.assertGreaterEqual(metrics.unique_word_ratio, 0.0)
        self.assertLessEqual(metrics.unique_word_ratio, 1.0)


class TestCitationMetrics(unittest.TestCase):
    def test_finds_author_date_citations(self):
        text = "This builds on prior work (Smith, 2020) and (Doe & Lee, 2019)."
        citations = find_citations(text)
        self.assertEqual(len(citations), 2)

    def test_finds_numeric_bracket_citations(self):
        text = "Prior studies [1] and [2, 3] establish the baseline."
        citations = find_citations(text)
        self.assertEqual(len(citations), 2)

    def test_citation_free_paragraph_share(self):
        paragraphs = [
            "This cites something (Smith, 2020).",
            "This paragraph has no citation at all.",
        ]
        metrics = compute_citation_metrics(paragraphs)
        self.assertEqual(metrics.citation_free_paragraph_share, 0.5)

    def test_empty_paragraphs(self):
        metrics = compute_citation_metrics([])
        self.assertEqual(metrics.citation_count, 0)


if __name__ == "__main__":
    unittest.main()
