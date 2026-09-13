"""Acceptance criteria: Independence (spec section 141) -- every specialist
Skill must still function outside the Suite, i.e. it must not have a hard
runtime reference to a Suite-only path (../shared/*, ../../shared/*,
../protocols/*, ../../protocols/*) inside its own bundled SKILL.md or
agents/openai.yaml."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SPECIALISTS = [
    "adaptive-model-router", "scholarly-corpus-builder",
    "scholarly-voice-engine", "journal-fit-engine",
]

# A relative path escaping the Skill's own directory toward Suite-only
# top-level folders. scholarly-agent is exempt: its whole purpose is Suite
# coordination, so it is allowed (and expected) to reference workflows/,
# shared/, and protocols/.
SUITE_ONLY_PATH_RE = re.compile(r"\.\./(\.\./)?(shared|protocols|workflows)/")


@pytest.mark.parametrize("name", SPECIALISTS)
def test_specialist_skill_md_has_no_hard_suite_path_dependency(name):
    skill_md = ROOT / "skills" / name / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    matches = SUITE_ONLY_PATH_RE.findall(text)
    assert not matches, f"skills/{name}/SKILL.md references a Suite-only path: {matches}"


@pytest.mark.parametrize("name", SPECIALISTS)
def test_specialist_agents_yaml_has_no_hard_suite_path_dependency(name):
    agents_yaml = ROOT / "skills" / name / "agents" / "openai.yaml"
    if not agents_yaml.exists():
        pytest.skip(f"{name} has no agents/openai.yaml")
    text = agents_yaml.read_text(encoding="utf-8")
    matches = SUITE_ONLY_PATH_RE.findall(text)
    assert not matches, f"skills/{name}/agents/openai.yaml references a Suite-only path: {matches}"


@pytest.mark.parametrize("name", SPECIALISTS)
def test_specialist_all_internal_references_resolve_within_own_directory(name):
    """Every references/*.md, disciplines/*.md link mentioned in SKILL.md
    must exist inside this same skill directory -- confirms it was packaged
    as a complete, self-contained tree (rule 42)."""
    skill_dir = ROOT / "skills" / name
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    for rel in re.findall(r"`((?:references|disciplines|assets)/[\w.\-/]+\.md)`", text):
        assert (skill_dir / rel).exists(), f"{name}: SKILL.md references missing file {rel}"


def test_scholarly_agent_all_internal_references_resolve_within_own_directory():
    """scholarly-agent is not in SPECIALISTS above because it is exempt from
    SUITE_ONLY_PATH_RE (it legitimately coordinates shared/ and protocols/)
    -- but its own workflow recipes are a different case: they are not
    Suite-only shared resources, they are scholarly-agent's own bundled
    content, so every references/workflows/*.md link in its SKILL.md must
    resolve inside its own directory exactly like a specialist's
    references/*.md links do. This is the regression guard for the
    theory-paper.md packaging incident: it fails if SKILL.md ever points at
    a workflow recipe that is not actually bundled inside
    skills/scholarly-agent/ itself."""
    skill_dir = ROOT / "skills" / "scholarly-agent"
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    refs = re.findall(r"`((?:references|scripts)/[\w.\-/]+\.(?:md|py))`", text)
    assert any(r.startswith("references/workflows/") for r in refs), (
        "expected at least one references/workflows/*.md reference in scholarly-agent's SKILL.md"
    )
    for rel in refs:
        assert (skill_dir / rel).exists(), f"scholarly-agent: SKILL.md references missing file {rel}"
