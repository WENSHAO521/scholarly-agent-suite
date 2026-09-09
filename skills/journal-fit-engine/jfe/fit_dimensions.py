"""Expanded evidence-backed fit dimensions (SKILL.md core workflow step 4,
references/fit-model.md, references/adaptation-policy.md). Each dimension
returns one of six categorical labels -- never a numeric score or
probability (SKILL.md's no-fake-precision rule applies here exactly as it
does to fit_model.py's overall verdict).

This module supplements, not replaces, fit_model.compute_fit(): that
function remains the single overall recommended/eliminated verdict. The
dimensions here are the itemized, per-axis evidence a caller can show for
"why this journal?" (SKILL.md's Output contract) or "why not" -- several of
them are honestly CANNOT_VERIFY or NOT_APPLICABLE because this Skill's two
free, keyless adapters (OpenAlex Sources, Crossref Journals) do not expose
that evidence; that is reported plainly rather than guessed.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from jfe.apc_oa import MANDATORY_APC, UNKNOWN as APC_UNKNOWN, classify as classify_apc_oa
from jfe.fit_model import _topic_overlap
from jfe.hard_filters import CANNOT_VERIFY as HF_CANNOT_VERIFY, FAIL as HF_FAIL, PASS as HF_PASS, check_inactive
from jfe.journal_evidence import JournalEvidence
from jfe.manuscript_profile import ManuscriptProfile, tokenize

MATCH = "MATCH"
PARTIAL_MATCH = "PARTIAL_MATCH"
WEAK_MATCH = "WEAK_MATCH"
MISMATCH = "MISMATCH"
CANNOT_VERIFY = "CANNOT_VERIFY"
NOT_APPLICABLE = "NOT_APPLICABLE"

_ACTIVITY_STATE_MAP = {HF_PASS: MATCH, HF_FAIL: MISMATCH, HF_CANNOT_VERIFY: CANNOT_VERIFY}


@dataclass
class DimensionResult:
    dimension: str
    result: str
    note: str


def _topic_like(manuscript_keywords: list, journal_topics: list, empty_note: str) -> tuple:
    if not manuscript_keywords or not journal_topics:
        return CANNOT_VERIFY, empty_note
    score, matched = _topic_overlap(manuscript_keywords, journal_topics)
    if score >= 0.55:
        return MATCH, f"Strong overlap: {', '.join(matched)}."
    if score >= 0.20:
        return PARTIAL_MATCH, f"Partial overlap: {', '.join(matched) if matched else 'none'}."
    if matched:
        return WEAK_MATCH, f"Weak overlap: {', '.join(matched)}."
    return MISMATCH, "No overlap found between the manuscript's keywords and this journal's indexed topics."


def scope_fit(manuscript: ManuscriptProfile, evidence: JournalEvidence) -> DimensionResult:
    """Coarse discipline/subdiscipline match against the journal's indexed
    topics -- distinct from topic_fit's finer-grained keyword overlap."""
    keyword_bag = sorted(tokenize(manuscript.discipline) | tokenize(manuscript.subdiscipline))
    result, note = _topic_like(keyword_bag, evidence.topics,
                                "This index has no topic data for the journal; scope fit could not be evaluated.")
    return DimensionResult("scope_fit", result, note)


def topic_fit(manuscript: ManuscriptProfile, evidence: JournalEvidence) -> DimensionResult:
    result, note = _topic_like(manuscript.keywords(), evidence.topics,
                                "This index has no topic data for the journal; topic fit could not be evaluated.")
    return DimensionResult("topic_fit", result, note)


def article_type_fit(manuscript: ManuscriptProfile) -> DimensionResult:
    if not manuscript.article_type:
        return DimensionResult("article_type_fit", NOT_APPLICABLE, "Manuscript article_type not stated.")
    return DimensionResult("article_type_fit", CANNOT_VERIFY,
                            "Accepted article types are not exposed by OpenAlex/Crossref index data; "
                            "check the journal's own author guidelines.")


def method_fit(manuscript: ManuscriptProfile) -> DimensionResult:
    if not manuscript.methods:
        return DimensionResult("method_fit", NOT_APPLICABLE, "Manuscript methods not stated.")
    return DimensionResult("method_fit", CANNOT_VERIFY,
                            "No per-journal method-prevalence evidence is available from this Skill's adapters.")


def audience_fit(manuscript: ManuscriptProfile) -> DimensionResult:
    if not manuscript.audience:
        return DimensionResult("audience_fit", NOT_APPLICABLE, "Manuscript audience not stated.")
    return DimensionResult("audience_fit", CANNOT_VERIFY,
                            "No per-journal audience evidence is available from this Skill's adapters.")


def activity_recency(evidence: JournalEvidence, current_year: Optional[int] = None) -> DimensionResult:
    filt = check_inactive(evidence, current_year)
    return DimensionResult("activity_recency", _ACTIVITY_STATE_MAP[filt.result], filt.reason)


def apc_constraint_fit(manuscript: ManuscriptProfile, evidence: JournalEvidence) -> DimensionResult:
    if not manuscript.constraints.get("no_mandatory_apc"):
        return DimensionResult("apc_constraint_fit", NOT_APPLICABLE, "No no_mandatory_apc constraint stated.")
    apc = classify_apc_oa(evidence)
    if apc.state == MANDATORY_APC:
        return DimensionResult("apc_constraint_fit", MISMATCH, apc.note)
    if apc.state == APC_UNKNOWN:
        return DimensionResult("apc_constraint_fit", CANNOT_VERIFY, apc.note)
    return DimensionResult("apc_constraint_fit", MATCH, apc.note)


