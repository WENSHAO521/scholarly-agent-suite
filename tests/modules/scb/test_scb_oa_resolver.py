import os
import sys
import unittest


from scb.oa_resolver import (
    ABSTRACT_AVAILABLE,
    ACCESS_RESTRICTED,
    LICENSE_UNKNOWN,
    METADATA_ONLY,
    OA_FULLTEXT_AVAILABLE,
    OA_LANDING_PAGE,
    OA_PDF_AVAILABLE,
    RESOLUTION_FAILED,
    STRUCTURED_FULLTEXT_AVAILABLE,
    resolve_access,
)
from scb.records import Access, CanonicalRecord


def _rec(**kwargs):
    defaults = dict(record_id="r1", title="Some Title")
    defaults.update(kwargs)
    return CanonicalRecord(**defaults)


class TestResolveAccess(unittest.TestCase):
    def test_structured_fulltext_wins_over_everything(self):
        rec = _rec(access=Access(pdf_url="http://x.pdf"))
        rec.versions.append({"kind": "structured_fulltext", "url": "http://x.xml", "license": "cc-by"})
        res = resolve_access(rec)
        self.assertEqual(res.state, STRUCTURED_FULLTEXT_AVAILABLE)
        self.assertTrue(res.readable)
        self.assertEqual(res.reuse_right, "known")

    def test_pdf_url_on_access_is_oa_pdf_available(self):
        rec = _rec(access=Access(pdf_url="http://x.pdf", license_verified=True))
        res = resolve_access(rec)
        self.assertEqual(res.state, OA_PDF_AVAILABLE)
        self.assertTrue(res.readable)

    def test_oa_version_entry_with_fulltext_version_kind(self):
        rec = _rec()
        rec.versions.append({"is_oa": True, "url": "http://repo/x", "version": "acceptedVersion"})
        res = resolve_access(rec)
        self.assertEqual(res.state, OA_FULLTEXT_AVAILABLE)
        self.assertTrue(res.readable)

    def test_oa_version_entry_landing_page_only(self):
        rec = _rec()
        rec.versions.append({"is_oa": True, "url": "http://publisher/landing", "version": None})
        res = resolve_access(rec)
        self.assertEqual(res.state, OA_LANDING_PAGE)
        self.assertFalse(res.readable)

    def test_abstract_available_when_no_fulltext(self):
        rec = _rec(abstract="An abstract.", access=Access(is_oa=False))
        res = resolve_access(rec)
        self.assertEqual(res.state, ABSTRACT_AVAILABLE)

    def test_access_restricted_when_no_abstract_and_confirmed_closed(self):
        rec = _rec(access=Access(is_oa=False))
        res = resolve_access(rec)
        self.assertEqual(res.state, ACCESS_RESTRICTED)
        self.assertEqual(res.reuse_right, "restricted")

    def test_license_unknown_when_no_oa_signal_at_all(self):
        rec = _rec(access=Access(is_oa=None))
        res = resolve_access(rec)
        self.assertEqual(res.state, LICENSE_UNKNOWN)

    def test_metadata_only_when_title_present_but_versions_list_nonempty_and_no_oa(self):
        rec = _rec(access=Access(is_oa=None))
        rec.versions.append({"is_oa": False, "url": "http://publisher/x"})
        res = resolve_access(rec)
        self.assertEqual(res.state, METADATA_ONLY)

    def test_resolution_failed_when_nothing_known(self):
        rec = CanonicalRecord(record_id="r1", title=None)
        res = resolve_access(rec)
        self.assertEqual(res.state, RESOLUTION_FAILED)

    def test_never_probes_or_fabricates_a_url(self):
        """The resolver must only ever surface a URL that was actually
        present on the record — never construct/guess one."""
        rec = _rec(access=Access(is_oa=True, best_url=None))
        res = resolve_access(rec)
        self.assertIsNone(res.url)


if __name__ == "__main__":
    unittest.main()
