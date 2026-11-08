"""Corpus Stability Engine (PART XXIV-XXVI). A profile should not be
trusted merely because a corpus exists — this module actually runs a
split-corpus comparison and reports which measurable features hold up.
No invented statistical confidence: STABLE/MOSTLY_STABLE/UNSTABLE labels
come from an explicit, documented threshold, not a fitted model.
"""

from __future__ import annotations

import random
import statistics
from dataclasses import dataclass, field
from typing import Callable, List, Optional, Tuple

from scb.analytics.sentence import compute_sentence_metrics
from scb.profile_schema import StyleProfile, build_style_profile
from scb.text_normalize import Document

STABLE = "STABLE"
MOSTLY_STABLE = "MOSTLY_STABLE"
UNSTABLE = "UNSTABLE"
INSUFFICIENT_SAMPLE = "INSUFFICIENT_SAMPLE"

MIN_DOCS_FOR_SPLIT_TEST = 10

# Relative-difference tolerance for a feature to count as "stable"
# between the two split-corpus halves. A documented threshold, not a
# fitted statistical model.
_RELATIVE_TOLERANCE = 0.35
_ABSOLUTE_FLOOR = 0.5  # avoids flagging near-zero values as wildly unstable


def split_corpus(documents: List[Document]) -> Tuple[List[Document], List[Document]]:
    """Deterministic alternating split — reproducible without a seed."""
    return documents[0::2], documents[1::2]


def _relative_diff(a: float, b: float) -> float:
    denom = max(abs(a), abs(b), _ABSOLUTE_FLOOR)
    return abs(a - b) / denom


# (label, extractor) pairs pulled from a StyleProfile.to_dict()-shaped structure.
_COMPARED_FEATURES: List[Tuple[str, Callable[[StyleProfile], Optional[float]]]] = [
    ("sentence.median_length", lambda p: p.sentence.get("median_length")),
    ("paragraph.median_length_words", lambda p: p.paragraph.get("median_length_words")),
    ("lexical.first_person_rate_per_1000", lambda p: p.lexical.get("first_person_rate_per_1000")),
    ("lexical.hedge_rate_per_1000", lambda p: p.lexical.get("hedge_rate_per_1000")),
    ("citations.citations_per_1000_words", lambda p: p.citations.get("citations_per_1000_words")),
]


@dataclass
class FeatureStability:
    feature: str
    value_a: Optional[float]
    value_b: Optional[float]
    relative_difference: Optional[float]
    stable: bool


@dataclass
class StabilityReport:
    status: str
    sample_size: int
    half_a_size: int = 0
    half_b_size: int = 0
    feature_results: List[FeatureStability] = field(default_factory=list)
    stable_feature_share: float = 0.0


def compare_profiles(profile_a: StyleProfile, profile_b: StyleProfile) -> List[FeatureStability]:
    results = []
    for name, extractor in _COMPARED_FEATURES:
        a, b = extractor(profile_a), extractor(profile_b)
        if a is None or b is None:
            results.append(FeatureStability(name, a, b, None, False))
            continue
        diff = _relative_diff(a, b)
        results.append(FeatureStability(name, a, b, round(diff, 3), diff <= _RELATIVE_TOLERANCE))
    return results


def run_stability_check(documents: List[Document], profile_type: str = "corpus", target: str = "") -> StabilityReport:
    n = len(documents)
    if n < MIN_DOCS_FOR_SPLIT_TEST:
        return StabilityReport(status=INSUFFICIENT_SAMPLE, sample_size=n)

    half_a, half_b = split_corpus(documents)
    profile_a = build_style_profile(profile_type, target, half_a)
    profile_b = build_style_profile(profile_type, target, half_b)

    results = compare_profiles(profile_a, profile_b)
    comparable = [r for r in results if r.relative_difference is not None]
    stable_count = sum(1 for r in comparable if r.stable)
    share = round(stable_count / len(comparable), 3) if comparable else 0.0

    if share >= 0.8:
        status = STABLE
    elif share >= 0.5:
        status = MOSTLY_STABLE
    else:
        status = UNSTABLE

    return StabilityReport(
        status=status,
        sample_size=n,
        half_a_size=len(half_a),
        half_b_size=len(half_b),
        feature_results=results,
        stable_feature_share=share,
    )


@dataclass
class BootstrapResult:
    feature: str
    iterations: int
    estimates: List[float]
    mean: float
    stdev: float
    min: float
    max: float


def bootstrap_sentence_median_length(
    documents: List[Document], iterations: int = 200, seed: int = 1234
) -> BootstrapResult:
    """Lightweight resampling (stdlib `random` only, per PART XXV — "do
    not turn this into a complex statistical package") to see how much a
    single numeric feature moves when the corpus is resampled with
    replacement."""
    rng = random.Random(seed)
    n = len(documents)
    estimates: List[float] = []

    if n == 0:
        return BootstrapResult("sentence.median_length", 0, [], 0.0, 0.0, 0.0, 0.0)

    for _ in range(iterations):
        sample = [documents[rng.randrange(n)] for _ in range(n)]
        text = "\n\n".join("\n\n".join(d.all_paragraphs()) for d in sample)
        metrics = compute_sentence_metrics(text)
        estimates.append(metrics.median_length)

    return BootstrapResult(
        feature="sentence.median_length",
        iterations=iterations,
        estimates=estimates,
        mean=round(statistics.mean(estimates), 3),
        stdev=round(statistics.pstdev(estimates), 3) if len(estimates) > 1 else 0.0,
        min=min(estimates),
        max=max(estimates),
    )
