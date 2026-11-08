import os
import sys
import unittest


from scb.multilingual import (
    ANALYTICS_SUPPORTED_LANGUAGES,
    build_cross_language_author_profile,
    build_language_aware_profile,
    detect_language,
    group_by_language,
)
from scb.text_normalize import normalize_text

EN_TEXT = "Introduction\nWe argue that institutions matter for policy outcomes and this pattern holds broadly."
DE_TEXT = "Einleitung\nWir argumentieren, dass diese Institution für die Politik von Bedeutung ist und dies für viele Fälle gilt."
ZH_TEXT = "引言\n我们认为制度对政策结果很重要，这一模式在许多情况下都成立。"
JA_TEXT = "はじめに\n私たちは制度が政策の結果にとって重要であると主張します。"
KO_TEXT = "서론\n우리는 제도가 정책 결과에 중요하다고 주장합니다."


class TestDetectLanguage(unittest.TestCase):
    def test_detects_english_via_stopwords(self):
        self.assertEqual(detect_language(EN_TEXT).code, "en")

    def test_detects_german_via_stopwords(self):
        self.assertEqual(detect_language(DE_TEXT).code, "de")

    def test_detects_chinese_via_script(self):
        result = detect_language(ZH_TEXT)
        self.assertEqual(result.code, "zh")
        self.assertEqual(result.method, "script:han")

    def test_detects_japanese_via_kana(self):
        result = detect_language(JA_TEXT)
        self.assertEqual(result.code, "ja")

    def test_detects_korean_via_hangul(self):
        result = detect_language(KO_TEXT)
        self.assertEqual(result.code, "ko")

    def test_empty_text_is_undetermined(self):
        self.assertEqual(detect_language("").code, "und")
        self.assertEqual(detect_language(None).code, "und")

    def test_gibberish_latin_text_is_undetermined_not_forced_to_english(self):
        result = detect_language("xk qz vv jjjj wwww zzzz")
        self.assertEqual(result.code, "und")


class TestGroupByLanguage(unittest.TestCase):
    def test_groups_by_explicit_language_tag(self):
        docs = [
            normalize_text(EN_TEXT, language="en"),
            normalize_text(DE_TEXT, language="de"),
        ]
        groups = group_by_language(docs)
        self.assertEqual(set(groups.keys()), {"en", "de"})

    def test_groups_by_detection_when_untagged(self):
        docs = [normalize_text(ZH_TEXT), normalize_text(EN_TEXT)]
        groups = group_by_language(docs)
        self.assertIn("zh", groups)
        self.assertIn("en", groups)

    def test_never_creates_a_merged_group(self):
        docs = [normalize_text(EN_TEXT, language="en"), normalize_text(DE_TEXT, language="de")]
        groups = group_by_language(docs)
        self.assertNotIn("en+de", groups)
        self.assertEqual(sum(len(v) for v in groups.values()), 2)


class TestBuildLanguageAwareProfile(unittest.TestCase):
    def test_english_gets_full_analytics(self):
        docs = [normalize_text(EN_TEXT, language="en") for _ in range(5)]
        profile = build_language_aware_profile(docs, "author", "test", "en")
        self.assertIsInstance(profile["lexical"], dict)
        self.assertIsInstance(profile["claims"], dict)

    def test_non_english_marks_cue_based_fields_not_applicable(self):
        docs = [normalize_text(ZH_TEXT, language="zh") for _ in range(5)]
        profile = build_language_aware_profile(docs, "author", "test", "zh")
        self.assertEqual(profile["lexical"], "not_applicable: analytics cue lists are English-only")
        self.assertEqual(profile["claims"], "not_applicable: analytics cue lists are English-only")
        self.assertTrue(any("English-only cue lists" in b for b in profile["known_biases"]))

    def test_cjk_word_count_bias_flagged(self):
        docs = [normalize_text(ZH_TEXT, language="zh") for _ in range(5)]
        profile = build_language_aware_profile(docs, "author", "test", "zh")
        self.assertTrue(any("whitespace tokenization" in b for b in profile["known_biases"]))


class TestBuildCrossLanguageAuthorProfile(unittest.TestCase):
    def test_separates_languages_never_merges_statistics(self):
        docs = [
            normalize_text(EN_TEXT, language="en"),
            normalize_text(EN_TEXT, language="en"),
            normalize_text(DE_TEXT, language="de"),
            normalize_text(DE_TEXT, language="de"),
        ]
        profile = build_cross_language_author_profile(docs, target="Test Author")
        self.assertEqual(set(profile["languages_present"]), {"en", "de"})
        self.assertEqual(profile["document_counts_by_language"], {"en": 2, "de": 2})
        self.assertIn("en", profile["language_specific_style"])
        self.assertIn("de", profile["language_specific_style"])

    def test_full_analytics_only_for_supported_languages(self):
        docs = [
            normalize_text(EN_TEXT, language="en"),
            normalize_text(ZH_TEXT, language="zh"),
        ]
        profile = build_cross_language_author_profile(docs)
        self.assertEqual(profile["full_analytics_available_for"], ["en"])
        self.assertEqual(profile["structural_metrics_only_for"], ["zh"])


if __name__ == "__main__":
    unittest.main()
