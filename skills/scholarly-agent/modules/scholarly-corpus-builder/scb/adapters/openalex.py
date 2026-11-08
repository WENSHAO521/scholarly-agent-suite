"""OpenAlex adapter (PART III §3). Broad scholarly discovery, DOI
enrichment, OA-location and version discovery. Anonymous access remains
possible; OPENALEX_API_KEY is optional (never embedded).
"""

from __future__ import annotations

import os
import urllib.parse
from typing import Any, Dict, List, Optional

from scb.adapters.base import AdapterCapabilities, BaseAdapter
from scb.records import Access, CanonicalRecord, Identifiers, ProvenanceEntry

BASE_URL = "https://api.openalex.org"

# NOTE: "host_venue" was a valid OpenAlex select field historically but
# is REJECTED by the live API as of 2026-09 (superseded by
# primary_location/sources) — confirmed live; do not re-add it.
# parse_work() already falls back to primary_location.source, so no
# other change was needed once this field was removed.
_DEFAULT_SELECT = (
    "id,doi,title,display_name,publication_year,publication_date,type,"
    "primary_location,best_oa_location,locations,open_access,authorships,"
    "abstract_inverted_index,concepts,biblio"
)


def reconstruct_abstract(inverted_index: Optional[Dict[str, List[int]]]) -> Optional[str]:
    """OpenAlex stores abstracts as {word: [positions]} to respect
    publisher redistribution limits; reconstruct plain text from it."""
    if not inverted_index:
        return None
    positions: List[tuple] = []
    for word, idxs in inverted_index.items():
        for idx in idxs:
            positions.append((idx, word))
    positions.sort(key=lambda p: p[0])
    return " ".join(word for _, word in positions)


def parse_work(data: Dict[str, Any]) -> CanonicalRecord:
    openalex_id = (data.get("id") or "").rsplit("/", 1)[-1] or None
    doi = data.get("doi")
    if doi:
        doi = doi.replace("https://doi.org/", "").lower()

    authors = []
    for a in data.get("authorships", []) or []:
        author = a.get("author") or {}
        authors.append({"name": author.get("display_name"), "openalex_author_id": (author.get("id") or "").rsplit("/", 1)[-1] or None})

    biblio = data.get("biblio") or {}
    host_venue = data.get("host_venue") or (data.get("primary_location") or {}).get("source") or {}
    open_access = data.get("open_access") or {}
    best_oa = data.get("best_oa_location") or {}

    record = CanonicalRecord(
        record_id="openalex:%s" % (openalex_id or doi or data.get("title", "")[:40]),
        title=data.get("title") or data.get("display_name"),
        authors=authors,
        publication_year=data.get("publication_year"),
        publication_date=data.get("publication_date"),
        venue=host_venue.get("display_name") if host_venue else None,
        publisher=host_venue.get("publisher") if host_venue else None,
        volume=biblio.get("volume"),
        issue=biblio.get("issue"),
        pages=(
            "%s-%s" % (biblio.get("first_page"), biblio.get("last_page"))
            if biblio.get("first_page") and biblio.get("last_page")
            else None
        ),
        work_type=data.get("type"),
        identifiers=Identifiers(doi=doi, openalex_id=openalex_id, issn=list(host_venue.get("issn") or [])),
        abstract=reconstruct_abstract(data.get("abstract_inverted_index")),
        keywords=[c.get("display_name") for c in (data.get("concepts") or []) if c.get("display_name")],
        access=Access(
            is_oa=open_access.get("is_oa"),
            oa_status=open_access.get("oa_status"),
            reuse_license=best_oa.get("license"),
            license_source="openalex" if best_oa.get("license") else None,
            license_verified=False,
            best_url=best_oa.get("url") or open_access.get("oa_url"),
            pdf_url=best_oa.get("pdf_url"),
            version=best_oa.get("version"),
        ),
    )
    for loc in data.get("locations", []) or []:
        record.versions.append(
            {
                "is_oa": loc.get("is_oa"),
                "url": loc.get("landing_page_url"),
                "pdf_url": loc.get("pdf_url"),
                "version": loc.get("version"),
                "license": loc.get("license"),
                "source_type": (loc.get("source") or {}).get("type"),
            }
        )
    record.add_provenance(ProvenanceEntry(adapter="openalex", operation="parse_work", source_identifier=openalex_id, verification="VERIFIED" if openalex_id else "NEEDS_CHECK"))
    return record


class OpenAlexAdapter(BaseAdapter):
    name = "openalex"
    capabilities = AdapterCapabilities(
        search=True,
        lookup=True,
        lookup_by_doi=True,
        abstract=True,
        locations=True,
        fulltext_pointer=True,
        version_metadata=True,
        journal_metadata=True,
    )

    def __init__(self, http_client, cache=None, mailto: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(http_client, cache)
        self.mailto = mailto or os.environ.get("OPENALEX_MAILTO")
        self.api_key = api_key or os.environ.get("OPENALEX_API_KEY")

    def _authed_url(self, url: str) -> str:
        params = []
        if self.mailto:
            params.append("mailto=%s" % urllib.parse.quote(self.mailto))
        if self.api_key:
            params.append("api_key=%s" % urllib.parse.quote(self.api_key))
        if not params:
            return url
        sep = "&" if "?" in url else "?"
        return url + sep + "&".join(params)

    def search(self, query: str, per_page: int = 25, cursor: str = "*", bypass_cache: bool = False) -> List[CanonicalRecord]:
        self._require("search")
        url = "%s/works?search=%s&select=%s&per-page=%d&cursor=%s" % (
            BASE_URL,
            urllib.parse.quote(query),
            _DEFAULT_SELECT,
            per_page,
            urllib.parse.quote(cursor),
        )
        data = self._cached_get_json("search", self._authed_url(url), {"query": query, "per_page": per_page, "cursor": cursor}, bypass_cache)
        return [parse_work(w) for w in data.get("results", [])]

    def lookup_by_doi(self, doi: str, bypass_cache: bool = False) -> Optional[CanonicalRecord]:
        self._require("lookup_by_doi")
        url = "%s/works/https://doi.org/%s" % (BASE_URL, doi)
        try:
            data = self._cached_get_json("lookup_by_doi", self._authed_url(url), {"doi": doi}, bypass_cache)
        except Exception:
            return None
        return parse_work(data)
