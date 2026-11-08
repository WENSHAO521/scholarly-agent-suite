import os
import sys
import unittest


from scb.analytics.claims import UNCLASSIFIED, analyze_claims, classify_sentence
from scb.analytics.rhetorical import analyze_rhetorical_moves, classify_paragraph_moves
from scb.analytics.rhythm import CLAIM, EVIDENCE, analyze_rhythm, tag_sentence_role
from scb.analytics.sections import compute_section_metrics
from scb.text_normalize import normalize_text


class TestClassifySentence(unittest.TestCase):
    def test_causal_cue(self):
        self.assertEqual(classify_sentence("Institutional weakness causes policy failure."), "causal")

    def test_associational_cue(self):
        self.assertEqual(classify_sentence("Income is associated with educational attainment."), "associational")

    def test_normative_cue(self):
        self.assertEqual(classify_sentence("Policymakers should adopt this reform."), "normative")

    def test_no_cue_is_unclassified(self):
        self.assertEqual(classify_sentence("The sky is blue today."), UNCLASSIFIED)

    def test_formal_beats_broader_cues(self):
        # "proof" cue should win even though the sentence also mentions "mechanism"
        self.assertEqual(classify_sentence("The proof relies on the mechanism described above."), "formal")


class TestAnalyzeClaims(unittest.TestCase):
    def test_hedge_cooccurrence_tracked(self):
        text = "This may cause an increase in adoption rates. This definitely causes a decrease."
        analysis = analyze_claims(text)
        self.assertIn("causal", analysis.category_counts)
        self.assertGreater(analysis.hedge_cooccurrence_rate.get("causal", 0), 0)

    def test_empty_text(self):
        analysis = analyze_claims("")
        self.assertEqual(analysis.total_sentences, 0)


class TestRhetoricalMoves(unittest.TestCase):
    def test_multiple_moves_can_appear_in_one_paragraph(self):
        para = "A key challenge remains unclear in prior research. We contribute to the literature by addressing this gap."
        moves = classify_paragraph_moves(para)
        self.assertIn("problem_framing", moves)
        self.assertIn("contribution", moves)

    def test_analyze_rhetorical_moves_shares(self):
        paragraphs = ["We contribute to the literature by doing X.", "This paragraph has no recognizable move."]
        analysis = analyze_rhetorical_moves(paragraphs)
        self.assertEqual(analysis.paragraph_count, 2)
        self.assertEqual(analysis.move_shares.get("contribution"), 0.5)


class TestRhythm(unittest.TestCase):
    def test_tag_sentence_role(self):
        self.assertEqual(tag_sentence_role("We argue that institutions matter."), CLAIM)
        self.assertEqual(tag_sentence_role("The data show a strong effect."), EVIDENCE)

    def test_detects_claim_evidence_pattern(self):
        para = "We argue that institutions matter. The data show a strong effect."
        analysis = analyze_rhythm([para])
        self.assertIn("claim_evidence", analysis.pattern_counts)

    def test_confidence_always_low(self):
        analysis = analyze_rhythm(["We argue that institutions matter. The data show a strong effect."])
        self.assertEqual(analysis.confidence, "low")

    def test_empty_input(self):
        analysis = analyze_rhythm([])
        self.assertEqual(analysis.paragraphs_analyzed, 0)


IMRAD_TEXT = """Introduction
This paper studies institutional mechanisms.

Methods
We use archival data.

Limitations
This study is limited by its sample size.
"""


class TestSectionMetrics(unittest.TestCase):
    def test_role_word_share_sums_near_one(self):
        doc = normalize_text(IMRAD_TEXT)
        metrics = compute_section_metrics(doc)
        self.assertAlmostEqual(sum(metrics.role_word_share.values()), 1.0, places=2)

    def test_detects_dedicated_limitations_section(self):
        doc = normalize_text(IMRAD_TEXT)
        metrics = compute_section_metrics(doc)
        self.assertTrue(metrics.has_dedicated_limitations_section)

    def test_no_sections_returns_zero(self):
        doc = normalize_text("")
        metrics = compute_section_metrics(doc)
        self.assertEqual(metrics.section_count, 0)


if __name__ == "__main__":
    unittest.main()
