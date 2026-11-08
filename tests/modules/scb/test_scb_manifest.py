import os
import sys
import unittest


from scb.manifest import (
    COMPLETE,
    COMPLETE_WITH_LIMITATIONS,
    FAILED,
    INSUFFICIENT,
    PARTIAL,
    build_manifest,
    counts_from_resolutions,
    determine_sufficiency,
)


class TestDetermineSufficiency(unittest.TestCase):
    def test_zero_usable_is_failed(self):
        self.assertEqual(determine_sufficiency(0, 30), FAILED)

    def test_full_target_is_complete(self):
        self.assertEqual(determine_sufficiency(30, 30), COMPLETE)

    def test_over_target_is_complete(self):
        self.assertEqual(determine_sufficiency(40, 30), COMPLETE)

    def test_70_percent_is_complete_with_limitations(self):
        self.assertEqual(determine_sufficiency(21, 30), COMPLETE_WITH_LIMITATIONS)

    def test_30_percent_is_partial(self):
        self.assertEqual(determine_sufficiency(9, 30), PARTIAL)

    def test_very_low_is_insufficient(self):
        self.assertEqual(determine_sufficiency(1, 30), INSUFFICIENT)

    def test_small_absolute_count_still_partial_via_floor(self):
        # 3 usable out of a target of 100 is only 3% but the explicit
        # floor of >=3 usable records still counts as PARTIAL, not
        # INSUFFICIENT — an illustrative-but-real corpus, not nothing.
        self.assertEqual(determine_sufficiency(3, 100), PARTIAL)


class TestCountsFromResolutions(unittest.TestCase):
    def test_counts_derived_from_actual_states(self):
        # `resolutions` represents records that already passed the
        # caller's requested-depth filter (see scb.acquisition) — so
        # every entry here is usable by construction, regardless of its
        # individual OA state; the per-state tally is a breakdown of
        # *how* each usable record resolved, not a second usability gate.
        states = [
            "STRUCTURED_FULLTEXT_AVAILABLE",
            "OA_FULLTEXT_AVAILABLE",
            "ABSTRACT_AVAILABLE",
            "ACCESS_RESTRICTED",
            "METADATA_ONLY",
        ]
        counts = counts_from_resolutions(discovered=10, normalized=8, duplicates_removed=2, resolutions=states)
        self.assertEqual(counts.discovered, 10)
        self.assertEqual(counts.usable, 5)  # all 5 already passed the depth filter
        self.assertEqual(counts.structured_fulltext, 1)
        self.assertEqual(counts.fulltext_available, 1)
        self.assertEqual(counts.abstract_available, 1)
        self.assertEqual(counts.restricted, 1)
        self.assertEqual(counts.metadata_only, 1)


class TestBuildManifest(unittest.TestCase):
    def test_manifest_status_matches_counts(self):
        counts = counts_from_resolutions(10, 10, 0, ["ABSTRACT_AVAILABLE"] * 10)
        manifest = build_manifest(
            corpus_id="test-corpus",
            corpus_type="journal",
            target="Journal X",
            purpose="journal_style",
            query={"q": "x"},
            sampling_info={"target_records": 10},
            retrieval_depth="LEVEL_1_ABSTRACT",
            requested_records=10,
            counts=counts,
            sources=["crossref"],
            known_biases=[],
            stop_reason="target reached",
        )
        self.assertEqual(manifest.status, COMPLETE)
        self.assertEqual(manifest.counts.usable, 10)
        d = manifest.to_dict()
        self.assertIn("builder_version", d)
        self.assertIn("counts", d)


if __name__ == "__main__":
    unittest.main()
