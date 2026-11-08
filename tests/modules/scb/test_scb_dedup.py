import os
import sys
import unittest


from scb.dedup import DISTINCT, LIKELY_SAME_WORK, REVIEW_REQUIRED, SAME_WORK, classify_pair, deduplicate
from scb.records import CanonicalRecord, Identifiers


def _rec(record_id, title, year=2024, authors=None, doi=None):
    return CanonicalRecord(
        record_id=record_id,
        title=title,
        publication_year=year,
        authors=[{"name": a} for a in (authors or ["Jane Doe"])],
        identifiers=Identifiers(doi=doi),
    )


class TestClassifyPair(unittest.TestCase):
    def test_same_doi_is_same_work(self):
        a = _rec("a", "Title One", doi="10.1/x")
        b = _rec("b", "A Totally Different Title", doi="10.1/x")
        self.assertEqual(classify_pair(a, b).status, SAME_WORK)

    def test_matching_title_author_year_is_likely_same_work(self):
        a = _rec("a", "On the Structure of Institutions", 2020, ["Jane Doe", "John Smith"])
        b = _rec("b", "On the Structure of Institutions", 2020, ["Jane Doe", "John Smith"])
        self.assertEqual(classify_pair(a, b).status, LIKELY_SAME_WORK)

    def test_similar_title_alone_is_review_required_not_same_work(self):
        a = _rec("a", "On the Structure of Institutions", 2020, ["Jane Doe"])
        b = _rec("b", "On the Structure of Institution", 2021, ["John Smith"])
        decision = classify_pair(a, b)
        self.assertEqual(decision.status, REVIEW_REQUIRED)

    def test_unrelated_works_are_distinct(self):
        a = _rec("a", "Quantum Field Theory Basics")
        b = _rec("b", "A History of Roman Law")
        self.assertEqual(classify_pair(a, b).status, DISTINCT)


class TestDeduplicate(unittest.TestCase):
    def test_removes_exact_doi_duplicates_and_merges_sources(self):
        a = _rec("a", "Title One", doi="10.1/x")
        a.sources = ["crossref"]
        b = _rec("b", "Title One (preprint)", doi="10.1/x")
        b.sources = ["arxiv"]
        c = _rec("c", "Unrelated Work")
        c.sources = ["openalex"]

        result = deduplicate([a, b, c])
        self.assertEqual(len(result.records), 2)
        self.assertEqual(result.duplicates_removed, 1)
        merged = [r for r in result.records if r.record_id == "a"][0]
        self.assertIn("crossref", merged.sources)
        self.assertIn("arxiv", merged.sources)

    def test_review_required_pairs_are_not_merged(self):
        a = _rec("a", "On the Structure of Institutions", 2020, ["Jane Doe"])
        b = _rec("b", "On the Structure of Institution", 2021, ["John Smith"])
        result = deduplicate([a, b])
        self.assertEqual(len(result.records), 2)
        self.assertEqual(len(result.review_required), 1)


if __name__ == "__main__":
    unittest.main()
