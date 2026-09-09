"""Book corpus profile builder (PART XLVII-XLVIII). Treats each supplied
Document as one chapter — books are analyzed on their own terms, not as
"enlarged journal articles" (PART XLVII).
"""

from __future__ import annotations

from typing import Any, Dict, List

from scb.analytics.paragraph import compute_paragraph_metrics
from scb.analytics.sentence import compute_sentence_metrics
from scb.profile_schema import build_style_profile
from scb.text_normalize import Document


def build_book_profile(chapters: List[Document], title: str = "") -> Dict[str, Any]:
    style = build_style_profile("book", title, chapters)

    chapter_word_counts = [sum(s.word_count for s in ch.sections) for ch in chapters]
    opening_sentences = []
    for ch in chapters:
        paras = ch.all_paragraphs()
        if paras:
            sentences = compute_sentence_metrics(paras[0])
            opening_sentences.append(sentences.median_length)

    return {
        "profile_type": "book",
        "title": title,
        "chapters_sampled": len(chapters),
        "chapter_length": {
            "median_words": sorted(chapter_word_counts)[len(chapter_word_counts) // 2] if chapter_word_counts else 0,
            "min_words": min(chapter_word_counts) if chapter_word_counts else 0,
            "max_words": max(chapter_word_counts) if chapter_word_counts else 0,
        },
        "chapter_opening_style": {
            "median_opening_sentence_length": (
                sorted(opening_sentences)[len(opening_sentences) // 2] if opening_sentences else 0
            ),
        },
        "narrative_density": style.lexical,
        "citation_distribution": style.citations,
        "argument_progression": style.argument_architecture,
        "recurring_concepts": [],  # not computed: needs cross-chapter concept/entity extraction (future work)
        "cross_chapter_transitions": [],  # not computed: needs cross-chapter reference detection (future work)
        "confidence": style.confidence,
        "sample_size_label": style.sample_size_label,
        "generated_at": style.generated_at,
    }
