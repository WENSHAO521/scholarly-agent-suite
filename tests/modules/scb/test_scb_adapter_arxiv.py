import os
import sys
import unittest
import xml.etree.ElementTree as ET


from scb.adapters.arxiv import ArxivAdapter, _NS, parse_entry
from scb.http_client import HttpClient, HttpResponse

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "arxiv")


def _load_feed():
    with open(os.path.join(FIXTURES, "feed_sample.xml"), "r", encoding="utf-8") as f:
        return f.read()


class TestParseEntry(unittest.TestCase):
    def setUp(self):
        root = ET.fromstring(_load_feed())
        self.entry = root.find("atom:entry", _NS)

    def test_basic_fields(self):
        rec = parse_entry(self.entry)
        self.assertEqual(rec.title, "Scaling Laws for Example Neural Networks")
        self.assertEqual(rec.identifiers.arxiv_id, "2301.12345")
        self.assertEqual(rec.identifiers.doi, "10.1234/arxiv.9999")
        self.assertEqual(len(rec.authors), 2)
        self.assertEqual(rec.publication_year, 2023)

    def test_version_stripped_from_base_id_but_kept_in_access_version(self):
        rec = parse_entry(self.entry)
        self.assertNotIn("v2", rec.identifiers.arxiv_id)
        self.assertEqual(rec.access.version, "2301.12345v2")

    def test_marked_open_access(self):
        rec = parse_entry(self.entry)
        self.assertTrue(rec.access.is_oa)
        self.assertIsNotNone(rec.access.pdf_url)


class TestArxivAdapter(unittest.TestCase):
    def test_search_parses_feed(self):
        body = _load_feed().encode("utf-8")

        def fake_transport(url, headers, timeout):
            self.assertIn("export.arxiv.org/api/query", url)
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = ArxivAdapter(http_client=client)
        results = adapter.search("scaling laws")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].identifiers.arxiv_id, "2301.12345")

    def test_lookup_by_arxiv_versions_treated_as_one_work(self):
        body = _load_feed().encode("utf-8")

        def fake_transport(url, headers, timeout):
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = ArxivAdapter(http_client=client)
        rec_v1 = adapter.lookup_by_arxiv("2301.12345v1")
        rec_v3 = adapter.lookup_by_arxiv("2301.12345v3")
        self.assertEqual(rec_v1.identifiers.arxiv_id, rec_v3.identifiers.arxiv_id)


if __name__ == "__main__":
    unittest.main()
