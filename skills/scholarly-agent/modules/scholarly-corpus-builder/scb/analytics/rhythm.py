"""Intellectual rhythm (PART XXII). Detects a small set of abstract
sentence-role sequences (claim -> evidence -> qualification, etc.) —
deliberately modest in scope: this is 2/3-gram tag-sequence matching
over a coarse per-sentence role tagger, not genuine discourse parsing.
Always reported at "low" confidence, and only the named abstract
patterns are stored — never verbatim phrase sequences (PART XXII: "never
store characteristic phrase banks").
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List

from scb.analytics.sentence import split_sentences

PROBLEM = "PROBLEM"
EVIDENCE = "EVIDENCE"
CLAIM = "CLAIM"
MECHANISM = "MECHANISM"
QUALIFICATION = "QUALIFICATION"
IMPLICATION = "IMPLICATION"
COUNTERARGUMENT = "COUNTERARGUMENT"
OTHER = "OTHER"

_ROLE_CUES = [
    (PROBLEM, ["remains unclear", "little is known", "poses a challenge", "an open question"]),
    (COUNTERARGUMENT, ["one might argue", "a possible objection", "one could contend", "critics have argued"]),
    (MECHANISM, ["the mechanism", "operates through", "works by", "process by which"]),
    (QUALIFICATION, ["it should be noted", "an important caveat", "we caution that", "limited to"]),
    (IMPLICATION, ["this implies", "the implications of", "suggests that policymakers", "these findings suggest"]),
    (EVIDENCE, ["the data show", "results indicate", "we find that", "as shown in"]),
    (CLAIM, ["we argue that", "we show that", "causes", "leads to", "results in", "is associated with"]),
]

# Named abstract patterns this module can detect, as tag n-grams.
_NAMED_PATTERNS = {
    (CLAIM, EVIDENCE, QUALIFICATION): "claim_evidence_qualification",
    (PROBLEM, MECHANISM, IMPLICATION): "problem_mechanism_implication",
    (CLAIM, COUNTERARGUMENT, CLAIM): "premise_objection_revised_claim",
    (EVIDENCE, CLAIM): "evidence_claim",
    (CLAIM, EVIDENCE): "claim_evidence",
    (PROBLEM, EVIDENCE): "problem_evidence",
}


def tag_sentence_role(sentence: str) -> str:
    lowered = sentence.lower()
    for role, cues in _ROLE_CUES:
        if any(cue in lowered for cue in cues):
            return role
    return OTHER


@dataclass
class RhythmAnalysis:
    paragraphs_analyzed: int
    pattern_counts: Dict[str, int] = field(default_factory=dict)
    dominant_pattern: str = None
    confidence: str = "low"


def _detect_patterns_in_tags(tags: List[str]) -> List[str]:
    found = []
    non_other = [t for t in tags if t != OTHER]
    for n in (3, 2):
        for i in range(len(non_other) - n + 1):
            gram = tuple(non_other[i : i + n])
            name = _NAMED_PATTERNS.get(gram)
            if name:
                found.append(name)
    return found


def analyze_rhythm(paragraphs: List[str]) -> RhythmAnalysis:
    non_empty = [p for p in paragraphs if p and p.strip()]
    if not non_empty:
        return RhythmAnalysis(paragraphs_analyzed=0)

    counts: Counter = Counter()
    for p in non_empty:
        sentences = split_sentences(p)
        tags = [tag_sentence_role(s) for s in sentences]
        for pattern_name in _detect_patterns_in_tags(tags):
            counts[pattern_name] += 1

    dominant = max(counts, key=counts.get) if counts else None
    return RhythmAnalysis(paragraphs_analyzed=len(non_empty), pattern_counts=dict(counts), dominant_pattern=dominant)
