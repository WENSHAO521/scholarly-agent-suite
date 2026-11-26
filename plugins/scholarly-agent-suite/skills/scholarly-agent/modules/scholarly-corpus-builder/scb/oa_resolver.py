"""Open Access Resolver (PART VII).

Input: a CanonicalRecord (already enriched by whichever adapters
contributed to it — see dedup.py, which merges `versions`/`sources`/
`provenance` from duplicate records into one). Output: an
AccessResolution naming the best currently-known lawful access state,
ordered from most to least actionable. Never probes hidden publisher
URLs and never bypasses authentication — if no OA location is known,
the resolver reports that honestly instead of guessing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from scb.records import CanonicalRecord

METADATA_ONLY = "METADATA_ONLY"
ABSTRACT_AVAILABLE = "ABSTRACT_AVAILABLE"
OA_LANDING_PAGE = "OA_LANDING_PAGE"
OA_FULLTEXT_AVAILABLE = "OA_FULLTEXT_AVAILABLE"
OA_PDF_AVAILABLE = "OA_PDF_AVAILABLE"
STRUCTURED_FULLTEXT_AVAILABLE = "STRUCTURED_FULLTEXT_AVAILABLE"
ACCESS_RESTRICTED = "ACCESS_RESTRICTED"
LICENSE_UNKNOWN = "LICENSE_UNKNOWN"
RESOLUTION_FAILED = "RESOLUTION_FAILED"

# Most to least informative — resolve_access() stops at the first state
# whose evidence requirement is met (PART VII "stop when sufficient
# lawful access is established").
_STATE_PRECEDENCE = [
    STRUCTURED_FULLTEXT_AVAILABLE,
    OA_PDF_AVAILABLE,
    OA_FULLTEXT_AVAILABLE,
    OA_LANDING_PAGE,
    ABSTRACT_AVAILABLE,
    ACCESS_RESTRICTED,
    LICENSE_UNKNOWN,
    METADATA_ONLY,
    RESOLUTION_FAILED,
]

# Fulltext-shaped version kinds vs. landing-page-shaped ones.
_FULLTEXT_VERSION_KINDS = {"acceptedVersion", "publishedVersion", "submittedVersion", "preprint"}


@dataclass
class AccessResolution:
    state: str
    readable: bool
    reuse_right: str  # "known" | "restricted" | "unknown"
    license_verified: bool
    version: Optional[str] = None
    url: Optional[str] = None
    evidence: List[str] = field(default_factory=list)

    def rank(self) -> int:
        try:
            return _STATE_PRECEDENCE.index(self.state)
        except ValueError:
            return len(_STATE_PRECEDENCE)


def _structured_fulltext_entry(versions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for v in versions:
        if v.get("kind") == "structured_fulltext" or v.get("format") in ("jats_xml", "tei_xml", "bioc"):
            return v
    return None


def _best_oa_version_entry(versions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    oa_entries = [v for v in versions if v.get("is_oa")]
    if not oa_entries:
        return None
    # Prefer entries that carry a pdf_url, then ones whose declared
    # version looks like actual text rather than a bare landing page.
    with_pdf = [v for v in oa_entries if v.get("pdf_url")]
    if with_pdf:
        return with_pdf[0]
    fulltext_shaped = [v for v in oa_entries if v.get("version") in _FULLTEXT_VERSION_KINDS]
    if fulltext_shaped:
        return fulltext_shaped[0]
    return oa_entries[0]


def resolve_access(record: CanonicalRecord) -> AccessResolution:
    evidence: List[str] = []
    access = record.access

    structured = _structured_fulltext_entry(record.versions)
    if structured is not None:
        evidence.append("versions:structured_fulltext")
        return AccessResolution(
            STRUCTURED_FULLTEXT_AVAILABLE,
            readable=True,
            reuse_right="known" if structured.get("license") else "unknown",
            license_verified=bool(structured.get("license")),
            version=structured.get("kind") or structured.get("format"),
            url=structured.get("url"),
            evidence=evidence,
        )

    if access.pdf_url:
        evidence.append("access.pdf_url")
        return AccessResolution(
            OA_PDF_AVAILABLE,
            readable=True,
            reuse_right="known" if access.license_verified else "unknown",
            license_verified=access.license_verified,
            version=access.version,
            url=access.pdf_url,
            evidence=evidence,
        )

    best_version = _best_oa_version_entry(record.versions)
    if best_version is not None:
        evidence.append("versions:oa_entry")
        if best_version.get("pdf_url"):
            return AccessResolution(
                OA_PDF_AVAILABLE, True,
                "known" if best_version.get("license") else "unknown",
                bool(best_version.get("license")),
                best_version.get("version"), best_version.get("pdf_url"), evidence,
            )
        is_fulltext = best_version.get("version") in _FULLTEXT_VERSION_KINDS
        state = OA_FULLTEXT_AVAILABLE if is_fulltext else OA_LANDING_PAGE
        return AccessResolution(
            state, is_fulltext,
            "known" if best_version.get("license") else "unknown",
            bool(best_version.get("license")),
            best_version.get("version"), best_version.get("url"), evidence,
        )

    if access.is_oa and access.best_url:
        evidence.append("access.best_url")
        is_fulltext = access.version in _FULLTEXT_VERSION_KINDS
        state = OA_FULLTEXT_AVAILABLE if is_fulltext else OA_LANDING_PAGE
        return AccessResolution(
            state, is_fulltext,
            "known" if access.license_verified else "unknown",
            access.license_verified,
            access.version, access.best_url, evidence,
        )

    if record.abstract:
        evidence.append("record.abstract")
        return AccessResolution(ABSTRACT_AVAILABLE, False, "unknown", False, evidence=evidence)

    if access.is_oa is False:
        evidence.append("access.is_oa=False")
        return AccessResolution(ACCESS_RESTRICTED, False, "restricted", False, evidence=evidence)

    if not record.title:
        evidence.append("no_bibliographic_data")
        return AccessResolution(RESOLUTION_FAILED, False, "unknown", False, evidence=evidence)

    if access.is_oa is None and not record.versions:
        evidence.append("no_oa_signal")
        return AccessResolution(LICENSE_UNKNOWN, False, "unknown", False, evidence=evidence)

    evidence.append("record.title")
    return AccessResolution(METADATA_ONLY, False, "unknown", False, evidence=evidence)
