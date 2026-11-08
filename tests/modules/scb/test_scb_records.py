import os
import sys
import unittest


from scb.records import Access, CanonicalRecord, Identifiers, ProvenanceEntry


class TestCanonicalRecord(unittest.TestCase):
    def test_round_trip_to_dict_from_dict(self):
        rec = CanonicalRecord(
            record_id="r1",
            title="A Study of Things",
            authors=[{"name": "Jane Doe"}],
            publication_year=2024,
            identifiers=Identifiers(doi="10.1234/abcd"),
            access=Access(is_oa=True, oa_status="gold"),
        )
        rec.add_provenance(ProvenanceEntry(adapter="crossref", operation="lookup_by_doi", verification="VERIFIED"))

        data = rec.to_dict()
        self.assertEqual(data["identifiers"]["doi"], "10.1234/abcd")
        self.assertEqual(data["access"]["oa_status"], "gold")
        self.assertEqual(data["sources"], ["crossref"])

        restored = CanonicalRecord.from_dict(data)
        self.assertEqual(restored.identifiers.doi, "10.1234/abcd")
        self.assertEqual(restored.provenance[0].adapter, "crossref")
        self.assertEqual(restored.provenance[0].verification, "VERIFIED")

    def test_defaults_are_independent_between_instances(self):
        a = CanonicalRecord(record_id="a")
        b = CanonicalRecord(record_id="b")
        a.authors.append({"name": "X"})
        self.assertEqual(b.authors, [])

    def test_add_provenance_deduplicates_sources(self):
        rec = CanonicalRecord(record_id="r1")
        rec.add_provenance(ProvenanceEntry(adapter="openalex", operation="search"))
        rec.add_provenance(ProvenanceEntry(adapter="openalex", operation="lookup"))
        self.assertEqual(rec.sources, ["openalex"])
        self.assertEqual(len(rec.provenance), 2)


if __name__ == "__main__":
    unittest.main()
