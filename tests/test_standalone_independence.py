"""Acceptance criteria: self-containment of the single scholarly-agent
Skill. Everything the Skill needs at runtime -- workflow recipes, modules,
protocols, shared policy -- must resolve from inside skills/scholarly-agent/
itself, never via a path that escapes it toward the repository root."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "scholarly-agent"
MODULES = [
    "adaptive-model-router", "scholarly-corpus-builder",
    "scholarly-voice-engine", "journal-fit-engine",
]

# A relative path escaping the Skill directory toward repository-root folders.
ESCAPING_PATH_RE = re.compile(r"\.\./\.\./(\.\./)?(shared|protocols|workflows)/")


def test_skill_md_has_no_path_escaping_the_skill():
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert not ESCAPING_PATH_RE.findall(text)


@pytest.mark.parametrize("name", MODULES)
def test_module_md_has_no_path_escaping_the_skill(name):
    text = (SKILL_DIR / "modules" / name / "MODULE.md").read_text(encoding="utf-8")
    assert not re.findall(r"\.\./\.\./\.\./", text), f"{name}: MODULE.md escapes the Skill directory"


@pytest.mark.parametrize("name", MODULES)
def test_module_internal_references_resolve_within_module(name):
    """Every references/*.md, disciplines/*.md, assets/*.md path mentioned in
    a MODULE.md must exist inside that same module directory."""
    module_dir = SKILL_DIR / "modules" / name
    text = (module_dir / "MODULE.md").read_text(encoding="utf-8")
    for rel in re.findall(r"`((?:references|disciplines|assets)/[\w.\-/]+\.md)`", text):
        assert (module_dir / rel).exists(), f"{name}: MODULE.md references missing file {rel}"


def test_skill_md_internal_references_resolve_within_skill():
    """Every references/, scripts/, modules/, protocols/, shared/ path in
    SKILL.md must resolve inside skills/scholarly-agent/. This also covers
    the theory-paper.md packaging incident: a workflow recipe referenced but
    not bundled inside the Skill itself fails here."""
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    refs = re.findall(
        r"`((?:references|scripts|modules|protocols|shared)/[\w.\-/]+\.(?:md|py|json))`", text
    )
    assert any(r.startswith("references/workflows/") for r in refs)
    assert any(r.startswith("modules/") for r in refs)
    for rel in refs:
        assert (SKILL_DIR / rel).exists(), f"SKILL.md references missing file {rel}"


def test_protocols_and_shared_live_inside_the_skill():
    assert (SKILL_DIR / "protocols").is_dir()
    assert (SKILL_DIR / "shared" / "integrity-policy.md").is_file()
    assert not (ROOT / "protocols").exists()
    assert not (ROOT / "shared").exists()
