"""True cross-Skill E2E: journal-fit-engine's real JOURNAL_STYLE_CONTEXT_V1
producer feeding scholarly-voice-engine's real consumer, both imported from
the synced skills/ tree (not reimplemented/mocked here) -- this verifies
the actual protocol handoff, not just "which Skill would be routed to."

Spec fixtures covered: E2E-03 (journal -> style context -> voice
adaptation), E2E-04 (observed evidence never lands in official
requirements), E2E-05 (stale evidence), E2E-06 (missing evidence).

E2E-07 through E2E-12 (Protocol Closure Phase) cover the second real
cross-Skill handoff this Suite closes: journal-fit-engine's real
TARGET_JOURNAL_PROFILE_V1 producer (jfe.target_journal_profile, added
v0.4.0) feeding scholarly-agent's real consumer
(skills/scholarly-agent/scripts/target_journal_adapter.py, the hard
compatibility gate) -- and, for a SELECTED target, on into the same
JOURNAL_STYLE_CONTEXT_V1 handoff above. Nothing here mocks the producer:
every profile is built by driving jfe's actual fit/apc/indexing/integrity
modules over real JournalEvidence/ManuscriptProfile objects, exactly as a
live journal-fit-engine call would.
"""
import sys
from pathlib import Path

import pytest
from conftest import load_module_at
from schema_lite import validate_file

ROOT = Path(__file__).resolve().parent.parent
JFE_SKILL_DIR = ROOT / "skills" / "journal-fit-engine"
VOICE_SKILL_DIR = ROOT / "skills" / "scholarly-voice-engine"
AGENT_SKILL_DIR = ROOT / "skills" / "scholarly-agent"
STYLE_CONTEXT_SCHEMA = ROOT / "protocols" / "journal-style-context.schema.json"
JOURNAL_PROFILE_SCHEMA = ROOT / "protocols" / "journal-profile.schema.json"

