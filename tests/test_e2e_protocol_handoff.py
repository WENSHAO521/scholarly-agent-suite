"""True cross-Skill E2E: journal-fit-engine's real JOURNAL_STYLE_CONTEXT_V1
producer feeding scholarly-voice-engine's real consumer, both imported from
the synced skills/ tree (not reimplemented/mocked here) -- this verifies
the actual protocol handoff, not just "which Skill would be routed to."

Spec fixtures covered: E2E-03 (journal -> style context -> voice
adaptation), E2E-04 (observed evidence never lands in official
requirements), E2E-05 (stale evidence), E2E-06 (missing evidence).
"""
import sys
from pathlib import Path

import pytest
from schema_lite import validate_file

ROOT = Path(__file__).resolve().parent.parent
JFE_SKILL_DIR = ROOT / "skills" / "journal-fit-engine"
VOICE_SKILL_DIR = ROOT / "skills" / "scholarly-voice-engine"
STYLE_CONTEXT_SCHEMA = ROOT / "protocols" / "journal-style-context.schema.json"

for _p in (str(JFE_SKILL_DIR), str(VOICE_SKILL_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from jfe.journal_evidence import JournalEvidence  # noqa: E402
from jfe.style_context import build_journal_style_context  # noqa: E402
from scripts.voice.journal_context import (  # noqa: E402
    apply_journal_style_context,
    from_journal_style_context_v1,
)


def _current_evidence(**overrides):
    fields = dict(display_name="Journal of Example Studies", issn_l="1234-5678",
                   issn=["1234-5678"], publisher="Example Press",
                   checked_at="2026-09-01T00:00:00+00:00")
    fields.update(overrides)
    return JournalEvidence(**fields)


class TestE2E03ProducerToConsumer:
    """Journal Fit Engine produces JOURNAL_STYLE_CONTEXT_V1; Scholarly Voice
    Engine consumes it. Official requirement survives, observed pattern
    survives, freshness survives, limitations survive."""

    def test_envelope_validates_against_the_canonical_suite_schema(self):
        envelope = build_journal_style_context(
            "Journal of Example Studies",
            official_requirements={"word_limit": 8000, "citation_style": "APA7"},
            observed_patterns={"tone": "formal", "contribution_placement_observed": "early"},
            freshness="current",
        )
        validate_file(envelope, STYLE_CONTEXT_SCHEMA)

    def test_official_requirement_survives_the_full_handoff(self):
        envelope = build_journal_style_context(
            "Journal of Example Studies",
            official_requirements={"word_limit": 8000},
            observed_patterns={"tone": "formal"},
            freshness="current",
        )
        context = from_journal_style_context_v1(envelope)
        _resolved, _conflicts, hard_requirements, _lim = apply_journal_style_context(context, {})
        assert hard_requirements == {"word_limit": 8000}

    def test_observed_pattern_survives_and_wins_at_current_freshness(self):
        envelope = build_journal_style_context(
            "Journal of Example Studies",
            official_requirements={"word_limit": 8000},
            observed_patterns={"tone": "formal"},
            freshness="current",
        )
        context = from_journal_style_context_v1(envelope)
        resolved, _conflicts, _hard, _lim = apply_journal_style_context(
            context, {"historical": {"tone": "informal"}})
        assert resolved["tone"] == "formal"

    def test_freshness_survives_the_full_handoff(self):
        envelope = build_journal_style_context(
            "Journal of Example Studies", official_requirements={"word_limit": 8000},
            observed_patterns={"tone": "formal"}, freshness="aging",
        )
        context = from_journal_style_context_v1(envelope)
        assert context.freshness == "aging"

    def test_journal_identifiers_from_real_evidence_survive_the_handoff(self):
        evidence = _current_evidence()
        envelope = build_journal_style_context(
            evidence.display_name,
            official_requirements={"word_limit": 8000},
            observed_patterns={"tone": "formal"},
            freshness="current",
            journal_identifiers={"issn": evidence.issn, "issn_l": evidence.issn_l,
                                  "publisher": evidence.publisher},
        )
        validate_file(envelope, STYLE_CONTEXT_SCHEMA)
        context = from_journal_style_context_v1(envelope)
        assert context.journal_identifiers["issn_l"] == "1234-5678"


class TestE2E04ContaminationRegression:
    """Corpus-derived observed evidence must never land in
    official_requirements, and a stated official rule must never be
    reported as merely descriptive -- enforced at the producer, and
    verified to still hold after the full round trip through the
    consumer."""

    def test_producer_rejects_observed_evidence_mislabeled_as_official(self):
        from jfe.style_context import StyleContextError

        with pytest.raises(StyleContextError):
            build_journal_style_context(
                "Journal of Example Studies",
                official_requirements={"word_limit": 8000, "mean_paragraph_length": 120},
                observed_patterns={},
            )

    def test_consumer_never_places_observed_fields_in_hard_requirements(self):
        envelope = build_journal_style_context(
            "Journal of Example Studies",
            official_requirements={"word_limit": 8000},
            observed_patterns={"mean_paragraph_length": 120, "tone": "formal"},
            freshness="current",
        )
        context = from_journal_style_context_v1(envelope)
        _resolved, _conflicts, hard_requirements, _lim = apply_journal_style_context(context, {})
        assert "mean_paragraph_length" not in hard_requirements
        assert "tone" not in hard_requirements
        assert hard_requirements == {"word_limit": 8000}


class TestE2E05StaleEvidence:
    """Stale evidence must not be silently treated as current -- the
    consumer must weight it down and keep the staleness warning visible."""

    def test_stale_freshness_survives_as_a_limitation(self):
        envelope = build_journal_style_context(
            "Journal of Example Studies", official_requirements={"word_limit": 8000},
            observed_patterns={"tone": "formal"}, freshness="stale",
        )
        context = from_journal_style_context_v1(envelope)
        _resolved, _conflicts, _hard, limitations = apply_journal_style_context(context, {})
        assert any("stale" in note for note in limitations)

    def test_stale_observed_pattern_yields_to_a_lower_precedence_layer(self):
        envelope = build_journal_style_context(
            "Journal of Example Studies", official_requirements={"word_limit": 8000},
            observed_patterns={"tone": "formal"}, freshness="stale",
        )
        context = from_journal_style_context_v1(envelope)
        resolved, _conflicts, _hard, _lim = apply_journal_style_context(
            context, {"historical": {"tone": "informal"}})
        assert resolved["tone"] == "informal"

    def test_stale_freshness_from_stamped_index_evidence_survives(self):
        """End to end from jfe's own live-evidence freshness computation
        (compute_freshness) through to the consumer's confidence gating."""
        import datetime

        from jfe.style_context import from_journal_evidence

        old_evidence = _current_evidence(checked_at=(
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=800)
        ).isoformat())
        envelope = from_journal_evidence(
            old_evidence, official_requirements={"word_limit": 8000},
            observed_patterns={"tone": "formal"},
        )
        assert envelope["freshness"] == "stale"
        context = from_journal_style_context_v1(envelope)
        resolved, _c, _h, limitations = apply_journal_style_context(
            context, {"historical": {"tone": "informal"}})
        assert resolved["tone"] == "informal"
        assert any("stale" in note for note in limitations)


class TestE2E06MissingEvidence:
    """When official/observed evidence cannot be confirmed, the handoff
    must say so explicitly -- never silently proceed as if it were
    verified."""

    def test_missing_official_requirements_produces_a_surviving_limitation(self):
        envelope = build_journal_style_context(
            "Journal of Example Studies", observed_patterns={"tone": "formal"}, freshness="current",
        )
        context = from_journal_style_context_v1(envelope)
        _resolved, _conflicts, hard_requirements, limitations = apply_journal_style_context(context, {})
        assert hard_requirements == {}
        assert any("no official_requirements" in note for note in limitations)

    def test_missing_observed_patterns_produces_a_surviving_limitation(self):
        envelope = build_journal_style_context(
            "Journal of Example Studies", official_requirements={"word_limit": 8000}, freshness="current",
        )
        context = from_journal_style_context_v1(envelope)
        assert context.observed_patterns == {}
        assert any("no observed_patterns" in note for note in envelope.get("limitations", []))

    def test_unverifiable_requirement_compatibility_is_cannot_verify_not_a_guess(self):
        from jfe.fit_dimensions import CANNOT_VERIFY, requirement_compatibility_fit
        from jfe.manuscript_profile import ManuscriptProfile

        result = requirement_compatibility_fit(ManuscriptProfile(word_count=5000), None)
        assert result.result == CANNOT_VERIFY
