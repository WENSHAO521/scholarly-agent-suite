"""PubMed adapter (PART III §5). Official NCBI E-utilities (ESearch +
EFetch). Configuration via NCBI_TOOL / NCBI_EMAIL / NCBI_API_KEY — none
hard-coded, none required for basic operation.
"""

from __future__ import annotations

import os
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Optional

from scb.adapters.base import AdapterCapabilities, BaseAdapter
from scb.records import Access, CanonicalRecord, Identifiers, ProvenanceEntry

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def _text(el, path) -> Optional[str]:
    found = el.find(path)
    if found is None or found.text is None:
        return None
    return " ".join(found.text.split())


def parse_article(article: ET.Element) -> CanonicalRecord:
    citation = article.find("MedlineCitation")
    pmid = _text(citation, "PMID")
    art = citation.find("Article")

    title = _text(art, "ArticleTitle")

    abstract_parts = []
    for ab in art.findall("Abstract/AbstractText"):
        label = ab.get("Label")
        text = " ".join((ab.text or "").split())
        if not text:
            continue
        abstract_parts.append("%s: %s" % (label, text) if label else text)
    abstract = " ".join(abstract_parts) if abstract_parts else None

    authors = []
    for a in art.findall("AuthorList/Author"):
        collective = _text(a, "CollectiveName")
        if collective:
            authors.append({"name": collective})
            continue
        last = _text(a, "LastName")
        fore = _text(a, "ForeName")
        name = " ".join(p for p in [fore, last] if p)
        if name:
            authors.append({"name": name})

    journal = art.find("Journal")
    venue = _text(journal, "Title") if journal is not None else None
    volume = _text(journal, "JournalIssue/Volume") if journal is not None else None
    issue = _text(journal, "JournalIssue/Issue") if journal is not None else None
    year = _text(journal, "JournalIssue/PubDate/Year") if journal is not None else None
    pub_year = int(year) if year and year.isdigit() else None

    doi = None
    for eloc in art.findall("ELocationID"):
        if eloc.get("EIdType") == "doi":
            doi = (eloc.text or "").strip().lower() or None

    pmcid = None
    for aid in article.findall("PubmedData/ArticleIdList/ArticleId"):
        if aid.get("IdType") == "pmc":
            pmcid = (aid.text or "").strip() or None
        if aid.get("IdType") == "doi" and not doi:
            doi = (aid.text or "").strip().lower() or None

    pub_types = [pt.text for pt in art.findall("PublicationTypeList/PublicationType") if pt.text]

    record = CanonicalRecord(
        record_id="pubmed:%s" % pmid,
        title=title,
        authors=authors,
        publication_year=pub_year,
        venue=venue,
        volume=volume,
        issue=issue,
        work_type=pub_types[0] if pub_types else None,
        identifiers=Identifiers(doi=doi, pmid=pmid, pmcid=("PMC%s" % pmcid.lstrip("PMC") if pmcid else None)),
        abstract=abstract,
        access=Access(),
    )
    record.add_provenance(ProvenanceEntry(adapter="pubmed", operation="parse_article", source_identifier=pmid, verification="VERIFIED" if pmid else "NEEDS_CHECK"))
    return record


class PubMedAdapter(BaseAdapter):
    name = "pubmed"
    capabilities = AdapterCapabilities(
        search=True,
        lookup=True,
        lookup_by_pmid=True,
        abstract=True,
    )

    def __init__(self, http_client, cache=None, tool: Optional[str] = None, email: Optional[str] = None, api_key: Optional[str] = None):
        super().__init__(http_client, cache)
        self.tool = tool or os.environ.get("NCBI_TOOL")
        self.email = email or os.environ.get("NCBI_EMAIL")
        self.api_key = api_key or os.environ.get("NCBI_API_KEY")

    def _extra_params(self) -> str:
        parts = []
        if self.tool:
            parts.append("tool=%s" % urllib.parse.quote(self.tool))
        if self.email:
            parts.append("email=%s" % urllib.parse.quote(self.email))
        if self.api_key:
            parts.append("api_key=%s" % urllib.parse.quote(self.api_key))
        return ("&" + "&".join(parts)) if parts else ""

    def _esearch(self, query: str, retmax: int, bypass_cache: bool) -> List[str]:
        url = "%s/esearch.fcgi?db=pubmed&term=%s&retmax=%d&retmode=json%s" % (
            BASE_URL,
            urllib.parse.quote(query),
            retmax,
            self._extra_params(),
        )
        data = self._cached_get_json("esearch", url, {"query": query, "retmax": retmax}, bypass_cache)
        return (data.get("esearchresult") or {}).get("idlist", [])

    def _efetch(self, pmids: List[str], bypass_cache: bool) -> List[CanonicalRecord]:
        if not pmids:
            return []
        url = "%s/efetch.fcgi?db=pubmed&id=%s&rettype=abstract&retmode=xml%s" % (
            BASE_URL,
            urllib.parse.quote(",".join(pmids)),
            self._extra_params(),
        )
        text = self._cached_get_text("efetch", url, {"ids": pmids}, bypass_cache)
        root = ET.fromstring(text)
        return [parse_article(a) for a in root.findall("PubmedArticle")]

    def search(self, query: str, retmax: int = 25, bypass_cache: bool = False) -> List[CanonicalRecord]:
        self._require("search")
        pmids = self._esearch(query, retmax, bypass_cache)
        return self._efetch(pmids, bypass_cache)

    def lookup_by_pmid(self, pmid: str, bypass_cache: bool = False) -> Optional[CanonicalRecord]:
        self._require("lookup_by_pmid")
        try:
            results = self._efetch([pmid], bypass_cache)
        except Exception:
            return None
        return results[0] if results else None
