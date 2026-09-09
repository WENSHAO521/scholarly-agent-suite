"""Consumes a TARGET_JOURNAL_PROFILE_V1 envelope from journal-fit-engine
(scholarly-agent-suite/protocols/journal-profile.schema.json) and turns it
into an orchestration selection decision for the target-journal-adaptation
workflow (workflows/target-journal-adaptation.md).

This is the first real downstream consumer of TARGET_JOURNAL_PROFILE_V1
(jfe.target_journal_profile.build_target_journal_profile(), added in
journal-fit-engine v0.4.0 / Suite v1.1.1). Until this module existed, the
protocol had a schema-validated producer and no consumer, so its status
stayed PARTIAL (see tests/test_protocols.py's
test_journal_fit_engines_real_target_journal_profile_producer_validates).

Responsibilities, and only these:
  validate   -- protocol/shape check on the incoming envelope. A wrong
                protocol or missing required field raises rather than being
                silently coerced (rule 79, shared/protocol-versioning.md).
  select     -- gate the manuscript's own stated hard constraints against
                only the facts the profile already verified (apc_status,
                indexing). Never re-derives fit, indexing, APC, or a
                quartile itself -- those stay journal-fit-engine's job. A
                fact the profile could not verify (apc_status/oa_status
                "unknown", a requested index absent from `indexing`) is
                NEEDS_VERIFICATION, never a guessed PASS or FAIL.
  preserve   -- provenance and every field this module cannot itself
                confirm survive unchanged into the selection result and
                (via journal_style_context_seed) into whatever
                JOURNAL_STYLE_CONTEXT_V1 envelope is built next.
  translate  -- TARGET_JOURNAL_PROFILE_V1's vocabulary (fit_assessment,
                apc_status, oa_status) is read here, never copied verbatim
                into JOURNAL_STYLE_CONTEXT_V1's vocabulary
                (official_requirements/observed_patterns): fit is not
                style, and an APC fact is not a writing requirement.
  propagate  -- hands the decision to the caller (typically
                references/orchestration-state.md's task-local state) as a
                plain dict/dataclass shape, not a second protocol --
                TARGET_JOURNAL_CONTEXT_V1 does not exist and should not.

A REJECTED selection is a hard stop: journal_style_context_seed() refuses
to build a style-context seed for it, because adapting a manuscript's style
for a journal the hard gate already eliminated wastes the adaptation and
buries the rejection reason (workflows/target-journal-adaptation.md).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

PROTOCOL = "TARGET_JOURNAL_PROFILE_V1"

SELECTED = "SELECTED"
REJECTED = "REJECTED"
NEEDS_VERIFICATION = "NEEDS_VERIFICATION"
SELECTION_STATES = (SELECTED, REJECTED, NEEDS_VERIFICATION)

# Severity ordering used to combine multiple gate checks: a later check may
# only escalate the outcome, never soften an earlier REJECTED/
# NEEDS_VERIFICATION back down (e.g. a stale-evidence downgrade must never
# erase an already-REJECTED hard-constraint mismatch).
_SEVERITY = {SELECTED: 0, NEEDS_VERIFICATION: 1, REJECTED: 2}


class TargetJournalProfileConsumerError(ValueError):
    """Raised on a wrong protocol, a missing required field, or an attempt
    to build a style-context seed from a REJECTED selection."""


@dataclass
class TargetJournalProfile:
    name: str
    freshness: str
    provenance: dict
    issn: Optional[str] = None
    scope_summary: Optional[str] = None
    indexing: list = field(default_factory=list)
    apc_status: Optional[str] = None
    oa_status: Optional[str] = None
    fit_assessment: Optional[str] = None


def from_target_journal_profile_v1(data: dict) -> TargetJournalProfile:
    """Validate and translate an incoming TARGET_JOURNAL_PROFILE_V1
    envelope. Raises TargetJournalProfileConsumerError on a wrong protocol
    or a missing required field -- never silently coerces a malformed
    payload."""
    if data.get("protocol") != PROTOCOL:
        raise TargetJournalProfileConsumerError(
            f"not a {PROTOCOL} envelope: protocol={data.get('protocol')!r}"
        )
    missing = {"name", "freshness", "provenance"} - set(data)
    if missing:
        raise TargetJournalProfileConsumerError(
            f"{PROTOCOL} envelope missing required field(s): {sorted(missing)}"
        )
    return TargetJournalProfile(
        name=data["name"],
        freshness=data["freshness"],
        provenance=dict(data["provenance"]),
        issn=data.get("issn"),
        scope_summary=data.get("scope_summary"),
        indexing=list(data.get("indexing") or []),
        apc_status=data.get("apc_status"),
        oa_status=data.get("oa_status"),
        fit_assessment=data.get("fit_assessment"),
    )


@dataclass
class SelectionResult:
    status: str
    reasons: list
    limitations: list
    provenance: dict


def _elevate(current: str, candidate: str) -> str:
    return candidate if _SEVERITY[candidate] > _SEVERITY[current] else current


def evaluate_target_journal_profile(
    profile: TargetJournalProfile, hard_constraints: Optional[dict] = None
) -> SelectionResult:
    """Gate a parsed profile against the manuscript's own stated hard
    constraints (typically MANUSCRIPT_PROFILE_V1.constraints -- e.g.
    `no_mandatory_apc`, `requires_indexing`). An unrequested constraint is
    never checked -- this function does not widen the checked set beyond
    what the caller actually asked for.

    Recognized hard_constraints keys:
      no_mandatory_apc (bool)      -- REJECTED if profile.apc_status ==
          "apc-required"; NEEDS_VERIFICATION if apc_status is unknown/absent
          (CANNOT_VERIFY is not a failure -- it is just unresolved).
      requires_indexing (list[str]) -- any requested index not present in
          profile.indexing is NEEDS_VERIFICATION, never REJECTED: the
          profile's `indexing` list only ever carries officially-verified
          entries, so absence means "not confirmed," not "confirmed absent."

    Every NEEDS_VERIFICATION-driving fact (unresolved apc_status, an
    unconfirmed requested index) is recorded in both `reasons` (the gate's
    own rationale) and `limitations` (the subset that must keep surviving
    into whatever artifact is built next -- see journal_style_context_seed);
    a REJECTED verdict's reason is not duplicated into `limitations` since
    journal_style_context_seed refuses to build past a REJECTED status at
    all.
    """
    hard_constraints = hard_constraints or {}
    reasons: list = []
    limitations: list = []
    status = SELECTED
    checked_a_perishable_fact = False

    if hard_constraints.get("no_mandatory_apc"):
        checked_a_perishable_fact = True
        if profile.apc_status == "apc-required":
            status = _elevate(status, REJECTED)
            reasons.append(
                f"{profile.name!r} has apc_status='apc-required'; manuscript states "
                "no_mandatory_apc -- hard mismatch."
            )
        elif profile.apc_status in (None, "unknown"):
            status = _elevate(status, NEEDS_VERIFICATION)
            note = (
                f"{profile.name!r} apc_status is unknown; cannot confirm the "
                "no_mandatory_apc constraint from this profile alone."
            )
            reasons.append(note)
            limitations.append(note)
        else:
            reasons.append(
                f"{profile.name!r} apc_status={profile.apc_status!r} satisfies the "
                "manuscript's no_mandatory_apc constraint."
            )

    requested_indexing = hard_constraints.get("requires_indexing") or []
    if requested_indexing:
        checked_a_perishable_fact = True
        unmet = [idx for idx in requested_indexing if idx not in profile.indexing]
        if unmet:
            status = _elevate(status, NEEDS_VERIFICATION)
            note = (
                f"{profile.name!r} profile does not confirm required indexing "
                f"{sorted(unmet)}; absence from a verified-only list is not evidence "
                "of non-inclusion."
            )
            reasons.append(note)
            limitations.append(note)
        met = [idx for idx in requested_indexing if idx in profile.indexing]
        if met:
            reasons.append(f"{profile.name!r} confirms required indexing {sorted(met)}.")

    if profile.freshness == "stale":
        limitations.append(
            f"target journal profile for {profile.name!r} is stale; re-verify before "
            "relying on it for a submission decision."
        )
        if checked_a_perishable_fact:
            status = _elevate(status, NEEDS_VERIFICATION)
            reasons.append(
                f"{profile.name!r} profile is stale and a hard constraint depends on a "
                "fact that can change over time; re-verify before treating this journal "
                "as selected."
            )

    return SelectionResult(
        status=status, reasons=reasons, limitations=limitations,
        provenance=dict(profile.provenance),
    )


def journal_style_context_seed(profile: TargetJournalProfile, selection: SelectionResult) -> dict:
    """The subset of a TARGET_JOURNAL_PROFILE_V1 that may safely seed a
    JOURNAL_STYLE_CONTEXT_V1 build
    (jfe.style_context.build_journal_style_context) -- identity, freshness,
    provenance-as-evidence, and limitations only.

    Deliberately excludes fit_assessment/apc_status/oa_status/indexing:
    those answer "is this a plausible target?", not "how should the
    manuscript be written for it?". `official_requirements` and
    `observed_patterns` must still come from their own real sources (a host
    LLM's guideline fetch, scholarly-corpus-builder) -- this function never
    invents either.

    Raises TargetJournalProfileConsumerError if `selection.status ==
    REJECTED`: a rejected target should not be adapted for unless the user
    explicitly overrides the gate -- check `selection.status` before
    calling this.
    """
    if selection.status == REJECTED:
        raise TargetJournalProfileConsumerError(
            f"{profile.name!r} was REJECTED by the hard compatibility gate "
            f"({'; '.join(selection.reasons)}); build a style context only on an "
            "explicit user override, never automatically."
        )
    seed = {
        "journal_name": profile.name,
        "freshness": profile.freshness,
        "evidence": [dict(profile.provenance)],
    }
    if selection.limitations:
        seed["limitations"] = list(selection.limitations)
    return seed
