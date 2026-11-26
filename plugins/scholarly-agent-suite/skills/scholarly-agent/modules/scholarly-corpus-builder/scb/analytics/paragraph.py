"""Paragraph-level features (PART XVIII)."""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import List

from scb.analytics.sentence import split_sentences


@dataclass
class ParagraphMetrics:
    paragraph_count: int
    median_length_words: float
    length_iqr_words: float
    mean_sentences_per_paragraph: float
    sentence_count_variance: float


def _word_count(paragraph: str) -> int:
    return len(paragraph.split())


def compute_paragraph_metrics(paragraphs: List[str]) -> ParagraphMetrics:
    non_empty = [p for p in paragraphs if p and p.strip()]
    if not non_empty:
        return ParagraphMetrics(0, 0.0, 0.0, 0.0, 0.0)

    lengths = [_word_count(p) for p in non_empty]
    sentence_counts = [len(split_sentences(p)) for p in non_empty]

    sorted_lengths = sorted(lengths)
    q1 = statistics.median(sorted_lengths[: len(sorted_lengths) // 2]) if len(sorted_lengths) >= 2 else sorted_lengths[0]
    upper_half = sorted_lengths[(len(sorted_lengths) + 1) // 2:]
    q3 = statistics.median(upper_half) if upper_half else sorted_lengths[-1]

    return ParagraphMetrics(
        paragraph_count=len(non_empty),
        median_length_words=statistics.median(lengths),
        length_iqr_words=q3 - q1,
        mean_sentences_per_paragraph=statistics.mean(sentence_counts),
        sentence_count_variance=statistics.pvariance(sentence_counts) if len(sentence_counts) > 1 else 0.0,
    )
