import os
import sys
import unittest


from scb.records import CanonicalRecord
from scb.sampling import diversified_sample


def _rec(rid, author, year, venue="J", volume="1", issue="1"):
    return CanonicalRecord(
        record_id=rid,
        title="Title %s" % rid,
        authors=[{"name": author}],
        publication_year=year,
        venue=venue,
        volume=volume,
        issue=issue,
    )


class TestDiversifiedSample(unittest.TestCase):
    def test_prevents_one_author_from_dominating(self):
        records = [_rec("r%d" % i, "Prolific Author", 2020 + (i % 5)) for i in range(20)]
        result = diversified_sample(records, target_records=10)
        # cap should have kicked in for the single-author case
        self.assertTrue(any(d.startswith("author:") for d in result.dominance_prevented))

    def test_backfills_to_target_when_pool_allows(self):
        records = [_rec("r%d" % i, "Prolific Author", 2020) for i in range(20)]
        result = diversified_sample(records, target_records=10)
        self.assertEqual(len(result.selected), 10)

    def test_does_not_exceed_target_when_pool_is_diverse(self):
        records = [_rec("r%d" % i, "Author %d" % i, 2020 + (i % 5)) for i in range(30)]
        result = diversified_sample(records, target_records=10)
        self.assertEqual(len(result.selected), 10)

    def test_diverse_pool_selected_without_dominance_flags(self):
        records = [_rec("r%d" % i, "Author %d" % i, 2015 + i, issue=str(i)) for i in range(10)]
        result = diversified_sample(records, target_records=10)
        self.assertEqual(len(result.selected), 10)
        self.assertEqual(result.dominance_prevented, [])

    def test_smaller_pool_than_target_returns_all(self):
        records = [_rec("r%d" % i, "Author %d" % i, 2020) for i in range(3)]
        result = diversified_sample(records, target_records=10)
        self.assertEqual(len(result.selected), 3)

    def test_year_distribution_recorded(self):
        records = [_rec("r%d" % i, "Author %d" % i, 2020) for i in range(5)]
        result = diversified_sample(records, target_records=5)
        self.assertEqual(result.year_distribution.get("2020"), 5)


if __name__ == "__main__":
    unittest.main()
