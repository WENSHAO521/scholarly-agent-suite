"""Canonical Scholarly Record — the single normalized shape every source
adapter produces (see references/source-adapters.md and PART II of the
architecture note). Lightweight dataclasses only; no ORM, no database.
"""

from __future__ import annotations

import copy
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Identifiers:
    doi: Optional[str] = None
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    openalex_id: Optional[str] = None
    arxiv_id: Optional[str] = None
    issn: List[str] = field(default_factory=list)
    other: List[Dict[str, str]] = field(default_factory=list)


@dataclass
class Access:
    readable: Optional[bool] = None
    is_oa: Optional[bool] = None
    oa_status: Optional[str] = None
    reuse_license: Optional[str] = None
    license_source: Optional[str] = None
    license_verified: bool = False
    best_url: Optional[str] = None
    pdf_url: Optional[str] = None
    version: Optional[str] = None


@dataclass
class ProvenanceEntry:
    adapter: str
    operation: str
    retrieved_at: Optional[str] = None
    source_identifier: Optional[str] = None
    verification: str = "NEEDS_CHECK"


@dataclass
class CanonicalRecord:
    """The normalized internal representation every adapter maps into.

    Field shape mirrors the JSON schema in the architecture note exactly
    so `to_dict()` output is safe to write straight into records.jsonl.
    """

    record_id: str
    title: Optional[str] = None
    subtitle: Optional[str] = None
    authors: List[Dict[str, Any]] = field(default_factory=list)
    publication_year: Optional[int] = None
    publication_date: Optional[str] = None
    venue: Optional[str] = None
    publisher: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    work_type: Optional[str] = None
    language: Optional[str] = None

    identifiers: Identifiers = field(default_factory=Identifiers)

    abstract: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)

    access: Access = field(default_factory=Access)

    versions: List[Dict[str, Any]] = field(default_factory=list)
    sources: List[str] = field(default_factory=list)
    provenance: List[ProvenanceEntry] = field(default_factory=list)
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    retrieved_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CanonicalRecord":
        data = copy.deepcopy(data)
        ident = data.pop("identifiers", {}) or {}
        acc = data.pop("access", {}) or {}
        prov_list = data.pop("provenance", []) or []
        return cls(
            identifiers=Identifiers(**ident),
            access=Access(**acc),
            provenance=[ProvenanceEntry(**p) if not isinstance(p, ProvenanceEntry) else p for p in prov_list],
            **data,
        )

    def add_provenance(self, entry: ProvenanceEntry) -> None:
        self.provenance.append(entry)
        if entry.adapter not in self.sources:
            self.sources.append(entry.adapter)
