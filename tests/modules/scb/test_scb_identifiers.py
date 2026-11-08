import os
import sys
import unittest


from scb.identifiers import (
    RESOLUTION_AMBIGUOUS,
    RESOLUTION_EXACT,
    RESOLUTION_UNRESOLVED,
    classify_identifier_match,
    normalize_arxiv,
    normalize_doi,
    normalize_issn,
    normalize_orcid,
    normalize_pmcid,
    normalize_pmid,
)
from scb.records import Identifiers


class TestDoiNormalization(unittest.TestCase):
    def test_strips_prefixes(self):
        self.assertEqual(normalize_doi("https://doi.org/10.1234/AbCd"), "10.1234/abcd")
        self.assertEqual(normalize_doi("http://dx.doi.org/10.1234/AbCd"), "10.1234/abcd")
        self.assertEqual(normalize_doi("doi:10.1234/AbCd"), "10.1234/abcd")
        self.assertEqual(normalize_doi("10.1234/AbCd"), "10.1234/abcd")

    def test_rejects_non_doi_shape(self):
        self.assertIsNone(normalize_doi("not-a-doi"))
        self.assertIsNone(normalize_doi(None))
        self.assertIsNone(normalize_doi(""))


class TestArxivNormalization(unittest.TestCase):
    def test_new_style_with_version(self):
        result = normalize_arxiv("arXiv:2301.12345v2")
        self.assertEqual(result.base, "2301.12345")
        self.assertEqual(result.version, 2)
        self.assertEqual(result.versioned, "2301.12345v2")

    def test_new_style_without_version(self):
        result = normalize_arxiv("2301.12345")
        self.assertIsNone(result.version)
        self.assertEqual(result.canonical, "2301.12345")

    def test_old_style(self):
        result = normalize_arxiv("cs.AI/0601001v1")
        self.assertEqual(result.version, 1)

    def test_invalid_returns_none(self):
        self.assertIsNone(normalize_arxiv("not-an-arxiv-id"))


class TestOtherIdentifiers(unittest.TestCase):
    def test_pmid(self):
        self.assertEqual(normalize_pmid("12345678"), "12345678")
        self.assertIsNone(normalize_pmid("PMID:123"))

    def test_pmcid(self):
        self.assertEqual(normalize_pmcid("PMC1234567"), "PMC1234567")
        self.assertEqual(normalize_pmcid("1234567"), "PMC1234567")
        self.assertEqual(normalize_pmcid("pmc1234567"), "PMC1234567")

    def test_issn(self):
        self.assertEqual(normalize_issn("1234-5678"), "1234-5678")
        self.assertIsNone(normalize_issn("12345678"))

    def test_orcid(self):
        self.assertEqual(normalize_orcid("https://orcid.org/0000-0001-2345-6789"), "0000-0001-2345-6789")
        self.assertEqual(normalize_orcid("0000-0001-2345-678X"), "0000-0001-2345-678X")


class TestIdentifierMatchClassification(unittest.TestCase):
    def test_exact_doi_match(self):
        a = Identifiers(doi="10.1234/x")
        b = Identifiers(doi="10.1234/x")
        self.assertEqual(classify_identifier_match(a, b), RESOLUTION_EXACT)

    def test_exact_arxiv_match_ignores_version(self):
        a = Identifiers(arxiv_id="2301.12345v1")
        b = Identifiers(arxiv_id="2301.12345v3")
        self.assertEqual(classify_identifier_match(a, b), RESOLUTION_EXACT)

    def test_both_have_identifiers_but_disagree_is_unresolved_not_ambiguous(self):
        a = Identifiers(doi="10.1234/x")
        b = Identifiers(doi="10.9999/y")
        self.assertEqual(classify_identifier_match(a, b), RESOLUTION_UNRESOLVED)

    def test_one_side_missing_identifiers_is_ambiguous(self):
        a = Identifiers(doi="10.1234/x")
        b = Identifiers()
        self.assertEqual(classify_identifier_match(a, b), RESOLUTION_AMBIGUOUS)

    def test_neither_side_has_identifiers_is_unresolved(self):
        a = Identifiers()
        b = Identifiers()
        self.assertEqual(classify_identifier_match(a, b), RESOLUTION_UNRESOLVED)


if __name__ == "__main__":
    unittest.main()
