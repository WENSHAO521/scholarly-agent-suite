"""Lightweight shape validators for the profile/request types this Skill
consumes or produces.

These deliberately mirror field names already used by the sibling skills
(scholarly-corpus-builder's author-profile.md / style-feature-schema.md,
journal-fit-engine's integration.md) and this Skill's own
references/integration.md conceptual contract, rather than defining a
competing schema. Validation is permissive by design: every field is
optional, since "unknown" is a valid state (see SKILL.md §Task
interpretation) — these functions catch shape *errors* (wrong type, unknown
enum value), not missing data.
"""
from __future__ import annotations

from dataclasses import dataclass, field

CLAIM_TYPES = (
    "descriptive",
    "associational",
    "causal",
    "mechanistic",
    "predictive",
    "interpretive",
    "normative",
    "formal",
)

CONFIDENCE_LEVELS = ("high", "moderate", "low")

VOICE_DIMENSION_LEVELS = ("very_low", "low", "medium", "high", "very_high")

EDITING_INTENSITIES = ("SURFACE_EDIT", "STRUCTURAL_EDIT", "ARGUMENT_RECONSTRUCTION")

OUTPUT_MODES = (
    "draft",
    "revise",
    "polish",
    "compress",
    "expand",
    "restructure",
    "rebuild_argument",
    "journal_adapt",
    "book_chapter",
    "author_voice",
    "disciplinary_convert",
    # A read-only quality-audit pass over input_text (references/quality-
    # audit.md) that reports findings without drafting/revising prose --
    # distinct from the audit step every other mode already runs before
    # returning text (SKILL.md step 13). Added for VOICE_REQUEST_V1
    # interop: the Suite's task enum includes "audit" and no existing mode
    # covers "check but don't rewrite."
    "audit",
)

QUALITY_STATES = (
    "PASS",
    "PASS_WITH_LIMITATIONS",
    "REPAIR_REQUIRED",
    "BLOCKED_BY_MISSING_EVIDENCE",
    "BLOCKED_BY_CITATION_UNCERTAINTY",
    "BLOCKED_BY_ARGUMENT_INCONSISTENCY",
)

# Fields on scholarly-corpus-builder's author-profile.md schema. Kept here
# only as a validation surface — that Skill's file is authoritative.
AUTHOR_PROFILE_FIELDS = (
    "profile_type",
    "source_count",
    "source_scope",
    "sentence_style",
    "paragraph_style",
    "argument_moves",
    "citation_behavior",
    "first_person",
    "claim_strength",
    "definition_style",
    "preferred_transitions",
    "section_patterns",
    "do_not_preserve",
)

# journal-fit-engine's two adaptation-target shapes (integration.md).
JOURNAL_TARGET_COMPACT_FIELDS = (
    "contribution_position",
    "mechanism_visibility",
    "policy_implication",
    "sentence_density",
)
JOURNAL_TARGET_FULL_FIELDS = (
    "genre",
    "contribution_position",
    "theory_density",
    "policy_implications",
    "methods_transparency",
    "introduction_length",
)


class SchemaError(ValueError):
    """Raised when a profile/request shape contains an invalid value."""


def _check_enum(value, allowed, field_name, errors):
    if value is not None and value not in allowed:
        errors.append(f"{field_name}: {value!r} not in {allowed}")


def validate_claim_type(claim_type: str | None) -> list[str]:
    errors: list[str] = []
    _check_enum(claim_type, CLAIM_TYPES, "claim_type", errors)
    return errors


def validate_confidence(confidence: str | None) -> list[str]:
    errors: list[str] = []
    _check_enum(confidence, CONFIDENCE_LEVELS, "confidence", errors)
    return errors


def validate_author_profile(profile: dict) -> list[str]:
    """Permissive check: unknown top-level keys are flagged, known keys are
    not type-checked beyond what's cheap to check here. Authoritative shape
    lives in scholarly-corpus-builder/references/author-profile.md.
    """
    errors: list[str] = []
    if profile.get("profile_type") not in (None, "author"):
        errors.append(f"profile_type: expected 'author', got {profile.get('profile_type')!r}")
    unknown = set(profile) - set(AUTHOR_PROFILE_FIELDS)
    if unknown:
        errors.append(f"unknown author-profile fields: {sorted(unknown)}")
    do_not_preserve = profile.get("do_not_preserve")
    if do_not_preserve is not None and not isinstance(do_not_preserve, list):
        errors.append("do_not_preserve: expected a list")
    return errors


def validate_journal_target(target: dict) -> list[str]:
    """Accepts either the compact target_voice_adjustment shape or the
    fuller journal_target shape — matches whichever field set is present.
    """
    errors: list[str] = []
    keys = set(target)
    if keys <= set(JOURNAL_TARGET_COMPACT_FIELDS):
        return errors
    if keys <= set(JOURNAL_TARGET_FULL_FIELDS):
        return errors
    unknown = keys - set(JOURNAL_TARGET_COMPACT_FIELDS) - set(JOURNAL_TARGET_FULL_FIELDS)
    if unknown:
        errors.append(f"unknown journal-target fields: {sorted(unknown)}")
    return errors


