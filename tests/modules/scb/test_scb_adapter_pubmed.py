import json
import os
import sys
import unittest
import xml.etree.ElementTree as ET


from scb.adapters.pubmed import PubMedAdapter, parse_article
from scb.http_client import HttpClient, HttpResponse

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "pubmed")


def _load_text(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as f:
        return f.read()


class TestParseArticle(unittest.TestCase):
    def setUp(self):
        root = ET.fromstring(_load_text("efetch_sample.xml"))
        self.article = root.find("PubmedArticle")

    def test_basic_fields(self):
        rec = parse_article(self.article)
        self.assertEqual(rec.identifiers.pmid, "33333333")
        self.assertEqual(rec.title, "Mechanisms of Example Cellular Response")
        self.assertEqual(rec.publication_year, 2022)
        self.assertEqual(len(rec.authors), 2)

    def test_doi_and_pmcid_linked(self):
        rec = parse_article(self.article)
        self.assertEqual(rec.identifiers.doi, "10.5555/example.4321")
        self.assertEqual(rec.identifiers.pmcid, "PMC9999999")

    def test_labeled_abstract_sections_joined(self):
        rec = parse_article(self.article)
        self.assertIn("BACKGROUND:", rec.abstract)
        self.assertIn("METHODS:", rec.abstract)


class TestPubMedAdapter(unittest.TestCase):
    def test_search_esearch_then_efetch(self):
        calls = []

        def fake_transport(url, headers, timeout):
            calls.append(url)
            if "esearch.fcgi" in url:
                return HttpResponse(200, {}, _load_text("esearch_sample.json").encode("utf-8"), url)
            return HttpResponse(200, {}, _load_text("efetch_sample.xml").encode("utf-8"), url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = PubMedAdapter(http_client=client)
        results = adapter.search("example cellular response")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].identifiers.pmid, "33333333")
        self.assertEqual(len(calls), 2)

    def test_lookup_by_pmid(self):
        def fake_transport(url, headers, timeout):
            return HttpResponse(200, {}, _load_text("efetch_sample.xml").encode("utf-8"), url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = PubMedAdapter(http_client=client)
        rec = adapter.lookup_by_pmid("33333333")
        self.assertIsNotNone(rec)
        self.assertEqual(rec.identifiers.pmid, "33333333")


if __name__ == "__main__":
    unittest.main()
