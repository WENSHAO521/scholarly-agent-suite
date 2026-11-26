"""Rhetorical move analytics (PART XIX). Rule-based keyword-cue
classification at paragraph granularity — outputs are INFERRED labels,
never presented as objective linguistic fact (PART XIX: "model-assisted
outputs must be labeled as inferred classifications").
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

# A paragraph may exhibit more than one move — these are not mutually
# exclusive, unlike claims.py's per-sentence categories.
_MOVE_CUES = {
    "problem_framing": ["a key challenge", "an important problem", "poses a challenge", "remains unclear", "little is known about", "poorly understood"],
    "literature_positioning": ["prior research", "previous studies", "existing literature", "scholars have argued", "the literature on"],
    "gap": ["few studies", "little research", "this gap", "received little attention", "remains understudied", "remains underexplored"],
    "research_question": ["we ask", "raises the question", "research question", "we investigate whether"],
    "hypothesis": ["we hypothesize", "we predict that", "our hypothesis"],
    "definition": ["we define", "is defined as", "refers to", "we use the term"],
    "mechanism": ["the mechanism", "operates through", "works by", "process by which"],
    "evidence": ["the data show", "results indicate", "as shown in table", "as shown in figure", "we find that"],
    "counterargument": ["one might argue", "a possible objection", "critics have argued", "one could contend"],
    "qualification": ["it should be noted", "an important caveat", "limited to", "we caution that"],
    "contribution": ["this paper contributes", "our contribution", "we contribute to", "adds to the literature"],
    "limitation": ["a limitation of this study", "one limitation is", "is limited by"],
    "implication": ["this implies", "the implications of", "these findings suggest that"],
    "future_research": ["future research should", "future work could", "further research is needed"],
}


def classify_paragraph_moves(paragraph: str) -> List[str]:
    lowered = paragraph.lower()
    return [move for move, cues in _MOVE_CUES.items() if any(cue in lowered for cue in cues)]


@dataclass
class RhetoricalMoveAnalysis:
    paragraph_count: int
    move_counts: Dict[str, int] = field(default_factory=dict)
    move_shares: Dict[str, float] = field(default_factory=dict)


def analyze_rhetorical_moves(paragraphs: List[str]) -> RhetoricalMoveAnalysis:
    non_empty = [p for p in paragraphs if p and p.strip()]
    if not non_empty:
        return RhetoricalMoveAnalysis(paragraph_count=0)

    counts: Counter = Counter()
    for p in non_empty:
        for move in classify_paragraph_moves(p):
            counts[move] += 1

    total = len(non_empty)
    shares = {move: round(n / total, 3) for move, n in counts.items()}
    return RhetoricalMoveAnalysis(paragraph_count=total, move_counts=dict(counts), move_shares=shares)
