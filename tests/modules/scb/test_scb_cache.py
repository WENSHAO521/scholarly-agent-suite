import os
import shutil
import sys
import tempfile
import time
import unittest


from scb.cache import FileCache, build_key


class TestBuildKey(unittest.TestCase):
    def test_deterministic_for_same_params(self):
        k1 = build_key("crossref", "lookup", {"doi": "10.1/x"})
        k2 = build_key("crossref", "lookup", {"doi": "10.1/x"})
        self.assertEqual(k1, k2)

    def test_param_order_does_not_matter(self):
        k1 = build_key("crossref", "lookup", {"a": 1, "b": 2})
        k2 = build_key("crossref", "lookup", {"b": 2, "a": 1})
        self.assertEqual(k1, k2)

    def test_different_params_differ(self):
        k1 = build_key("crossref", "lookup", {"doi": "10.1/x"})
        k2 = build_key("crossref", "lookup", {"doi": "10.1/y"})
        self.assertNotEqual(k1, k2)


class TestFileCache(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="scb-cache-test-")
        self.cache = FileCache(root=self.tmp, ttl_seconds=3600)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_set_then_get(self):
        key = build_key("openalex", "search", {"q": "x"})
        self.cache.set("openalex", key, {"hello": "world"})
        self.assertEqual(self.cache.get("openalex", key), {"hello": "world"})

    def test_missing_key_returns_none(self):
        self.assertIsNone(self.cache.get("openalex", "nonexistent"))

    def test_expired_entry_returns_none(self):
        short_cache = FileCache(root=self.tmp, ttl_seconds=0.05)
        key = build_key("openalex", "search", {"q": "x"})
        short_cache.set("openalex", key, {"a": 1})
        time.sleep(0.1)
        self.assertIsNone(short_cache.get("openalex", key))

    def test_bypass_ignores_cached_value(self):
        key = build_key("openalex", "search", {"q": "x"})
        self.cache.set("openalex", key, {"a": 1})
        self.assertIsNone(self.cache.get("openalex", key, bypass=True))

    def test_clear_removes_entries(self):
        key = build_key("openalex", "search", {"q": "x"})
        self.cache.set("openalex", key, {"a": 1})
        self.cache.clear("openalex")
        self.assertIsNone(self.cache.get("openalex", key))


if __name__ == "__main__":
    unittest.main()
