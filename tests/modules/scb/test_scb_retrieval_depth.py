import os
import sys
import unittest


from scb.oa_resolver import AccessResolution
from scb.retrieval_depth import (
    LEVEL_0_METADATA,
    LEVEL_1_ABSTRACT,
    LEVEL_2_STRUCTURE,
    LEVEL_3_FULLTEXT,
    depth_reached,
    meets_requested_depth,
)


class TestDepthReached(unittest.TestCase):
    def test_readable_fulltext_is_level_3(self):
        res = AccessResolution("OA_FULLTEXT_AVAILABLE", readable=True, reuse_right="unknown", license_verified=False)
        self.assertEqual(depth_reached(res, has_abstract=True), LEVEL_3_FULLTEXT)

    def test_structured_fulltext_readable_is_level_3(self):
        res = AccessResolution("STRUCTURED_FULLTEXT_AVAILABLE", readable=True, reuse_right="unknown", license_verified=False)
        self.assertEqual(depth_reached(res, has_abstract=False), LEVEL_3_FULLTEXT)

    def test_abstract_only_is_level_1(self):
        res = AccessResolution("ABSTRACT_AVAILABLE", readable=False, reuse_right="unknown", license_verified=False)
        self.assertEqual(depth_reached(res, has_abstract=True), LEVEL_1_ABSTRACT)

    def test_metadata_only_is_level_0(self):
        res = AccessResolution("METADATA_ONLY", readable=False, reuse_right="unknown", license_verified=False)
        self.assertEqual(depth_reached(res, has_abstract=False), LEVEL_0_METADATA)


class TestMeetsRequestedDepth(unittest.TestCase):
    def test_fulltext_satisfies_abstract_request(self):
        res = AccessResolution("OA_PDF_AVAILABLE", readable=True, reuse_right="unknown", license_verified=False)
        self.assertTrue(meets_requested_depth(res, True, LEVEL_1_ABSTRACT))

    def test_metadata_only_does_not_satisfy_abstract_request(self):
        res = AccessResolution("METADATA_ONLY", readable=False, reuse_right="unknown", license_verified=False)
        self.assertFalse(meets_requested_depth(res, False, LEVEL_1_ABSTRACT))


if __name__ == "__main__":
    unittest.main()
