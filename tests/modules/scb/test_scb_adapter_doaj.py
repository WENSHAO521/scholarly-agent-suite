import json
import os
import sys
import unittest


from scb.adapters.doaj import DoajAdapter, parse_article, parse_journal
from scb.http_client import HttpClient, HttpResponse

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "doaj")


def _load_fixture(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestParseArticle(unittest.TestCase):
    def setUp(self):
        self.item = _load_fixture("article_search_sample.json")["results"][0]

    def test_basic_fields(self):
        rec = parse_article(self.item)
        self.assertEqual(rec.identifiers.doi, "10.7777/example.1111")
        self.assertEqual(rec.title, "Open Access Patterns in Regional Economics")
        self.assertEqual(rec.venue, "Regional Economics Open Journal")

    def test_journal_license_never_written_into_article_access(self):
        """The critical DOAJ trap this adapter must avoid: a journal
        stating 'we publish under CC BY' does not verify this specific
        article's content license."""
        rec = parse_article(self.item)
        self.assertIsNone(rec.access.reuse_license)
        self.assertFalse(rec.access.license_verified)

    def test_journal_license_recorded_as_conflict_note_not_silently_dropped(self):
        rec = parse_article(self.item)
        self.assertTrue(any(c["field"] == "reuse_license" for c in rec.conflicts))

    def test_is_oa_true_since_doaj_only_indexes_oa_journals(self):
        rec = parse_article(self.item)
        self.assertTrue(rec.access.is_oa)


class TestParseJournal(unittest.TestCase):
    def test_journal_metadata_kept_separate(self):
        item = _load_fixture("journal_search_sample.json")["results"][0]
        journal = parse_journal(item)
        self.assertEqual(journal["title"], "Regional Economics Open Journal")
        self.assertIn("2222-3333", journal["issns"])
        self.assertEqual(journal["license"][0]["type"], "CC BY")


class TestDoajAdapter(unittest.TestCase):
    def test_search_parses_results(self):
        body = json.dumps(_load_fixture("article_search_sample.json")).encode("utf-8")

        def fake_transport(url, headers, timeout):
            self.assertIn("doaj.org/api/search/articles", url)
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = DoajAdapter(http_client=client)
        results = adapter.search("open access regional economics")
        self.assertEqual(len(results), 1)

    def test_journal_metadata_by_issn(self):
        body = json.dumps(_load_fixture("journal_search_sample.json")).encode("utf-8")

        def fake_transport(url, headers, timeout):
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = DoajAdapter(http_client=client)
        journal = adapter.journal_metadata_by_issn("2222-3333")
        self.assertIsNotNone(journal)
        self.assertEqual(journal["publisher"], "Open Regional Press")


if __name__ == "__main__":
    unittest.main()
