"""Corpus manifest (PART XII). Every corpus produces a manifest whose
counts are derived from actual records — never a claimed count that
wasn't really retrieved/processed (see references/corpus-policy.md
"Corpus build record" and "no fabricated source counts").
"""

from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List

from scb import __version__ as BUILDER_VERSION
from scb.oa_resolver import (
    ABSTRACT_AVAILABLE,
    OA_FULLTEXT_AVAILABLE,
    OA_PDF_AVAILABLE,
    STRUCTURED_FULLTEXT_AVAILABLE,
)

COMPLETE = "COMPLETE"
COMPLETE_WITH_LIMITATIONS = "COMPLETE_WITH_LIMITATIONS"
PARTIAL = "PARTIAL"
INSUFFICIENT = "INSUFFICIENT"
FAILED = "FAILED"


@dataclass
class CorpusCounts:
    discovered: int = 0
    normalized: int = 0
    duplicates_removed: int = 0
    usable: int = 0
    rejected: int = 0
    metadata_only: int = 0
    abstract_available: int = 0
    structured_fulltext: int = 0
    fulltext_available: int = 0
    restricted: int = 0


def counts_from_resolutions(discovered: int, normalized: int, duplicates_removed: int, resolutions: List[str], rejected: int = 0) -> CorpusCounts:
    """`resolutions` should be the OA-resolution states of records that
    have ALREADY been selected as meeting the caller's requested
    retrieval depth (see scb.acquisition — it depth-filters before
    calling this). `usable` is therefore simply `len(resolutions)`:
    "usable" means "met the depth actually requested," not a fixed
    abstract-or-better bar — a caller who only asked for
    LEVEL_0_METADATA and got exactly that has a usable record, even
    though its access happens to be restricted at fuller depths. The
    per-state tally below is purely a transparency breakdown of *how*
    each usable record resolved, not a second usability gate."""
    counts = CorpusCounts(discovered=discovered, normalized=normalized, duplicates_removed=duplicates_removed, rejected=rejected)
    counts.usable = len(resolutions)
    for state in resolutions:
        if state == STRUCTURED_FULLTEXT_AVAILABLE:
            counts.structured_fulltext += 1
        elif state in (OA_FULLTEXT_AVAILABLE, OA_PDF_AVAILABLE):
            counts.fulltext_available += 1
        elif state == ABSTRACT_AVAILABLE:
            counts.abstract_available += 1
        elif state == "ACCESS_RESTRICTED":
            counts.restricted += 1
        elif state == "OA_LANDING_PAGE":
            pass  # already counted in `usable`; no dedicated sub-bucket
        else:
            counts.metadata_only += 1
    return counts


def determine_sufficiency(usable: int, target_records: int) -> str:
    """Explicit thresholds, not an expensive convergence algorithm
    (PART XI: "do not implement an expensive convergence algorithm
    yet")."""
    if target_records <= 0:
        return FAILED
    if usable <= 0:
        return FAILED
    ratio = usable / target_records
    if ratio >= 1.0:
        return COMPLETE
    if ratio >= 0.7:
        return COMPLETE_WITH_LIMITATIONS
    if usable >= 3 or ratio >= 0.3:
        return PARTIAL
    return INSUFFICIENT


@dataclass
class CorpusManifest:
    corpus_id: str
    corpus_type: str
    target: str
    purpose: str
    created_at: str
    builder_version: str
    query: Dict[str, Any] = field(default_factory=dict)
    sampling: Dict[str, Any] = field(default_factory=dict)
    retrieval_depth: str = ""
    requested_records: int = 0
    counts: CorpusCounts = field(default_factory=CorpusCounts)
    sources: List[str] = field(default_factory=list)
    known_biases: List[str] = field(default_factory=list)
    stop_reason: str = ""
    status: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_manifest(
    corpus_id: str,
    corpus_type: str,
    target: str,
    purpose: str,
    query: Dict[str, Any],
    sampling_info: Dict[str, Any],
    retrieval_depth: str,
    requested_records: int,
    counts: CorpusCounts,
    sources: List[str],
    known_biases: List[str],
    stop_reason: str,
) -> CorpusManifest:
    status = determine_sufficiency(counts.usable, requested_records)
    return CorpusManifest(
        corpus_id=corpus_id,
        corpus_type=corpus_type,
        target=target,
        purpose=purpose,
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        builder_version=BUILDER_VERSION,
        query=query,
        sampling=sampling_info,
        retrieval_depth=retrieval_depth,
        requested_records=requested_records,
        counts=counts,
        sources=sources,
        known_biases=known_biases,
        stop_reason=stop_reason,
        status=status,
    )
