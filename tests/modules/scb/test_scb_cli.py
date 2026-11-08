import contextlib
import io
import json
import os
import sys
import unittest


from scb import cli
from scb.adapters.base import AdapterCapabilities
from scb.records import Access, CanonicalRecord, Identifiers


class FakeAdapter:
    capabilities = AdapterCapabilities(search=True, lookup_by_doi=True)

    def __init__(self, http_client=None):
        pass

    def search(self, query):
        return [CanonicalRecord(record_id="r1", title="Result for %s" % query, abstract="An abstract about %s." % query)]

    def lookup_by_doi(self, doi):
        if doi == "10.1/missing":
            return None
        return CanonicalRecord(record_id="r1", title="Found", identifiers=Identifiers(doi=doi))


class TestCliLookupAndSearch(unittest.TestCase):
    def setUp(self):
        self._orig_registry = dict(cli.ADAPTER_REGISTRY)
        cli.ADAPTER_REGISTRY["fake"] = FakeAdapter

    def tearDown(self):
        cli.ADAPTER_REGISTRY.clear()
        cli.ADAPTER_REGISTRY.update(self._orig_registry)

    def _run(self, argv):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli.main(argv)
        return code, buf.getvalue()

    def test_lookup_by_doi_success(self):
        code, out = self._run(["lookup", "--adapter", "fake", "--doi", "10.1/x"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(data["identifiers"]["doi"], "10.1/x")

    def test_lookup_not_found_returns_nonzero(self):
        code, _ = self._run(["lookup", "--adapter", "fake", "--doi", "10.1/missing"])
        self.assertEqual(code, 1)

    def test_search_returns_json_list(self):
        code, out = self._run(["search", "--adapter", "fake", "policy diffusion"])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertEqual(len(data), 1)
        self.assertIn("policy diffusion", data[0]["title"])

    def test_unknown_adapter_exits(self):
        with self.assertRaises(SystemExit):
            self._run(["lookup", "--adapter", "not_a_real_adapter", "--doi", "x"])

    def test_acquire_runs_full_pipeline(self):
        code, out = self._run([
            "acquire", "--corpus-type", "journal", "--purpose", "journal_style",
            "--adapters", "fake", "--target-records", "1", "policy diffusion",
        ])
        self.assertEqual(code, 0)
        data = json.loads(out)
        self.assertIn("manifest", data)
        self.assertEqual(data["manifest"]["corpus_type"], "journal")
        self.assertIsNone(data["records"])  # --include-records not passed

    def test_acquire_include_records_flag(self):
        code, out = self._run([
            "acquire", "--corpus-type", "journal", "--purpose", "journal_style",
            "--adapters", "fake", "--target-records", "1", "--include-records", "policy diffusion",
        ])
        data = json.loads(out)
        self.assertIsNotNone(data["records"])
        self.assertEqual(len(data["records"]), 1)


class TestCliResolveOa(unittest.TestCase):
    def test_resolve_oa_reads_stdin_json(self):
        record = CanonicalRecord(
            record_id="r1", title="T",
            access=Access(pdf_url="http://x.pdf", license_verified=True),
        )
        payload = json.dumps(record.to_dict())

        buf_out = io.StringIO()
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(payload)
        try:
            with contextlib.redirect_stdout(buf_out):
                code = cli.main(["resolve-oa"])
        finally:
            sys.stdin = old_stdin

        self.assertEqual(code, 0)
        data = json.loads(buf_out.getvalue())
        self.assertEqual(data["state"], "OA_PDF_AVAILABLE")


class TestBuildParser(unittest.TestCase):
    def test_parser_requires_a_command(self):
        parser = cli.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args([])


if __name__ == "__main__":
    unittest.main()
