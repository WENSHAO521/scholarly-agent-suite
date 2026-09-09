"""Acceptance criteria: negative orchestration triggers (spec sections 66,
151) and narrow trigger boundary (spec section 16-17). These Skills are
natural-language-triggered, not code-triggered, so what is actually
verifiable offline is: (1) the frontmatter description states the narrow
boundary explicitly, and (2) the documented negative examples are present so
a host/eval harness has them to test against (see evals/ for the executable
version of these same cases)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _frontmatter_description(skill_md_text: str) -> str:
    end = skill_md_text.find("\n---", 3)
    block = skill_md_text[3:end]
    for line in block.splitlines():
        if line.startswith("description:"):
            return line.split(":", 1)[1].strip()
    raise AssertionError("no description: field found")


def test_orchestrator_description_states_two_or_more_specialist_threshold():
    text = (ROOT / "skills" / "scholarly-agent" / "SKILL.md").read_text(encoding="utf-8")
    description = _frontmatter_description(text)
    assert "two or more specialist" in description
    assert "do not invoke" in description


def test_orchestrator_documents_do_not_activate_examples():
    text = (ROOT / "skills" / "scholarly-agent" / "SKILL.md").read_text(encoding="utf-8")
    assert "Do not activate" in text
    for phrase in ["Fix this sentence", "What does APC mean", "Translate this title"]:
        assert phrase in text


def test_routing_matrix_documents_negative_examples():
    text = (ROOT / "skills" / "scholarly-agent" / "references" / "routing-matrix.md").read_text(encoding="utf-8")
    assert "Negative examples" in text
    for phrase in ["Fix this grammar", "What's a DOI", "Format this citation", "Translate this title"]:
        assert phrase in text


def test_specialist_descriptions_carry_their_own_narrow_boundary():
    """Each specialist's own description should distinguish itself from the
    others (rule 56: avoid competing implicit triggers)."""
    boundary_terms = {
        "adaptive-model-router": ["routing", "delegation"],
        "scholarly-corpus-builder": ["corpora", "profiles"],
        "scholarly-voice-engine": ["writing", "voice"],
        "journal-fit-engine": ["journal", "fit"],
    }
    for name, terms in boundary_terms.items():
        text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
        description = _frontmatter_description(text).lower()
        for term in terms:
            assert term in description, f"{name} description missing expected boundary term '{term}'"
