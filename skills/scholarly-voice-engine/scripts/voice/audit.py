"""Heuristic prose-audit helpers operationalizing
references/human-scholarly-prose.md and references/quality-audit.md.

These are deliberately simple pattern/statistics checks, not NLP or a
generic-AI-detector: they exist to catch the specific, named failure modes
those reference files describe (transition repetition, uniform sentence
length, citation dumping), not to classify text as "AI-written" — see
references/integration.md §Out of scope.
"""
from __future__ import annotations

import re
import statistics

# Kept in sync with human-scholarly-prose.md §Transitions to avoid overusing
# and quality-audit.md's expanded list. Matched case-insensitively.
GENERIC_AI_PHRASES = [
    r"\bfurthermore\b",
    r"\bmoreover\b",
    r"\badditionally\b",
    r"\bit is important to note that\b",
    r"\bit is worth noting that\b",
    r"\bin today's rapidly changing world\b",
    r"\bthis study aims to\b",
    r"\bthis paper seeks to\b",
    r"\bthe findings highlight the importance of\b",
    r"\bfrom this perspective\b",
    r"\bin conclusion\b",
]

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
_CITATION_CLUSTER_RE = re.compile(r"\(([^()]*?;[^()]*?;[^()]*?;[^()]*?)\)")


def scan_generic_phrases(text: str) -> dict[str, int]:
    """Return {pattern: match_count} for every generic-AI phrase pattern
    found at least once, case-insensitively."""
    lowered = text.lower()
    hits: dict[str, int] = {}
    for pattern in GENERIC_AI_PHRASES:
        count = len(re.findall(pattern, lowered))
        if count:
            hits[pattern] = count
    return hits


def _sentence_lengths(text: str) -> list[int]:
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    return [len(s.split()) for s in sentences]


def sentence_length_variation(text: str) -> float:
    """Coefficient of variation (stdev/mean) of sentence length in words.
    Returns 0.0 for fewer than two sentences (not enough signal)."""
    lengths = _sentence_lengths(text)
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return statistics.pstdev(lengths) / mean


def flag_uniform_sentence_length(text: str, threshold: float = 0.15) -> bool:
    """True if sentence lengths vary less than `threshold` (coefficient of
    variation) across at least three sentences — see
    human-scholarly-prose.md §Controlled asymmetry."""
    if len(_sentence_lengths(text)) < 3:
        return False
    return sentence_length_variation(text) < threshold


def find_citation_dumps(text: str, min_citations: int = 4) -> list[str]:
    """Return parenthetical clusters with at least `min_citations`
    semicolon-separated entries — a proxy for citation dumping (see
    citation-integrity.md §Integration over dumping)."""
    dumps = []
    for match in _CITATION_CLUSTER_RE.finditer(text):
        cluster = match.group(1)
        if len(cluster.split(";")) >= min_citations:
            dumps.append(match.group(0))
    return dumps


def find_repeated_sentences(text: str) -> list[str]:
    """Return sentences (normalized, case-insensitive) that appear more than
    once verbatim — a proxy for redundancy (quality-audit.md §Redundancy
    audit). Short sentences (<4 words) are ignored to avoid flagging
    incidental repeats like transitional fragments."""
    sentences = [s.strip() for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    seen: dict[str, int] = {}
    for s in sentences:
        if len(s.split()) < 4:
            continue
        key = s.lower()
        seen[key] = seen.get(key, 0) + 1
    return [s for s, count in seen.items() if count > 1]
