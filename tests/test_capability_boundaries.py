"""Acceptance criteria: the dispatcher must not duplicate module logic, and
module boundaries stay explicit after the v2 single-Skill merge. Heuristic
textual check: the top-level SKILL.md must not itself prescribe
domain-specific rules that belong to a module (citation formatting, model
names, journal ranking formulas, source-API details) -- those live in the
owning modules/<name>/MODULE.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "scholarly-agent"

SCOPE_CREEP_MARKERS = [
    "impact factor >",  # journal-fit-engine's ranking logic
    "gpt-5",  # a hardwired model name (adaptive-model-router's job)
    "gpt-4",
    "apa 7th edition",  # citation formatting specifics (voice module's job)
    "openalex api",  # corpus module's acquisition detail
]


def test_dispatcher_skill_md_has_no_scope_creep_markers():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8").lower()
    found = [m for m in SCOPE_CREEP_MARKERS if m in text]
    assert not found, f"SKILL.md appears to duplicate module logic: {found}"


def test_agents_yaml_declares_boundary_constraints_and_modules():
    text = (SKILL_DIR / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for marker in [
        "load_only_the_modules_a_request_needs",
        "dispatcher_never_inlines_module_domain_rules",
        "module_boundaries_follow_shared_capability_boundaries",
        "never_fabricate_citations_metrics_or_acceptance_probabilities",
    ]:
        assert marker in text
    for name in [
        "adaptive-model-router", "scholarly-corpus-builder",
        "scholarly-voice-engine", "journal-fit-engine", "peer-review-engine", "prose-polish-engine",
    ]:
        assert f"modules/{name}/MODULE.md" in text
        assert (SKILL_DIR / "modules" / name / "MODULE.md").is_file()


def test_capability_boundaries_doc_names_dispatcher_and_all_modules():
    text = (SKILL_DIR / "shared" / "capability-boundaries.md").read_text(encoding="utf-8")
    for name in [
        "adaptive-model-router", "scholarly-corpus-builder",
        "scholarly-voice-engine", "journal-fit-engine", "peer-review-engine", "prose-polish-engine", "scholarly-agent",
    ]:
        assert name in text