@dataclass
class VoiceRequest:
    """Mirrors references/integration.md's VOICE_REQUEST shape."""

    task: str = "draft"
    discipline: str | None = None
    genre: str | None = None
    research_design: str | None = None
    audience: str | None = None
    language: str = "en"
    editing_mode: str = "surface"
    voice_strength: str = "medium"
    author_profile: dict | None = None
    scholarly_profile: dict | None = None
    journal_context: dict | None = None
    constraints: dict = field(default_factory=dict)

    def validate(self) -> list[str]:
        errors: list[str] = []
        _check_enum(self.task, OUTPUT_MODES, "task", errors)
        _check_enum(
            self.editing_mode,
            ("surface", "structural", "argument_reconstruction"),
            "editing_mode",
            errors,
        )
        _check_enum(self.voice_strength, ("low", "medium", "high"), "voice_strength", errors)
        if self.author_profile:
            errors.extend(validate_author_profile(self.author_profile))
        if self.journal_context:
            errors.extend(validate_journal_target(self.journal_context))
        return errors


@dataclass
class VoiceOutput:
    """Mirrors references/integration.md's VOICE_OUTPUT shape."""

    mode: str
    discipline: str | None = None
    genre: str | None = None
    voice_profile: dict = field(default_factory=dict)
    integrity_status: str = "PASS"
    limitations: list = field(default_factory=list)
    output: str = ""

    def validate(self) -> list[str]:
        errors: list[str] = []
        _check_enum(self.integrity_status, QUALITY_STATES, "integrity_status", errors)
        return errors


# --- Optional scholarly-agent-suite protocol interoperability -------------
#
# This Skill's own conceptual VOICE_REQUEST/VOICE_OUTPUT contract above
# (references/integration.md) is the authoritative, tested shape; it works
# standalone with no Suite present. The functions below are an additive,
# optional translation layer for a host that speaks the Suite's narrower
# orchestration-envelope protocols (VOICE_REQUEST_V1 / VOICE_OUTPUT_V1,
# additionalProperties: false) -- this Skill never requires them and never
# rewrites its own internal fields to match them.

# Suite's coarse orchestrator-facing `task` -> this Skill's own richer
# OUTPUT_MODES. "audit" is not looked up here: it maps 1:1 by name (both
# use the literal string "audit"), included in OUTPUT_MODES above.
VOICE_REQUEST_V1_TASK_MAP = {
    "draft": "draft",
    "revise": "revise",
    "audit": "audit",
    "adapt-to-journal": "journal_adapt",
    "calibrate-author-voice": "author_voice",
    "continue-chapter": "book_chapter",
}

# This Skill's own integrity_status states -> VOICE_OUTPUT_V1's narrower
# validation_state enum (which has no citation/argument-specific states).
# Both refined states still surface in VoiceOutput.limitations so nothing
# is silently lost in translation.
_VOICE_OUTPUT_V1_STATE_MAP = {
    "PASS": "PASS",
    "PASS_WITH_LIMITATIONS": "PASS_WITH_LIMITATIONS",
    "REPAIR_REQUIRED": "REPAIR_REQUIRED",
    "BLOCKED_BY_MISSING_EVIDENCE": "BLOCKED_BY_MISSING_EVIDENCE",
    "BLOCKED_BY_CITATION_UNCERTAINTY": "BLOCKED_BY_MISSING_EVIDENCE",
    "BLOCKED_BY_ARGUMENT_INCONSISTENCY": "REPAIR_REQUIRED",
}


def from_voice_request_v1(data: dict) -> VoiceRequest:
    """Translate an incoming VOICE_REQUEST_V1 envelope (see
    scholarly-agent-suite/protocols/voice-request.schema.json) into this
    Skill's own VoiceRequest. Raises SchemaError on an unrecognized
    protocol/task or a resulting request that fails VoiceRequest.validate().
    """
    if data.get("protocol") != "VOICE_REQUEST_V1":
        raise SchemaError(f"not a VOICE_REQUEST_V1 envelope: protocol={data.get('protocol')!r}")
    task = data.get("task")
    mode = VOICE_REQUEST_V1_TASK_MAP.get(task)
    if mode is None:
        raise SchemaError(f"unrecognized VOICE_REQUEST_V1 task: {task!r}")

    request = VoiceRequest(
        task=mode,
        discipline=data.get("discipline"),
        genre=data.get("genre"),
        constraints=dict(data.get("constraints") or {}),
    )
    errors = request.validate()
    if errors:
        raise SchemaError("; ".join(errors))
    return request


def to_voice_output_v1(output: VoiceOutput) -> dict:
    """Translate this Skill's own VoiceOutput into a VOICE_OUTPUT_V1 envelope
    (see scholarly-agent-suite/protocols/voice-output.schema.json). The two
    citation/argument-specific integrity_status values collapse onto the
    nearest VOICE_OUTPUT_V1 state, with that narrowing recorded in
    `limitations` so it is never silently lost.
    """
    errors = output.validate()
    if errors:
        raise SchemaError("; ".join(errors))

    limitations = list(output.limitations)
    validation_state = _VOICE_OUTPUT_V1_STATE_MAP[output.integrity_status]
    if output.integrity_status in ("BLOCKED_BY_CITATION_UNCERTAINTY", "BLOCKED_BY_ARGUMENT_INCONSISTENCY"):
        limitations.append(
            f"original integrity_status was {output.integrity_status}, "
            f"reported as {validation_state} for VOICE_OUTPUT_V1 compatibility"
        )

    envelope = {
        "protocol": "VOICE_OUTPUT_V1",
        "output_text": output.output,
        "validation_state": validation_state,
        "limitations": limitations,
    }
    return envelope
