"""Offline robustness tests (PART XCI). CI is deterministic and never
depends on live API uptime — every failure mode here is simulated via
the injectable HTTP transport.
"""

import json
import os
import sys
import unittest


from scb.adapters.arxiv import ArxivAdapter
from scb.adapters.crossref import CrossrefAdapter
from scb.adapters.doaj import DoajAdapter
from scb.adapters.openalex import OpenAlexAdapter
from scb.adapters.pmc import PMCAdapter
from scb.adapters.pubmed import PubMedAdapter
from scb.http_client import HttpClient, HttpError, HttpResponse
from scb.acquisition import CorpusRequest, acquire_corpus


def _raising_transport(status, transient=False):
    def transport(url, headers, timeout):
        raise HttpError("simulated failure", status=status, transient=transient)
    return transport


def _malformed_json_transport(url, headers, timeout):
    return HttpResponse(200, {}, b"{not valid json", url)


def _malformed_xml_transport(url, headers, timeout):
    return HttpResponse(200, {}, b"<not><valid</xml>", url)


def _empty_results_transport(url, headers, timeout):
    if "esearch" in url:
        return HttpResponse(200, {}, json.dumps({"esearchresult": {"idlist": []}}).encode("utf-8"), url)
    return HttpResponse(200, {}, json.dumps({"results": [], "message": {"items": []}}).encode("utf-8"), url)


class TestNotFoundHandling(unittest.TestCase):
    """404 / not_found must return None, not raise, for every lookup_by_* method."""

    def test_crossref_lookup_not_found(self):
        client = HttpClient(user_agent="t", transport=_raising_transport(404), sleep_fn=lambda s: None)
        adapter = CrossrefAdapter(http_client=client)
        self.assertIsNone(adapter.lookup_by_doi("10.1/x"))

    def test_openalex_lookup_not_found(self):
        client = HttpClient(user_agent="t", transport=_raising_transport(404), sleep_fn=lambda s: None)
        adapter = OpenAlexAdapter(http_client=client)
        self.assertIsNone(adapter.lookup_by_doi("10.1/x"))

    def test_arxiv_lookup_not_found(self):
        client = HttpClient(user_agent="t", transport=_raising_transport(404), sleep_fn=lambda s: None)
        adapter = ArxivAdapter(http_client=client)
        self.assertIsNone(adapter.lookup_by_arxiv("1234.5678"))

    def test_pmc_lookup_not_found(self):
        client = HttpClient(user_agent="t", transport=_raising_transport(404), sleep_fn=lambda s: None)
        adapter = PMCAdapter(http_client=client)
        self.assertIsNone(adapter.lookup_by_pmcid("PMC1"))

    def test_doaj_lookup_not_found(self):
        client = HttpClient(user_agent="t", transport=lambda url, h, t: HttpResponse(200, {}, b'{"results": []}', url), sleep_fn=lambda s: None)
        adapter = DoajAdapter(http_client=client)
        self.assertIsNone(adapter.lookup_by_doi("10.1/x"))


class TestRateLimitAndServerErrorsExhaustRetryThenSurface(unittest.TestCase):
    """A persistent 429/503 should exhaust the bounded retry policy and
    then either raise (search) or return None (lookup) — never hang,
    never silently fabricate a result."""

    def test_persistent_429_raises_after_retries_on_search(self):
        client = HttpClient(user_agent="t", transport=_raising_transport(429, transient=True), sleep_fn=lambda s: None)
        adapter = CrossrefAdapter(http_client=client)
        with self.assertRaises(HttpError):
            adapter.search("x")

    def test_persistent_503_lookup_returns_none_not_raise(self):
        client = HttpClient(user_agent="t", transport=_raising_transport(503, transient=True), sleep_fn=lambda s: None)
        adapter = CrossrefAdapter(http_client=client)
        self.assertIsNone(adapter.lookup_by_doi("10.1/x"))


class TestMalformedResponses(unittest.TestCase):
    def test_malformed_json_does_not_silently_fabricate_a_record(self):
        client = HttpClient(user_agent="t", transport=_malformed_json_transport, sleep_fn=lambda s: None)
        adapter = CrossrefAdapter(http_client=client)
        with self.assertRaises(Exception):
            adapter.search("x")

    def test_malformed_xml_does_not_silently_fabricate_a_record(self):
        client = HttpClient(user_agent="t", transport=_malformed_xml_transport, sleep_fn=lambda s: None)
        adapter = ArxivAdapter(http_client=client)
        with self.assertRaises(Exception):
            adapter.search("x")


class TestEmptyResults(unittest.TestCase):
    def test_empty_search_results_is_empty_list_not_error(self):
        client = HttpClient(user_agent="t", transport=_empty_results_transport, sleep_fn=lambda s: None)
        adapter = CrossrefAdapter(http_client=client)
        self.assertEqual(adapter.search("x"), [])

    def test_pubmed_empty_esearch_returns_empty_list(self):
        client = HttpClient(user_agent="t", transport=_empty_results_transport, sleep_fn=lambda s: None)
        adapter = PubMedAdapter(http_client=client)
        self.assertEqual(adapter.search("x"), [])


class TestAcquisitionSurvivesMixedFailures(unittest.TestCase):
    def test_acquisition_completes_with_some_adapters_down(self):
        good_client = HttpClient(
            user_agent="t",
            transport=lambda url, h, t: HttpResponse(
                200, {}, json.dumps({"message": {"items": []}}).encode("utf-8"), url
            ),
            sleep_fn=lambda s: None,
        )
        down_client = HttpClient(user_agent="t", transport=_raising_transport(503, transient=True), sleep_fn=lambda s: None)

        adapters = {
            "crossref": CrossrefAdapter(http_client=good_client),
            "openalex": OpenAlexAdapter(http_client=down_client),
        }
        request = CorpusRequest(corpus_type="journal", target="x", purpose="journal_style", target_records=5)
        result = acquire_corpus(request, adapters)
        self.assertIn("openalex", result.adapter_errors)
        self.assertEqual(result.manifest.status, "FAILED")  # zero usable — but this must be reported, not crash


if __name__ == "__main__":
    unittest.main()
