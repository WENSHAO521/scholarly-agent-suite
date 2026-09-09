"""Crossref adapter (PART III §4). DOI authority and canonical
bibliographic metadata. CROSSREF_MAILTO is optional but recommended (puts
requests in Crossref's "polite pool").
"""

from __future__ import annotations

import os
import re
import urllib.parse
from typing import Any, Dict, List, Optional

from scb.adapters.base import AdapterCapabilities, BaseAdapter
from scb.records import Access, CanonicalRecord, Identifiers, ProvenanceEntry

BASE_URL = "https://api.crossref.org"

_JATS_TAG_RE = re.compile(r"</?jats:[a-zA-Z0-9]+[^>]*>")


def _strip_jats(abstract: Optional[str]) -> Optional[str]:
    """Crossref deposits abstracts wrapped in JATS XML tags; strip them
    for plain-text use while leaving non-JATS abstracts untouched."""
    if not abstract:
        return None
    text = _JATS_TAG_RE.sub("", abstract).strip()
    return text or None


def _date_from_parts(date_field: Optional[Dict[str, Any]]) -> Optional[str]:
    if not date_field:
        return None
    parts = date_field.get("date-parts")
    if not parts or not parts[0]:
        return None
    p = parts[0]
    if len(p) == 3:
        return "%04d-%02d-%02d" % tuple(p)
    if len(p) == 2:
        return "%04d-%02d" % tuple(p)
    if len(p) == 1:
        return "%04d" % p[0]
    return None


def parse_work(item: Dict[str, Any]) -> CanonicalRecord:
    doi = (item.get("DOI") or "").lower() or None
    authors = []
    for a in item.get("author", []) or []:
        given = a.get("given", "")
        family = a.get("family", "")
        name = (given + " " + family).strip() or a.get("name")
        authors.append({"name": name, "orcid": a.get("ORCID")})

    date_field = item.get("published") or item.get("published-print") or item.get("published-online") or item.get("issued")
    pub_date = _date_from_parts(date_field)
    pub_year = None
    if pub_date:
        try:
            pub_year = int(pub_date[:4])
        except ValueError:
            pub_year = None

    licenses = item.get("license") or []
    reuse_license = licenses[0].get("URL") if licenses else None

    titles = item.get("title") or []
    container = item.get("container-title") or []

    record = CanonicalRecord(
        record_id="crossref:%s" % (doi or (titles[0][:40] if titles else "unknown")),
        title=titles[0] if titles else None,
        authors=authors,
        publication_year=pub_year,
        publication_date=pub_date,
        venue=container[0] if container else None,
        publisher=item.get("publisher"),
        volume=item.get("volume"),
        issue=item.get("issue"),
        pages=item.get("page"),
        work_type=item.get("type"),
        identifiers=Identifiers(doi=doi, issn=list(item.get("ISSN") or [])),
        abstract=_strip_jats(item.get("abstract")),
        access=Access(
            reuse_license=reuse_license,
            license_source="crossref" if reuse_license else None,
            license_verified=bool(reuse_license),
            best_url=item.get("URL"),
        ),
    )
    record.add_provenance(
        ProvenanceEntry(adapter="crossref", operation="parse_work", source_identifier=doi, verification="VERIFIED" if doi else "NEEDS_CHECK")
    )
    return record


class CrossrefAdapter(BaseAdapter):
    name = "crossref"
    capabilities = AdapterCapabilities(
        search=True,
        lookup=True,
        lookup_by_doi=True,
        journal_metadata=True,
    )

    def __init__(self, http_client, cache=None, mailto: Optional[str] = None):
        super().__init__(http_client, cache)
        self.mailto = mailto or os.environ.get("CROSSREF_MAILTO")

    def _authed_url(self, url: str) -> str:
        if not self.mailto:
            return url
        sep = "&" if "?" in url else "?"
        return url + sep + "mailto=" + urllib.parse.quote(self.mailto)

    def search(self, query: str, rows: int = 25, cursor: str = "*", bypass_cache: bool = False) -> List[CanonicalRecord]:
        self._require("search")
        url = "%s/works?query=%s&rows=%d&cursor=%s" % (BASE_URL, urllib.parse.quote(query), rows, urllib.parse.quote(cursor))
        data = self._cached_get_json("search", self._authed_url(url), {"query": query, "rows": rows, "cursor": cursor}, bypass_cache)
        items = (data.get("message") or {}).get("items", [])
        return [parse_work(item) for item in items]

    def lookup_by_doi(self, doi: str, bypass_cache: bool = False) -> Optional[CanonicalRecord]:
        self._require("lookup_by_doi")
        url = "%s/works/%s" % (BASE_URL, urllib.parse.quote(doi, safe=""))
        try:
            data = self._cached_get_json("lookup_by_doi", self._authed_url(url), {"doi": doi}, bypass_cache)
        except Exception:
            return None
        message = data.get("message")
        if not message:
            return None
        return parse_work(message)