def oa_model_fit(manuscript: ManuscriptProfile, evidence: JournalEvidence) -> DimensionResult:
    """Reads an optional `requires_oa: bool` manuscript constraint -- a
    natural extension of ManuscriptProfile.constraints (already a free-form
    dict; see references/manuscript-profile.md), not a schema change."""
    requires_oa = manuscript.constraints.get("requires_oa")
    if requires_oa is None:
        return DimensionResult("oa_model_fit", NOT_APPLICABLE, "No requires_oa constraint stated.")
    if evidence.is_oa is None:
        return DimensionResult("oa_model_fit", CANNOT_VERIFY, "Index did not resolve OA status for this source.")
    if bool(requires_oa) == bool(evidence.is_oa):
        return DimensionResult("oa_model_fit", MATCH,
                                f"Manuscript requires OA={bool(requires_oa)}; index reports is_oa={evidence.is_oa}.")
    return DimensionResult("oa_model_fit", MISMATCH,
                            f"Manuscript requires OA={bool(requires_oa)}; index reports is_oa={evidence.is_oa}.")


def journal_integrity_fit(evidence: JournalEvidence,
                           secondary: Optional[JournalEvidence] = None) -> DimensionResult:
    from jfe.integrity import WARNING as INT_WARNING, VERIFIED as INT_VERIFIED, screen as integrity_screen

    result = integrity_screen(evidence, secondary)
    label = {INT_VERIFIED: MATCH, INT_WARNING: WEAK_MATCH}.get(result.overall, CANNOT_VERIFY)
    notes = "; ".join(f"{c.name}={c.result}" for c in result.checks)
    return DimensionResult("journal_integrity", label, notes)


def indexing_evidence_fit(manuscript: ManuscriptProfile, evidence: JournalEvidence) -> DimensionResult:
    """Reads an optional `requires_indexing: list[str]` manuscript
    constraint. Only "DOAJ" is actually checkable by this Skill's adapters
    (see jfe.indexing) -- any other requested index is honestly
    CANNOT_VERIFY, never assumed satisfied or unsatisfied."""
    requested = manuscript.constraints.get("requires_indexing")
    if not requested:
        return DimensionResult("indexing_evidence", NOT_APPLICABLE, "No requires_indexing constraint stated.")
    requested = [str(r).upper() for r in requested]
    unchecked = [r for r in requested if r != "DOAJ"]
    if "DOAJ" not in requested:
        return DimensionResult(
            "indexing_evidence", CANNOT_VERIFY,
            f"Cannot verify: {', '.join(unchecked)} -- requires an authenticated/paid index this "
            "Skill's adapters do not query.",
        )
    if evidence.is_in_doaj is None:
        note = "Index did not report a DOAJ inclusion flag for this source."
    elif evidence.is_in_doaj:
        note = "Confirmed in DOAJ."
    else:
        note = "Not confirmed in DOAJ by this index."
    if unchecked:
        note += f" Cannot verify: {', '.join(unchecked)}."
    if evidence.is_in_doaj is None:
        return DimensionResult("indexing_evidence", CANNOT_VERIFY, note)
    return DimensionResult("indexing_evidence", MATCH if evidence.is_in_doaj else MISMATCH, note)


def requirement_compatibility_fit(manuscript: ManuscriptProfile,
                                   official_requirements: Optional[dict]) -> DimensionResult:
    """Compares the manuscript against a caller-supplied official_requirements
    dict (typically the same one used to build a JOURNAL_STYLE_CONTEXT_V1
    envelope via jfe.style_context -- see that module). This Skill's own
    adapters never populate official_requirements themselves (OpenAlex/
    Crossref are bibliographic indexes, not author-guideline sources)."""
    if not official_requirements:
        return DimensionResult("requirement_compatibility", CANNOT_VERIFY,
                                "No official_requirements supplied; verify the journal's own author "
                                "guidelines directly.")
    word_limit = official_requirements.get("word_limit")
    if word_limit is None or manuscript.word_count is None:
        return DimensionResult("requirement_compatibility", CANNOT_VERIFY,
                                "word_limit and/or manuscript word_count not both stated.")
    if manuscript.word_count <= word_limit:
        return DimensionResult("requirement_compatibility", MATCH,
                                f"Manuscript word_count={manuscript.word_count} is within the stated "
                                f"word_limit={word_limit}.")
    return DimensionResult("requirement_compatibility", MISMATCH,
                            f"Manuscript word_count={manuscript.word_count} exceeds the stated "
                            f"word_limit={word_limit}.")


def assess_all(manuscript: ManuscriptProfile, evidence: JournalEvidence, *,
               secondary: Optional[JournalEvidence] = None,
               official_requirements: Optional[dict] = None,
               current_year: Optional[int] = None) -> list:
    """All 11 dimensions from references/fit-model.md's expanded fit model,
    in the order documented there. Never aggregated into a single number --
    a caller (or the LLM's own reasoning) weighs these against the
    manuscript's actual priorities."""
    return [
        scope_fit(manuscript, evidence),
        topic_fit(manuscript, evidence),
        article_type_fit(manuscript),
        method_fit(manuscript),
        audience_fit(manuscript),
        activity_recency(evidence, current_year),
        apc_constraint_fit(manuscript, evidence),
        oa_model_fit(manuscript, evidence),
        journal_integrity_fit(evidence, secondary),
        indexing_evidence_fit(manuscript, evidence),
        requirement_compatibility_fit(manuscript, official_requirements),
    ]
