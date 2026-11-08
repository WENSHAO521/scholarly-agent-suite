"""TARGET_JOURNAL_PROFILE_V1 producer
(scholarly-agent-suite/protocols/journal-profile.schema.json).

Composes journal-fit-engine's existing evidence-backed modules
(jfe.journal_evidence, jfe.apc_oa, jfe.fit_model, jfe.indexing,
jfe.integrity) into the canonical envelope Suite workflows (e.g.
workflows/target-journal-adaptation.md) consume for one resolved candidate
journal. A pure adapter/serializer, not a second fact-gathering layer: it
never re-derives evidence itself, and every optional field it cannot
honestly support from the objects handed to it is simply left out of the
envelope -- the schema requires only protocol/name/freshness/provenance --
rather than guessed or defaulted to a value that looks more complete than
the evidence actually is.

Deliberately narrower than references/journal-profile.md's full journal-
profile concept (audience, word limits, submission rules, editorial
process, discontinuation detail -- SKILL.md-scoped LLM-reasoning tasks):
this module only covers what the existing evidence-backed modules can
mechanically verify, and TARGET_JOURNAL_PROFILE_V1's schema has no field
for the rest.
"""
from __future__ import annotations

from typing import Optional

from jfe.apc_oa import (
    APCClassification,
    DIAMOND_OA,
    HYBRID_OA_OPTIONAL,
    MANDATORY_APC,
)
from jfe.fit_model import (
    EXCELLENT_FIT,
    FitResult,
    NOT_RECOMMENDED,
    PLAUSIBLE_FIT,
    STRETCH,
    STRONG_FIT as FIT_MODEL_STRONG_FIT,
    WEAK_FIT as FIT_MODEL_WEAK_FIT,
)
from jfe.indexing import IndexingAssessment, OFFICIALLY_VERIFIED
from jfe.integrity import IntegrityScreen, VERIFIED as INTEGRITY_VERIFIED, WARNING as INTEGRITY_WARNING
from jfe.journal_evidence import JournalEvidence
from jfe.style_context import compute_freshness

PROTOCOL = "TARGET_JOURNAL_PROFILE_V1"
PROVENANCE_PROTOCOL = "PROVENANCE_RECORD_V1"

# Schema's fit_assessment enum (journal-profile.schema.json) -- a different,
# coarser vocabulary than fit_model's own 6-label scale.
STRONG_FIT = "STRONG_FIT"
MODERATE_FIT = "MODERATE_FIT"
WEAK_FIT = "WEAK_FIT"
NOT_ASSESSED = "NOT_ASSESSED"

_FIT_LABEL_MAP = {
    EXCELLENT_FIT: STRONG_FIT,
    FIT_MODEL_STRONG_FIT: STRONG_FIT,
    PLAUSIBLE_FIT: MODERATE_FIT,
    STRETCH: WEAK_FIT,
    FIT_MODEL_WEAK_FIT: WEAK_FIT,
    NOT_RECOMMENDED: WEAK_FIT,
}

_SOURCE_LABELS = {
    "openalex": "OpenAlex",
    "crossref": "Crossref",
    "openalex+crossref": "OpenAlex/Crossref",
}


class TargetJournalProfileError(Exception):
    """Raised when the evidence handed in cannot honestly support the
    envelope's required fields -- never silently filled with a guess."""


def _primary_issn(evidence: JournalEvidence) -> Optional[str]:
    if evidence.issn_l:
        return evidence.issn_l
    if evidence.issn:
        return evidence.issn[0]
    return None


def _scope_summary(evidence: JournalEvidence) -> Optional[str]:
    if not evidence.topics:
        return None
    source_label = _SOURCE_LABELS.get(evidence.source, evidence.source or "index")
    return (
        f"Indexed subject areas ({source_label}, not the journal's own scope "
        f"statement): {', '.join(evidence.topics)}."
    )


def _apc_oa_status(apc: Optional[APCClassification]):
    if apc is None:
        return None, None
    if apc.state == MANDATORY_APC:
        return "apc-required", "fully-oa"
    if apc.state == DIAMOND_OA:
        return "no-apc", "fully-oa"
    if apc.state == HYBRID_OA_OPTIONAL:
        # No mandatory fee applies to the default (non-OA) publication
        # path; OA is available only for an optional fee. oa_status
        # carries that nuance so "no-apc" here is never read as "fully
        # free OA" -- the two fields must be read together.
        return "no-apc", "hybrid"
    return "unknown", "unknown"


