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
