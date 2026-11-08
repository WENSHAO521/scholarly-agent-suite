"""Lexical features (PART XVII). Keyword/pattern-based proxies — every
value here is a heuristic density, not a validated linguistic
measurement (see references/style-feature-schema.md).
"""

from __future__ import annotations

import re
from dataclasses import dataclass

_FIRST_PERSON_RE = re.compile(r"\b(I|we|us|our|ours|my|mine)\b", re.IGNORECASE)
_PASSIVE_RE = re.compile(r"\b(is|are|was|were|been|being|be)\s+\w+ed\b", re.IGNORECASE)
_NOMINALIZATION_RE = re.compile(r"\b\w+(tion|ment|ity|ance|ence|ness)\b", re.IGNORECASE)

_HEDGE_WORDS = {
    "may", "might", "could", "suggest", "suggests", "suggested", "appears",
    "appear", "seems", "seem", "likely", "possibly", "perhaps", "tends",
    "tend", "somewhat", "relatively", "arguably", "presumably", "plausibly",
}
_CERTAINTY_WORDS = {
    "clearly", "demonstrates", "demonstrate", "proves", "prove", "definitively",
    "undoubtedly", "certainly", "conclusively", "unambiguously", "confirms",
    "confirm", "establishes", "establish",
}
_TRANSITION_WORDS = {
    "however", "therefore", "moreover", "furthermore", "nonetheless",
    "consequently", "thus", "hence", "nevertheless", "accordingly",
    "meanwhile", "similarly", "conversely", "in addition", "in contrast",
    "as a result", "for example", "for instance", "in other words",
}


def _tokenize(text: str):
    return re.findall(r"[A-Za-z']+", text)


def _rate_per_1000_words(count: int, total_words: int) -> float:
    if total_words == 0:
        return 0.0
    return round(count * 1000.0 / total_words, 2)


@dataclass
class LexicalMetrics:
    word_count: int
    unique_word_ratio: float  # type-token ratio proxy
    first_person_rate_per_1000: float
    passive_voice_rate_per_1000: float
    nominalization_rate_per_1000: float
    hedge_rate_per_1000: float
    certainty_rate_per_1000: float
    transition_rate_per_1000: float


def compute_lexical_metrics(text: str) -> LexicalMetrics:
    tokens = _tokenize(text)
    total_words = len(tokens)
    if total_words == 0:
        return LexicalMetrics(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    lower_tokens = [t.lower() for t in tokens]
    unique_ratio = round(len(set(lower_tokens)) / total_words, 3)

    first_person_count = len(_FIRST_PERSON_RE.findall(text))
    passive_count = len(_PASSIVE_RE.findall(text))
    nominalization_count = len(_NOMINALIZATION_RE.findall(text))
    hedge_count = sum(1 for t in lower_tokens if t in _HEDGE_WORDS)
    certainty_count = sum(1 for t in lower_tokens if t in _CERTAINTY_WORDS)

    lower_text = text.lower()
    transition_count = sum(lower_text.count(phrase) for phrase in _TRANSITION_WORDS)

    return LexicalMetrics(
        word_count=total_words,
        unique_word_ratio=unique_ratio,
        first_person_rate_per_1000=_rate_per_1000_words(first_person_count, total_words),
        passive_voice_rate_per_1000=_rate_per_1000_words(passive_count, total_words),
        nominalization_rate_per_1000=_rate_per_1000_words(nominalization_count, total_words),
        hedge_rate_per_1000=_rate_per_1000_words(hedge_count, total_words),
        certainty_rate_per_1000=_rate_per_1000_words(certainty_count, total_words),
        transition_rate_per_1000=_rate_per_1000_words(transition_count, total_words),
    )
