import datetime
import os
import sys
import unittest


from scb.refresh import (
    AGING,
    CURRENT,
    INCOMPLETE,
    NEW_TARGET,
    STALE,
    USER_REQUESTED_REFRESH,
    corpus_selection_gate,
    diff_profiles,
)


def _manifest(days_old, status="COMPLETE", now=None):
    now = now or datetime.datetime(2026, 9, 9, tzinfo=datetime.timezone.utc)
    created = now - datetime.timedelta(days=days_old)
    return {"created_at": created.isoformat(), "status": status}, now


class TestCorpusSelectionGate(unittest.TestCase):
    def test_no_cached_manifest_is_new_target(self):
        decision = corpus_selection_gate(None, "journal")
        self.assertEqual(decision.state, NEW_TARGET)

    def test_user_requested_refresh_always_wins(self):
        manifest, now = _manifest(1)
        decision = corpus_selection_gate(manifest, "journal", user_requested_refresh=True, now=now)
        self.assertEqual(decision.state, USER_REQUESTED_REFRESH)

    def test_incomplete_build_status_overrides_freshness(self):
        manifest, now = _manifest(1, status="PARTIAL")
        decision = corpus_selection_gate(manifest, "journal", now=now)
        self.assertEqual(decision.state, INCOMPLETE)

    def test_journal_within_window_is_current(self):
        manifest, now = _manifest(30, status="COMPLETE")
        decision = corpus_selection_gate(manifest, "journal", now=now)
        self.assertEqual(decision.state, CURRENT)

    def test_journal_beyond_window_is_stale(self):
        manifest, now = _manifest(400, status="COMPLETE")
        decision = corpus_selection_gate(manifest, "journal", now=now)
        self.assertEqual(decision.state, STALE)

    def test_journal_aging_window(self):
        manifest, now = _manifest(270, status="COMPLETE")
        decision = corpus_selection_gate(manifest, "journal", now=now)
        self.assertEqual(decision.state, AGING)

    def test_fast_moving_journal_uses_shorter_window(self):
        manifest, now = _manifest(120, status="COMPLETE")
        decision_normal = corpus_selection_gate(manifest, "journal", fast_moving=False, now=now)
        decision_fast = corpus_selection_gate(manifest, "journal", fast_moving=True, now=now)
        self.assertEqual(decision_normal.state, CURRENT)
        self.assertEqual(decision_fast.state, AGING)

    def test_historical_scholar_never_goes_stale(self):
        manifest, now = _manifest(3650, status="COMPLETE")
        decision = corpus_selection_gate(manifest, "historical_scholar", now=now)
        self.assertEqual(decision.state, CURRENT)

    def test_unparseable_timestamp_is_new_target(self):
        manifest = {"created_at": "not-a-date", "status": "COMPLETE"}
        decision = corpus_selection_gate(manifest, "journal")
        self.assertEqual(decision.state, NEW_TARGET)


class TestDiffProfiles(unittest.TestCase):
    def test_newly_observed_feature_detected(self):
        old = {"rhetorical_moves": {"contribution": 0.2}}
        new = {"rhetorical_moves": {"contribution": 0.2, "limitation": 0.4}}
        diff = diff_profiles(old, new)
        self.assertIn("limitation", diff.newly_observed)


if __name__ == "__main__":
    unittest.main()
