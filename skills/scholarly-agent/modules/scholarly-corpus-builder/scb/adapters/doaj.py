"""DOAJ adapter (PART III §8). Structured DOAJ metadata: OA journal
identity/verification and article metadata.

Critical distinction this module exists to enforce: DOAJ journal-level
license metadata (bibjson.journal.license — "this journal publishes under
CC BY") describes the *journal's stated policy*, not a verified per
article license. This adapter therefore never writes a journal license
into an article record's access.reuse_license — see parse_article()
below and `references/copyright-boundary.md`.
"""

from __future__ import annotations

import urllib.parse
from typing import Any, Dict, List, Optional

from scb.adapters.base import AdapterCapabilities, BaseAdapter
from scb.records import Access, CanonicalRecord, Identifiers, ProvenanceEntry

BASE_URL = "https://doaj.org/api"


def parse_journal_license(bibjson_journal: Dict[str, Any]) -> List[Dict[str, str]]:
    """Journal-level stated license policy — metadata about the venue,
    not a verified claim about any specific article's content license."""
    return [
        {"type": lic.get("type"), "url": lic.get("url")}
        for lic in (bibjson_journal.get("license") or [])
        if lic.get("type")
    ]


def parse_article(item: Dict[str, Any]) -> CanonicalRecord:
    bibjson = item.get("bibjson", {})
    journal = bibjson.get("journal", {}) or {}

    identifiers = {i.get("type"): i.get("id") for i in bibjson.get("identifier", []) or []}
    doi = (identifiers.get("doi") or "").lower() or None
    issn = [v for k, v in identifiers.items() if k in ("issn", "eissn") and v]

    authors = [{"name": a.get("name")} for a in bibjson.get("author", []) or [] if a.get("name")]

    fulltext_url = None
    for link in bibjson.get("link", []) or []:
        if link.get("type") == "fulltext":
            fulltext_url = link.get("url")
            break

    year = bibjson.get("year")
    pub_year = int(year) if year and str(year).isdigit() else None

    journal_license = parse_journal_license(journal)

    record = CanonicalRecord(
        record_id="doaj:%s" % item.get("id"),
        title=bibjson.get("title"),
        authors=authors,
        publication_year=pub_year,
        venue=journal.get("title"),
        publisher=journal.get("publisher"),
        volume=journal.get("volume"),
        issue=journal.get("number"),
        identifiers=Identifiers(doi=doi, issn=issn or list(journal.get("issns") or [])),
        abstract=bibjson.get("abstract"),
        access=Access(
            is_oa=True,  # DOAJ only indexes fully-OA journals
            oa_status="doaj_indexed",
            # Deliberately NOT set from journal_license — see module docstring.
            reuse_license=None,
            license_verified=False,
            best_url=fulltext_url,
        ),
    )
    if journal_license:
        record.conflicts.append(
            {
                "field": "reuse_license",
                "note": "journal states license policy %r at the venue level; this is not a "
                "verified per-article license — confirm on the article itself before reuse" % journal_license,
            }
        )
    record.add_provenance(ProvenanceEntry(adapter="doaj", operation="parse_article", source_identifier=item.get("id"), verification="NEEDS_CHECK"))
    return record


def parse_journal(item: Dict[str, Any]) -> Dict[str, Any]:
    """Journal-level metadata for the journal_metadata capability — kept
    entirely separate from any article's access/license fields."""
    bibjson = item.get("bibjson", {})
    return {
        "title": bibjson.get("title"),
        "issns": [i.get("id") for i in bibjson.get("identifier", []) or [] if i.get("type") in ("pissn", "eissn")],
        "publisher": (bibjson.get("publisher") or {}).get("name"),
        "license": parse_journal_license(bibjson),
        "oa_start": (bibjson.get("oa_start") or {}).get("year"),
        "doaj_seal": bibjson.get("boai") or item.get("admin", {}).get("seal"),
    }


class DoajAdapter(BaseAdapter):
    name = "doaj"
    capabilities = AdapterCapabilities(
        search=True,
        lookup_by_doi=True,
        journal_metadata=True,
    )

    def search(self, query: str, page: int = 1, page_size: int = 25, bypass_cache: bool = False) -> List[CanonicalRecord]:
        self._require("search")
        url = "%s/search/articles/%s?page=%d&pageSize=%d" % (BASE_URL, urllib.parse.quote(query), page, page_size)
        data = self._cached_get_json("search", url, {"query": query, "page": page, "page_size": page_size}, bypass_cache)
        return [parse_article(item) for item in data.get("results", [])]

    def lookup_by_doi(self, doi: str, bypass_cache: bool = False) -> Optional[CanonicalRecord]:
        self._require("lookup_by_doi")
        results = self.search("doi:%s" % doi, page_size=1, bypass_cache=bypass_cache)
        return results[0] if results else None

    def journal_metadata_by_issn(self, issn: str, bypass_cache: bool = False) -> Optional[Dict[str, Any]]:
        self._require("journal_metadata")
        url = "%s/search/journals/issn:%s" % (BASE_URL, urllib.parse.quote(issn))
        data = self._cached_get_json("journal_by_issn", url, {"issn": issn}, bypass_cache)
        results = data.get("results", [])
        if not results:
            return None
        return parse_journal(results[0])
