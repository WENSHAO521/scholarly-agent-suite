"""Builds and validates a JOURNAL_STYLE_CONTEXT_V1 envelope -- the protocol
handoff to scholarly-voice-engine
(scholarly-agent-suite/protocols/journal-style-context.schema.json).

Non-negotiable separation (SKILL.md §Evidence discipline, shared/
terminology.md's "Official requirement" / "Observed style" entries):
`official_requirements` may only ever contain facts stated in a journal's
own author guidelines (word limits, citation style, structure mandates,
blinding rules). `observed_patterns` may only ever contain descriptive
regularities measured from a corpus of published articles (typically by
scholarly-corpus-builder). This module enforces that separation
structurally where it can (see `_check_no_bucket_contamination`) and never
blurs the two itself.

This Skill's own two adapters (OpenAlex Sources, Crossref Journals) are
bibliographic indexes, not author-guideline sources or corpus samples --
`build_journal_style_context` never derives `official_requirements` or
`observed_patterns` from its own JournalEvidence. Both are caller-supplied
(typically: official_requirements from a host LLM that fetched the
journal's real guidelines page; observed_patterns forwarded from
scholarly-corpus-builder's OBSERVED-tagged journal profile). What this
module *does* derive from its own evidence is `journal_identifiers`
(ISSN/publisher -- identity metadata, not a style requirement) and
`freshness` (from JournalEvidence.checked_at).
"""
from __future__ import annotations

import datetime
from typing import Optional

from jfe.journal_evidence import JournalEvidence

PROTOCOL = "JOURNAL_STYLE_CONTEXT_V1"
FRESHNESS_STATES = ("current", "aging", "stale")

# references/refresh-policy.md / scholarly-corpus-builder's documented
# journal freshness windows (6-12 months) -- reused here rather than
# inventing a second set of thresholds for the same kind of fact.
_CURRENT_WINDOW_DAYS = 183   # ~6 months
_AGING_WINDOW_DAYS = 365     # ~12 months

# Field names reserved to one bucket. A key from one list appearing in the
# *other* bucket is a structural contamination error (E2E regression case:
# corpus-derived evidence must never be presented as an official
# requirement, and vice versa) -- this is a best-effort, not exhaustive,
# check: it catches the known vocabulary, not every possible mistake.
_OFFICIAL_ONLY_KEYS = frozenset({
    "word_limit", "abstract_word_limit", "citation_style", "required_sections",
    "structure_required", "blinding_required", "article_type_rules",
    "submission_instructions", "language_policy", "supplementary_material_policy",
    "title_requirements",
})
_OBSERVED_ONLY_KEYS = frozenset({
    "mean_paragraph_length", "mean_sentence_length", "citation_density",
    "abstract_structure_common", "introduction_style", "heading_case_common",
    "section_word_share", "rhetorical_moves_common", "tone_observed",
    "contribution_placement_observed",
})


class StyleContextError(ValueError):
    """Raised when a JOURNAL_STYLE_CONTEXT_V1 envelope would have an
    invalid shape or violate the official/observed separation rule."""


def _check_no_bucket_contamination(official_requirements: dict, observed_patterns: dict) -> None:
    leaked_into_official = set(official_requirements) & _OBSERVED_ONLY_KEYS
    if leaked_into_official:
        raise StyleContextError(
            f"official_requirements contains observed-pattern-only field(s) {sorted(leaked_into_official)} "
            "-- descriptive corpus evidence must never be presented as an official requirement."
        )
    leaked_into_observed = set(observed_patterns) & _OFFICIAL_ONLY_KEYS
    if leaked_into_observed:
        raise StyleContextError(
            f"observed_patterns contains official-requirement-only field(s) {sorted(leaked_into_observed)} "
            "-- a stated author-guideline rule must never be reported as merely descriptive."
        )


def compute_freshness(checked_at_iso: Optional[str], *, now: Optional[datetime.datetime] = None) -> str:
    """current / aging / stale from an ISO-8601 checked_at timestamp, or
    'stale' (safe default -- never silently 'current') if checked_at is
    missing or unparseable."""
    if not checked_at_iso:
        return "stale"
    try:
        checked_at = datetime.datetime.fromisoformat(checked_at_iso)
    except ValueError:
        return "stale"
    if checked_at.tzinfo is None:
        checked_at = checked_at.replace(tzinfo=datetime.timezone.utc)
    now = now or datetime.datetime.now(datetime.timezone.utc)
    age_days = (now - checked_at).total_seconds() / 86400
    if age_days <= _CURRENT_WINDOW_DAYS:
        return "current"
    if age_days <= _AGING_WINDOW_DAYS:
        return "aging"
    return "stale"


