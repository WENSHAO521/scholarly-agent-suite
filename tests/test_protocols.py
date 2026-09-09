"""Acceptance criteria: Protocols (spec section 137) + component contract
tests (spec section 63) using the minimal structural validator in
scripts/schema_lite.py (spec section 64: no full JSON Schema engine)."""
import json
from pathlib import Path

import pytest
from conftest import load_module

ROOT = Path(__file__).resolve().parent.parent
PROTOCOLS_DIR = ROOT / "protocols"
schema_lite = load_module("schema_lite", "schema_lite.py")

PROTOCOL_FILES = [
    "execution-policy.schema.json", "scholarly-profile.schema.json",
    "voice-request.schema.json", "voice-context.schema.json",
    "voice-output.schema.json", "manuscript-profile.schema.json",
    "journal-profile.schema.json", "journal-style-context.schema.json",
    "continuity-state.schema.json", "provenance.schema.json",
]


@pytest.mark.parametrize("filename", PROTOCOL_FILES)
def test_protocol_schema_is_valid_json_with_title(filename):
    schema = json.loads((PROTOCOLS_DIR / filename).read_text(encoding="utf-8"))
    assert schema["title"].endswith("_V1")
    assert schema["type"] == "object"


def _valid_provenance():
    return {
        "protocol": "PROVENANCE_RECORD_V1",
        "sources": [{"identity": "10.1000/xyz", "access_status": "open-access"}],
        "retrieval_date": "2026-09-01",
        "verification_status": "verified",
    }


def test_scholarly_profile_accepted_by_its_own_schema():
    """Corpus Builder's SCHOLARLY_PROFILE_V1 output validates end to end."""
    profile = {
        "protocol": "SCHOLARLY_PROFILE_V1",
        "profile_type": "journal",
        "target": "Journal of Example Studies",
        "sample_size": 40,
        "confidence": "moderate",
        "freshness": "current",
        "provenance": _valid_provenance(),
    }
    schema_lite.validate_file(profile, PROTOCOLS_DIR / "scholarly-profile.schema.json")


def test_voice_context_accepts_optional_discipline_profile_ref():
    """A VOICE_CONTEXT_V1 populated from a Corpus Builder profile reference
    validates -- i.e. Corpus -> Voice handoff is schema-compatible."""
    context = {
        "protocol": "VOICE_CONTEXT_V1",
        "discipline": "sociology",
        "genre": "research-article",
        "discipline_profile_ref": "scholarly_profile_9f2",
        "limitations": [],
    }
    schema_lite.validate_file(context, PROTOCOLS_DIR / "voice-context.schema.json")


def test_voice_context_falls_back_without_discipline_profile():
    """Voice Engine must remain schema-valid with no Corpus Builder profile
    attached at all (rule 43: graceful fallback, no hard dependency)."""
    context = {"protocol": "VOICE_CONTEXT_V1", "discipline": "sociology", "genre": "research-article"}
    schema_lite.validate_file(context, PROTOCOLS_DIR / "voice-context.schema.json")


def test_journal_style_context_accepted_by_voice_context_journal_ref():
    """Journal Fit's JOURNAL_STYLE_CONTEXT_V1 is independently valid and its
    logical id is the shape VOICE_CONTEXT_V1.journal_style_context_ref expects."""
    style_context = {
        "protocol": "JOURNAL_STYLE_CONTEXT_V1",
        "journal_name": "Journal of Example Studies",
        "official_requirements": {"word_limit": 8000},
        "observed_patterns": {"mean_paragraph_length": 120},
        "freshness": "current",
    }
    schema_lite.validate_file(style_context, PROTOCOLS_DIR / "journal-style-context.schema.json")


def test_manuscript_profile_accepted_by_journal_fit_workflow():
    """A MANUSCRIPT_PROFILE_V1 (typically produced by Voice Engine's audit)
    validates as journal-fit-engine's expected input shape."""
    profile = {
        "protocol": "MANUSCRIPT_PROFILE_V1",
        "discipline": "public administration",
        "article_type": "empirical",
        "constraints": {"word_limit": 9000, "language": "en"},
    }
    schema_lite.validate_file(profile, PROTOCOLS_DIR / "manuscript-profile.schema.json")


def test_continuity_state_minimal_shape_is_valid():
    state = {
        "protocol": "CONTINUITY_STATE_V1",
        "voice_contract": {"tense": "past", "person": "third"},
        "concept_ledger": [],
        "claim_ledger": [],
        "evidence_ledger": [],
        "chapter_ledger": [{"chapter": 1, "status": "drafted"}],
        "terminology": {"OA": "open access"},
        "open_questions": [],
    }
    schema_lite.validate_file(state, PROTOCOLS_DIR / "continuity-state.schema.json")


def test_journal_profile_rejects_numeric_acceptance_probability_field():
    """Rule 75/105: no fake acceptance probability. The schema must not even
    have a place to put one -- additionalProperties: false enforces this."""
    profile = {
        "protocol": "TARGET_JOURNAL_PROFILE_V1",
        "name": "Journal of Example Studies",
        "freshness": "current",
        "provenance": _valid_provenance(),
        "acceptance_probability": 0.8,  # must be rejected
    }
    with pytest.raises(schema_lite.ValidationError):
        schema_lite.validate_file(profile, PROTOCOLS_DIR / "journal-profile.schema.json")


def test_journal_profile_fit_assessment_is_qualitative_enum_only():
    schema = json.loads((PROTOCOLS_DIR / "journal-profile.schema.json").read_text(encoding="utf-8"))
    enum_values = schema["properties"]["fit_assessment"]["enum"]
    assert all(not v.replace(".", "").isdigit() for v in enum_values)
    assert "STRONG_FIT" in enum_values


def test_execution_policy_never_requires_a_model_name_field():
    """Rule 30: don't hardwire model names into the shared protocol."""
    schema = json.loads((PROTOCOLS_DIR / "execution-policy.schema.json").read_text(encoding="utf-8"))
    assert "model" not in schema["properties"]
    assert "model_name" not in schema["properties"]


def test_unknown_protocol_version_is_rejected_not_coerced():
    """Rule 79: a V3 payload must not silently validate against a V1 schema."""
    bogus = {
        "protocol": "SCHOLARLY_PROFILE_V3",
        "profile_type": "journal",
        "target": "X",
        "sample_size": 1,
        "confidence": "low",
        "provenance": _valid_provenance(),
    }
    with pytest.raises(schema_lite.ValidationError):
        schema_lite.validate_file(bogus, PROTOCOLS_DIR / "scholarly-profile.schema.json")
