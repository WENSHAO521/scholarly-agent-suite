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
