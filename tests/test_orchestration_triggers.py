"""Acceptance criteria: trigger boundary of the single scholarly-agent
Skill and its dispatch paths. Skills are natural-language-triggered, so
what is verifiable offline is that (1) the frontmatter description covers
every module's domain and states the negative boundary, and (2) the
documented negative examples and module-selection paths are present for a
host/eval harness to test against (see evals/ for the executable cases)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "scholarly-agent"


def _frontmatter_description(skill_md_text: str) -> str:
    end = skill_md_text.find("\n---", 3)
    block = skill_md_text[3:end]
    for line in block.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError("no description: field found")


def test_description_covers_every_module_domain():
    description = _frontmatter_description((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")).lower()
    for term in [
        "drafting", "revising",          # voice
        "corpora", "style profiles",     # corpus
        "journals",                      # journal fit
        "executed",                      # router
    ]:
        assert term in description, f"description missing '{term}'"


def test_description_states_negative_boundary():
    description = _frontmatter_description((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
    assert "Do not invoke" in description
    assert "only the internal module" in description


def test_skill_md_documents_do_not_activate_examples():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert "Do not activate" in text
    for phrase in ["Fix this sentence", "What does APC mean", "Translate this title"]:
        assert phrase in text


def test_skill_md_documents_three_dispatch_paths():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    for path_name in ["**No module.**", "**Single module.**", "**Multi-module workflow.**"]:
        assert path_name in text


def test_routing_matrix_documents_negative_examples():
    text = (SKILL_DIR / "references" / "routing-matrix.md").read_text(encoding="utf-8")
    assert "Negative examples" in text
    for phrase in ["Fix this grammar", "What's a DOI", "Format this citation", "Translate this title"]:
        assert phrase in text


def test_each_module_keeps_its_scope_line():
    """Each module's MODULE.md carries its former Skill description as a
    Scope line, so the dispatcher can tell modules apart."""
    boundary_terms = {
        "adaptive-model-router": ["routing", "delegation"],
        "scholarly-corpus-builder": ["corpora", "profiles"],
        "scholarly-voice-engine": ["writing", "voice"],
        "journal-fit-engine": ["journal", "fit"],
    }
    for name, terms in boundary_terms.items():
        text = (SKILL_DIR / "modules" / name / "MODULE.md").read_text(encoding="utf-8")
        scope = next(l for l in text.splitlines() if l.startswith("> Scope:")).lower()
        for term in terms:
            assert term in scope, f"{name} scope missing '{term}'"
