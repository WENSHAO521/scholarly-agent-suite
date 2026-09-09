"""Unit tests for scripts/target_journal_adapter.py -- the first real
downstream consumer of TARGET_JOURNAL_PROFILE_V1 (spec: Protocol Closure
Phase). These test the adapter's own logic in isolation (protocol
validation, the hard-compatibility gate's truth table, the style-context
seed's contamination guard); tests/test_e2e_protocol_handoff.py separately
drives the same module against journal-fit-engine's *real* producer.
"""
from pathlib import Path

import pytest
from conftest import load_module_at

ROOT = Path(__file__).resolve().parent.parent
AGENT_SKILL_DIR = ROOT / "skills" / "scholarly-agent"

adapter = load_module_at(
    "target_journal_adapter", AGENT_SKILL_DIR / "scripts" / "target_journal_adapter.py"
)


def _profile(**overrides):
    fields = dict(
        protocol="TARGET_JOURNAL_PROFILE_V1",
        name="Journal of Example Studies",
        freshness="current",
        provenance={
            "protocol": "PROVENANCE_RECORD_V1",
            "sources": [{"identity": "1234-5678", "access_status": "metadata-only"}],
            "retrieval_date": "2026-09-01",
            "verification_status": "unverified",
        },
    )
    fields.update(overrides)
    return fields


class TestValidation:
    def test_wrong_protocol_is_rejected(self):
        with pytest.raises(adapter.TargetJournalProfileConsumerError):
            adapter.from_target_journal_profile_v1({"protocol": "SOMETHING_ELSE_V1"})

    def test_missing_required_field_is_rejected(self):
        data = _profile()
        del data["freshness"]
        with pytest.raises(adapter.TargetJournalProfileConsumerError):
            adapter.from_target_journal_profile_v1(data)

    def test_minimal_envelope_parses(self):
        profile = adapter.from_target_journal_profile_v1(_profile())
        assert profile.name == "Journal of Example Studies"
        assert profile.indexing == []
        assert profile.apc_status is None


