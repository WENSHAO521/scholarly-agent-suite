import json
import os
import sys
import unittest


from scb.adapters.pmc import PMCAdapter, parse_idconv_record
from scb.http_client import HttpClient, HttpResponse

FIXTURES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures", "pmc")


def _load_fixture(name):
    with open(os.path.join(FIXTURES, name), "r", encoding="utf-8") as f:
        return json.load(f)


class TestParseIdconvRecord(unittest.TestCase):
    def test_basic_fields(self):
        rec = _load_fixture("idconv_sample.json")["records"][0]
        canonical = parse_idconv_record(rec)
        self.assertEqual(canonical.identifiers.pmcid, "PMC1817752")
        self.assertEqual(canonical.identifiers.pmid, "17375194")
        self.assertEqual(canonical.identifiers.doi, "10.1371/journal.pone.0000308")

    def test_does_not_guess_access_status(self):
        """This adapter no longer has a lawful lightweight way to
        determine OA status/license (the legacy OA Web Service was
        decommissioned) — it must not fabricate a guess."""
        rec = _load_fixture("idconv_sample.json")["records"][0]
        canonical = parse_idconv_record(rec)
        self.assertIsNone(canonical.access.is_oa)
        self.assertIsNone(canonical.access.reuse_license)
        self.assertFalse(canonical.access.license_verified)


class TestPMCAdapter(unittest.TestCase):
    def test_lookup_by_pmcid_success(self):
        body = json.dumps(_load_fixture("idconv_sample.json")).encode("utf-8")

        def fake_transport(url, headers, timeout):
            self.assertIn("idconv", url)
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = PMCAdapter(http_client=client)
        rec = adapter.lookup_by_pmcid("PMC1817752")
        self.assertIsNotNone(rec)
        self.assertEqual(rec.identifiers.pmid, "17375194")

    def test_lookup_by_pmcid_error_returns_none(self):
        body = json.dumps(_load_fixture("idconv_error_sample.json")).encode("utf-8")

        def fake_transport(url, headers, timeout):
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = PMCAdapter(http_client=client)
        rec = adapter.lookup_by_pmcid("PMC0000000")
        self.assertIsNone(rec)

    def test_lookup_by_pmid_and_by_doi_both_use_idconv(self):
        body = json.dumps(_load_fixture("idconv_sample.json")).encode("utf-8")
        calls = []

        def fake_transport(url, headers, timeout):
            calls.append(url)
            return HttpResponse(200, {}, body, url)

        client = HttpClient(user_agent="test/1.0", transport=fake_transport, sleep_fn=lambda s: None)
        adapter = PMCAdapter(http_client=client)
        adapter.lookup_by_pmid("17375194")
        adapter.lookup_by_doi("10.1371/journal.pone.0000308")
        self.assertEqual(len(calls), 2)

    def test_declares_no_fulltext_pointer_capability(self):
        """Must not claim a capability it can no longer lawfully/lightly
        fulfill now that the OA Web Service is gone."""
        adapter = PMCAdapter(http_client=HttpClient(user_agent="test/1.0"))
        caps = adapter.capabilities.as_list()
        self.assertNotIn("fulltext_pointer", caps)
        self.assertNotIn("version_metadata", caps)


if __name__ == "__main__":
    unittest.main()
