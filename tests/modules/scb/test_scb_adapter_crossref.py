import json
import os
import sys
import unittest


from scb.adapters.crossref import CrossrefAdapter, parse_work
from scb.http_client import HttpClient, HttpResponse

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "crossref")


def _load_fixture(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestParseWork(unittest.TestCase):
    def setUp(self):
        self.data = _load_fixture("work_sample.json")

    def test_basic_fields(self):
        rec = parse_work(self.data)
        self.assertEqual(rec.identifiers.doi, "10.1234/example.5678")
        self.assertEqual(rec.title, "Institutional Mechanisms and Policy Diffusion")
        self.assertEqual(rec.publication_year, 2023)
        self.assertEqual(rec.publication_date, "2023-04-15")
        self.assertEqual(len(rec.authors), 2)
        self.assertEqual(rec.authors[0]["name"], "Jane Doe")

    def test_license_marked_verified_when_present(self):
        rec = parse_work(self.data)
        self.assertTrue(rec.access.license_verified)
        self.assertEqual(rec.access.license_source, "crossref")

    def test_jats_tags_stripped_from_abstract(self):
        rec = parse_work(self.data)
        self.assertEqual(rec.abstract, "This paper examines institutional mechanisms.")

    def test_no_license_is_unverified(self):
        data = dict(self.data)
        data.pop("license")
        rec = parse_work(data)
        self.assertFalse(rec.access.license_verified)
        self.assertIsNone(rec.access.reuse_license)


class TestCrossrefAdapterCapabilities(unittest.TestCase):
    def test_declares_only_supported_capabilities(self):
        adapter = CrossrefAdapter(http_client=HttpClient(user_agent="test/1.0"))
        caps = adapter.capabilities.as_list()
        self.assertIn("search", caps)
        self.assertIn("lookup_by_doi", caps)
        self.assertNotIn("lookup_by_pmid", caps)
        self.assertNotIn("abstract", caps)  # Crossref rarely deposits abstracts; not a reliable capability


class TestCrossrefAdapterSearch(unittest.TestCase):
    def test_search_parses_message_items(self):
        work = _load_fixture("work_sample.json")
        body = json.dumps({"message": {"items": [work]}}).encode("utf-8")

        def fake_transport(url, headers, timeout):
            self.assertIn("api.crossref.org/works", url)
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = CrossrefAdapter(http_client=client)
        results = adapter.search("institutional mechanisms")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].identifiers.doi, "10.1234/example.5678")

    def test_lookup_by_doi_parses_message(self):
        work = _load_fixture("work_sample.json")
        body = json.dumps({"message": work}).encode("utf-8")

        def fake_transport(url, headers, timeout):
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = CrossrefAdapter(http_client=client)
        rec = adapter.lookup_by_doi("10.1234/example.5678")
        self.assertIsNotNone(rec)
        self.assertEqual(rec.title, "Institutional Mechanisms and Policy Diffusion")


if __name__ == "__main__":
    unittest.main()
