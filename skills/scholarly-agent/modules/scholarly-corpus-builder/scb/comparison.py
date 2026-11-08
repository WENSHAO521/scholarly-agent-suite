"""Corpus/Profile Comparison Engine (PART XLIX, LIII, LVIII-LIX).

Compares two profiles (Journal A vs B, discipline eras, author vs
target journal, ...) and reports shared traits, differences, and
adaptation implications. Never mechanically averages two profiles
together (PART XXXIX) — composite synthesis keeps the author's voice as
the thing being adapted *from*, not blended away.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from scb.profile_schema import label_density, label_sentence_length

# Numeric leaf paths this module knows how to compare across two
# profile dicts, however they're shaped (journal/discipline/author all
# nest these slightly differently).
_COMPARISON_PATHS: List[Tuple[str, ...]] = [
    ("sentence_style", "median_length"),
    ("sentence", "median_length"),
    ("citation_behavior", "citations_per_1000_words"),
    ("citations", "citations_per_1000_words"),
]

# A profile that only exposes a label (e.g. journal profiles deliberately
# expose "short"/"moderate"/"long" rather than a raw number — see
# references/journal-profile.md) can still be compared to a profile that
# has the raw number, by bucketing the raw number with the same rule
# (scb.profile_schema.label_sentence_length / label_density) and
# comparing labels instead of fabricating false numeric precision.
_BUCKETED_COMPARISONS: List[Tuple[str, Tuple[str, ...], Tuple[str, ...], Any]] = [
    ("sentence_length", ("sentence_style", "median_length"), ("prose", "sentence_length"), label_sentence_length),
    ("sentence_length", ("sentence", "median_length"), ("prose", "sentence_length"), label_sentence_length),
    ("citation_density", ("citation_behavior", "citations_per_1000_words"), ("citations", "density"), label_density),
    ("citation_density", ("citations", "citations_per_1000_words"), ("citations", "density"), label_density),
]

_MATERIAL_DIFFERENCE_THRESHOLD = 0.25


def _get_path(d: Dict[str, Any], path: Tuple[str, ...]) -> Optional[float]:
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur if isinstance(cur, (int, float)) else None


def _get_str_path(d: Dict[str, Any], path: Tuple[str, ...]) -> Optional[str]:
    cur: Any = d
    for key in path:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur if isinstance(cur, str) else None


def _collect_numeric_features(profile: Dict[str, Any]) -> Dict[str, float]:
    found = {}
    for path in _COMPARISON_PATHS:
        val = _get_path(profile, path)
        if val is not None:
            found[".".join(path)] = val
    return found


def _bucketed_comparisons(profile_a: Dict[str, Any], profile_b: Dict[str, Any]) -> List[Tuple[str, str, str]]:
    """Returns (feature_name, label_a, label_b) for every bucketed
    comparison where at least one side only has a label and the other
    has a raw number (or both have labels directly)."""
    results = []
    seen_features = set()
    for feature_name, numeric_path, label_path, bucket_fn in _BUCKETED_COMPARISONS:
        if feature_name in seen_features:
            continue
        numeric_a, numeric_b = _get_path(profile_a, numeric_path), _get_path(profile_b, numeric_path)
        label_a_direct, label_b_direct = _get_str_path(profile_a, label_path), _get_str_path(profile_b, label_path)

        resolved_a = bucket_fn(numeric_a) if numeric_a is not None else label_a_direct
        resolved_b = bucket_fn(numeric_b) if numeric_b is not None else label_b_direct

        # Skip if both sides already had the raw number — that's handled
        # by the precise numeric comparison instead.
        if numeric_a is not None and numeric_b is not None:
            continue
        if resolved_a is not None and resolved_b is not None:
            results.append((feature_name, resolved_a, resolved_b))
            seen_features.add(feature_name)
    return results


@dataclass
class ProfileComparison:
    shared_traits: List[str] = field(default_factory=list)
    differences: List[Dict[str, Any]] = field(default_factory=list)
    adaptation_implications: List[str] = field(default_factory=list)
    do_not_change: List[str] = field(default_factory=list)


def compare_profiles(profile_a: Dict[str, Any], profile_b: Dict[str, Any], label_a: str = "A", label_b: str = "B") -> ProfileComparison:
    features_a = _collect_numeric_features(profile_a)
    features_b = _collect_numeric_features(profile_b)

    shared = []
    differences = []
    for key in sorted(set(features_a) & set(features_b)):
        val_a, val_b = features_a[key], features_b[key]
        denom = max(abs(val_a), abs(val_b), 0.5)
        rel_diff = abs(val_a - val_b) / denom
        if rel_diff < _MATERIAL_DIFFERENCE_THRESHOLD:
            shared.append(key)
        else:
            differences.append({"feature": key, label_a: val_a, label_b: val_b, "relative_difference": round(rel_diff, 3)})

    first_person_a = profile_a.get("first_person")
    first_person_b = profile_b.get("first_person")
    if first_person_a and first_person_b:
        if first_person_a == first_person_b:
            shared.append("first_person")
        else:
            differences.append({"feature": "first_person", label_a: first_person_a, label_b: first_person_b})

    for feature_name, resolved_a, resolved_b in _bucketed_comparisons(profile_a, profile_b):
        if resolved_a == resolved_b:
            shared.append(feature_name)
        else:
            differences.append({"feature": feature_name, label_a: resolved_a, label_b: resolved_b})

    return ProfileComparison(shared_traits=shared, differences=differences)


def author_vs_journal_adaptation(author_profile: Dict[str, Any], journal_profile: Dict[str, Any]) -> ProfileComparison:
    """PART LIX: recommend surface-level adaptation while explicitly
    preserving the author's substantive voice — never recommends
    imitating the journal's phrasing."""
    comparison = compare_profiles(author_profile, journal_profile, "author", "journal")

    adaptation_implications = []
    do_not_change = []

    journal_intro = journal_profile.get("introduction", {})
    if journal_intro.get("contribution_position") == "commonly state the contribution explicitly":
        adaptation_implications.append(
            "This journal's sampled corpus commonly states the contribution explicitly and early — "
            "consider surfacing your contribution sooner in the introduction."
        )

    for diff in comparison.differences:
        if diff["feature"] in ("sentence_style.median_length", "sentence.median_length", "sentence_length"):
            adaptation_implications.append(
                "Your sentences run longer than this journal's observed norm — consider trimming "
                "extreme outliers, but do not flatten your sentence-level voice to match."
            )
            do_not_change.append("author's conceptual sentence complexity")

    do_not_change.append("author's substantive argumentative voice")
    do_not_change.append("author's citation ethics and accuracy")

    comparison.adaptation_implications = adaptation_implications
    comparison.do_not_change = do_not_change
    return comparison


