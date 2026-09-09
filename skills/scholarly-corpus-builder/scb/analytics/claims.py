"""Claim calibration (PART XX). Rule-based keyword-cue classification —
this is an INFERRED, heuristic label per sentence, not an objective
linguistic fact. Never rewrites an associational cue into a causal
claim: cue lists are disjoint by construction and matched in a fixed
priority order so a sentence gets at most one category.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from scb.analytics.sentence import split_sentences

UNCLASSIFIED = "unclassified"

# Checked in this order; the first match wins. Ordered from most
# specific/rare cue language to most general, so e.g. a formal-math cue
# is never swallowed by a broader interpretive cue.
_CUE_PRIORITY = [
    ("formal", ["theorem", "lemma", " proof ", "axiom", "corollary", "proposition"]),
    ("mechanistic", ["mechanism", "pathway", "process by which", "via which", "through which"]),
    ("causal", ["cause ", "causes", "caused", "causing", "leads to", "led to", "results in", "resulted in", "brings about", "due to"]),
    ("predictive", [" will ", "predicts", "predicted", "forecasts", "is expected to", "are expected to", "is likely to increase", "is likely to decrease"]),
    ("normative", [" should ", "ought to", " must ", "needs to", "is necessary to", "policymakers should"]),
    ("associational", ["associated with", "correlated with", "correlates with", "related to", "linked to"]),
    ("interpretive", ["suggests that", "this suggests", "indicates that", "implies that", "points to the possibility"]),
    ("descriptive", ["we observe", "we find that", "the data show", "consists of", "is characterized by"]),
]

_HEDGE_MARKERS = {"may", "might", "could", "suggest", "suggests", "appears", "seems", "likely", "possibly", "perhaps"}


def classify_sentence(sentence: str) -> str:
    lowered = " " + sentence.lower() + " "
    for category, cues in _CUE_PRIORITY:
        if any(cue in lowered for cue in cues):
            return category
    return UNCLASSIFIED


@dataclass
class ClaimAnalysis:
    total_sentences: int
    category_counts: Dict[str, int] = field(default_factory=dict)
    category_shares: Dict[str, float] = field(default_factory=dict)
    hedge_cooccurrence_rate: Dict[str, float] = field(default_factory=dict)
    dominant_category: Optional[str] = None


def _has_hedge(sentence: str) -> bool:
    lowered = sentence.lower()
    return any(w in lowered for w in _HEDGE_MARKERS)


def analyze_claims(text: str) -> ClaimAnalysis:
    sentences = split_sentences(text)
    if not sentences:
        return ClaimAnalysis(total_sentences=0)

    counts: Counter = Counter()
    hedged_counts: Counter = Counter()
    for s in sentences:
        category = classify_sentence(s)
        counts[category] += 1
        if category != UNCLASSIFIED and _has_hedge(s):
            hedged_counts[category] += 1

    total = len(sentences)
    shares = {cat: round(n / total, 3) for cat, n in counts.items()}
    hedge_rates = {
        cat: round(hedged_counts[cat] / counts[cat], 3)
        for cat in counts
        if cat != UNCLASSIFIED and counts[cat] > 0
    }

    classified = {cat: n for cat, n in counts.items() if cat != UNCLASSIFIED}
    dominant = max(classified, key=classified.get) if classified else None

    return ClaimAnalysis(
        total_sentences=total,
        category_counts=dict(counts),
        category_shares=shares,
        hedge_cooccurrence_rate=hedge_rates,
        dominant_category=dominant,
    )
