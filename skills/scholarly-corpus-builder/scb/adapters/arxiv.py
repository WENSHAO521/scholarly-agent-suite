"""arXiv adapter (PART III §7). Official machine-readable Atom feed
discovery. Versions (v1, v2, ...) are treated as one work, not separate
works — see scb.identifiers.normalize_arxiv.
"""

from __future__ import annotations

import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Optional

from scb.adapters.base import AdapterCapabilities, BaseAdapter
from scb.identifiers import normalize_arxiv
from scb.records import Access, CanonicalRecord, Identifiers, ProvenanceEntry

BASE_URL = "https://export.arxiv.org/api/query"

_NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
    "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
}


def _text(el, path) -> Optional[str]:
    found = el.find(path, _NS)
    if found is None or found.text is None:
        return None
    return " ".join(found.text.split())


def parse_entry(entry: ET.Element) -> CanonicalRecord:
    raw_id = _text(entry, "atom:id") or ""
    arxiv_full = raw_id.rsplit("/abs/", 1)[-1] if "/abs/" in raw_id else raw_id
    parsed = normalize_arxiv(arxiv_full)
    base_id = parsed.base if parsed else arxiv_full

    authors = []
    for author_el in entry.findall("atom:author", _NS):
        name = _text(author_el, "atom:name")
        if name:
            authors.append({"name": name})

    categories = [c.get("term") for c in entry.findall("atom:category", _NS) if c.get("term")]
    doi = _text(entry, "arxiv:doi")
    journal_ref = _text(entry, "arxiv:journal_ref")

    pdf_url = None
    for link in entry.findall("atom:link", _NS):
        if link.get("title") == "pdf":
            pdf_url = link.get("href")

    published = _text(entry, "atom:published")
    pub_year = None
    if published:
        try:
            pub_year = int(published[:4])
        except ValueError:
            pub_year = None

    record = CanonicalRecord(
        record_id="arxiv:%s" % base_id,
        title=_text(entry, "atom:title"),
        authors=authors,
        publication_year=pub_year,
        publication_date=published[:10] if published else None,
        venue=journal_ref,
        work_type="preprint",
        identifiers=Identifiers(doi=doi.lower() if doi else None, arxiv_id=base_id),
        abstract=_text(entry, "atom:summary"),
        subjects=categories,
        access=Access(
            is_oa=True,
            oa_status="green",
            best_url=raw_id or None,
            pdf_url=pdf_url,
            version=parsed.versioned if parsed else None,
        ),
    )
    if parsed and parsed.version:
        record.versions.append({"kind": "preprint", "is_oa": True, "url": raw_id, "version": "v%d" % parsed.version})
    record.add_provenance(ProvenanceEntry(adapter="arxiv", operation="parse_entry", source_identifier=base_id, verification="VERIFIED"))
    return record


class ArxivAdapter(BaseAdapter):
    name = "arxiv"
    capabilities = AdapterCapabilities(
        search=True,
        lookup=True,
        lookup_by_arxiv=True,
        abstract=True,
        version_metadata=True,
    )

    def search(self, query: str, max_results: int = 25, start: int = 0, bypass_cache: bool = False) -> List[CanonicalRecord]:
        self._require("search")
        url = "%s?search_query=%s&start=%d&max_results=%d" % (
            BASE_URL,
            urllib.parse.quote(query),
            start,
            max_results,
        )
        text = self._cached_get_text("search", url, {"query": query, "start": start, "max_results": max_results}, bypass_cache)
        root = ET.fromstring(text)
        return [parse_entry(e) for e in root.findall("atom:entry", _NS)]

    def lookup_by_arxiv(self, arxiv_id: str, bypass_cache: bool = False) -> Optional[CanonicalRecord]:
        self._require("lookup_by_arxiv")
        parsed = normalize_arxiv(arxiv_id)
        base_id = parsed.base if parsed else arxiv_id
        url = "%s?id_list=%s" % (BASE_URL, urllib.parse.quote(base_id))
        try:
            text = self._cached_get_text("lookup_by_arxiv", url, {"id": base_id}, bypass_cache)
        except Exception:
            return None
        root = ET.fromstring(text)
        entries = root.findall("atom:entry", _NS)
        if not entries:
            return None
        return parse_entry(entries[0])