def synthesize_composite_voice(
    author_profile: Optional[Dict[str, Any]] = None,
    discipline_profile: Optional[Dict[str, Any]] = None,
    journal_profile: Optional[Dict[str, Any]] = None,
    historical_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """PART XXXIX: composite synthesis with conflict resolution — never
    mechanically averages every layer; author voice is preserved and
    the other layers are adaptation inputs, in the PART XXXVI precedence
    order (author > discipline > journal > historical)."""
    conflicts = []
    if author_profile and journal_profile:
        adaptation = author_vs_journal_adaptation(author_profile, journal_profile)
        if adaptation.differences:
            conflicts.append({
                "between": ["author", "journal"],
                "differences": adaptation.differences,
                "resolution": "preserve author voice; adapt only the surface-level differences listed",
            })

    layers_present = [
        name for name, profile in [
            ("author", author_profile), ("discipline", discipline_profile),
            ("journal", journal_profile), ("historical", historical_profile),
        ] if profile
    ]

    return {
        "layers_present": layers_present,
        "precedence": [l for l in ("author", "discipline", "journal", "historical") if l in layers_present],
        "conflicts": conflicts,
        "note": "Journal profile is an observed pattern, not a requirement; historical profile "
                "contributes structural patterns only, never phrasing.",
    }
