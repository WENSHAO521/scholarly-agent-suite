"""Acceptance criteria: Plugin/component presence, frontmatter, uniqueness,
versions (spec sections 62, 123, 141)."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILL_NAMES = [
    "scholarly-agent", "adaptive-model-router", "scholarly-corpus-builder",
    "scholarly-voice-engine", "journal-fit-engine",
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


@pytest.mark.parametrize("name", SKILL_NAMES)
def test_skill_frontmatter_name_matches_directory(name):
    skill_md = ROOT / "skills" / name / "SKILL.md"
    fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    assert fm["name"] == name
    assert fm["description"], "description must be non-empty"


@pytest.mark.parametrize("name", SKILL_NAMES)
def test_no_double_nesting(name):
    skill_dir = ROOT / "skills" / name
    assert not (skill_dir / name).is_dir(), f"skills/{name}/{name}/ double-nesting detected"


def test_no_duplicate_skill_names():
    names = []
    for name in SKILL_NAMES:
        skill_md = ROOT / "skills" / name / "SKILL.md"
        fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        names.append(fm["name"])
    assert len(names) == len(set(names)), f"duplicate Skill names found: {names}"


def test_components_json_has_all_five_with_required_fields():
    data = json.loads((ROOT / "COMPONENTS.json").read_text(encoding="utf-8"))
    components = data["components"]
    for name in SKILL_NAMES:
        assert name in components, f"COMPONENTS.json missing entry for {name}"
        entry = components[name]
        assert entry.get("version")
        assert entry.get("role")
        assert entry.get("source_repository")
        assert entry.get("source_commit")


def test_component_versions_are_not_forced_to_match_suite_version():
    """Spec rule 7: a valid release need not have all skills == suite version."""
    data = json.loads((ROOT / "COMPONENTS.json").read_text(encoding="utf-8"))
    versions = {name: entry["version"] for name, entry in data["components"].items()}
    # This suite's actual v1.0.0 release legitimately mixes versions
    # (0.2.0 / 0.9.0 / 1.0.0 / 0.1.0 / 1.0.0) -- assert that heterogeneity,
    # not homogeneity, is what COMPONENTS.json currently records.
    assert len(set(versions.values())) > 1


def test_compatibility_ranges_declared_for_all_specialists():
    data = json.loads((ROOT / "COMPONENTS.json").read_text(encoding="utf-8"))
    compatibility = data["compatibility"]
    for name in ["adaptive-model-router", "scholarly-corpus-builder", "scholarly-voice-engine", "journal-fit-engine"]:
        assert name in compatibility


def test_source_commits_are_full_shas_not_branch_names():
    data = json.loads((ROOT / "scripts" / "component-sources.json").read_text(encoding="utf-8"))
    for entry in data["components"]:
        ref = entry["ref"]
        assert len(ref) == 40 and all(c in "0123456789abcdef" for c in ref), (
            f"{entry['name']}: ref {ref!r} is not a pinned 40-char commit sha"
        )
