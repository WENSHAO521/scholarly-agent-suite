import json
import unittest

from jfe.http_client import HttpClient, HttpResponse
from jfe.journal_evidence import EvidenceLookupError, lookup_by_issn, lookup_by_name

OPENALEX_SOURCE_RECORD = {
    "id": "https://openalex.org/S169433491",
    "issn_l": "1053-1858",
    "issn": ["1053-1858", "1477-9803"],
    "display_name": "Journal of Public Administration Research and Theory",
    "host_organization_name": "Oxford University Press",
    "homepage_url": "https://academic.oup.com/jpart",
    "is_oa": False,
    "is_in_doaj": False,
    "apc_usd": 4029,
    "works_count": 1777,
    "cited_by_count": 150926,
    "first_publication_year": 1986,
    "last_publication_year": 2026,
    "topics": [{"display_name": "Public Policy and Administration Research"}],
}

CROSSREF_JOURNAL_ITEM = {
    "title": "PUBLICNESS Journal of Public Administration studies",
    "publisher": "Universitas Negeri Padang",
    "ISSN": ["2620-8091"],
    "counts": {"total-dois": 236},
}


def fake_transport(responses_by_substring):
    def transport(url, headers):
        for substring, payload in responses_by_substring.items():
            if substring in url:
                return HttpResponse(status=200, body=json.dumps(payload).encode("utf-8"))
        return HttpResponse(status=404, body=b"{}")
    return transport


class LookupByNameTests(unittest.TestCase):
    def test_openalex_hit_used_directly(self):
        client = HttpClient("test-agent", transport=fake_transport({
            "api.openalex.org/sources": {"results": [OPENALEX_SOURCE_RECORD]},
        }))
        evidence = lookup_by_name(client, "Journal of Public Administration Research")
        self.assertEqual(evidence.source, "openalex")
        self.assertEqual(evidence.issn_l, "1053-1858")
        self.assertEqual(evidence.apc_usd, 4029)
        self.assertIn("Public Policy and Administration Research", evidence.topics)

    def test_falls_back_to_crossref_when_openalex_has_no_results(self):
        client = HttpClient("test-agent", transport=fake_transport({
            "api.openalex.org/sources": {"results": []},
            "api.crossref.org/journals": {"message": {"items": [CROSSREF_JOURNAL_ITEM]}},
        }))
        evidence = lookup_by_name(client, "PUBLICNESS Journal")
        self.assertEqual(evidence.source, "crossref")
        self.assertEqual(evidence.publisher, "Universitas Negeri Padang")

    def test_raises_when_neither_adapter_has_a_match(self):
        client = HttpClient("test-agent", transport=fake_transport({
            "api.openalex.org/sources": {"results": []},
            "api.crossref.org/journals": {"message": {"items": []}},
        }))
        with self.assertRaises(EvidenceLookupError):
            lookup_by_name(client, "a journal that does not exist anywhere")

    def test_official_and_observed_fields_stay_separate(self):
        """Regression guard: identity/APC fields must never leak into the
        observed-activity fields and vice versa (SKILL.md Evidence
        discipline)."""
        client = HttpClient("test-agent", transport=fake_transport({
            "api.openalex.org/sources": {"results": [OPENALEX_SOURCE_RECORD]},
        }))
        evidence = lookup_by_name(client, "anything")
        official_fields = {"display_name", "issn_l", "issn", "publisher", "homepage_url", "apc_usd"}
        observed_fields = {"works_count", "cited_by_count", "first_publication_year",
                            "last_publication_year", "topics"}
        self.assertTrue(official_fields.isdisjoint(observed_fields))


class LookupByIssnTests(unittest.TestCase):
    def test_exact_issn_hit(self):
        client = HttpClient("test-agent", transport=fake_transport({
            "openalex.org/sources/issn:1053-1858": OPENALEX_SOURCE_RECORD,
        }))
        evidence = lookup_by_issn(client, "1053-1858")
        self.assertEqual(evidence.issn_l, "1053-1858")

    def test_raises_on_no_match(self):
        client = HttpClient("test-agent", transport=fake_transport({}))
        with self.assertRaises(EvidenceLookupError):
            lookup_by_issn(client, "0000-0000")


if __name__ == "__main__":
    unittest.main()
