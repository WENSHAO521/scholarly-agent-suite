"""Identifier normalization and resolution states (PART IV).

Normalizes DOI / PMID / PMCID / OpenAlex ID / arXiv ID / ISSN / ORCID into
canonical forms, and classifies how confidently two identifier sets refer
to the same work.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

RESOLUTION_EXACT = "EXACT"
RESOLUTION_PROBABLE = "PROBABLE"
RESOLUTION_AMBIGUOUS = "AMBIGUOUS"
RESOLUTION_UNRESOLVED = "UNRESOLVED"

_DOI_PREFIX_RE = re.compile(r"^(doi:|https?://(dx\.)?doi\.org/)", re.IGNORECASE)
_DOI_SHAPE_RE = re.compile(r"^10\.\d{4,9}/\S+$")

_ARXIV_NEW_RE = re.compile(r"^(?P<base>\d{4}\.\d{4,5})(v(?P<version>\d+))?$")
_ARXIV_OLD_RE = re.compile(
    r"^(?P<base>[a-z-]+(\.[A-Z]{2})?/\d{7})(v(?P<version>\d+))?$", re.IGNORECASE
)

_PMID_RE = re.compile(r"^\d+$")
_PMCID_RE = re.compile(r"^(PMC)?(\d+)$", re.IGNORECASE)
_ISSN_RE = re.compile(r"^\d{4}-\d{3}[\dXx]$")
_ORCID_RE = re.compile(r"^(https?://orcid\.org/)?(\d{4}-\d{4}-\d{4}-\d{3}[\dXx])$")


def normalize_doi(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    value = raw.strip()
    value = _DOI_PREFIX_RE.sub("", value)
    value = value.strip().rstrip("/")
    value = value.lower()
    if not _DOI_SHAPE_RE.match(value):
        return None
    return value


@dataclass
class ArxivId:
    base: str
    version: Optional[int]

    @property
    def canonical(self) -> str:
        return self.base

    @property
    def versioned(self) -> str:
        if self.version is None:
            return self.base
        return "%sv%d" % (self.base, self.version)


def normalize_arxiv(raw: Optional[str]) -> Optional[ArxivId]:
    if not raw:
        return None
    value = raw.strip()
    value = re.sub(r"^arxiv:", "", value, flags=re.IGNORECASE)
    value = re.sub(r"^https?://arxiv\.org/abs/", "", value, flags=re.IGNORECASE)
    m = _ARXIV_NEW_RE.match(value) or _ARXIV_OLD_RE.match(value)
    if not m:
        return None
    base = m.group("base")
    version = m.group("version")
    return ArxivId(base=base, version=int(version) if version else None)


def normalize_pmid(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    value = str(raw).strip()
    if not _PMID_RE.match(value):
        return None
    return value


def normalize_pmcid(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    value = str(raw).strip()
    m = _PMCID_RE.match(value)
    if not m:
        return None
    return "PMC%s" % m.group(2)


def normalize_issn(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    value = raw.strip().upper()
    if not _ISSN_RE.match(value):
        return None
    return value


def normalize_orcid(raw: Optional[str]) -> Optional[str]:
    if not raw:
        return None
    m = _ORCID_RE.match(raw.strip())
    if not m:
        return None
    return m.group(2).upper()


def classify_identifier_match(a: "Identifiers", b: "Identifiers") -> str:  # noqa: F821
    """Compare two records' Identifiers objects (scb.records.Identifiers).

    Never promotes a weak title match into EXACT — this function only
    looks at identifiers, on purpose (see dedup.py for the full chain,
    which falls back to title/author comparison only after this returns
    UNRESOLVED).
    """
    if a.doi and b.doi and a.doi == b.doi:
        return RESOLUTION_EXACT
    if a.pmid and b.pmid and a.pmid == b.pmid:
        return RESOLUTION_EXACT
    if a.pmcid and b.pmcid and a.pmcid == b.pmcid:
        return RESOLUTION_EXACT
    if a.openalex_id and b.openalex_id and a.openalex_id == b.openalex_id:
        return RESOLUTION_EXACT
    if a.arxiv_id and b.arxiv_id:
        a_base = normalize_arxiv(a.arxiv_id)
        b_base = normalize_arxiv(b.arxiv_id)
        if a_base and b_base and a_base.base == b_base.base:
            return RESOLUTION_EXACT

    has_any_a = any([a.doi, a.pmid, a.pmcid, a.openalex_id, a.arxiv_id])
    has_any_b = any([b.doi, b.pmid, b.pmcid, b.openalex_id, b.arxiv_id])
    if has_any_a and has_any_b:
        # Both sides carry identifiers but none matched — treat as distinct,
        # not ambiguous: a shared title alone should not soften this.
        return RESOLUTION_UNRESOLVED
    if has_any_a or has_any_b:
        return RESOLUTION_AMBIGUOUS
    return RESOLUTION_UNRESOLVED
