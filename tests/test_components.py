"""Acceptance criteria for the v2 single-Skill layout: exactly one Skill
(`scholarly-agent`) ships under skills/, and its modules (the four former
specialist Skills plus native ones such as peer-review-engine) live inside it as on-demand modules under
skills/scholarly-agent/modules/<name>/MODULE.md."""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "scholarly-agent"
MODULE_NAMES = [
    "adaptive-model-router", "scholarly-corpus-builder",
    "scholarly-voice-engine", "journal-fit-engine", "peer-review-engine",
]


def parse_frontmatter(text: str) -> dict:
    assert text.startswith("---")
    end = text.find("\n---", 3)
    assert end != -1
    result = {}
    current_key = None
    for line in text[3:end].splitlines():
        if not line.strip():
            continue
        if line[0] in " \t" and current_key:
            result[current_key] += " " + line.strip()
            continue
        key, _, value = line.partition(":")
        current_key = key.strip()
        result[current_key] = value.strip()
    return result


def test_exactly_one_skill_ships():
    skill_dirs = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())
    assert skill_dirs == ["scholarly-agent"], skill_dirs


def test_no_skill_md_anywhere_else_under_skills():
    """A stray SKILL.md inside a module would make a host register it as a
    second, competing Skill -- the exact thing the merge removed."""
    found = sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "skills").rglob("SKILL.md"))
    assert found == ["skills/scholarly-agent/SKILL.md"], found


def test_skill_frontmatter_name_matches_directory():
    fm = parse_frontmatter((SKILL_DIR / "SKILL.md").read_text(encoding="utf-8"))
    assert fm["name"] == "scholarly-agent"
    assert fm["description"]


def test_no_double_nesting():
    assert not (SKILL_DIR / "scholarly-agent").is_dir()


@pytest.mark.parametrize("name", MODULE_NAMES)
def test_module_present_without_frontmatter(name):
    module_md = SKILL_DIR / "modules" / name / "MODULE.md"
    assert module_md.is_file(), f"modules/{name}/MODULE.md missing"
    assert not module_md.read_text(encoding="utf-8").startswith("---"), (
        f"modules/{name}/MODULE.md must not carry Skill frontmatter"
    )


@pytest.mark.parametrize("name", MODULE_NAMES)
def test_module_referenced_from_skill_md(name):
    text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
    assert f"modules/{name}/MODULE.md" in text


def test_components_json_lists_one_skill_and_its_modules():
    data = json.loads((ROOT / "COMPONENTS.json").read_text(encoding="utf-8"))
    assert data["skill"] == "scholarly-agent"
    assert sorted(data["modules"]) == sorted(MODULE_NAMES)
    for name, entry in data["modules"].items():
        assert entry["path"] == f"skills/scholarly-agent/modules/{name}"
        assert (ROOT / entry["path"]).is_dir()
        assert entry.get("role")
        if "merged_from" in entry:
            origin = entry["merged_from"]
            assert origin["repository"].startswith("https://github.com/")
            assert len(origin["commit"]) == 40
            assert origin["version"]
        else:  # a module created in this repository
            assert entry["origin"] == {"native": True, "added_in": entry["origin"]["added_in"]}
            assert re.match(r"^\d+\.\d+\.\d+$", entry["origin"]["added_in"])


def test_components_json_suite_version_matches_version_file():
    suite_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    data = json.loads((ROOT / "COMPONENTS.json").read_text(encoding="utf-8"))
    assert data["suite_version"] == suite_version
