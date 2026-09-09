"""Categorical fit model (SKILL.md §No fake precision, references/fit-
model.md). An internal numeric score exists for ranking candidates against
each other, but the only thing ever surfaced as a result is one of the six
category labels -- never a percentage or decimal presented as an
acceptance-style probability.
"""
from __future__ import annotations

from dataclasses import dataclass

from jfe.journal_evidence import JournalEvidence
from jfe.manuscript_profile import ManuscriptProfile, tokenize

EXCELLENT_FIT = "EXCELLENT FIT"
STRONG_FIT = "STRONG FIT"
PLAUSIBLE_FIT = "PLAUSIBLE FIT"
STRETCH = "STRETCH"
WEAK_FIT = "WEAK FIT"
NOT_RECOMMENDED = "NOT RECOMMENDED"

_LABEL_THRESHOLDS = (
    (0.75, EXCELLENT_FIT),
    (0.55, STRONG_FIT),
    (0.35, PLAUSIBLE_FIT),
    (0.20, STRETCH),
    (0.05, WEAK_FIT),
)


@dataclass
class FitResult:
    label: str
    topic_overlap_terms: list
    explanation: str
    hard_eliminated: bool


def _topic_overlap(manuscript_keywords: list[str], journal_topics: list[str]) -> tuple[float, list[str]]:
    if not manuscript_keywords or not journal_topics:
        return 0.0, []
    topic_words: set[str] = set()
    for topic in journal_topics:
        topic_words |= tokenize(topic)
    matched = sorted(set(manuscript_keywords) & topic_words)
    if not manuscript_keywords:
        return 0.0, matched
    return len(matched) / len(manuscript_keywords), matched


def _label_for_score(score: float) -> str:
    for threshold, label in _LABEL_THRESHOLDS:
        if score >= threshold:
            return label
    return NOT_RECOMMENDED


def compute_fit(manuscript: ManuscriptProfile, evidence: JournalEvidence,
                 hard_eliminated: bool) -> FitResult:
    """Never returns a numeric score to the caller -- only the label and the
    matched terms that justify it (SKILL.md §Output contract: every
    recommendation must answer 'why this journal?' with concrete evidence).
    """
    if hard_eliminated:
        return FitResult(NOT_RECOMMENDED, [], "Eliminated by a hard filter; soft fit is not evaluated.", True)

    score, matched_terms = _topic_overlap(manuscript.keywords(), evidence.topics)
    label = _label_for_score(score)

    if matched_terms:
        explanation = (f"Topic overlap with this journal's indexed subject areas: "
                        f"{', '.join(matched_terms)}.")
    elif evidence.topics:
        explanation = ("No overlap found between the manuscript's stated discipline/topic keywords "
                        "and this journal's indexed subject areas -- topic fit is weak on this evidence.")
    else:
        explanation = "This index has no topic data for the journal; topic fit could not be evaluated."

    return FitResult(label, matched_terms, explanation, False)
