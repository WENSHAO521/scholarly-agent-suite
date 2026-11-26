"""Profile Compiler and Cross-Skill Protocols (PART XXXVII-XLIII).

Turns a measured corpus profile into a usable writing policy while
keeping three statuses strictly distinct (PART XXXVIII):

  OBSERVED    a pattern found in the sampled corpus — descriptive only
  RECOMMENDED a suggestion this compiler derived from that pattern
  MANDATORY   only ever set from caller-supplied official requirements
              (e.g. a journal's actual author guidelines) — this module
              never invents a MANDATORY statement from observed data.

Also builds the three standardized output contracts downstream skills
consume (SCHOLARLY_PROFILE_V1, VOICE_CONTEXT_V1, JOURNAL_STYLE_CONTEXT_V1)
so this skill returns compact profiles, not raw corpora, by default
(references/integration.md).
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional

OBSERVED = "OBSERVED"
RECOMMENDED = "RECOMMENDED"
MANDATORY = "MANDATORY"

PROTOCOL_SCHOLARLY_PROFILE_V1 = "SCHOLARLY_PROFILE_V1"
PROTOCOL_VOICE_CONTEXT_V1 = "VOICE_CONTEXT_V1"
PROTOCOL_JOURNAL_STYLE_CONTEXT_V1 = "JOURNAL_STYLE_CONTEXT_V1"

# Downstream voice precedence (PART XXXVI): author > discipline > journal > historical.
VOICE_PRECEDENCE = ["author", "discipline", "journal", "historical"]


@dataclass
class PolicyStatement:
    text: str
    status: str  # OBSERVED | RECOMMENDED | MANDATORY
    basis: str
    confidence: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def compile_scholarly_profile_v1(
    profile_type: str,
    target: str,
    style_profile: Dict[str, Any],
    stability_status: Optional[str] = None,
    provenance_summary: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    return {
        "protocol": PROTOCOL_SCHOLARLY_PROFILE_V1,
        "profile_type": profile_type,
        "target": target,
        "measured_features": {
            "sentence": style_profile.get("sentence_style") or style_profile.get("sentence"),
            "paragraph": style_profile.get("paragraph_style") or style_profile.get("paragraph"),
            "lexical": style_profile.get("lexical"),
            "citations": style_profile.get("citation_behavior") or style_profile.get("citations"),
        },
        "inferred_features": {
            "claims": style_profile.get("claims") or style_profile.get("claim_conventions"),
            "rhetorical_moves": style_profile.get("rhetorical_moves") or style_profile.get("argument_moves"),
            "intellectual_rhythm": style_profile.get("intellectual_rhythm") or style_profile.get("argument_architecture"),
        },
        "confidence": style_profile.get("confidence"),
        "sample_size": style_profile.get("sample_size") or style_profile.get("source_count"),
        "sample_size_label": style_profile.get("sample_size_label"),
        "stability": stability_status or "not_evaluated",
        "provenance_summary": provenance_summary or [],
        "known_biases": style_profile.get("known_biases", []),
    }


# --- Schema-conformant SCHOLARLY_PROFILE_V1 (protocols/scholarly-profile.schema.json)
#
# compile_scholarly_profile_v1() above predates the shared protocol schema and
# emits a looser shape (provenance_summary instead of a PROVENANCE_RECORD_V1,
# a per-feature confidence dict, scb-internal stability labels). It is kept
# unchanged for existing callers. compile_scholarly_profile_protocol_v1() is
# the producer other modules consume: its output validates against the
# schema (additionalProperties: false), and every narrowing it performs is
# recorded in `biases` rather than silently dropped.

_SCHEMA_CONFIDENCE = {"low": "low", "medium": "moderate", "moderate": "moderate", "high": "high"}
_CONFIDENCE_ORDER = ["low", "moderate", "high"]
_MEASURED_KEYS = ("sentence", "paragraph", "lexical", "citations")
_INFERRED_KEYS = ("claims", "rhetorical_moves", "intellectual_rhythm")


def _overall_schema_confidence(confidence: Any) -> str:
    """The weakest measured-feature confidence, mapped onto the schema enum.
    Inferred features are excluded because they are reported separately and
    are low-confidence by design; taking the minimum never overstates."""
    if isinstance(confidence, str):
        return _SCHEMA_CONFIDENCE.get(confidence, "low")
    if not isinstance(confidence, dict) or not confidence:
        return "low"
    values = [confidence.get(k) for k in _MEASURED_KEYS if confidence.get(k)]
    if not values:
        values = [confidence.get("overall") or "low"]
    mapped = [_SCHEMA_CONFIDENCE.get(v, "low") for v in values]
    return min(mapped, key=_CONFIDENCE_ORDER.index)


PROTOCOL_PROVENANCE_RECORD_V1 = "PROVENANCE_RECORD_V1"
_USER_ADAPTERS = {"user_files", "user_bibliography"}


def _source_identity(record: Any) -> tuple:
    """(identity, is_identified). Never a title/author guess
    (shared/provenance-policy.md: 'Source identity')."""
    ids = record.identifiers
    if ids.doi:
        return ids.doi, True
    for scheme, value in (("pmid", ids.pmid), ("pmcid", ids.pmcid), ("arxiv", ids.arxiv_id)):
        if value:
            return "%s:%s" % (scheme, value), True
    if record.access.best_url:
        return record.access.best_url, True
    adapters = {p.adapter for p in record.provenance}
    if adapters & _USER_ADAPTERS:
        return "user-supplied:%s" % record.record_id, True
    return "record:%s" % record.record_id, False


def _access_status(record: Any, verified: bool) -> str:
    adapters = {p.adapter for p in record.provenance}
    if "user_files" in adapters or (adapters & _USER_ADAPTERS and not verified):
        return "user-supplied"
    if record.access.is_oa:
        return "open-access"
    if record.access.readable is False:
        return "access-restricted"
    if record.access.is_oa is False:
        return "metadata-only"
    return "unknown"


def build_provenance_record_v1(records: List[Any], retrieval_date: Optional[str] = None) -> Dict[str, Any]:
    """Build a PROVENANCE_RECORD_V1 from the CanonicalRecords a profile was
    built from -- the real producer for the record that
    compile_scholarly_profile_protocol_v1() requires.

    - A source counts as verified only if one of its provenance entries is
      VERIFIED (an adapter lookup confirmed it); user-imported metadata
      (scb.bibliography) stays unverified until then.
    - Overall status: all verified -> verified; none -> unverified; mixed ->
      partially-verified; any recorded field conflict or unidentified source
      -> conflicting, with one conflict note per issue (never silently
      resolved).
    - retrieval_date is the caller's date, else the latest retrieved_at on
      the records. With neither, it raises instead of inventing a date.
    """
    if not records:
        raise ValueError("PROVENANCE_RECORD_V1 needs at least one source record")
    sources: List[Dict[str, Any]] = []
    notes: List[str] = []
    verified_flags: List[bool] = []
    dates: List[str] = []
    for record in records:
        verified = any(p.verification == "VERIFIED" for p in record.provenance)
        verified_flags.append(verified)
        identity, identified = _source_identity(record)
        if not identified:
            notes.append("%s: no DOI, PMID, arXiv ID, or URL; source identity unconfirmed" % record.record_id)
        for conflict in record.conflicts or []:
            field = conflict.get("field", "?")
            issue = conflict.get("issue") or "values disagree"
            notes.append("%s: %s: %s" % (identity, field, issue))
        sources.append({
            "identity": identity,
            "access_status": _access_status(record, verified),
            "verification": "VERIFIED" if verified else "NEEDS_CHECK",
            "via": sorted({p.adapter for p in record.provenance}),
        })
        for stamp in [record.retrieved_at] + [p.retrieved_at for p in record.provenance]:
            if stamp:
                dates.append(str(stamp)[:10])
    if retrieval_date is None:
        if not dates:
            raise ValueError("no retrieval date given and none recorded on the source records")
        retrieval_date = max(dates)
    if notes:
        status = "conflicting"
    elif all(verified_flags):
        status = "verified"
    elif any(verified_flags):
        status = "partially-verified"
    else:
        status = "unverified"
    record_v1: Dict[str, Any] = {
        "protocol": PROTOCOL_PROVENANCE_RECORD_V1,
        "sources": sources,
        "retrieval_date": retrieval_date,
        "verification_status": status,
    }
    if notes:
        record_v1["conflict_notes"] = notes
    return record_v1


def compile_scholarly_profile_protocol_v1(
    style_profile: Dict[str, Any],
    provenance: Dict[str, Any],
    stability_status: Optional[str] = None,
    freshness: Optional[str] = None,
) -> Dict[str, Any]:
    """Build a SCHOLARLY_PROFILE_V1 that validates against the shared schema.

    `style_profile` is StyleProfile.to_dict() output. `provenance` must be a
    PROVENANCE_RECORD_V1 dict; it is required by the schema and is never
    invented here -- a missing or wrong-protocol record raises ValueError.
    `stability_status` takes scb.stability's labels (STABLE, MOSTLY_STABLE,
    UNSTABLE, INSUFFICIENT_SAMPLE) or None.
    """
    if not isinstance(provenance, dict) or provenance.get("protocol") != "PROVENANCE_RECORD_V1":
        raise ValueError("SCHOLARLY_PROFILE_V1 requires a PROVENANCE_RECORD_V1 provenance record")

    biases = list(style_profile.get("known_biases") or [])
    label = style_profile.get("sample_size_label")
    if label:
        biases.append("sample size label: %s" % label)

    if stability_status == "STABLE":
        stability = "stable"
    elif stability_status in ("MOSTLY_STABLE", "UNSTABLE"):
        stability = "unstable"
        if stability_status == "MOSTLY_STABLE":
            biases.append(
                "split-corpus stability was MOSTLY_STABLE: some features differ between "
                "corpus halves, so the profile is reported as unstable rather than stable"
            )
    else:
        stability = "untested"
        if stability_status == "INSUFFICIENT_SAMPLE":
            biases.append("split-corpus stability not testable: insufficient sample")

    profile: Dict[str, Any] = {
        "protocol": PROTOCOL_SCHOLARLY_PROFILE_V1,
        "profile_type": style_profile["profile_type"],
        "target": style_profile["target"],
        "sample_size": int(style_profile.get("sample_size") or 0),
        "measured_features": {k: style_profile.get(k) or {} for k in _MEASURED_KEYS},
        "inferred_features": {k: style_profile.get(k) or ({} if k != "intellectual_rhythm" else []) for k in _INFERRED_KEYS},
        "confidence": _overall_schema_confidence(style_profile.get("confidence")),
        "stability": stability,
        "biases": biases,
        "provenance": provenance,
    }
    if freshness is not None:
        if freshness not in ("current", "aging", "stale"):
            raise ValueError("freshness must be one of current, aging, stale")
        profile["freshness"] = freshness
    return profile


def _author_voice_statements(author_profile: Dict[str, Any]) -> List[PolicyStatement]:
    statements = []
    variation = (author_profile.get("sentence_style") or {}).get("variation")
    if variation:
        statements.append(PolicyStatement(
            "Preserve the author's established sentence-length variation (%s)." % variation,
            RECOMMENDED, "author.sentence_style.variation", "medium",
        ))
    first_person = author_profile.get("first_person")
    if first_person:
        statements.append(PolicyStatement(
            "Match the author's established first-person usage (%s)." % first_person,
            RECOMMENDED, "author.first_person", "medium",
        ))
    for trait in author_profile.get("do_not_preserve", []):
        statements.append(PolicyStatement(
            "Do not preserve: %s (this is a correction target, not part of the author's voice)." % trait,
            MANDATORY, "author.do_not_preserve", "high",
        ))
    return statements


def _discipline_statements(discipline_profile: Dict[str, Any]) -> List[PolicyStatement]:
    statements = []
    conventions = discipline_profile.get("uncertainty_conventions")
    if conventions:
        statements.append(PolicyStatement(
            "Discipline convention for hedging/qualification: %s." % conventions,
            OBSERVED, "discipline.uncertainty_conventions", "medium",
        ))
    return statements


def _journal_statements(journal_profile: Dict[str, Any]) -> List[PolicyStatement]:
    statements = []
    intro = journal_profile.get("introduction", {})
    if intro.get("contribution_position"):
        statements.append(PolicyStatement(
            "In the sampled corpus, this journal's introductions %s "
            "(an observed pattern, not a formal submission requirement)." % intro["contribution_position"],
            OBSERVED, "journal.introduction.contribution_position", journal_profile.get("confidence", "medium"),
        ))
    return statements


def compile_voice_context_v1(
    author_profile: Optional[Dict[str, Any]] = None,
    discipline_profile: Optional[Dict[str, Any]] = None,
    journal_profile: Optional[Dict[str, Any]] = None,
    historical_profile: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    statements: List[PolicyStatement] = []
    if author_profile:
        statements.extend(_author_voice_statements(author_profile))
    if discipline_profile:
        statements.extend(_discipline_statements(discipline_profile))
    if journal_profile:
        statements.extend(_journal_statements(journal_profile))
    if historical_profile:
        for trait in historical_profile.get("transferable_strengths", []):
            statements.append(PolicyStatement(
                "Historical-tradition transferable pattern available: %s (a structural pattern, not "
                "phrasing to imitate)." % trait,
                RECOMMENDED, "historical.transferable_strengths", "low",
            ))

    return {
        "protocol": PROTOCOL_VOICE_CONTEXT_V1,
        "discipline": discipline_profile.get("discipline") if discipline_profile else None,
        "genre": (journal_profile or {}).get("article_types"),
        "author_voice": author_profile or {},
        "voice_precedence": VOICE_PRECEDENCE,
        "voice_constraints": [s.to_dict() for s in statements],
        "claim_calibration": (author_profile or discipline_profile or {}).get("claim_strength")
        or (author_profile or discipline_profile or {}).get("claim_conventions"),
        "section_specific_policies": {
            "introduction": _journal_statements(journal_profile)[0].to_dict() if journal_profile and _journal_statements(journal_profile) else None,
        },
    }


def compile_journal_style_context_v1(
    journal_profile: Dict[str, Any],
    official_requirements: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    adaptation_suggestions = []
    if journal_profile.get("limitations"):
        adaptation_suggestions.append(
            "The sampled corpus shows: %s" % "; ".join(journal_profile["limitations"])
        )

    return {
        "protocol": PROTOCOL_JOURNAL_STYLE_CONTEXT_V1,
        "journal": journal_profile.get("journal"),
        "official_requirements": official_requirements or {},
        "observed_style_profile": journal_profile,
        "stability": journal_profile.get("confidence"),
        "adaptation_suggestions": adaptation_suggestions,
        "evidence_date": journal_profile.get("profile_generated_at"),
    }
