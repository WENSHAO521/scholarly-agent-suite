import os
import sys
import unittest


from scb.acquisition import CorpusRequest, acquire_corpus
from scb.adapters.base import AdapterCapabilities
from scb.manifest import COMPLETE, PARTIAL
from scb.records import Access, CanonicalRecord, Identifiers


class FakeAdapter:
    def __init__(self, records, capabilities=None, raises=False):
        self._records = records
        self.capabilities = capabilities or AdapterCapabilities(search=True)
        self._raises = raises

    def search(self, query):
        if self._raises:
            raise RuntimeError("simulated adapter failure")
        return self._records


def _rec(rid, doi=None, abstract="An abstract.", is_oa=True, year=2022, author="Author One"):
    return CanonicalRecord(
        record_id=rid,
        title="Title %s" % rid,
        authors=[{"name": author}],
        publication_year=year,
        identifiers=Identifiers(doi=doi),
        abstract=abstract,
        access=Access(is_oa=is_oa, best_url=("http://x/%s" % rid) if is_oa else None),
    )


class TestCorpusRequest(unittest.TestCase):
    def test_rejects_unknown_corpus_type(self):
        with self.assertRaises(ValueError):
            CorpusRequest(corpus_type="not_a_type", target="x", purpose="journal_style")


class TestAcquireCorpus(unittest.TestCase):
    def test_full_pipeline_reaches_complete_status(self):
        records = [_rec("r%d" % i, author="Author %d" % i) for i in range(10)]
        adapters = {"crossref": FakeAdapter(records)}
        request = CorpusRequest(corpus_type="journal", target="Journal X", purpose="journal_style", target_records=10)
        result = acquire_corpus(request, adapters)
        self.assertEqual(len(result.records), 10)
        self.assertEqual(result.manifest.status, COMPLETE)
        self.assertEqual(result.manifest.counts.discovered, 10)

    def test_deduplicates_across_adapters(self):
        rec_a = _rec("a", doi="10.1/x")
        rec_b = _rec("b", doi="10.1/x")  # same DOI, different adapter
        adapters = {
            "crossref": FakeAdapter([rec_a]),
            "openalex": FakeAdapter([rec_b]),
        }
        request = CorpusRequest(corpus_type="journal", target="x", purpose="journal_style", target_records=5)
        result = acquire_corpus(request, adapters)
        self.assertEqual(result.manifest.counts.duplicates_removed, 1)
        self.assertEqual(len(result.records), 1)

    def test_one_failing_adapter_does_not_sink_acquisition(self):
        good = [_rec("r%d" % i, author="Author %d" % i) for i in range(5)]
        adapters = {
            "crossref": FakeAdapter(good),
            "broken": FakeAdapter([], raises=True),
        }
        request = CorpusRequest(corpus_type="journal", target="x", purpose="journal_style", target_records=5)
        result = acquire_corpus(request, adapters)
        self.assertEqual(len(result.records), 5)
        self.assertIn("broken", result.adapter_errors)

    def test_partial_corpus_when_pool_smaller_than_target(self):
        records = [_rec("r%d" % i, author="Author %d" % i) for i in range(3)]
        adapters = {"crossref": FakeAdapter(records)}
        request = CorpusRequest(corpus_type="journal", target="x", purpose="journal_style", target_records=30)
        result = acquire_corpus(request, adapters)
        self.assertEqual(result.manifest.status, PARTIAL)

    def test_retrieval_depth_filters_metadata_only_records(self):
        # No abstract and access.is_oa unresolved => metadata-only records
        # should not satisfy a LEVEL_1_ABSTRACT request.
        thin_records = [_rec("r%d" % i, abstract=None, is_oa=None, author="Author %d" % i) for i in range(5)]
        adapters = {"crossref": FakeAdapter(thin_records)}
        request = CorpusRequest(corpus_type="journal", target="x", purpose="journal_style", target_records=5)
        result = acquire_corpus(request, adapters)
        self.assertEqual(len(result.records), 0)
        self.assertEqual(result.manifest.status, "FAILED")

    def test_metadata_only_records_are_usable_when_that_depth_was_requested(self):
        # Regression test: a caller who explicitly asks for only
        # LEVEL_0_METADATA must have those metadata-only records counted
        # as usable — "usable" means "met the requested depth," not a
        # fixed abstract-or-better bar (see scb/manifest.py).
        thin_records = [_rec("r%d" % i, abstract=None, is_oa=None, author="Author %d" % i) for i in range(5)]
        adapters = {"crossref": FakeAdapter(thin_records)}
        request = CorpusRequest(
            corpus_type="journal", target="x", purpose="journal_style",
            target_records=5, retrieval_depth="LEVEL_0_METADATA",
        )
        result = acquire_corpus(request, adapters)
        self.assertEqual(len(result.records), 5)
        self.assertEqual(result.manifest.counts.usable, 5)
        self.assertEqual(result.manifest.status, "COMPLETE")

    def test_manifest_counts_are_never_fabricated(self):
        records = [_rec("r%d" % i, author="Author %d" % i) for i in range(4)]
        adapters = {"crossref": FakeAdapter(records)}
        request = CorpusRequest(corpus_type="journal", target="x", purpose="journal_style", target_records=4)
        result = acquire_corpus(request, adapters)
        self.assertEqual(result.manifest.counts.discovered, 4)
        self.assertEqual(result.manifest.counts.normalized, 4)
        self.assertEqual(result.manifest.counts.usable, 4)


if __name__ == "__main__":
    unittest.main()
