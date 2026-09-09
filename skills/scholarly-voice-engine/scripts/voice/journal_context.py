"""Consumes a JOURNAL_STYLE_CONTEXT_V1 envelope from journal-fit-engine
(scholarly-agent-suite/protocols/journal-style-context.schema.json), closing
the gap references/integration.md previously flagged as "not yet
reconciled": journal-fit-engine now emits this protocol directly
(jfe.style_context.build_journal_style_context()); this module is the
consumer half.

The protocol's own non-negotiable separation carries through here exactly:
`official_requirements` (a journal's own stated author-guideline facts) and
`observed_patterns` (descriptive corpus regularities) are never merged into
one undifferentiated "journal style" blob. This module keeps them on two
different paths:

  official_requirements -> `hard_requirements` on JournalStyleContext.
      Always preserved verbatim, never confidence-gated, never overridden
      by anything lower in references/corpus-profile-integration.md's
      precedence order (they sit between the user's explicit constraints
      and the manuscript's own scientific integrity -- see
      references/journal-style-adaptation.md).

  observed_patterns -> fed into profile_merge.resolve_voice_precedence()
      as the existing "journal" layer, confidence-gated by `freshness`
      exactly the way that function already gates a low-confidence journal
      contribution. This reuses the tested precedence/confidence-gating
      machinery rather than inventing a second one.

Unknown stays unknown: a missing or absent `freshness` is treated as the
lowest confidence (never silently "current"), and every evidence gap
(`no official_requirements supplied`, `no observed_patterns supplied`,
staleness) produces a `limitations` entry that is carried through, never
dropped.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from scripts.voice.profile_merge import CONFIDENCE_GATED_LAYERS, resolve_voice_precedence

PROTOCOL = "JOURNAL_STYLE_CONTEXT_V1"
FRESHNESS_STATES = ("current", "aging", "stale")

_FRESHNESS_TO_CONFIDENCE = {
    "current": "high",
    "aging": "moderate",
    "stale": "low",
    None: "low",  # unstated freshness is never treated as trustworthy
}

assert "journal" in CONFIDENCE_GATED_LAYERS, (
    "journal_context.py assumes profile_merge treats the 'journal' layer as "
    "confidence-gated; that assumption changed upstream and this module's "
    "freshness -> confidence gating no longer does anything."
)


class JournalContextError(ValueError):
    """Raised when a JOURNAL_STYLE_CONTEXT_V1 payload has an invalid shape."""


@dataclass
class JournalStyleContext:
    journal_name: str
    official_requirements: dict = field(default_factory=dict)
    observed_patterns: dict = field(default_factory=dict)
    freshness: str | None = None
    journal_identifiers: dict = field(default_factory=dict)
    article_type: str | None = None
    evidence: list = field(default_factory=list)
    limitations: list = field(default_factory=list)


def from_journal_style_context_v1(data: dict) -> JournalStyleContext:
    """Validate and translate an incoming JOURNAL_STYLE_CONTEXT_V1 envelope.
    Raises JournalContextError on a wrong protocol, missing required field,
    a non-dict official_requirements/observed_patterns, or an out-of-enum
    freshness value -- never silently coerces a malformed payload."""
    if data.get("protocol") != PROTOCOL:
        raise JournalContextError(f"not a {PROTOCOL} envelope: protocol={data.get('protocol')!r}")
    missing = {"journal_name", "official_requirements", "observed_patterns"} - set(data)
    if missing:
        raise JournalContextError(f"{PROTOCOL} envelope missing required field(s): {sorted(missing)}")
    official_requirements = data["official_requirements"]
    observed_patterns = data["observed_patterns"]
    if not isinstance(official_requirements, dict):
        raise JournalContextError("official_requirements must be an object")
    if not isinstance(observed_patterns, dict):
        raise JournalContextError("observed_patterns must be an object")
    freshness = data.get("freshness")
    if freshness is not None and freshness not in FRESHNESS_STATES:
        raise JournalContextError(f"freshness must be one of {FRESHNESS_STATES} or absent, got {freshness!r}")

    limitations = list(data.get("limitations") or [])
    if freshness is None:
        limitations.append(
            f"journal_style_context for {data['journal_name']!r} did not state freshness; "
            "observed_patterns treated as low-confidence."
        )
    elif freshness == "stale":
        limitations.append(
            f"journal_style_context for {data['journal_name']!r} is stale; observed_patterns "
            "weighted as low-confidence, verify before relying on them."
        )
    if not official_requirements:
        limitations.append(
            f"no official_requirements in journal_style_context for {data['journal_name']!r}; "
            "no journal-stated hard constraints are being enforced beyond the manuscript's own "
            "explicit constraints."
        )

    return JournalStyleContext(
        journal_name=data["journal_name"],
        official_requirements=dict(official_requirements),
        observed_patterns=dict(observed_patterns),
        freshness=freshness,
        journal_identifiers=dict(data.get("journal_identifiers") or {}),
        article_type=data.get("article_type"),
        evidence=list(data.get("evidence") or []),
        limitations=limitations,
    )


def apply_journal_style_context(context: JournalStyleContext, layers: dict,
                                 confidence: dict | None = None) -> tuple:
    """Fold a JournalStyleContext into an existing voice-precedence layer
    set (see profile_merge.resolve_voice_precedence). `layers` should
    already carry whatever "author"/"discipline"/"historical" field maps
    apply; this function adds/overwrites the "journal" layer from
    `context.observed_patterns` and gates it by `context.freshness`.

    Returns (resolved, conflicts, hard_requirements, limitations):
      resolved / conflicts  -- straight from resolve_voice_precedence(),
          covering only the confidence-gated observed_patterns layer.
      hard_requirements     -- context.official_requirements, verbatim,
          returned separately because these sit ABOVE author/discipline/
          journal/historical precedence entirely (references/
          journal-style-adaptation.md) and must never be confidence-gated
          or silently dropped by resolve_voice_precedence's layer logic.
      limitations           -- context.limitations, unchanged (propagate,
          never re-summarize away a freshness/evidence-gap warning).
    """
    merged_layers = dict(layers)
    merged_layers["journal"] = dict(context.observed_patterns)
    merged_confidence = dict(confidence or {})
    merged_confidence["journal"] = _FRESHNESS_TO_CONFIDENCE[context.freshness]

    resolved, conflicts = resolve_voice_precedence(merged_layers, merged_confidence)
    return resolved, conflicts, dict(context.official_requirements), list(context.limitations)
