"""Common adapter abstraction (PART III §1) shared by every source
adapter.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import List, Optional

from scb.cache import FileCache, build_key
from scb.http_client import AVAILABLE, HttpClient, HttpError, classify_state
from scb.records import CanonicalRecord

CAPABILITY_NAMES = (
    "search",
    "lookup",
    "lookup_by_doi",
    "lookup_by_pmid",
    "lookup_by_pmcid",
    "lookup_by_arxiv",
    "abstract",
    "locations",
    "fulltext_pointer",
    "version_metadata",
    "journal_metadata",
)


@dataclass
class AdapterCapabilities:
    search: bool = False
    lookup: bool = False
    lookup_by_doi: bool = False
    lookup_by_pmid: bool = False
    lookup_by_pmcid: bool = False
    lookup_by_arxiv: bool = False
    abstract: bool = False
    locations: bool = False
    fulltext_pointer: bool = False
    version_metadata: bool = False
    journal_metadata: bool = False

    def as_list(self) -> List[str]:
        return [f.name for f in fields(self) if getattr(self, f.name)]


class CapabilityNotSupported(NotImplementedError):
    def __init__(self, adapter_name: str, capability: str):
        super().__init__("%s does not support capability %r" % (adapter_name, capability))
        self.adapter_name = adapter_name
        self.capability = capability


class BaseAdapter:
    name: str = "base"
    capabilities: AdapterCapabilities = AdapterCapabilities()

    def __init__(self, http_client: HttpClient, cache: Optional[FileCache] = None):
        self.http_client = http_client
        self.cache = cache
        self._last_error: Optional[HttpError] = None

    def state(self) -> str:
        return AVAILABLE if self._last_error is None else classify_state(self._last_error)

    def _require(self, capability: str) -> None:
        if not getattr(self.capabilities, capability, False):
            raise CapabilityNotSupported(self.name, capability)

    def _cached_get_json(self, operation: str, url: str, params: dict, bypass_cache: bool = False) -> dict:
        key = build_key(self.name, operation, params)
        if self.cache is not None:
            cached = self.cache.get(self.name, key, bypass=bypass_cache)
            if cached is not None:
                return cached
        try:
            resp = self.http_client.get(url)
        except HttpError as e:
            self._last_error = e
            raise
        self._last_error = None
        data = resp.json()
        if self.cache is not None:
            self.cache.set(self.name, key, data)
        return data

    def _cached_get_text(self, operation: str, url: str, params: dict, bypass_cache: bool = False) -> str:
        key = build_key(self.name, operation, params)
        if self.cache is not None:
            cached = self.cache.get(self.name, key, bypass=bypass_cache)
            if cached is not None:
                return cached
        try:
            resp = self.http_client.get(url)
        except HttpError as e:
            self._last_error = e
            raise
        self._last_error = None
        text = resp.text()
        if self.cache is not None:
            self.cache.set(self.name, key, text)
        return text

    # Every concrete adapter overrides only the operations it declares in
    # `capabilities`; the rest raise CapabilityNotSupported via _require().
    def search(self, query: str, **kwargs) -> List[CanonicalRecord]:
        self._require("search")
        raise NotImplementedError

    def lookup_by_doi(self, doi: str) -> Optional[CanonicalRecord]:
        self._require("lookup_by_doi")
        raise NotImplementedError

    def lookup_by_pmid(self, pmid: str) -> Optional[CanonicalRecord]:
        self._require("lookup_by_pmid")
        raise NotImplementedError

    def lookup_by_pmcid(self, pmcid: str) -> Optional[CanonicalRecord]:
        self._require("lookup_by_pmcid")
        raise NotImplementedError

    def lookup_by_arxiv(self, arxiv_id: str) -> Optional[CanonicalRecord]:
        self._require("lookup_by_arxiv")
        raise NotImplementedError
