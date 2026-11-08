import os
import sys
import unittest


from scb.profile_schema import ILLUSTRATIVE, LIMITED, build_style_profile, sample_size_label
from scb.text_normalize import normalize_text

SAMPLE_DOC_TEXT = """Introduction
This paper studies institutional mechanisms in policy diffusion (Smith, 2020). We argue that coercive pressure causes convergence.

Methods
We use archival data from twelve countries.

Results
The data show a strong effect of coercive pressure on adoption timing.

Limitations
This study is limited by its focus on a single policy domain.
"""


class TestSampleSizeLabel(unittest.TestCase):
    def test_thresholds(self):
        self.assertEqual(sample_size_label(2), ILLUSTRATIVE)
        self.assertEqual(sample_size_label(10), LIMITED)


class TestBuildStyleProfile(unittest.TestCase):
    def test_empty_corpus(self):
        profile = build_style_profile("journal", "Journal X", [])
        self.assertEqual(profile.sample_size, 0)
        self.assertEqual(profile.confidence["overall"], "low")

    def test_profile_from_documents(self):
        docs = [normalize_text(SAMPLE_DOC_TEXT) for _ in range(6)]
        profile = build_style_profile("journal", "Journal X", docs, known_biases=["OA bias"])
        self.assertEqual(profile.sample_size, 6)
        self.assertEqual(profile.sample_size_label, LIMITED)
        self.assertGreater(profile.sentence["median_length"], 0)
        self.assertIn("OA bias", profile.known_biases)
        self.assertIn("limitations_section_share", profile.sections)
        self.assertEqual(profile.sections["limitations_section_share"], 1.0)

    def test_to_dict_is_json_shaped(self):
        docs = [normalize_text(SAMPLE_DOC_TEXT)]
        profile = build_style_profile("author", "Test Author", docs)
        d = profile.to_dict()
        self.assertIn("sentence", d)
        self.assertIn("confidence", d)
        self.assertIsInstance(d["intellectual_rhythm"], list)

    def test_rhythm_confidence_always_low(self):
        docs = [normalize_text(SAMPLE_DOC_TEXT) for _ in range(30)]
        profile = build_style_profile("discipline", "Field X", docs)
        self.assertEqual(profile.confidence["intellectual_rhythm"], "low")


if __name__ == "__main__":
    unittest.main()
