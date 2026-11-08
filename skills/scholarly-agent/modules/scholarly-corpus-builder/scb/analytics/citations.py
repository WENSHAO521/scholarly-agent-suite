"""Citation analytics (PART XVIII). Detects common in-text citation
marker shapes — author-date and numeric-bracket styles. This is a
pattern-matching proxy for citation *presence and position*, not a
bibliometric quality signal (PART XVIII: "do not judge quality solely
from citation density" — this module makes no quality claim at all).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from scb.analytics.sentence import split_sentences

# (Author, 2020) / (Author & Other, 2020) / (Author et al., 2020) / (Author, 2020, p. 5)
_AUTHOR_DATE_RE = re.compile(
    r"\(([A-Z][A-Za-z\-']+(?:\s(?:&|and)\s[A-Z][A-Za-z\-']+|\set al\.)?,?\s\d{4}[a-z]?(?:,\s*p{1,2}\.\s*\d+)?)\)"
)
# [1] / [1,2] / [1-3]
_NUMERIC_BRACKET_RE = re.compile(r"\[\d+(?:[,\-]\s?\d+)*\]")


def find_citations(text: str) -> List[str]:
    return _AUTHOR_DATE_RE.findall(text) + _NUMERIC_BRACKET_RE.findall(text)


@dataclass
class CitationMetrics:
    citation_count: int
    citations_per_1000_words: float
    sentence_final_citation_share: float
    citation_free_paragraph_share: float


def compute_citation_metrics(paragraphs: List[str]) -> CitationMetrics:
    all_text = "\n\n".join(paragraphs)
    word_count = len(all_text.split())
    citations = find_citations(all_text)
    citation_count = len(citations)

    if word_count == 0:
        return CitationMetrics(0, 0.0, 0.0, 0.0)

    sentences = []
    for p in paragraphs:
        sentences.extend(split_sentences(p))
    sentence_final = 0
    for s in sentences:
        tail = s.rstrip()
        if _AUTHOR_DATE_RE.search(tail[-40:]) or _NUMERIC_BRACKET_RE.search(tail[-20:]):
            if tail.endswith(")") or tail.endswith("]") or tail.endswith(").") or tail.endswith("].") :
                sentence_final += 1
    sentence_final_share = round(sentence_final / len(sentences), 3) if sentences else 0.0

    non_empty_paragraphs = [p for p in paragraphs if p and p.strip()]
    citation_free = sum(1 for p in non_empty_paragraphs if not find_citations(p))
    citation_free_share = round(citation_free / len(non_empty_paragraphs), 3) if non_empty_paragraphs else 0.0

    return CitationMetrics(
        citation_count=citation_count,
        citations_per_1000_words=round(citation_count * 1000.0 / word_count, 2),
        sentence_final_citation_share=sentence_final_share,
        citation_free_paragraph_share=citation_free_share,
    )
