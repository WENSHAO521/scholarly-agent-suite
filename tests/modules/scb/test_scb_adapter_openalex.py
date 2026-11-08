import json
import os
import sys
import unittest


from scb.adapters.openalex import OpenAlexAdapter, parse_work, reconstruct_abstract
from scb.http_client import HttpClient, HttpResponse

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "openalex")


def _load_fixture(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestReconstructAbstract(unittest.TestCase):
    def test_reorders_inverted_index(self):
        idx = {"world": [1], "hello": [0]}
        self.assertEqual(reconstruct_abstract(idx), "hello world")

    def test_none_for_empty(self):
        self.assertIsNone(reconstruct_abstract(None))
        self.assertIsNone(reconstruct_abstract({}))


class TestParseWork(unittest.TestCase):
    def setUp(self):
        self.data = _load_fixture("work_sample.json")

    def test_basic_fields(self):
        rec = parse_work(self.data)
        self.assertEqual(rec.title, "Institutional Mechanisms and Policy Diffusion")
        self.assertEqual(rec.identifiers.doi, "10.1234/example.5678")
        self.assertEqual(rec.identifiers.openalex_id, "W1234567890")
        self.assertEqual(rec.publication_year, 2023)
        self.assertEqual(len(rec.authors), 2)

    def test_access_does_not_equate_oa_with_unrestricted_reuse(self):
        rec = parse_work(self.data)
        self.assertTrue(rec.access.is_oa)
        # is_oa=True but reuse_license must come from the actual OA
        # location's license, not be assumed permissive.
        self.assertEqual(rec.access.reuse_license, "cc-by")

    def test_locations_captured_as_versions(self):
        rec = parse_work(self.data)
        self.assertEqual(len(rec.versions), 2)
        oa_versions = [v for v in rec.versions if v["is_oa"]]
        self.assertEqual(len(oa_versions), 1)
        self.assertEqual(oa_versions[0]["version"], "acceptedVersion")

    def test_provenance_recorded(self):
        rec = parse_work(self.data)
        self.assertEqual(rec.sources, ["openalex"])
        self.assertEqual(rec.provenance[0].verification, "VERIFIED")


class TestOpenAlexAdapterCapabilities(unittest.TestCase):
    def test_declares_only_supported_capabilities(self):
        adapter = OpenAlexAdapter(http_client=HttpClient(user_agent="test/1.0"))
        caps = adapter.capabilities.as_list()
        self.assertIn("search", caps)
        self.assertIn("lookup_by_doi", caps)
        self.assertNotIn("lookup_by_pmid", caps)
        self.assertNotIn("lookup_by_arxiv", caps)


class TestOpenAlexAdapterSearch(unittest.TestCase):
    def test_search_uses_injected_transport_and_parses_results(self):
        work = _load_fixture("work_sample.json")
        body = json.dumps({"results": [work]}).encode("utf-8")

        def fake_transport(url, headers, timeout):
            self.assertIn("api.openalex.org/works", url)
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = OpenAlexAdapter(http_client=client)
        results = adapter.search("institutional mechanisms")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].identifiers.doi, "10.1234/example.5678")


if __name__ == "__main__":
    unittest.main()