for _p in (str(JFE_SKILL_DIR), str(VOICE_SKILL_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from jfe.apc_oa import classify as classify_apc_oa  # noqa: E402
from jfe.fit_model import compute_fit  # noqa: E402
from jfe.indexing import assess_indexing  # noqa: E402
from jfe.integrity import screen as integrity_screen  # noqa: E402
from jfe.journal_evidence import JournalEvidence  # noqa: E402
from jfe.manuscript_profile import ManuscriptProfile  # noqa: E402
from jfe.style_context import build_journal_style_context  # noqa: E402
from jfe.target_journal_profile import build_target_journal_profile  # noqa: E402
from scripts.voice.journal_context import (  # noqa: E402
    apply_journal_style_context,
    from_journal_style_context_v1,
)

# scholarly-agent's scripts/ sits under a directory literally named
# "scripts" too, same as scholarly-voice-engine's above -- loaded by
# explicit path (see conftest.load_module_at) rather than
# sys.path + `import scripts...`, which would collide with the
# scripts.voice import already bound to VOICE_SKILL_DIR's "scripts" package
# in this same process.
target_journal_adapter = load_module_at(
    "target_journal_adapter", AGENT_SKILL_DIR / "scripts" / "target_journal_adapter.py"
)


def _build_target_journal_profile(evidence, manuscript=None, secondary=None, hard_eliminated=False):
    """Drives jfe's real fit/apc/indexing/integrity pipeline over `evidence`
    (and optional `manuscript`/`secondary` evidence), then the real
    producer -- never hand-builds the intermediate FitResult/
    APCClassification/IndexingAssessment/IntegrityScreen objects."""
    manuscript = manuscript or ManuscriptProfile()
    fit = compute_fit(manuscript, evidence, hard_eliminated)
    apc = classify_apc_oa(evidence)
    indexing_assessment = assess_indexing(evidence)
    integrity = integrity_screen(evidence, secondary)
    return build_target_journal_profile(
        evidence, fit_result=fit, apc_classification=apc,
        indexing_assessment=indexing_assessment, integrity=integrity,
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


class TestE2E07StrongTarget:
    """Journal-fit-engine's real producer feeding scholarly-agent's real
    consumer: a strong-fit, APC-compatible, DOAJ-confirmed candidate is
    SELECTED, and a JOURNAL_STYLE_CONTEXT_V1 seed can be built from it."""

    def test_strong_target_is_selected_and_seeds_a_style_context(self):
        evidence = JournalEvidence(
            display_name="Journal of Example Studies", issn_l="1234-5678",
            issn=["1234-5678"], publisher="Example Press", is_oa=True,
            apc_usd=None, is_in_doaj=True, topics=["Sociology"], source="openalex",
            checked_at="2026-09-01T00:00:00+00:00",
        )
        manuscript = ManuscriptProfile(discipline="sociology", topic="sociology")
        profile = _build_target_journal_profile(evidence, manuscript)
        validate_file(profile, JOURNAL_PROFILE_SCHEMA)
        assert profile["fit_assessment"] == "STRONG_FIT"
        assert profile["apc_status"] == "no-apc"

        parsed = target_journal_adapter.from_target_journal_profile_v1(profile)
        selection = target_journal_adapter.evaluate_target_journal_profile(
            parsed, {"no_mandatory_apc": True, "requires_indexing": ["DOAJ"]}
        )
        assert selection.status == target_journal_adapter.SELECTED

        seed = target_journal_adapter.journal_style_context_seed(parsed, selection)
        envelope = build_journal_style_context(
            seed["journal_name"],
            official_requirements={"word_limit": 8000, "citation_style": "APA7"},
            observed_patterns={"tone": "formal"},
            freshness=seed["freshness"],
            evidence=seed["evidence"],
            limitations=seed.get("limitations"),
        )
        validate_file(envelope, STYLE_CONTEXT_SCHEMA)
        assert envelope["journal_name"] == "Journal of Example Studies"


class TestE2E08APCHardMismatch:
    """A journal with a real, producer-confirmed mandatory APC must be
    REJECTED against a manuscript's no_mandatory_apc constraint -- and the
    rejection must block a style-context seed rather than silently letting
    adaptation proceed."""

    def test_mandatory_apc_journal_is_rejected_not_adapted(self):
        evidence = JournalEvidence(
            display_name="Journal of Example Studies", issn_l="1234-5678",
            issn=["1234-5678"], publisher="Example Press", is_oa=True,
            apc_usd=2000, is_in_doaj=True, topics=["Sociology"], source="openalex",
            checked_at="2026-09-01T00:00:00+00:00",
        )
        profile = _build_target_journal_profile(evidence)
        assert profile["apc_status"] == "apc-required"

        parsed = target_journal_adapter.from_target_journal_profile_v1(profile)
        selection = target_journal_adapter.evaluate_target_journal_profile(
            parsed, {"no_mandatory_apc": True}
        )
        assert selection.status == target_journal_adapter.REJECTED
        assert any("apc-required" in reason for reason in selection.reasons)

        with pytest.raises(target_journal_adapter.TargetJournalProfileConsumerError):
            target_journal_adapter.journal_style_context_seed(parsed, selection)


class TestE2E09UnknownIndexing:
    """This Skill's adapters can never verify a paid index (e.g. SSCI) --
    the consumer must report that as NEEDS_VERIFICATION, never fabricate a
    pass or a fail."""

    def test_unverifiable_indexing_requirement_needs_verification(self):
        evidence = JournalEvidence(
            display_name="Journal of Example Studies", issn_l="1234-5678",
            issn=["1234-5678"], publisher="Example Press", is_oa=True,
            apc_usd=None, is_in_doaj=None, topics=["Sociology"], source="openalex",
            checked_at="2026-09-01T00:00:00+00:00",
        )
        profile = _build_target_journal_profile(evidence)
        assert profile.get("indexing", []) == []  # never a fabricated SSCI entry

        parsed = target_journal_adapter.from_target_journal_profile_v1(profile)
        selection = target_journal_adapter.evaluate_target_journal_profile(
            parsed, {"requires_indexing": ["SSCI"]}
        )
        assert selection.status == target_journal_adapter.NEEDS_VERIFICATION
        assert any("SSCI" in note for note in selection.limitations)


class TestE2E10StaleEvidence:
    """Stale producer evidence must not be silently treated as current when
    a hard constraint actually depends on a fact that can change over
    time."""

    def test_stale_evidence_with_a_checked_constraint_needs_verification(self):
        import datetime

        old_checked_at = (
            datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=800)
        ).isoformat()
        evidence = JournalEvidence(
            display_name="Journal of Example Studies", issn_l="1234-5678",
            issn=["1234-5678"], publisher="Example Press", is_oa=True,
            apc_usd=None, is_in_doaj=True, topics=["Sociology"], source="openalex",
            checked_at=old_checked_at,
        )
        profile = _build_target_journal_profile(evidence)
        assert profile["freshness"] == "stale"

        parsed = target_journal_adapter.from_target_journal_profile_v1(profile)
        selection = target_journal_adapter.evaluate_target_journal_profile(
            parsed, {"no_mandatory_apc": True}
        )
        assert selection.status == target_journal_adapter.NEEDS_VERIFICATION
        assert any("stale" in note for note in selection.limitations)


class TestE2E11ProvenancePreserved:
    """Source identifiers, retrieval date, and verification status must
    remain locatable after the full producer -> consumer -> style-context
    handoff, not summarized away."""

    def test_provenance_survives_selection_and_the_style_context_seed(self):
        primary = JournalEvidence(
            display_name="Journal of Example Studies", issn_l="1234-5678",
            issn=["1234-5678"], publisher="Example Press", is_oa=True,
            apc_usd=None, is_in_doaj=True, topics=["Sociology"], source="openalex",
            checked_at="2026-09-01T00:00:00+00:00",
        )
        secondary = JournalEvidence(
            display_name="Journal of Example Studies", issn_l="1234-5678",
            issn=["1234-5678"], publisher="Example Press", source="crossref",
            checked_at="2026-09-01T00:00:00+00:00",
        )
        profile = _build_target_journal_profile(primary, secondary=secondary)
        assert profile["provenance"]["verification_status"] == "verified"

        parsed = target_journal_adapter.from_target_journal_profile_v1(profile)
        selection = target_journal_adapter.evaluate_target_journal_profile(parsed, {})
        assert selection.provenance == profile["provenance"]

        seed = target_journal_adapter.journal_style_context_seed(parsed, selection)
        assert seed["evidence"] == [profile["provenance"]]
        assert seed["evidence"][0]["sources"][0]["identity"] == "1234-5678"
        assert seed["evidence"][0]["retrieval_date"] == "2026-09-01"

        envelope = build_journal_style_context(
            seed["journal_name"], official_requirements={"word_limit": 8000},
            observed_patterns={"tone": "formal"}, freshness=seed["freshness"],
            evidence=seed["evidence"],
        )
        validate_file(envelope, STYLE_CONTEXT_SCHEMA)
        assert envelope["evidence"][0]["sources"][0]["identity"] == "1234-5678"


class TestE2E12NoProfileToStyleContamination:
    """A journal's fit/APC/OA/indexing verdicts answer "is this a plausible
    target?", never "how should this manuscript be written?" -- they must
    never leak into official_requirements/observed_patterns on the way to
    JOURNAL_STYLE_CONTEXT_V1, and official/observed must stay separated on
    the far side exactly as they do for the style-context-only handoff
    above."""

    def test_seed_and_final_envelope_never_carry_fit_or_apc_vocabulary(self):
        evidence = JournalEvidence(
            display_name="Journal of Example Studies", issn_l="1234-5678",
            issn=["1234-5678"], publisher="Example Press", is_oa=True,
            apc_usd=None, is_in_doaj=True, topics=["Sociology"], source="openalex",
            checked_at="2026-09-01T00:00:00+00:00",
        )
        manuscript = ManuscriptProfile(discipline="sociology", topic="sociology")
        profile = _build_target_journal_profile(evidence, manuscript)

        parsed = target_journal_adapter.from_target_journal_profile_v1(profile)
        selection = target_journal_adapter.evaluate_target_journal_profile(
            parsed, {"no_mandatory_apc": True}
        )
        seed = target_journal_adapter.journal_style_context_seed(parsed, selection)
        forbidden = {"apc_status", "oa_status", "fit_assessment", "indexing", "scope_summary"}
        assert not (forbidden & set(seed))

        envelope = build_journal_style_context(
            seed["journal_name"],
            official_requirements={"word_limit": 8000},
            observed_patterns={"mean_paragraph_length": 120},
            freshness=seed["freshness"], evidence=seed["evidence"],
        )
        validate_file(envelope, STYLE_CONTEXT_SCHEMA)
        assert not (forbidden & set(envelope["official_requirements"]))
        assert not (forbidden & set(envelope["observed_patterns"]))

        context = from_journal_style_context_v1(envelope)
        _resolved, _conflicts, hard_requirements, _lim = apply_journal_style_context(context, {})
        assert hard_requirements == {"word_limit": 8000}
