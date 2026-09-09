"""Journal integrity screening (references/journal-integrity.md). Reports
VERIFIED / WARNING / CANNOT_VERIFY per signal -- never a "predatory
probability" or a blanket verdict. A journal is never labeled "predatory"
here; that is a strong, reputational claim SKILL.md reserves for the LLM's
own reasoning over evidence this module cannot gather (editorial-board
transparency, peer-review description, archiving participation, COPE
membership -- none of which OpenAlex/Crossref expose). This module checks
only what its two index adapters can actually see: identity completeness,
cross-source identity consistency, recent activity, and APC/OA
transparency. Discontinuation-status detail (ceased/renamed/merged) beyond
the recent-activity proxy is out of scope here for the same reason.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from jfe.hard_filters import CANNOT_VERIFY as HF_CANNOT_VERIFY, FAIL as HF_FAIL, PASS as HF_PASS, check_inactive
from jfe.journal_evidence import JournalEvidence

VERIFIED = "VERIFIED"
WARNING = "WARNING"
CANNOT_VERIFY = "CANNOT_VERIFY"

_ACTIVITY_STATE_MAP = {HF_PASS: VERIFIED, HF_FAIL: WARNING, HF_CANNOT_VERIFY: CANNOT_VERIFY}


@dataclass
class IntegrityCheck:
    name: str
    result: str
    reason: str


@dataclass
class IntegrityScreen:
    checks: list
    overall: str


def check_identity_completeness(evidence: JournalEvidence) -> IntegrityCheck:
    has_issn = bool(evidence.issn_l or evidence.issn)
    has_publisher = bool(evidence.publisher)
    if has_issn and has_publisher:
        return IntegrityCheck("identity_completeness", VERIFIED,
                               f"Index records both an ISSN and a publisher ({evidence.publisher}) for this source.")
    missing = [n for n, present in (("ISSN", has_issn), ("publisher", has_publisher)) if not present]
    return IntegrityCheck("identity_completeness", WARNING,
                           f"Index is missing {', '.join(missing)} for this source -- identity is not fully "
                           "verifiable from this evidence alone; check the journal's own official page.")


def check_cross_source_consistency(primary: JournalEvidence,
                                    secondary: Optional[JournalEvidence]) -> IntegrityCheck:
    """Compares identity fields between two independently-fetched
    JournalEvidence records (e.g. one from OpenAlex, one from Crossref) for
    the same journal. `secondary` is optional -- jfe.journal_evidence's
    lookup functions only ever return one adapter's result -- a caller that
    wants this check populated must fetch a second adapter explicitly."""
    if secondary is None:
        return IntegrityCheck("cross_source_consistency", CANNOT_VERIFY,
                               "Only one index source was queried; cross-source identity consistency was not checked.")
    primary_issn = set(primary.issn) | ({primary.issn_l} if primary.issn_l else set())
    secondary_issn = set(secondary.issn) | ({secondary.issn_l} if secondary.issn_l else set())
    conflicts = []
    if primary_issn and secondary_issn and not (primary_issn & secondary_issn):
        conflicts.append(f"ISSN sets do not overlap: {sorted(primary_issn)} vs {sorted(secondary_issn)}")
    if primary.publisher and secondary.publisher and primary.publisher.strip().lower() != secondary.publisher.strip().lower():
        conflicts.append(f"publisher differs: {primary.publisher!r} vs {secondary.publisher!r}")
    if conflicts:
        return IntegrityCheck("cross_source_consistency", WARNING, "; ".join(conflicts))
    if not (primary_issn or secondary_issn):
        return IntegrityCheck("cross_source_consistency", CANNOT_VERIFY,
                               "Neither source recorded an ISSN to cross-check.")
    return IntegrityCheck("cross_source_consistency", VERIFIED,
                           f"ISSN/publisher agree between {primary.source} and {secondary.source}.")


def check_activity(evidence: JournalEvidence, current_year: Optional[int] = None) -> IntegrityCheck:
    filt = check_inactive(evidence, current_year)
    return IntegrityCheck("recent_activity", _ACTIVITY_STATE_MAP[filt.result], filt.reason)


def check_apc_transparency(evidence: JournalEvidence) -> IntegrityCheck:
    if evidence.is_oa is None:
        return IntegrityCheck("apc_transparency", CANNOT_VERIFY,
                               "OA status not resolved by the index; APC transparency cannot be assessed.")
    if evidence.is_oa and evidence.apc_usd is None:
        return IntegrityCheck("apc_transparency", WARNING,
                               "Journal is marked open access but the index has no APC figure -- verify the fee "
                               "(or its absence) directly on the journal's own page before assuming diamond OA.")
    return IntegrityCheck("apc_transparency", VERIFIED,
                           "Index records a definite fee state (APC amount present) for this source."
                           if evidence.apc_usd is not None else
                           "Journal is not marked open access; no mandatory gold-OA APC expected via this route.")


def screen(evidence: JournalEvidence, secondary: Optional[JournalEvidence] = None,
           current_year: Optional[int] = None) -> IntegrityScreen:
    checks = [
        check_identity_completeness(evidence),
        check_cross_source_consistency(evidence, secondary),
        check_activity(evidence, current_year),
        check_apc_transparency(evidence),
    ]
    if any(c.result == WARNING for c in checks):
        overall = WARNING
    elif any(c.result == CANNOT_VERIFY for c in checks):
        overall = CANNOT_VERIFY
    else:
        overall = VERIFIED
    return IntegrityScreen(checks, overall)
