"""Deduplication engine (PART V).

Priority chain: exact DOI -> PMID/PMCID -> OpenAlex ID -> arXiv/DOI
association -> normalized title+authors+year -> conservative fuzzy title
comparison. Never merges on title similarity alone.
"""

from __future__ import annotations

import difflib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from scb.identifiers import classify_identifier_match, RESOLUTION_EXACT
from scb.records import CanonicalRecord

SAME_WORK = "SAME_WORK"
LIKELY_SAME_WORK = "LIKELY_SAME_WORK"
REVIEW_REQUIRED = "REVIEW_REQUIRED"
DISTINCT = "DISTINCT"

# A fuzzy title match alone can only ever reach REVIEW_REQUIRED, never
# SAME_WORK/LIKELY_SAME_WORK — see classify_pair().
_TITLE_SIMILARITY_REVIEW_THRESHOLD = 0.90
_AUTHOR_YEAR_SIMILARITY_THRESHOLD = 0.93

_WS_RE = re.compile(r"\s+")
_PUNCT_RE = re.compile(r"[^\w\s]")


def _normalize_title(title: Optional[str]) -> str:
    if not title:
        return ""
    t = title.lower().strip()
    t = _PUNCT_RE.sub("", t)
    t = _WS_RE.sub(" ", t)
    return t


def _normalize_authors(authors: List[Dict]) -> List[str]:
    names = []
    for a in authors or []:
        name = a.get("name") or a.get("display_name") or ""
        name = name.lower().strip()
        if name:
            names.append(name)
    return sorted(names)


def _title_similarity(a: str, b: str) -> float:
    na, nb = _normalize_title(a), _normalize_title(b)
    if not na or not nb:
        return 0.0
    return difflib.SequenceMatcher(None, na, nb).ratio()


@dataclass
class DedupDecision:
    status: str
    reason: str
    evidence: Dict = field(default_factory=dict)


def classify_pair(a: CanonicalRecord, b: CanonicalRecord) -> DedupDecision:
    id_match = classify_identifier_match(a.identifiers, b.identifiers)
    if id_match == RESOLUTION_EXACT:
        return DedupDecision(SAME_WORK, "matching persistent identifier", {"identifier_match": id_match})

    title_sim = _title_similarity(a.title, b.title)
    same_year = (
        a.publication_year is not None
        and b.publication_year is not None
        and a.publication_year == b.publication_year
    )
    authors_a, authors_b = _normalize_authors(a.authors), _normalize_authors(b.authors)
    same_authors = bool(authors_a) and authors_a == authors_b

    if title_sim >= _AUTHOR_YEAR_SIMILARITY_THRESHOLD and same_year and same_authors:
        return DedupDecision(
            LIKELY_SAME_WORK,
            "normalized title + authors + year match",
            {"title_similarity": round(title_sim, 3), "year": a.publication_year},
        )

    if title_sim >= _TITLE_SIMILARITY_REVIEW_THRESHOLD:
        return DedupDecision(
            REVIEW_REQUIRED,
            "high title similarity without full identifier/author/year corroboration",
            {"title_similarity": round(title_sim, 3)},
        )

    return DedupDecision(DISTINCT, "no corroborating identifier, title, author, or year match", {})


def deduplicate(records: List[CanonicalRecord]) -> "DedupResult":
    """Greedy clustering over classify_pair(). O(n^2); fine for the
    10-500 record target range this Skill is designed for (PART LXXIII)."""
    clusters: List[List[int]] = []
    review_pairs: List[Dict] = []
    assigned = [-1] * len(records)

    for i, rec in enumerate(records):
        if assigned[i] != -1:
            continue
        cluster = [i]
        assigned[i] = len(clusters)
        for j in range(i + 1, len(records)):
            if assigned[j] != -1:
                continue
            decision = classify_pair(rec, records[j])
            if decision.status in (SAME_WORK, LIKELY_SAME_WORK):
                cluster.append(j)
                assigned[j] = len(clusters)
            elif decision.status == REVIEW_REQUIRED:
                review_pairs.append(
                    {"a": records[i].record_id, "b": records[j].record_id, "evidence": decision.evidence}
                )
        clusters.append(cluster)

    deduplicated: List[CanonicalRecord] = []
    duplicate_groups: List[List[str]] = []
    for cluster in clusters:
        primary = records[cluster[0]]
        if len(cluster) > 1:
            group_ids = [records[idx].record_id for idx in cluster]
            duplicate_groups.append(group_ids)
            for idx in cluster[1:]:
                primary.sources.extend(s for s in records[idx].sources if s not in primary.sources)
                primary.provenance.extend(records[idx].provenance)
        deduplicated.append(primary)

    return DedupResult(
        records=deduplicated,
        duplicates_removed=len(records) - len(deduplicated),
        duplicate_groups=duplicate_groups,
        review_required=review_pairs,
    )


@dataclass
class DedupResult:
    records: List[CanonicalRecord]
    duplicates_removed: int
    duplicate_groups: List[List[str]]
    review_required: List[Dict]
