"""Cross-module protocol handoffs added with the v2 single-Skill merge.

Both handoffs below were broken before v2.0.0 and were only uncovered once
the modules shared one tree and one test run:

- corpus -> voice (SCHOLARLY_PROFILE_V1): scb's original
  compile_scholarly_profile_v1() emitted a shape the shared schema rejects
  (no PROVENANCE_RECORD_V1, per-feature confidence dict, scb-internal
  stability labels). compile_scholarly_profile_protocol_v1() is the
  schema-conformant producer.
- voice/user -> journal fit (MANUSCRIPT_PROFILE_V1): a schema-valid envelope
  was rejected by jfe's ManuscriptProfile.from_dict() (unknown 'protocol'
  field, different field names and article_type vocabulary).
  jfe.manuscript_profile.from_manuscript_profile_v1() is the translation.

Real module code throughout -- no mocks.
"""
import sys
from pathlib import Path

import pytest
from conftest import load_module_at
from schema_lite import ValidationError, validate_file

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "scholarly-agent"
MODULES = SKILL_DIR / "modules"
PROTOCOLS = SKILL_DIR / "protocols"

for _p in (str(MODULES / "scholarly-corpus-builder"), str(MODULES / "journal-fit-engine")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from jfe.fit_model import compute_fit  # noqa: E402
from jfe.journal_evidence import JournalEvidence  # noqa: E402
from jfe.manuscript_profile import ProfileError, from_manuscript_profile_v1  # noqa: E402
from scb.compiler import compile_scholarly_profile_protocol_v1, compile_scholarly_profile_v1  # noqa: E402
from scb.profile_schema import build_style_profile  # noqa: E402
from scb.text_normalize import Document, Section  # noqa: E402

voice_schema = load_module_at(
    "voice_profile_schema_v2_handoff",
    MODULES / "scholarly-voice-engine" / "scripts" / "voice" / "profile_schema.py",
)

PROVENANCE = {
    "protocol": "PROVENANCE_RECORD_V1",
    "sources": [
        {"identity": "10.1234/example.1", "access_status": "open-access"},
        {"identity": "user-file:draft-2025.docx", "access_status": "user-supplied"},
    ],
    "retrieval_date": "2026-11-01",
    "verification_status": "verified",
}


def _doc(i: int) -> Document:
    return Document(
        title=f"Paper {i}",
        abstract="We examine policy diffusion.",
        sections=[
            Section("Introduction", "introduction", [
                "We argue that policy diffusion depends on institutional capacity (Smith, 2020). "
                "This suggests a conditional mechanism. However, prior work rarely tests it.",
            ]),
            Section("Discussion", "discussion", [
                "The results may indicate that capacity matters. We define capacity as administrative reach. "
                "Further work should examine other regions [12].",
            ]),
        ],
    )


def _style_profile(n: int) -> dict:
    return build_style_profile("journal", "Journal of Example Studies", [_doc(i) for i in range(n)]).to_dict()


# --- corpus -> voice: SCHOLARLY_PROFILE_V1 -----------------------------------

class TestScholarlyProfileCorpusToVoice:
    def test_legacy_producer_is_not_schema_conformant(self):
        """Documents the defect this release fixes; if the legacy producer is
        ever made conformant, fold it into the new one and drop this."""
        legacy = compile_scholarly_profile_v1("journal", "J", _style_profile(3))
        with pytest.raises(ValidationError):
            validate_file(legacy, PROTOCOLS / "scholarly-profile.schema.json")

    def test_protocol_producer_validates_against_shared_schema(self):
        profile = compile_scholarly_profile_protocol_v1(_style_profile(6), PROVENANCE)
        validate_file(profile, PROTOCOLS / "scholarly-profile.schema.json")
        assert profile["sample_size"] == 6
        assert profile["provenance"]["sources"][0]["identity"] == "10.1234/example.1"

    def test_small_sample_never_overstates_confidence(self):
        profile = compile_scholarly_profile_protocol_v1(_style_profile(3), PROVENANCE)
        assert profile["confidence"] == "low"
        assert any("sample size label" in b for b in profile["biases"])

    def test_medium_confidence_maps_to_schema_moderate(self):
        profile = compile_scholarly_profile_protocol_v1(_style_profile(6), PROVENANCE)
        assert profile["confidence"] == "moderate"

    def test_mostly_stable_is_reported_unstable_with_reason(self):
        profile = compile_scholarly_profile_protocol_v1(_style_profile(6), PROVENANCE, stability_status="MOSTLY_STABLE")
        assert profile["stability"] == "unstable"
        assert any("MOSTLY_STABLE" in b for b in profile["biases"])

    def test_missing_provenance_is_refused_not_invented(self):
        with pytest.raises(ValueError):
            compile_scholarly_profile_protocol_v1(_style_profile(6), {})

    def test_voice_module_accepts_profile_in_its_request(self):
        profile = compile_scholarly_profile_protocol_v1(_style_profile(6), PROVENANCE, freshness="current")
        request = voice_schema.VoiceRequest(task="journal_adapt", scholarly_profile=profile)
        assert request.validate() == []
        assert request.scholarly_profile["measured_features"]["sentence"]["median_length"] > 0


# --- voice/user -> journal fit: MANUSCRIPT_PROFILE_V1 ------------------------

def _envelope(**overrides) -> dict:
    data = {
        "protocol": "MANUSCRIPT_PROFILE_V1",
        "discipline": "political science",
        "topic": "policy diffusion and institutional capacity",
        "research_question": "When does institutional capacity condition policy diffusion?",
        "contribution": "A conditional theory of diffusion",
        "methods": "process tracing; comparative case study",
        "article_type": "theory",
        "constraints": {"word_limit": 9000, "apc": "none"},
    }
    data.update(overrides)
    return data


class TestManuscriptProfileToJournalFit:
    def test_envelope_validates_against_shared_schema(self):
        validate_file(_envelope(), PROTOCOLS / "manuscript-profile.schema.json")

    def test_envelope_translates_into_journal_fit_profile(self):
        profile = from_manuscript_profile_v1(_envelope())
        assert profile.article_type == "other"
        assert profile.contribution_type == "theoretical"
        assert profile.central_contribution == "A conditional theory of diffusion"
        assert profile.methods == ["process tracing", "comparative case study"]
        assert profile.constraints == {"word_limit": 9000, "apc": "none"}

    def test_translated_profile_drives_real_fit_model(self):
        profile = from_manuscript_profile_v1(_envelope(article_type="empirical"))
        assert profile.article_type == "original-research"
        evidence = JournalEvidence(display_name="Journal of Policy Diffusion", topics=["policy diffusion", "institutional capacity"])
        fit = compute_fit(profile, evidence, hard_eliminated=False)
        assert fit.topic_overlap_terms
        assert not fit.hard_eliminated

    @pytest.mark.parametrize("bad", [
        {"protocol": "SOMETHING_ELSE"},
        {"article_type": "novel"},
        {"discipline": ""},
    ])
    def test_bad_envelopes_are_rejected(self, bad):
        with pytest.raises(ProfileError):
            from_manuscript_profile_v1(_envelope(**bad))
