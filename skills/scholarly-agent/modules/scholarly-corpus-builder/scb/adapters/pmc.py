"""PMC adapter (PART III §6).

IMPORTANT — verified live on 2026-09-09: NCBI fully decommissioned the
legacy per-article "PMC OA Web Service" REST API (oa.fcgi) in August
2026, replacing it with bulk PMC Cloud Service (AWS S3) datasets. There
is no longer a lightweight per-PMCID REST call that returns license/
full-text pointers — only bulk dataset downloads, which this Skill
deliberately does not implement (PART LXXIX "no heavy infrastructure";
PART LXXIII targets 10-500 records, not bulk corpus mirroring).

What this adapter still does, and does live (verified against the real
NCBI ID Converter API): resolve PMID <-> PMCID <-> DOI. That's a
genuinely useful, still-functioning capability for identifier
resolution and dedup. It no longer claims to determine OA status,
license, or a full-text pointer for a PMCID — callers needing that
should rely on OpenAlex locations or Crossref license data instead (see
scb/oa_resolver.py's resolution sequence, which already prefers those
and only turns to PMC for the identifier cross-reference).
"""

from __future__ import annotations

import urllib.parse
from typing import Any, Dict, List, Optional

from scb.adapters.base import AdapterCapabilities, BaseAdapter
from scb.identifiers import normalize_doi, normalize_pmcid, normalize_pmid
from scb.records import Access, CanonicalRecord, Identifiers, ProvenanceEntry

IDCONV_URL = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"


def parse_idconv_record(rec: Dict[str, Any]) -> CanonicalRecord:
    pmcid = normalize_pmcid(rec.get("pmcid"))
    pmid = normalize_pmid(str(rec["pmid"])) if rec.get("pmid") else None
    doi = normalize_doi(rec.get("doi"))

    canonical = CanonicalRecord(
        record_id="pmc:%s" % (pmcid or pmid or doi or "unknown"),
        identifiers=Identifiers(pmcid=pmcid, pmid=pmid, doi=doi),
        # Deliberately not asserted: this adapter no longer has a lawful,
        # lightweight way to determine OA status/license for a PMCID —
        # see module docstring. Leave Access fields at their honest
        # "unknown" defaults rather than guessing.
        access=Access(),
    )
    canonical.add_provenance(
        ProvenanceEntry(
            adapter="pmc",
            operation="idconv",
            source_identifier=pmcid or pmid or doi,
            verification="VERIFIED" if pmcid else "NEEDS_CHECK",
        )
    )
    return canonical


class PMCAdapter(BaseAdapter):
    name = "pmc"
    capabilities = AdapterCapabilities(
        lookup_by_pmcid=True,
        lookup_by_pmid=True,
        lookup_by_doi=True,
    )

    def __init__(self, http_client, cache=None, tool: Optional[str] = None, email: Optional[str] = None):
        super().__init__(http_client, cache)
        self.tool = tool
        self.email = email

    def _idconv(self, identifier: str, bypass_cache: bool = False) -> Optional[CanonicalRecord]:
        params = ["ids=%s" % urllib.parse.quote(identifier), "format=json"]
        if self.tool:
            params.append("tool=%s" % urllib.parse.quote(self.tool))
        if self.email:
            params.append("email=%s" % urllib.parse.quote(self.email))
        url = "%s?%s" % (IDCONV_URL, "&".join(params))
        try:
            data = self._cached_get_json("idconv", url, {"id": identifier}, bypass_cache)
        except Exception:
            return None
        records = data.get("records", [])
        if not records or records[0].get("status") == "error":
            return None
        return parse_idconv_record(records[0])

    def lookup_by_pmcid(self, pmcid: str, bypass_cache: bool = False) -> Optional[CanonicalRecord]:
        self._require("lookup_by_pmcid")
        normalized = normalize_pmcid(pmcid)
        if not normalized:
            return None
        return self._idconv(normalized, bypass_cache)

    def lookup_by_pmid(self, pmid: str, bypass_cache: bool = False) -> Optional[CanonicalRecord]:
        self._require("lookup_by_pmid")
        return self._idconv(pmid, bypass_cache)

    def lookup_by_doi(self, doi: str, bypass_cache: bool = False) -> Optional[CanonicalRecord]:
        self._require("lookup_by_doi")
        return self._idconv(doi, bypass_cache)
