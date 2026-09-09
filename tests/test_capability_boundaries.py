"""Acceptance criteria: Orchestrator must not duplicate specialist logic
(spec section 136, rule 3, rule 156). Heuristic textual check: the
orchestrator's own SKILL.md must not itself prescribe domain-specific rules
that belong to a specialist (e.g. citation formatting, model names, journal
ranking formulas) -- it should only ever *refer* to the specialist that owns
that rule."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Phrases that would indicate the orchestrator is doing a specialist's job
# itself, rather than delegating to it.
SCOPE_CREEP_MARKERS = [
    "impact factor >",  # journal-fit-engine's ranking logic
    "gpt-5",  # a hardwired model name (adaptive-model-router's job)
    "gpt-4",
    "apa 7th edition",  # citation formatting specifics (voice-engine's job)
    "openalex api",  # corpus-builder's acquisition detail
]


def test_orchestrator_skill_md_has_no_scope_creep_markers():
    text = (ROOT / "skills" / "scholarly-agent" / "SKILL.md").read_text(encoding="utf-8").lower()
    found = [m for m in SCOPE_CREEP_MARKERS if m in text]
    assert not found, f"scholarly-agent SKILL.md appears to duplicate specialist logic: {found}"


def test_orchestrator_agents_yaml_declares_boundary_constraints():
    text = (ROOT / "skills" / "scholarly-agent" / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for marker in [
        "never_perform_model_routing_directly",
        "never_perform_corpus_acquisition_directly",
        "never_prescribe_academic_prose_rules_directly",
        "never_perform_journal_ranking_directly",
    ]:
        assert marker in text


def test_capability_boundaries_doc_names_all_five_skills():
    text = (ROOT / "shared" / "capability-boundaries.md").read_text(encoding="utf-8")
    for name in [
        "adaptive-model-router", "scholarly-corpus-builder",
        "scholarly-voice-engine", "journal-fit-engine", "scholarly-agent",
    ]:
        assert name in text
