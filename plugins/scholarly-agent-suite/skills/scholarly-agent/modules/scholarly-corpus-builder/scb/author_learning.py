"""Author Profile Differential Learning (PART XXXIV) and Edit-Diff
Learning (PART XXXV).

Neither function here persists anything — persistence (if any) is a
caller/host concern, and PART XXXV is explicit that full private
documents must never be stored globally and that persistent learning
must never be silently enabled. These functions are pure: given inputs,
they return a merged profile / a set of observed tendencies.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from scb.analytics.citations import compute_citation_metrics
from scb.analytics.claims import analyze_claims
from scb.analytics.lexical import compute_lexical_metrics
from scb.analytics.sentence import compute_sentence_metrics
from scb.profiles.author import build_author_profile
from scb.text_normalize import Document

# (dict-path tuples) numeric leaves this module knows how to blend and
# compare between an old and a newly-derived author profile.
_NUMERIC_PATHS: List[Tuple[str, ...]] = [
    ("sentence_style", "median_length"),
    ("sentence_style", "mean_length"),
    ("paragraph_style", "median_length_words"),
    ("citation_behavior", "citations_per_1000_words"),
]

_MIN_CONFIDENT_SAMPLE = 5
_STABLE_RELATIVE_THRESHOLD = 0.10


def _get_path(d: Dict[str, Any], path: Tuple[str, ...]) -> Optional[float]:
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur if isinstance(cur, (int, float)) else None


def _set_path(d: Dict[str, Any], path: Tuple[str, ...], value: Any) -> None:
    cur = d
    for key in path[:-1]:
        cur = cur.setdefault(key, {})
    cur[path[-1]] = value


@dataclass
class ProfileDiff:
    stable: List[str] = field(default_factory=list)
    strengthening: List[str] = field(default_factory=list)
    weakening: List[str] = field(default_factory=list)
    new: List[str] = field(default_factory=list)
    uncertain: List[str] = field(default_factory=list)


def merge_author_profile(
    previous_profile: Dict[str, Any],
    new_documents: List[Document],
    source_scope_addition: str = "",
) -> Tuple[Dict[str, Any], ProfileDiff]:
    """previous_profile -> (updated_profile, diff). Does not require the
    old profile's source documents — only its previously computed
    numbers — so it never re-processes text unnecessarily (PART XXXIV:
    "do not rebuild the whole personal profile unnecessarily")."""
    new_profile = build_author_profile(new_documents, source_scope=source_scope_addition)

    old_count = int(previous_profile.get("source_count", 0) or 0)
    new_count = int(new_profile.get("source_count", 0) or 0)
    combined_count = old_count + new_count

    merged = copy.deepcopy(previous_profile)
    merged["source_count"] = combined_count
    old_scope = previous_profile.get("source_scope", "") or ""
    merged["source_scope"] = "; ".join(s for s in [old_scope, source_scope_addition] if s)

    diff = ProfileDiff()

    for path in _NUMERIC_PATHS:
        old_val = _get_path(previous_profile, path)
        new_val = _get_path(new_profile, path)
        label = ".".join(path)
        if old_val is None and new_val is None:
            continue
        if old_val is None:
            _set_path(merged, path, new_val)
            diff.new.append(label)
            continue
        if new_val is None:
            continue

        if old_count == 0:
            merged_val = new_val
        else:
            merged_val = (old_val * old_count + new_val * new_count) / combined_count
        _set_path(merged, path, round(merged_val, 3))

        if old_count < _MIN_CONFIDENT_SAMPLE or new_count < _MIN_CONFIDENT_SAMPLE:
            diff.uncertain.append(label)
            continue
        relative_change = abs(new_val - old_val) / max(abs(old_val), 1e-6)
        if relative_change < _STABLE_RELATIVE_THRESHOLD:
            diff.stable.append(label)
        elif new_val > old_val:
            diff.strengthening.append(label)
        else:
            diff.weakening.append(label)

    old_moves = set(previous_profile.get("argument_moves", []) or [])
    new_moves = set(new_profile.get("argument_moves", []) or [])
    for move in sorted(new_moves - old_moves):
        diff.new.append("argument_moves:%s" % move)
    merged["argument_moves"] = sorted(old_moves | new_moves)

    merged["do_not_preserve"] = previous_profile.get("do_not_preserve") or new_profile.get("do_not_preserve")
    merged["generated_at"] = new_profile["generated_at"]

    return merged, diff


# --- Edit-diff learning (PART XXXV) -----------------------------------

@dataclass
class EditTendency:
    dimension: str
    direction: str  # "shortened" | "lengthened" | "increased" | "decreased"
    pairs_observed: int
    pairs_matching: int

    @property
    def consistency(self) -> float:
        if self.pairs_observed == 0:
            return 0.0
        return round(self.pairs_matching / self.pairs_observed, 3)


def analyze_edit_diffs(draft_final_pairs: List[Tuple[str, str]]) -> List[EditTendency]:
    """Compares an AI draft against a user-edited final version for each
    pair and reports which directional tendencies recur — never stores
    the input text itself, only aggregate directional counts."""
    if not draft_final_pairs:
        return []

    dimensions = {
        "sentence_length": lambda t: compute_sentence_metrics(t).median_length,
        "hedge_rate": lambda t: compute_lexical_metrics(t).hedge_rate_per_1000,
        "first_person_rate": lambda t: compute_lexical_metrics(t).first_person_rate_per_1000,
        "transition_rate": lambda t: compute_lexical_metrics(t).transition_rate_per_1000,
    }

    tallies: Dict[str, Dict[str, int]] = {dim: {"up": 0, "down": 0, "observed": 0} for dim in dimensions}

    for draft, final in draft_final_pairs:
        if not draft or not final:
            continue
        for dim, extractor in dimensions.items():
            draft_val = extractor(draft)
            final_val = extractor(final)
            tallies[dim]["observed"] += 1
            if final_val > draft_val * 1.05:
                tallies[dim]["up"] += 1
            elif final_val < draft_val * 0.95:
                tallies[dim]["down"] += 1

    direction_labels = {
        "sentence_length": ("lengthened", "shortened"),
        "hedge_rate": ("increased", "decreased"),
        "first_person_rate": ("increased", "decreased"),
        "transition_rate": ("increased", "decreased"),
    }

    results: List[EditTendency] = []
    for dim, counts in tallies.items():
        observed = counts["observed"]
        if observed == 0:
            continue
        up_label, down_label = direction_labels[dim]
        if counts["up"] >= counts["down"] and counts["up"] > 0:
            results.append(EditTendency(dim, up_label, observed, counts["up"]))
        elif counts["down"] > 0:
            results.append(EditTendency(dim, down_label, observed, counts["down"]))
    return results
