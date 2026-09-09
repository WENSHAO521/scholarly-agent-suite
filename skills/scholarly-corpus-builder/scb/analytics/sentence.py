"""Sentence-level features (PART XVII). Simple, deterministic rule-based
sentence segmentation — not a full NLP tokenizer, but reproducible and
dependency-free.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass
from typing import List

# A conservative abbreviation list to reduce false sentence breaks. Not
# exhaustive — this is a heuristic proxy, not a POS-tagged splitter.
_ABBREVIATIONS = {
    "e.g.", "i.e.", "etc.", "vs.", "cf.", "et al.", "fig.", "eq.", "no.",
    "pp.", "vol.", "dr.", "mr.", "mrs.", "ms.", "prof.", "u.s.", "u.k.",
}

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"“(])")


def split_sentences(text: str) -> List[str]:
    if not text or not text.strip():
        return []
    normalized = text.strip()
    raw_splits = _SENTENCE_SPLIT_RE.split(normalized)

    sentences: List[str] = []
    buffer = ""
    for chunk in raw_splits:
        buffer = (buffer + " " + chunk).strip() if buffer else chunk
        tail = buffer.rsplit(" ", 1)[-1].lower()
        if tail in _ABBREVIATIONS:
            continue
        sentences.append(buffer)
        buffer = ""
    if buffer:
        sentences.append(buffer)
    return [s.strip() for s in sentences if s.strip()]


@dataclass
class SentenceMetrics:
    sentence_count: int
    word_count: int
    median_length: float
    mean_length: float
    length_iqr: float
    length_variance: float
    short_sentence_share: float  # <= 10 words
    long_sentence_share: float  # >= 30 words


def _word_count(sentence: str) -> int:
    return len(re.findall(r"\S+", sentence))


def compute_sentence_metrics(text: str) -> SentenceMetrics:
    sentences = split_sentences(text)
    lengths = [_word_count(s) for s in sentences]
    total_words = sum(lengths)

    if not lengths:
        return SentenceMetrics(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    sorted_lengths = sorted(lengths)
    q1 = statistics.median(sorted_lengths[: len(sorted_lengths) // 2]) if len(sorted_lengths) >= 2 else sorted_lengths[0]
    upper_half = sorted_lengths[(len(sorted_lengths) + 1) // 2:]
    q3 = statistics.median(upper_half) if upper_half else sorted_lengths[-1]

    return SentenceMetrics(
        sentence_count=len(lengths),
        word_count=total_words,
        median_length=statistics.median(lengths),
        mean_length=statistics.mean(lengths),
        length_iqr=q3 - q1,
        length_variance=statistics.pvariance(lengths) if len(lengths) > 1 else 0.0,
        short_sentence_share=sum(1 for l in lengths if l <= 10) / len(lengths),
        long_sentence_share=sum(1 for l in lengths if l >= 30) / len(lengths),
    )
