import os
import sys
import unittest


from scb.author_learning import analyze_edit_diffs, merge_author_profile
from scb.profiles.author import build_author_profile
from scb.text_normalize import normalize_text

SAMPLE_TEXT = """Introduction
This paper studies institutional mechanisms in policy diffusion (Smith, 2020). We argue that coercive pressure causes convergence.

Methods
We use archival data from twelve countries.
"""


def _docs(n):
    return [normalize_text(SAMPLE_TEXT) for _ in range(n)]


class TestMergeAuthorProfile(unittest.TestCase):
    def test_merge_increments_source_count(self):
        old_profile = build_author_profile(_docs(6), source_scope="6 early papers")
        merged, diff = merge_author_profile(old_profile, _docs(6), source_scope_addition="6 new papers")
        self.assertEqual(merged["source_count"], 12)
        self.assertIn("6 early papers", merged["source_scope"])
        self.assertIn("6 new papers", merged["source_scope"])

    def test_identical_new_documents_are_reported_stable(self):
        old_profile = build_author_profile(_docs(6), source_scope="initial")
        _, diff = merge_author_profile(old_profile, _docs(6), source_scope_addition="more of the same")
        self.assertIn("sentence_style.median_length", diff.stable)

    def test_small_sample_addition_marked_uncertain(self):
        old_profile = build_author_profile(_docs(6), source_scope="initial")
        _, diff = merge_author_profile(old_profile, _docs(2), source_scope_addition="two new")
        self.assertIn("sentence_style.median_length", diff.uncertain)

    def test_do_not_preserve_retained_from_previous_profile(self):
        old_profile = build_author_profile(_docs(6), do_not_preserve=["overlong intros"])
        merged, _ = merge_author_profile(old_profile, _docs(6))
        self.assertEqual(merged["do_not_preserve"], ["overlong intros"])

    def test_zero_old_documents_uses_new_values_directly(self):
        old_profile = {"source_count": 0, "source_scope": "", "argument_moves": []}
        merged, diff = merge_author_profile(old_profile, _docs(6), source_scope_addition="first upload")
        self.assertEqual(merged["source_count"], 6)


class TestAnalyzeEditDiffs(unittest.TestCase):
    def test_detects_consistent_shortening(self):
        long_draft = "This is a considerably longer and more elaborately qualified sentence that goes on for quite a while. " * 3
        short_final = "This is short. Very short."
        pairs = [(long_draft, short_final)] * 4
        tendencies = analyze_edit_diffs(pairs)
        dims = {t.dimension: t for t in tendencies}
        self.assertIn("sentence_length", dims)
        self.assertEqual(dims["sentence_length"].direction, "shortened")
        self.assertEqual(dims["sentence_length"].pairs_observed, 4)

    def test_empty_pairs_returns_empty(self):
        self.assertEqual(analyze_edit_diffs([]), [])

    def test_does_not_store_raw_text_in_result(self):
        pairs = [("UNIQUE_DRAFT_MARKER_TEXT here.", "UNIQUE_FINAL_MARKER_TEXT here.")]
        tendencies = analyze_edit_diffs(pairs)
        result_str = str(tendencies)
        self.assertNotIn("UNIQUE_DRAFT_MARKER_TEXT", result_str)
        self.assertNotIn("UNIQUE_FINAL_MARKER_TEXT", result_str)


if __name__ == "__main__":
    unittest.main()