def journal_identifiers_from_evidence(evidence: JournalEvidence) -> dict:
    """Identity metadata -- not a style requirement, not observed evidence.
    Kept as its own field so it never has to be smuggled into either
    bucket."""
    return {
        "issn": list(evidence.issn),
        "issn_l": evidence.issn_l,
        "publisher": evidence.publisher,
    }


def build_journal_style_context(
    journal_name: str,
    *,
    official_requirements: Optional[dict] = None,
    observed_patterns: Optional[dict] = None,
    freshness: str = "current",
    journal_identifiers: Optional[dict] = None,
    article_type: Optional[str] = None,
    evidence: Optional[list] = None,
    limitations: Optional[list] = None,
    generated_at: Optional[str] = None,
) -> dict:
    """Assemble and validate a JOURNAL_STYLE_CONTEXT_V1 envelope.

    Every field the caller does not actually have evidence for should be
    left as an empty dict/list -- never invented (SKILL.md's no-fabrication
    rule). `limitations` is appended to, not replaced, when this function
    detects an evidence gap itself (missing official_requirements/
    observed_patterns), so caller-supplied limitations are preserved.
    """
    if not journal_name or not isinstance(journal_name, str):
        raise StyleContextError("journal_name must be a non-empty string")
    if freshness not in FRESHNESS_STATES:
        raise StyleContextError(f"freshness must be one of {FRESHNESS_STATES}, got {freshness!r}")

    official_requirements = dict(official_requirements or {})
    observed_patterns = dict(observed_patterns or {})
    _check_no_bucket_contamination(official_requirements, observed_patterns)

    limitations = list(limitations or [])
    if not official_requirements:
        limitations.append(
            f"no official_requirements supplied for {journal_name!r}; verify the journal's own "
            "author guidelines directly before submission."
        )
    if not observed_patterns:
        limitations.append(
            f"no observed_patterns supplied for {journal_name!r}; no corpus-derived style evidence "
            "is available for this journal."
        )
    if freshness == "stale":
        limitations.append(
            f"style context for {journal_name!r} is stale; treat observed_patterns as low-confidence "
            "and re-verify before relying on them."
        )

    envelope = {
        "protocol": PROTOCOL,
        "journal_name": journal_name,
        "official_requirements": official_requirements,
        "observed_patterns": observed_patterns,
        "freshness": freshness,
    }
    if journal_identifiers:
        envelope["journal_identifiers"] = journal_identifiers
    if article_type:
        envelope["article_type"] = article_type
    if evidence:
        envelope["evidence"] = evidence
    if limitations:
        envelope["limitations"] = limitations
    if generated_at:
        envelope["generated_at"] = generated_at
    return envelope


def from_journal_evidence(
    evidence: JournalEvidence,
    *,
    official_requirements: Optional[dict] = None,
    observed_patterns: Optional[dict] = None,
    article_type: Optional[str] = None,
    limitations: Optional[list] = None,
) -> dict:
    """Convenience entry point tying this Skill's own live evidence lookup
    (jfe.journal_evidence) to the protocol builder. `journal_identifiers`
    and `freshness` are derived from `evidence`; official_requirements/
    observed_patterns must still be supplied by the caller -- this Skill's
    index adapters are not a source for either (see module docstring)."""
    limitations = list(limitations or [])
    limitations.append(
        f"journal_identifiers sourced from a bibliographic index ({evidence.source}), not the "
        "journal's own official page -- see evidence.provenance_note."
    )
    return build_journal_style_context(
        evidence.display_name or "unknown journal",
        official_requirements=official_requirements,
        observed_patterns=observed_patterns,
        freshness=compute_freshness(evidence.checked_at),
        journal_identifiers=journal_identifiers_from_evidence(evidence),
        article_type=article_type,
        limitations=limitations,
        generated_at=evidence.checked_at,
    )
