"""Corpus Selection Gate and refresh diff (references/refresh-policy.md,
PART LXIX-LXXII). Code form of the policy already documented there —
this module does not change that policy, it executes it.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Any, Dict, Optional

from scb.comparison import compare_profiles

CURRENT = "CURRENT"
STALE = "STALE"
INSUFFICIENT = "INSUFFICIENT"
NEW_TARGET = "NEW_TARGET"
USER_REQUESTED_REFRESH = "USER_REQUESTED_REFRESH"

AGING = "AGING"
INCOMPLETE = "INCOMPLETE"

# (lower_days, upper_days) — below lower: CURRENT, between: AGING,
# above upper: STALE. None means "no periodic refresh" (historical
# scholar, author — refresh only on new material or explicit request).
_FRESHNESS_WINDOWS_DAYS: Dict[str, Any] = {
    "discipline": (365, 730),
    "journal": (180, 365),
    "journal_fast_moving": (90, 180),
    "historical_scholar": (None, None),
    "author": (None, None),
    "book": (365, 730),
}

_INCOMPLETE_STATUSES = {"INSUFFICIENT", "PARTIAL", "FAILED"}


@dataclass
class GateDecision:
    state: str
    reason: str
    age_days: Optional[int] = None


def corpus_selection_gate(
    cached_manifest: Optional[Dict[str, Any]],
    corpus_type: str,
    fast_moving: bool = False,
    user_requested_refresh: bool = False,
    now: Optional[datetime.datetime] = None,
) -> GateDecision:
    if user_requested_refresh:
        return GateDecision(USER_REQUESTED_REFRESH, "explicit user refresh request")

    if cached_manifest is None:
        return GateDecision(NEW_TARGET, "no cached profile for this target")

    build_status = cached_manifest.get("status")
    if build_status in _INCOMPLETE_STATUSES:
        return GateDecision(INCOMPLETE, "cached build status was %r" % build_status)

    created_raw = cached_manifest.get("created_at") or cached_manifest.get("profile_generated_at")
    if not created_raw:
        return GateDecision(NEW_TARGET, "cached manifest has no creation timestamp")

    try:
        created_at = datetime.datetime.fromisoformat(created_raw)
    except (TypeError, ValueError):
        return GateDecision(NEW_TARGET, "cached manifest timestamp could not be parsed")

    now = now or datetime.datetime.now(created_at.tzinfo)
    age_days = (now - created_at).days

    window_key = "journal_fast_moving" if (fast_moving and corpus_type == "journal") else corpus_type
    lower, upper = _FRESHNESS_WINDOWS_DAYS.get(window_key, (None, None))

    if lower is None:
        return GateDecision(CURRENT, "%s has no periodic refresh window" % corpus_type, age_days)
    if age_days <= lower:
        return GateDecision(CURRENT, "%d days old, within the %d-day freshness window" % (age_days, lower), age_days)
    if age_days <= upper:
        return GateDecision(AGING, "%d days old, within the %d-%d day aging window" % (age_days, lower, upper), age_days)
    return GateDecision(STALE, "%d days old, beyond the %d-day staleness threshold" % (age_days, upper), age_days)


@dataclass
class RefreshDiff:
    stable_features: list
    changed_features: list
    newly_observed: list


def diff_profiles(old_profile: Dict[str, Any], new_profile: Dict[str, Any]) -> RefreshDiff:
    """Reuses the comparison engine's shared/differences classification
    to report a refresh diff (PART LXX/LXXI: stable / changed / newly
    observed features) instead of duplicating comparison logic."""
    comparison = compare_profiles(old_profile, new_profile, "previous", "refreshed")
    old_keys = set()
    for feature_dict_name in ("rhetorical_moves", "claim_conventions"):
        old_keys |= set((old_profile.get(feature_dict_name) or {}).keys())
    new_keys = set()
    for feature_dict_name in ("rhetorical_moves", "claim_conventions"):
        new_keys |= set((new_profile.get(feature_dict_name) or {}).keys())
    newly_observed = sorted(new_keys - old_keys)

    return RefreshDiff(
        stable_features=comparison.shared_traits,
        changed_features=[d["feature"] for d in comparison.differences],
        newly_observed=newly_observed,
    )
