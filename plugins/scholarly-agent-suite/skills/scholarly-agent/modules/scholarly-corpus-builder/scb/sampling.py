"""Sampling Engine (PART X). Diversifies a candidate pool instead of
taking the first N results — prevents one special issue, one author, one
laboratory, or one methodology from dominating a corpus.
"""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from scb.records import CanonicalRecord

DEFAULT_MAX_SHARE_PER_AUTHOR = 0.34
DEFAULT_MAX_SHARE_PER_YEAR = 0.5
DEFAULT_MAX_SHARE_PER_ISSUE = 0.34

# Suggested defaults — heuristics, not statistical guarantees (PART XI).
SUGGESTED_TARGETS = {
    "journal": (20, 50),
    "discipline": (40, 100),
    "author": (5, 20),
    "historical_scholar": (None, None),  # representative selected works, no fixed range
}


def _primary_author(rec: CanonicalRecord) -> Optional[str]:
    if rec.authors:
        return rec.authors[0].get("name")
    return None


def _issue_key(rec: CanonicalRecord):
    return (rec.venue, rec.volume, rec.issue)


@dataclass
class SamplingResult:
    selected: List[CanonicalRecord]
    deferred: List[CanonicalRecord]
    caps: Dict[str, int]
    author_distribution: Dict[str, int] = field(default_factory=dict)
    year_distribution: Dict[str, int] = field(default_factory=dict)
    dominance_prevented: List[str] = field(default_factory=list)


def diversified_sample(
    records: List[CanonicalRecord],
    target_records: int,
    max_share_per_author: float = DEFAULT_MAX_SHARE_PER_AUTHOR,
    max_share_per_year: float = DEFAULT_MAX_SHARE_PER_YEAR,
    max_share_per_issue: float = DEFAULT_MAX_SHARE_PER_ISSUE,
) -> SamplingResult:
    """`records` should already be ordered by the caller's preferred
    priority (e.g. relevance, then recency) — this function enforces
    diversity caps over that order, it does not itself rank relevance.
    """
    caps = {
        "author": max(1, math.ceil(target_records * max_share_per_author)),
        "year": max(1, math.ceil(target_records * max_share_per_year)),
        "issue": max(1, math.ceil(target_records * max_share_per_issue)),
    }
    counts = {"author": Counter(), "year": Counter(), "issue": Counter()}
    selected: List[CanonicalRecord] = []
    deferred: List[CanonicalRecord] = []
    dominance_prevented: List[str] = []

    for rec in records:
        if len(selected) >= target_records:
            deferred.append(rec)
            continue

        author = _primary_author(rec)
        year = rec.publication_year
        issue = _issue_key(rec) if rec.issue else None

        if author and counts["author"][author] >= caps["author"]:
            deferred.append(rec)
            dominance_prevented.append("author:%s" % author)
            continue
        if year and counts["year"][year] >= caps["year"]:
            deferred.append(rec)
            dominance_prevented.append("year:%s" % year)
            continue
        if issue and counts["issue"][issue] >= caps["issue"]:
            deferred.append(rec)
            dominance_prevented.append("issue:%s" % (issue,))
            continue

        selected.append(rec)
        if author:
            counts["author"][author] += 1
        if year:
            counts["year"][year] += 1
        if issue:
            counts["issue"][issue] += 1

    # Backfill toward the target if strict caps left the sample short —
    # diversity is a soft constraint, hitting the requested size is not
    # sacrificed to it once the pool is otherwise exhausted.
    if len(selected) < target_records:
        still_deferred = []
        for rec in deferred:
            if len(selected) >= target_records:
                still_deferred.append(rec)
                continue
            selected.append(rec)
        deferred = still_deferred

    return SamplingResult(
        selected=selected,
        deferred=deferred,
        caps=caps,
        author_distribution=dict(Counter(_primary_author(r) for r in selected if _primary_author(r))),
        year_distribution=dict(Counter(str(r.publication_year) for r in selected if r.publication_year)),
        dominance_prevented=dominance_prevented,
    )
