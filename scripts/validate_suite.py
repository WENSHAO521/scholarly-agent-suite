#!/usr/bin/env python3
"""Suite-level validator for scholarly-agent-suite.

Checks the acceptance criteria for the v2 single-Skill layout (plugin
manifest, exactly one Skill with its modules, protocol schema validity,
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
from workflow_manifest import CANONICAL_WORKFLOWS_DIR, REQUIRED_WORKFLOWS  # noqa: E402
import sync_workflows  # noqa: E402

SKILL_NAME = "scholarly-agent"
SKILL_DIR = ROOT / "skills" / SKILL_NAME
MODULE_NAMES = [
    "adaptive-model-router",
    "scholarly-corpus-builder",
    "scholarly-voice-engine",
    "journal-fit-engine",
    "peer-review-engine",
    "prose-polish-engine",
    "translation-engine",
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
    "review-report.schema.json": "REVIEW_REPORT_V1",
    "editorial-decision.schema.json": "EDITORIAL_DECISION_V1",
    "polish-report.schema.json": "POLISH_REPORT_V1",
    "translation-report.schema.json": "TRANSLATION_REPORT_V1",
}

# The single source of truth for required workflow recipes lives in
# scripts/workflow_manifest.py -- imported above, not redeclared here.


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


def validate_skill_and_modules(report: Report) -> dict[str, dict]:
    """v2 layout: exactly one Skill under skills/, its modules inside it."""
    skills_dir = ROOT / "skills"
    skill_dirs = sorted(p.name for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []
    report.check("skills/ contains exactly one Skill (scholarly-agent)", skill_dirs == [SKILL_NAME], f"found {skill_dirs}")
    stray = sorted(p.relative_to(ROOT).as_posix() for p in skills_dir.rglob("SKILL.md") if p.parent != SKILL_DIR)
    report.check("no SKILL.md outside skills/scholarly-agent/", not stray, f"found {stray}")
    skill_md = SKILL_DIR / "SKILL.md"
    report.check("skills/scholarly-agent/SKILL.md exists", skill_md.exists())
    frontmatters: dict[str, dict] = {}
    if skill_md.exists():
        text = skill_md.read_text(encoding="utf-8")
        try:
            fm = parse_frontmatter(text)
        except ValueError as exc:
            report.check("skills/scholarly-agent/SKILL.md has valid frontmatter", False, str(exc))
            fm = {}
        else:
            report.check("skills/scholarly-agent/SKILL.md has valid frontmatter", True)
            frontmatters[SKILL_NAME] = fm
        report.check("SKILL.md name is 'scholarly-agent'", fm.get("name") == SKILL_NAME, f"found {fm.get('name')!r}")
        report.check("SKILL.md has non-empty description", bool(fm.get("description")))
    else:
        text = ""
    for name in MODULE_NAMES:
        module_md = SKILL_DIR / "modules" / name / "MODULE.md"
        report.check(f"modules/{name}/MODULE.md exists", module_md.exists())
        if module_md.exists():
            report.check(
                f"modules/{name}/MODULE.md has no Skill frontmatter",
                not module_md.read_text(encoding="utf-8").startswith("---"),
            )
        report.check(f"SKILL.md references modules/{name}/MODULE.md", f"modules/{name}/MODULE.md" in text)
    return frontmatters


def validate_components_json(report: Report) -> None:
    components_path = ROOT / "COMPONENTS.json"
    report.check("COMPONENTS.json exists", components_path.exists())
    if not components_path.exists():
        return
    data = json.loads(components_path.read_text(encoding="utf-8"))
    report.check("COMPONENTS.json has 'suite'", data.get("suite") == "scholarly-agent-suite")
    report.check("COMPONENTS.json skill is 'scholarly-agent'", data.get("skill") == SKILL_NAME)
    version_file = ROOT / "VERSION"
    if version_file.exists():
        suite_version = version_file.read_text(encoding="utf-8").strip()
        report.check(
            "COMPONENTS.json suite_version matches VERSION file",
            data.get("suite_version") == suite_version,
            f"COMPONENTS.json={data.get('suite_version')!r} VERSION={suite_version!r}",
        )
    modules = data.get("modules", {})
    report.check("COMPONENTS.json lists exactly the expected modules", sorted(modules) == sorted(MODULE_NAMES), f"found {sorted(modules)}")
    sha_re = re.compile(r"^[0-9a-f]{40}$")
    for name in MODULE_NAMES:
        entry = modules.get(name)
        if entry is None:
            continue
        report.check(f"COMPONENTS.json {name} path exists", (ROOT / entry.get("path", "")).is_dir())
        report.check(f"COMPONENTS.json {name} has role", bool(entry.get("role")))
        if "merged_from" in entry:
            origin = entry["merged_from"]
            report.check(f"COMPONENTS.json {name} merged_from has repository and version", bool(origin.get("repository")) and bool(origin.get("version")))
            report.check(f"COMPONENTS.json {name} merged_from commit is a full sha", bool(sha_re.match(origin.get("commit", ""))))
        else:
            native = entry.get("origin", {})
            report.check(f"COMPONENTS.json {name} is native with added_in version", native.get("native") is True and bool(native.get("added_in")))


def validate_protocols(report: Report) -> None:
    protocols_dir = SKILL_DIR / "protocols"
    for filename, protocol_id in PROTOCOL_FILES.items():
        path = protocols_dir / filename
        report.check(f"skills/scholarly-agent/protocols/{filename} exists", path.exists())
        if not path.exists():
            continue
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            report.check(f"skills/scholarly-agent/protocols/{filename} is valid JSON", False, str(exc))
            continue
        report.check(f"skills/scholarly-agent/protocols/{filename} is valid JSON", True)
        report.check(
            f"protocols/{filename} title == {protocol_id}",
            schema.get("title") == protocol_id,
        )
        report.check(f"skills/scholarly-agent/protocols/{filename} declares 'type': 'object'", schema.get("type") == "object")
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
    skill_md_text = (ROOT / "skills" / "scholarly-agent" / "SKILL.md")
    skill_md_content = skill_md_text.read_text(encoding="utf-8") if skill_md_text.exists() else ""
    for filename in REQUIRED_WORKFLOWS:
        path = CANONICAL_WORKFLOWS_DIR / filename
        report.check(f"skills/scholarly-agent/references/workflows/{filename} exists", path.exists())
        report.check(
            f"scholarly-agent SKILL.md references references/workflows/{filename}",
            f"references/workflows/{filename}" in skill_md_content,
        )
    drift = sync_workflows.check_drift()
    report.check(
        "workflows/ documentation mirror matches skills/scholarly-agent/references/workflows/ exactly",
        not drift,
        "; ".join(drift),
    )


def validate_shared_docs(report: Report) -> None:
    for filename in [
        "integrity-policy.md", "provenance-policy.md", "terminology.md",
        "protocol-versioning.md", "capability-boundaries.md",
    ]:
        report.check(f"skills/scholarly-agent/shared/{filename} exists", (SKILL_DIR / "shared" / filename).exists())


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
    frontmatters = validate_skill_and_modules(report)
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
