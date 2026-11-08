"""Multilingual and cross-language support (PART XLIV-XLVI).

Honest scope: `detect_language()` is a real, working heuristic for a
defined language set (script-based for CJK/Korean, stopword-frequency
based for a handful of Latin-script languages) — not a statistical
language-ID model. More importantly: scb/analytics/{lexical,claims,
rhetorical,rhythm}.py all match against English-language cue words and
phrases ("however", "we argue that", "should", ...). Run against
non-English text, those cue lists simply won't match anything, which
would silently produce misleading near-zero rates if presented as
measurements. This module's `build_language_aware_profile()` therefore
explicitly marks those sub-features `not_applicable` for any language
other than English, rather than let a meaningless zero look like a
real finding. Sentence/paragraph word counts use `str.split()`
whitespace tokenization, which under-counts languages that don't use
inter-word spaces (Chinese, Japanese) — this is called out in the
profile's `known_biases`, not silently presented as accurate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Optional

from scb.profile_schema import StyleProfile, build_style_profile
from scb.text_normalize import Document

# Languages the analytics engine's English-cue-based sub-features
# (lexical/claims/rhetorical_moves/intellectual_rhythm) can meaningfully
# be run against today.
ANALYTICS_SUPPORTED_LANGUAGES = {"en"}

_CJK_RE = re.compile(r"[一-鿿]")
_HIRAGANA_KATAKANA_RE = re.compile(r"[぀-ヿ]")
_HANGUL_RE = re.compile(r"[가-힣]")

# Small stopword sets — enough to distinguish these languages from each
# other and from English via relative frequency, not a full lexicon.
_STOPWORDS = {
    "en": {"the", "and", "of", "to", "in", "is", "that", "we", "this", "for"},
    "de": {"der", "die", "das", "und", "ist", "wir", "diese", "für", "mit", "auf"},
    "fr": {"le", "la", "les", "et", "de", "est", "nous", "cette", "pour", "avec"},
    "es": {"el", "la", "los", "las", "y", "de", "es", "nosotros", "esta", "para"},
}


@dataclass
class LanguageDetection:
    code: str  # ISO-639-1 where confidently detected, "und" otherwise
    confidence: str  # "high" | "medium" | "low"
    method: str


def detect_language(text: Optional[str]) -> LanguageDetection:
    if not text or not text.strip():
        return LanguageDetection("und", "low", "empty_input")

    if _HANGUL_RE.search(text):
        return LanguageDetection("ko", "high", "script:hangul")
    if _HIRAGANA_KATAKANA_RE.search(text):
        return LanguageDetection("ja", "high", "script:hiragana_katakana")
    if _CJK_RE.search(text):
        return LanguageDetection("zh", "medium", "script:han")

    tokens = re.findall(r"[a-zA-ZäöüßéèêàçñÁÉÍÓÚáéíóú']+", text.lower())
    if not tokens:
        return LanguageDetection("und", "low", "no_recognizable_tokens")

    token_set = set(tokens)
    scores = {lang: len(token_set & words) for lang, words in _STOPWORDS.items()}
    best_lang = max(scores, key=scores.get)
    best_score = scores[best_lang]
    if best_score == 0:
        return LanguageDetection("und", "low", "no_stopword_match")
    runner_up = max((s for lang, s in scores.items() if lang != best_lang), default=0)
    confidence = "high" if best_score >= 3 and best_score > runner_up else "medium"
    return LanguageDetection(best_lang, confidence, "stopword_frequency")


def group_by_language(documents: List[Document]) -> Dict[str, List[Document]]:
    """Groups documents by Document.language when set, else by
    detect_language() over the abstract/title. Never merges groups —
    callers must build a separate baseline per language (PART XLIV)."""
    groups: Dict[str, List[Document]] = {}
    for doc in documents:
        if doc.language:
            code = doc.language
        else:
            sample_text = doc.abstract or (doc.sections[0].text if doc.sections else "") or doc.title or ""
            code = detect_language(sample_text).code
        groups.setdefault(code, []).append(doc)
    return groups


def build_language_aware_profile(documents: List[Document], profile_type: str, target: str, language_code: str) -> Dict:
    """Wraps build_style_profile but marks English-cue-based
    sub-features not_applicable for unsupported languages instead of
    presenting a misleading near-zero measurement."""
    profile = build_style_profile(profile_type, target, documents)
    result = profile.to_dict()
    result["language"] = language_code

    if language_code not in ANALYTICS_SUPPORTED_LANGUAGES:
        for field_name in ("lexical", "claims", "rhetorical_moves", "intellectual_rhythm"):
            result[field_name] = "not_applicable: analytics cue lists are English-only"
        result.setdefault("known_biases", [])
        result["known_biases"] = list(result["known_biases"]) + [
            "language=%s: lexical/claim/rhetorical-move/rhythm analytics were not run "
            "(English-only cue lists would produce a misleading near-zero result)" % language_code
        ]
        if language_code in ("zh", "ja"):
            result["known_biases"].append(
                "language=%s: word counts use whitespace tokenization, which under-counts "
                "languages without inter-word spaces — sentence/paragraph length figures are unreliable" % language_code
            )
    return result


def build_cross_language_author_profile(documents: List[Document], target: str = "") -> Dict:
    """PART XLVI: maintains language-specific style separately per
    language, plus reports which language-independent structural
    signals (sentence/paragraph counts) remain available across all
    languages present — never merges per-language numbers into one
    blended statistic."""
    groups = group_by_language(documents)
    per_language = {
        lang: build_language_aware_profile(docs, "author", target, lang)
        for lang, docs in groups.items()
    }

    analyzable_languages = [l for l in groups if l in ANALYTICS_SUPPORTED_LANGUAGES]
    structural_only_languages = [l for l in groups if l not in ANALYTICS_SUPPORTED_LANGUAGES]

    return {
        "profile_type": "cross_language_author",
        "target": target,
        "languages_present": sorted(groups),
        "document_counts_by_language": {lang: len(docs) for lang, docs in groups.items()},
        "language_specific_style": per_language,
        "full_analytics_available_for": analyzable_languages,
        "structural_metrics_only_for": structural_only_languages,
        "note": (
            "Sentence/paragraph/lexical/claim/rhetorical statistics are never merged across "
            "languages — see language_specific_style for each language's own baseline."
        ),
    }
