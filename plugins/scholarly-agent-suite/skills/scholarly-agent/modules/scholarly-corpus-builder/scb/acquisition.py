"""Corpus Acquisition Engine (PART IX + orchestration). Ties together
search across configured adapters -> dedup -> OA resolution -> sampling
-> sufficiency gate -> manifest.

This module never bypasses access controls and never retries a failed
adapter beyond what scb.http_client already does — an adapter failure is
recorded and the engine proceeds with whatever other sources returned
(PART XLVI "retrieval problems are not reasoning problems").
"""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from scb.dedup import deduplicate
from scb.manifest import CorpusManifest, build_manifest, counts_from_resolutions
from scb.oa_resolver import resolve_access
from scb.records import CanonicalRecord
from scb.retrieval_depth import LEVEL_1_ABSTRACT, meets_requested_depth
from scb.sampling import diversified_sample

CORPUS_TYPES = ("discipline", "journal", "historical_scholar", "author", "book", "comparison")


@dataclass
class CorpusRequest:
    corpus_type: str
    target: str
    purpose: str
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    article_types: List[str] = field(default_factory=list)
    target_records: int = 30
    retrieval_depth: str = LEVEL_1_ABSTRACT
    languages: List[str] = field(default_factory=list)
    constraints: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.corpus_type not in CORPUS_TYPES:
            raise ValueError("unknown corpus_type %r; expected one of %r" % (self.corpus_type, CORPUS_TYPES))


@dataclass
class AcquisitionResult:
    records: List[CanonicalRecord]
    manifest: CorpusManifest
    adapter_errors: Dict[str, str] = field(default_factory=dict)
    review_required: List[Dict[str, Any]] = field(default_factory=list)


def _corpus_id(request: CorpusRequest) -> str:
    digest = hashlib.sha256(("%s|%s" % (request.corpus_type, request.target)).encode("utf-8")).hexdigest()[:10]
    return "%s-%s-%s" % (request.corpus_type, digest, uuid.uuid4().hex[:6])


def acquire_corpus(request: CorpusRequest, adapters: Dict[str, Any]) -> AcquisitionResult:
    """`adapters` maps a name to an already-configured adapter instance
    (its own per_page/rows/retmax/max_results limit is that adapter's
    concern, not the orchestrator's — each adapter's default is used)."""
    discovered_records: List[CanonicalRecord] = []
    adapter_errors: Dict[str, str] = {}
    sources_used: List[str] = []

    for name, adapter in adapters.items():
        if not getattr(adapter.capabilities, "search", False):
            continue
        sources_used.append(name)
        try:
            results = adapter.search(request.target)
        except Exception as e:  # noqa: BLE001 — one bad adapter must not sink acquisition
            adapter_errors[name] = str(e)
            continue
        discovered_records.extend(results)

    discovered = len(discovered_records)
    dedup_result = deduplicate(discovered_records)
    normalized = len(dedup_result.records)

    resolutions = {rec.record_id: resolve_access(rec) for rec in dedup_result.records}
    depth_filtered = [
        rec for rec in dedup_result.records
        if meets_requested_depth(resolutions[rec.record_id], bool(rec.abstract), request.retrieval_depth)
    ]
    rejected = normalized - len(depth_filtered)

    sampling_result = diversified_sample(depth_filtered, request.target_records)

    counts = counts_from_resolutions(
        discovered=discovered,
        normalized=normalized,
        duplicates_removed=dedup_result.duplicates_removed,
        resolutions=[resolutions[r.record_id].state for r in sampling_result.selected],
        rejected=rejected,
    )

    known_biases = []
    if len(set(sources_used)) <= 1 and sources_used:
        known_biases.append("single_source_bias: only %s was queried" % sources_used[0])
    if adapter_errors:
        known_biases.append("partial_source_coverage: %s failed and were skipped" % ", ".join(adapter_errors))

    manifest = build_manifest(
        corpus_id=_corpus_id(request),
        corpus_type=request.corpus_type,
        target=request.target,
        purpose=request.purpose,
        query={"target": request.target, "date_from": request.date_from, "date_to": request.date_to, "article_types": request.article_types},
        sampling_info={"target_records": request.target_records, "caps": sampling_result.caps, "dominance_prevented": sampling_result.dominance_prevented},
        retrieval_depth=request.retrieval_depth,
        requested_records=request.target_records,
        counts=counts,
        sources=sources_used,
        known_biases=known_biases,
        stop_reason=(
            "target_records reached" if len(sampling_result.selected) >= request.target_records
            else "candidate pool exhausted before reaching target_records"
        ),
    )

    return AcquisitionResult(
        records=sampling_result.selected,
        manifest=manifest,
        adapter_errors=adapter_errors,
        review_required=dedup_result.review_required,
    )
