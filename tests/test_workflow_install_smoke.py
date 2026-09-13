"""Install/runtime smoke test: constructs the same filesystem layout an
*installed* scholarly-agent Skill actually receives -- not the repository
root -- and proves workflow resolution works from inside it.

This is the test that would have caught the original incident directly: a
test that only ever looks at the repository root (as
tests/test_workflows.py and scripts/validate_suite.py do) can pass while a
real installed copy is still broken, if the installed layout differs from
the dev repo's layout in any way the source-only checks don't model. Here
the installed layout is built explicitly and deliberately excludes
everything a standalone/plugin/ZIP install would not carry: no repository
root, no top-level workflows/ mirror, no shared/ or protocols/, no tests/
or scripts/ from the Suite root -- only what scholarly-agent's own package
directory contains.
"""
import shutil
from pathlib import Path

import pytest

from conftest import load_module

ROOT = Path(__file__).resolve().parent.parent
workflow_manifest = load_module("workflow_manifest", "workflow_manifest.py")
REQUIRED_WORKFLOWS = workflow_manifest.REQUIRED_WORKFLOWS


@pytest.fixture
def installed_scholarly_agent(tmp_path) -> Path:
    """Build an installed-Skill-only layout: exactly what a host exposing
    just the declared skills/ tree would hand to scholarly-agent, placed
    well outside the repository (pytest's tmp_path, not a repo subdirectory)
    so there is no way for a lookup to accidentally succeed by walking up
    to the real repository root."""
    install_root = tmp_path / "installed" / "scholarly-agent"
    shutil.copytree(ROOT / "skills" / "scholarly-agent", install_root)
    return install_root


def _load_resolver(install_root: Path):
    return load_module(
        "installed_workflow_resolver",
        str(install_root / "scripts" / "workflow_resolver.py"),
    )


def test_installed_skill_root_has_no_repository_context(installed_scholarly_agent):
    """Sanity check on the fixture itself: prove this is genuinely an
    isolated install, not an accidental copy of the whole repo."""
    assert not (installed_scholarly_agent / ".git").exists()
    assert not (installed_scholarly_agent.parent / "workflows").exists()
    assert not (installed_scholarly_agent.parent / "shared").exists()
    assert not (installed_scholarly_agent.parent / "protocols").exists()
    assert not (installed_scholarly_agent.parent.parent / "workflows").exists()


def test_install_can_load_skill_md(installed_scholarly_agent):
    skill_md = installed_scholarly_agent / "SKILL.md"
    assert skill_md.is_file()
    text = skill_md.read_text(encoding="utf-8")
    assert text.startswith("---")
    assert "scholarly-agent" in text


def test_install_can_resolve_workflow_index(installed_scholarly_agent):
    """The workflow index is the set of references/workflows/*.md
    referenced by SKILL.md -- resolve every one of them from inside the
    installed layout and confirm none require anything outside it."""
    skill_md_text = (installed_scholarly_agent / "SKILL.md").read_text(encoding="utf-8")
    resolver = _load_resolver(installed_scholarly_agent)
    for name in REQUIRED_WORKFLOWS:
        assert f"references/workflows/{name}" in skill_md_text, (
            f"{name} is in the required workflow index but SKILL.md does not "
            "reference it by its in-package path"
        )
        resolution = resolver.resolve_workflow(installed_scholarly_agent, name)
        assert resolution.ok, (
            f"{name}: expected RESOLVED from the installed runtime, got "
            f"{resolution.status}: {resolution.detail}"
        )


@pytest.mark.parametrize("name", ["theory-paper.md", "empirical-paper.md", "target-journal-adaptation.md"])
def test_install_resolves_specific_high_value_workflows(installed_scholarly_agent, name):
    """The three workflows the task's acceptance criteria name explicitly --
    theory-paper.md is the one the original incident actually failed on."""
    resolver = _load_resolver(installed_scholarly_agent)
    resolution = resolver.resolve_workflow(installed_scholarly_agent, name)
    assert resolution.status == resolver.RESOLVED, f"{name}: {resolution.status} -- {resolution.detail}"
    assert resolution.path is not None
    assert resolution.path.is_file()
    assert resolution.path.read_text(encoding="utf-8").strip()


def test_install_fails_if_only_available_from_repository_root(installed_scholarly_agent, tmp_path):
    """The regression this whole test module exists to prevent: if a
    workflow were reachable only via the repository root's workflows/ (not
    from inside the installed Skill), this test must fail. Simulate exactly
    that broken state by deleting the file from the installed copy while
    leaving the repository root copy untouched, and confirm resolution
    correctly reports a runtime gap rather than silently succeeding by
    reading the repository root instead."""
    resolver = _load_resolver(installed_scholarly_agent)
    target = installed_scholarly_agent / "references" / "workflows" / "theory-paper.md"
    assert target.is_file()
    assert (ROOT / "workflows" / "theory-paper.md").is_file()  # repo-root mirror still has it

    target.unlink()
    resolution = resolver.resolve_workflow(installed_scholarly_agent, "theory-paper.md")
    assert resolution.status == resolver.WORKFLOW_RUNTIME_MISSING, (
        "resolution must not silently succeed via the repository root's workflows/ mirror -- "
        f"got {resolution.status}: {resolution.detail}"
    )


def test_install_reports_unresolvable_not_missing_when_directory_absent(tmp_path):
    """If references/workflows/ itself is absent from the install (e.g. an
    incomplete or misconfigured install), resolution must report
    WORKFLOW_UNRESOLVABLE, never a false WORKFLOW_RUNTIME_MISSING -- this is
    the exact distinction the original incident collapsed."""
    broken_root = tmp_path / "broken-install"
    (broken_root / "scripts").mkdir(parents=True)
    shutil.copy2(
        ROOT / "skills" / "scholarly-agent" / "scripts" / "workflow_resolver.py",
        broken_root / "scripts" / "workflow_resolver.py",
    )
    resolver = load_module("broken_install_workflow_resolver", str(broken_root / "scripts" / "workflow_resolver.py"))
    resolution = resolver.resolve_workflow(broken_root, "theory-paper.md")
    assert resolution.status == resolver.WORKFLOW_UNRESOLVABLE, resolution.status
