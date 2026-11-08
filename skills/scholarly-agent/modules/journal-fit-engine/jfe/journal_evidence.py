"""Live journal evidence lookup via OpenAlex Sources and Crossref Journals
-- the two adapters used are public, keyless, standard bibliographic
indexes (see references/evidence-policy.md's evidence hierarchy: official/
index evidence before secondary listings). Neither is a journal's own
official page; both are labeled as index-sourced accordingly.

Deliberately keeps OFFICIAL_REQUIREMENTS-adjacent fields (issn, publisher,
homepage_url, apc) separate from OBSERVED_CORPUS_PROFILE-adjacent fields
(works_count, topics, cited_by_count) per references/evidence-policy.md and
SKILL.md's Evidence discipline -- this class never blurs the two.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from typing import Optional

from jfe.http_client import HttpClient, HttpError

OPENALEX_SOURCES_URL = "https://api.openalex.org/sources"
CROSSREF_JOURNALS_URL = "https://api.crossref.org/journals"

DEFAULT_MAILTO = "research@example.com"


class EvidenceLookupError(Exception):
    """Raised when neither adapter could resolve the journal."""


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


@dataclass
class JournalEvidence:
    # Identity / OFFICIAL_REQUIREMENTS-adjacent (index-sourced, not the
    # journal's own page -- see provenance below).
    display_name: Optional[str] = None
    issn_l: Optional[str] = None
    issn: list = field(default_factory=list)
    publisher: Optional[str] = None
    homepage_url: Optional[str] = None
    is_oa: Optional[bool] = None
    is_in_doaj: Optional[bool] = None
    apc_usd: Optional[int] = None

    # OBSERVED_CORPUS_PROFILE-adjacent (index-measured activity signals,
    # not editorial policy).
    works_count: Optional[int] = None
    cited_by_count: Optional[int] = None
    first_publication_year: Optional[int] = None
    last_publication_year: Optional[int] = None
    topics: list = field(default_factory=list)

    # Provenance (rule: never present index data as the journal's own
    # official statement).
    source: str = "unknown"  # "openalex" | "crossref" | "openalex+crossref"
    checked_at: Optional[str] = None
    provenance_note: str = "Sourced from a bibliographic index (OpenAlex/Crossref), not the journal's own official page. Verify against the journal's actual submission guidelines before relying on this for a real submission decision."


def _openalex_to_evidence(record: dict) -> JournalEvidence:
    apc = record.get("apc_usd")
    return JournalEvidence(
        display_name=record.get("display_name"),
        issn_l=record.get("issn_l"),
        issn=list(record.get("issn") or []),
        publisher=record.get("host_organization_name"),
        homepage_url=record.get("homepage_url"),
        is_oa=record.get("is_oa"),
        is_in_doaj=record.get("is_in_doaj"),
        apc_usd=apc if isinstance(apc, int) else None,
        works_count=record.get("works_count"),
        cited_by_count=record.get("cited_by_count"),
        first_publication_year=record.get("first_publication_year"),
        last_publication_year=record.get("last_publication_year"),
        topics=[t.get("display_name") for t in (record.get("topics") or []) if t.get("display_name")],
        source="openalex",
    )


def _crossref_to_evidence(item: dict) -> JournalEvidence:
    # Crossref's Journals API returns ISSN as a flat list of strings, e.g.
    # "ISSN": ["2620-8091"] -- unlike some other Crossref endpoints that use
    # {"type": ..., "value": ...} objects. This adapter only ever calls the
    # Journals API, so only the flat-string shape needs handling.
    raw_issns = item.get("ISSN") or []
    issns = [i for i in raw_issns if isinstance(i, str)]
    return JournalEvidence(
        display_name=item.get("title"),
        issn=issns,
        publisher=item.get("publisher"),
        works_count=(item.get("counts") or {}).get("total-dois"),
        source="crossref",
    )


def lookup_by_name(client: HttpClient, query: str, mailto: str = DEFAULT_MAILTO) -> JournalEvidence:
    """Search OpenAlex Sources first (richer: APC, OA, topics, activity
    years); fall back to Crossref Journals if OpenAlex has no match. Raises
    EvidenceLookupError if neither adapter finds a candidate."""
    import urllib.parse

    openalex_url = (f"{OPENALEX_SOURCES_URL}?search={urllib.parse.quote(query)}"
                     f"&per-page=1&mailto={urllib.parse.quote(mailto)}")
    try:
        data = client.get_json(openalex_url)
        results = data.get("results") or []
        if results:
            evidence = _openalex_to_evidence(results[0])
            evidence.checked_at = _now_iso()
            return evidence
    except HttpError:
        pass

    crossref_url = (f"{CROSSREF_JOURNALS_URL}?query={urllib.parse.quote(query)}"
                     f"&rows=1&mailto={urllib.parse.quote(mailto)}")
    try:
        data = client.get_json(crossref_url)
        items = (data.get("message") or {}).get("items") or []
        if items:
            evidence = _crossref_to_evidence(items[0])
            evidence.checked_at = _now_iso()
            return evidence
    except HttpError:
        pass

    raise EvidenceLookupError(f"no journal found for query: {query!r} in OpenAlex or Crossref")


def lookup_by_issn(client: HttpClient, issn: str, mailto: str = DEFAULT_MAILTO) -> JournalEvidence:
    """Exact ISSN lookup via OpenAlex Sources (issn_l or issn array)."""
    import urllib.parse

    url = f"{OPENALEX_SOURCES_URL}/issn:{urllib.parse.quote(issn)}?mailto={urllib.parse.quote(mailto)}"
    try:
        record = client.get_json(url)
        if record.get("id"):
            evidence = _openalex_to_evidence(record)
            evidence.checked_at = _now_iso()
            return evidence
    except HttpError:
        pass
    raise EvidenceLookupError(f"no journal found for ISSN: {issn!r}")