def _fit_assessment(fit: Optional[FitResult], evidence: JournalEvidence) -> str:
    if fit is None:
        return NOT_ASSESSED
    if not fit.hard_eliminated and not evidence.topics:
        # fit_model.compute_fit's own label conflates "no topic data to
        # evaluate" with NOT_RECOMMENDED (topic-overlap score defaults to
        # 0.0 either way). This schema's whole point is a qualitative,
        # never-fabricated verdict, so a producer sitting on top of it must
        # not repeat that conflation -- "we could not assess this" and "we
        # assessed this as a poor fit" are different claims.
        return NOT_ASSESSED
    return _FIT_LABEL_MAP.get(fit.label, NOT_ASSESSED)


def _indexing_list(indexing: Optional[IndexingAssessment]) -> list:
    if indexing is None:
        return []
    # "as verified, not assumed" (schema): only entries this Skill's
    # adapters actually confirmed, never the CANNOT_VERIFY placeholders
    # indexing.assess_indexing() also returns for the unreachable paid
    # indexes/metrics.
    return [e.name for e in indexing.entries if e.state == OFFICIALLY_VERIFIED and e.value]


def _provenance(evidence: JournalEvidence, integrity: Optional[IntegrityScreen]) -> dict:
    if not evidence.checked_at:
        raise TargetJournalProfileError(
            "evidence.checked_at is required to build a PROVENANCE_RECORD_V1 "
            "retrieval_date -- never fabricated as 'now'."
        )
    identity = _primary_issn(evidence) or evidence.homepage_url or evidence.display_name
    if not identity:
        raise TargetJournalProfileError(
            "evidence has no ISSN, homepage_url, or display_name to use as a "
            "provenance source identity."
        )
    access_status = "metadata-only" if evidence.source in ("openalex", "crossref", "openalex+crossref") else "unknown"
    source_entry = {"identity": identity, "access_status": access_status}
    if evidence.source and evidence.source != "unknown":
        source_entry["index"] = evidence.source

    verification_status = "unverified"
    conflict_notes = []
    if integrity is not None:
        cross_source = next(
            (c for c in integrity.checks if c.name == "cross_source_consistency"), None
        )
        if cross_source is not None:
            if cross_source.result == INTEGRITY_VERIFIED:
                verification_status = "verified"
            elif cross_source.result == INTEGRITY_WARNING:
                verification_status = "conflicting"
                conflict_notes.append(cross_source.reason)
            # CANNOT_VERIFY (no secondary source queried) leaves the honest
            # default: "unverified".

    record = {
        "protocol": PROVENANCE_PROTOCOL,
        "sources": [source_entry],
        "retrieval_date": evidence.checked_at[:10],
        "verification_status": verification_status,
    }
    if conflict_notes:
        record["conflict_notes"] = conflict_notes
    return record


def build_target_journal_profile(
    evidence: JournalEvidence,
    *,
    fit_result: Optional[FitResult] = None,
    apc_classification: Optional[APCClassification] = None,
    indexing_assessment: Optional[IndexingAssessment] = None,
    integrity: Optional[IntegrityScreen] = None,
) -> dict:
    """Assemble and validate a TARGET_JOURNAL_PROFILE_V1 envelope from
    already-computed jfe evidence/results.

    Every keyword argument is optional and independently omittable -- a
    caller that only has `evidence` (e.g. a bare lookup-journal result,
    with no manuscript to evaluate fit against) still gets a valid, if
    thinner, envelope; `fit_assessment` becomes NOT_ASSESSED rather than
    the call failing. Only `evidence` itself, `evidence.display_name`, and
    `evidence.checked_at` are hard requirements, because the schema
    requires `name`, `freshness`, and `provenance.retrieval_date` and none
    of those may be fabricated.
    """
    if not evidence.display_name:
        raise TargetJournalProfileError("evidence.display_name is required as the profile's 'name'.")

    profile = {
        "protocol": PROTOCOL,
        "name": evidence.display_name,
        "freshness": compute_freshness(evidence.checked_at),
        "provenance": _provenance(evidence, integrity),
    }

    issn = _primary_issn(evidence)
    if issn:
        profile["issn"] = issn

    scope_summary = _scope_summary(evidence)
    if scope_summary:
        profile["scope_summary"] = scope_summary

    indexing_list = _indexing_list(indexing_assessment)
    if indexing_list:
        profile["indexing"] = indexing_list

    apc_status, oa_status = _apc_oa_status(apc_classification)
    if apc_status:
        profile["apc_status"] = apc_status
    if oa_status:
        profile["oa_status"] = oa_status

    profile["fit_assessment"] = _fit_assessment(fit_result, evidence)

    return profile