class TestHardCompatibilityGate:
    def test_no_constraints_selects_by_default(self):
        profile = adapter.from_target_journal_profile_v1(_profile())
        result = adapter.evaluate_target_journal_profile(profile, {})
        assert result.status == adapter.SELECTED
        assert result.provenance == profile.provenance

    def test_apc_hard_mismatch_rejects(self):
        profile = adapter.from_target_journal_profile_v1(_profile(apc_status="apc-required"))
        result = adapter.evaluate_target_journal_profile(profile, {"no_mandatory_apc": True})
        assert result.status == adapter.REJECTED
        assert any("apc-required" in r for r in result.reasons)

    def test_apc_compatible_status_selects(self):
        profile = adapter.from_target_journal_profile_v1(_profile(apc_status="no-apc"))
        result = adapter.evaluate_target_journal_profile(profile, {"no_mandatory_apc": True})
        assert result.status == adapter.SELECTED

    def test_unknown_apc_status_needs_verification_not_rejection(self):
        profile = adapter.from_target_journal_profile_v1(_profile(apc_status="unknown"))
        result = adapter.evaluate_target_journal_profile(profile, {"no_mandatory_apc": True})
        assert result.status == adapter.NEEDS_VERIFICATION

    def test_absent_apc_status_needs_verification_not_rejection(self):
        profile = adapter.from_target_journal_profile_v1(_profile())
        result = adapter.evaluate_target_journal_profile(profile, {"no_mandatory_apc": True})
        assert result.status == adapter.NEEDS_VERIFICATION

    def test_unconfirmed_indexing_needs_verification_never_rejected(self):
        profile = adapter.from_target_journal_profile_v1(_profile(indexing=["DOAJ"]))
        result = adapter.evaluate_target_journal_profile(profile, {"requires_indexing": ["SSCI"]})
        assert result.status == adapter.NEEDS_VERIFICATION
        assert not any("SSCI" in r and "REJECTED" in r for r in result.reasons)

    def test_confirmed_indexing_selects(self):
        profile = adapter.from_target_journal_profile_v1(_profile(indexing=["DOAJ"]))
        result = adapter.evaluate_target_journal_profile(profile, {"requires_indexing": ["DOAJ"]})
        assert result.status == adapter.SELECTED

    def test_unrequested_constraint_is_never_checked(self):
        """A profile with apc_status=apc-required is fine if the manuscript
        never asked for no_mandatory_apc -- the gate does not invent checks
        the caller did not request."""
        profile = adapter.from_target_journal_profile_v1(_profile(apc_status="apc-required"))
        result = adapter.evaluate_target_journal_profile(profile, {})
        assert result.status == adapter.SELECTED

    def test_stale_freshness_alone_does_not_force_needs_verification(self):
        """No hard constraint touches a perishable fact -- stale evidence
        is still surfaced as a limitation but does not block selection
        (mirrors workflow rule: skip refresh when nothing current-fact-
        dependent was actually requested)."""
        profile = adapter.from_target_journal_profile_v1(_profile(freshness="stale"))
        result = adapter.evaluate_target_journal_profile(profile, {})
        assert result.status == adapter.SELECTED
        assert any("stale" in note for note in result.limitations)

    def test_stale_freshness_with_checked_perishable_fact_needs_verification(self):
        profile = adapter.from_target_journal_profile_v1(
            _profile(freshness="stale", apc_status="no-apc")
        )
        result = adapter.evaluate_target_journal_profile(profile, {"no_mandatory_apc": True})
        assert result.status == adapter.NEEDS_VERIFICATION
        assert any("stale" in note for note in result.limitations)

    def test_stale_freshness_never_softens_an_existing_rejection(self):
        profile = adapter.from_target_journal_profile_v1(
            _profile(freshness="stale", apc_status="apc-required")
        )
        result = adapter.evaluate_target_journal_profile(profile, {"no_mandatory_apc": True})
        assert result.status == adapter.REJECTED

    def test_provenance_is_preserved_unchanged(self):
        data = _profile()
        profile = adapter.from_target_journal_profile_v1(data)
        result = adapter.evaluate_target_journal_profile(profile, {})
        assert result.provenance == data["provenance"]


class TestStyleContextSeed:
    def test_rejected_selection_refuses_to_seed(self):
        profile = adapter.from_target_journal_profile_v1(_profile(apc_status="apc-required"))
        result = adapter.evaluate_target_journal_profile(profile, {"no_mandatory_apc": True})
        with pytest.raises(adapter.TargetJournalProfileConsumerError):
            adapter.journal_style_context_seed(profile, result)

    def test_selected_seed_carries_identity_freshness_and_provenance(self):
        profile = adapter.from_target_journal_profile_v1(_profile())
        result = adapter.evaluate_target_journal_profile(profile, {})
        seed = adapter.journal_style_context_seed(profile, result)
        assert seed["journal_name"] == "Journal of Example Studies"
        assert seed["freshness"] == "current"
        assert seed["evidence"] == [profile.provenance]

    def test_seed_never_carries_fit_or_apc_vocabulary(self):
        """Structural guard against Profile -> Style contamination: fit_assessment,
        apc_status, oa_status, and indexing answer a different question than
        official_requirements/observed_patterns and must never leak across."""
        profile = adapter.from_target_journal_profile_v1(
            _profile(apc_status="apc-required", oa_status="fully-oa",
                     fit_assessment="STRONG_FIT", indexing=["DOAJ"])
        )
        result = adapter.evaluate_target_journal_profile(profile, {})
        seed = adapter.journal_style_context_seed(profile, result)
        forbidden_keys = {"apc_status", "oa_status", "fit_assessment", "indexing"}
        assert not (forbidden_keys & set(seed))

    def test_needs_verification_seed_carries_the_limitation(self):
        profile = adapter.from_target_journal_profile_v1(
            _profile(indexing=[])
        )
        result = adapter.evaluate_target_journal_profile(profile, {"requires_indexing": ["SSCI"]})
        assert result.status == adapter.NEEDS_VERIFICATION
        seed = adapter.journal_style_context_seed(profile, result)
        assert "limitations" in seed
