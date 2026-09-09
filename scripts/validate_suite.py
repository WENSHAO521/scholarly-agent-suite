#!/usr/bin/env python3
"""Suite-level validator for scholarly-agent-suite.

Checks the acceptance criteria from the Suite spec (plugin manifest,
component presence/frontmatter/uniqueness, protocol schema validity,
COMPONENTS.json consistency, and workflow recipe references). Offline and
deterministic -- no network calls (rule 95).

Usage: python scripts/validate_suite.py
Exits 0 if every check passes, 1 otherwise, printing a PASS/FAIL line per
check.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from schema_lite import validate as schema_validate  # noqa: E402

SKILL_NAMES = [
    "scholarly-agent",
    "adaptive-model-router",
    "scholarly-corpus-builder",
    "scholarly-voice-engine",
    "journal-fit-engine",
]

PROTOCOL_FILES = {
    "execution-policy.schema.json": "EXECUTION_POLICY_V1",
    "scholarly-profile.schema.json": "SCHOLARLY_PROFILE_V1",
    "voice-request.schema.json": "VOICE_REQUEST_V1",
    "voice-context.schema.json": "VOICE_CONTEXT_V1",
    "voice-output.schema.json": "VOICE_OUTPUT_V1",
    "manuscript-profile.schema.json": "MANUSCRIPT_PROFILE_V1",
    "journal-profile.schema.json": "TARGET_JOURNAL_PROFILE_V1",
    "journal-style-context.schema.json": "JOURNAL_STYLE_CONTEXT_V1",
    "continuity-state.schema.json": "CONTINUITY_STATE_V1",
    "provenance.schema.json": "PROVENANCE_RECORD_V1",
}

WORKFLOW_FILES = [
    "paper-from-idea.md", "paper-from-notes.md", "revise-manuscript.md",
    "journal-selection.md", "target-journal-adaptation.md",
    "literature-review.md", "theory-paper.md", "empirical-paper.md",
    "systematic-review.md", "nature-commentary.md", "book-project.md",
    "monograph-chapter.md", "author-voice-calibration.md",
    "corpus-profile-build.md",
]

MINIMUM_REQUIRED_WORKFLOWS = [
    "paper-from-idea.md", "revise-manuscript.md", "journal-selection.md",
    "target-journal-adaptation.md", "literature-review.md",
    "nature-commentary.md", "book-project.md", "author-voice-calibration.md",
]


class Report:
    def __init__(self) -> None:
        self.failures: list[str] = []
        self.passes: list[str] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        if condition:
            self.passes.append(name)
        else:
            self.failures.append(f"{name}{': ' + detail if detail else ''}")

    def ok(self) -> bool:
        return not self.failures


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---"):
        raise ValueError("no frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise ValueError("frontmatter not closed")
    block = text[3:end]
    result: dict[str, str] = {}
    current_key = None
    for line in block.splitlines():
        if not line.strip():
            continue
        if line.startswith(" ") or line.startswith("\t"):
            if current_key:
                result[current_key] += " " + line.strip()
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            current_key = key.strip()
            result[current_key] = value.strip()
    return result


def validate_plugin_manifest(report: Report) -> None:
    manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    report.check("plugin.json exists", manifest_path.exists())
    if not manifest_path.exists():
        return
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for field in ("name", "version", "description", "author"):
        report.check(f"plugin.json has '{field}'", field in manifest)
    report.check("plugin.json name is 'scholarly-agent-suite'", manifest.get("name") == "scholarly-agent-suite")
    author = manifest.get("author", {})
    for field in ("name", "email", "url"):
        report.check(f"plugin.json author.{field} present", field in author)
    report.check("plugin.json has 'skills' path", manifest.get("skills") == "./skills/")
    skills_dir = ROOT / "skills"
    report.check("skills/ directory exists", skills_dir.is_dir())

    version_file = (ROOT / "VERSION")
    if version_file.exists():
        suite_version = version_file.read_text(encoding="utf-8").strip()
        report.check(
            "plugin.json version matches VERSION file",
            manifest.get("version") == suite_version,
            f"plugin.json={manifest.get('version')!r} VERSION={suite_version!r}",
        )


def validate_components_present_and_unique(report: Report) -> dict[str, dict]:
    skills_dir = ROOT / "skills"
    frontmatters: dict[str, dict] = {}
    seen_names: dict[str, str] = {}
    for skill_name in SKILL_NAMES:
        skill_dir = skills_dir / skill_name
        skill_md = skill_dir / "SKILL.md"
        report.check(f"skills/{skill_name}/ exists", skill_dir.is_dir())
        report.check(f"skills/{skill_name}/SKILL.md exists", skill_md.exists())
        if not skill_md.exists():
            continue
        # Reject double-nesting (rule 14): skills/<name>/<name>/SKILL.md must not exist.
        nested = skill_dir / skill_name
        report.check(f"skills/{skill_name}/ is not double-nested", not nested.is_dir())
        try:
            fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
        except ValueError as exc:
            report.check(f"skills/{skill_name}/SKILL.md has valid frontmatter", False, str(exc))
            continue
        report.check(f"skills/{skill_name}/SKILL.md has valid frontmatter", True)
        report.check(
            f"skills/{skill_name}/SKILL.md name matches directory",
            fm.get("name") == skill_name,
            f"found name={fm.get('name')!r}",
        )
        report.check(
            f"skills/{skill_name}/SKILL.md has non-empty description",
            bool(fm.get("description")),
        )
        frontmatters[skill_name] = fm
        name = fm.get("name")
        if name in seen_names:
            report.check(f"skill name '{name}' is unique", False, f"also used by {seen_names[name]}")
        else:
            seen_names[name] = skill_name
    report.check(
        "no duplicate Skill names across bundled skills",
        len(seen_names) == len([f for f in frontmatters.values() if f.get("name")]),
    )
    return frontmatters


def validate_components_json(report: Report) -> None:
    components_path = ROOT / "COMPONENTS.json"
    report.check("COMPONENTS.json exists", components_path.exists())
    if not components_path.exists():
        return
    data = json.loads(components_path.read_text(encoding="utf-8"))
    report.check("COMPONENTS.json has 'suite'", data.get("suite") == "scholarly-agent-suite")
    report.check("COMPONENTS.json has 'suite_version'", "suite_version" in data)
    version_file = ROOT / "VERSION"
    if version_file.exists():
        suite_version = version_file.read_text(encoding="utf-8").strip()
        report.check(
            "COMPONENTS.json suite_version matches VERSION file",
            data.get("suite_version") == suite_version,
            f"COMPONENTS.json={data.get('suite_version')!r} VERSION={suite_version!r} "
            "-- run `python scripts/sync_components.py` to regenerate COMPONENTS.json after bumping VERSION",
        )
        scholarly_agent_entry = data.get("components", {}).get("scholarly-agent", {})
        report.check(
            "COMPONENTS.json scholarly-agent version matches VERSION file",
            scholarly_agent_entry.get("version") == suite_version,
            f"COMPONENTS.json scholarly-agent.version={scholarly_agent_entry.get('version')!r} "
            f"VERSION={suite_version!r}",
        )
    components = data.get("components", {})
    for name in SKILL_NAMES:
        entry = components.get(name)
        report.check(f"COMPONENTS.json has entry for {name}", entry is not None)
        if entry is None:
            continue
        report.check(f"COMPONENTS.json {name} has version", bool(entry.get("version")))
        report.check(f"COMPONENTS.json {name} has role", bool(entry.get("role")))
        report.check(f"COMPONENTS.json {name} has source_repository", bool(entry.get("source_repository")))
        report.check(f"COMPONENTS.json {name} has source_commit", bool(entry.get("source_commit")))

    compatibility = data.get("compatibility", {})
    version_re = re.compile(r"^(>=|<)(\d+(?:\.\d+)*)$")
    for name in ["adaptive-model-router", "scholarly-corpus-builder", "scholarly-voice-engine", "journal-fit-engine"]:
        range_expr = compatibility.get(name)
        report.check(f"compatibility range declared for {name}", bool(range_expr))
        if not range_expr:
            continue
        parts = [p.strip() for p in range_expr.split(",")]
        parsed_ok = all(version_re.match(p) for p in parts)
        report.check(f"compatibility range for {name} parses ('{range_expr}')", parsed_ok)
        if not parsed_ok:
            continue
        packaged_version = components.get(name, {}).get("version", "")
        report.check(
            f"packaged {name} version {packaged_version!r} satisfies declared range {range_expr!r}",
            _version_in_range(packaged_version, parts),
        )


def _version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(p) for p in v.split("."))


def _version_in_range(version: str, parts: list[str]) -> bool:
    if not version:
        return False
    v = _version_tuple(version)
    for part in parts:
        op, bound = (part[:2], part[2:]) if part.startswith(">=") else (part[0], part[1:])
        bound_t = _version_tuple(bound)
        # pad shorter tuple for comparison
        length = max(len(v), len(bound_t))
        vv = v + (0,) * (length - len(v))
        bb = bound_t + (0,) * (length - len(bound_t))
        if op == ">=" and not vv >= bb:
            return False
        if op == "<" and not vv < bb:
            return False
    return True


def validate_protocols(report: Report) -> None:
    protocols_dir = ROOT / "protocols"
    for filename, protocol_id in PROTOCOL_FILES.items():
        path = protocols_dir / filename
        report.check(f"protocols/{filename} exists", path.exists())
        if not path.exists():
            continue
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.check(f"protocols/{filename} is valid JSON", False, str(exc))
            continue
        report.check(f"protocols/{filename} is valid JSON", True)
        report.check(
            f"protocols/{filename} title == {protocol_id}",
            schema.get("title") == protocol_id,
        )
        report.check(f"protocols/{filename} declares 'type': 'object'", schema.get("type") == "object")
        # Structural self-check: every property referenced in 'required' must
        # be declared in 'properties' (a schema bug would break every producer/consumer).
        required = set(schema.get("required", []))
        properties = set(schema.get("properties", {}).keys())
        report.check(
            f"protocols/{filename} required fields are all declared",
            required.issubset(properties),
            f"missing: {required - properties}",
        )


def validate_workflows(report: Report, orchestrator_frontmatter_found: bool) -> None:
    workflows_dir = ROOT / "workflows"
    skill_md_text = (ROOT / "skills" / "scholarly-agent" / "SKILL.md")
    skill_md_content = skill_md_text.read_text(encoding="utf-8") if skill_md_text.exists() else ""
    for filename in WORKFLOW_FILES:
        path = workflows_dir / filename
        report.check(f"workflows/{filename} exists", path.exists())
    for filename in MINIMUM_REQUIRED_WORKFLOWS:
        report.check(
            f"scholarly-agent SKILL.md references workflows/{filename}",
            filename in skill_md_content,
        )


def validate_shared_docs(report: Report) -> None:
    for filename in [
        "integrity-policy.md", "provenance-policy.md", "terminology.md",
        "protocol-versioning.md", "capability-boundaries.md",
    ]:
        report.check(f"shared/{filename} exists", (ROOT / "shared" / filename).exists())


def validate_no_double_nesting(report: Report) -> None:
    skills_dir = ROOT / "skills"
    for skill_dir in skills_dir.iterdir():
        if not skill_dir.is_dir():
            continue
        nested = skill_dir / skill_dir.name
        report.check(f"{skill_dir.name}/ has no self-named nested directory", not nested.is_dir())


def main() -> int:
    report = Report()
    validate_plugin_manifest(report)
    frontmatters = validate_components_present_and_unique(report)
    validate_components_json(report)
    validate_protocols(report)
    validate_workflows(report, "scholarly-agent" in frontmatters)
    validate_shared_docs(report)
    validate_no_double_nesting(report)

    for name in report.passes:
        print(f"PASS  {name}")
    for name in report.failures:
        print(f"FAIL  {name}", file=sys.stderr)

    total = len(report.passes) + len(report.failures)
    print(f"\n{len(report.passes)}/{total} checks passed.")
    return 0 if report.ok() else 1


if __name__ == "__main__":
    sys.exit(main())
