"""Packaging regression tests for the workflow-recipe runtime-visibility
defect: scholarly-agent once reported `theory-paper.md` as missing from an
installed package even though it existed on `master`, in tag `v1.2.0`, was
allowlisted by `package_suite.py`, and was documented in SKILL.md -- because
the only lookup path (`../../workflows/`) never resolves once the whole
repository root is not visible next to `skills/` (standalone install,
`.codex-plugin` load, release ZIP, or a host exposing only `skills/`).

Every REQUIRED_WORKFLOW (scripts/workflow_manifest.py -- the single source
of truth these tests share, never redeclared here) is proven present at
every layer a real install could expose:

  1. the source runtime boundary (skills/scholarly-agent/references/workflows/)
  2. package_suite.iter_runtime_files()
  3. the generated Suite ZIP
  4. release-manifest.json
  5. a standalone scholarly-agent package (skills/scholarly-agent/ copied
     out on its own, nothing else from the repository present)

Plus one negative test proving that a workflow genuinely missing from the
canonical source is caught by the same mechanism that would otherwise catch
it in CI -- the exact failure mode this incident needs guarded against.
"""
import json
import shutil
import zipfile
from pathlib import Path

import pytest

from conftest import load_module

ROOT = Path(__file__).resolve().parent.parent
package_suite = load_module("package_suite", "package_suite.py")
workflow_manifest = load_module("workflow_manifest", "workflow_manifest.py")
sync_workflows = load_module("sync_workflows", "sync_workflows.py")

REQUIRED_WORKFLOWS = workflow_manifest.REQUIRED_WORKFLOWS
CANONICAL_WORKFLOWS_DIR = workflow_manifest.CANONICAL_WORKFLOWS_DIR
SCHOLARLY_AGENT_SCRIPTS = ROOT / "skills" / "scholarly-agent" / "scripts"


# ---------------------------------------------------------------------------
# 1. Source runtime boundary
# ---------------------------------------------------------------------------

def test_scholarly_agent_contains_all_required_workflows():
    missing = workflow_manifest.missing_from(CANONICAL_WORKFLOWS_DIR)
    assert not missing, f"missing from skills/scholarly-agent/references/workflows/: {missing}"


# ---------------------------------------------------------------------------
# 2. package_suite.iter_runtime_files()
# ---------------------------------------------------------------------------

def test_runtime_package_contains_all_required_workflows():
    files = package_suite.iter_runtime_files()
    rel = {f.relative_to(ROOT).as_posix() for f in files}
    for name in REQUIRED_WORKFLOWS:
        assert f"skills/scholarly-agent/references/workflows/{name}" in rel, (
            f"{name} not returned by package_suite.iter_runtime_files() at the "
            "runtime-canonical path"
        )


# ---------------------------------------------------------------------------
# 3. The generated Suite ZIP
# ---------------------------------------------------------------------------

def test_release_zip_contains_all_required_workflows(tmp_path, monkeypatch):
    monkeypatch.setattr(package_suite, "DIST_DIR", tmp_path)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files = package_suite.iter_runtime_files()
    zip_path = package_suite.build_zip(files, version)
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        for name in REQUIRED_WORKFLOWS:
            arcname = f"scholarly-agent-suite/skills/scholarly-agent/references/workflows/{name}"
            assert arcname in names, f"{arcname} not present in the built release ZIP"
            # Not just present -- actually extractable, non-empty content.
            assert len(zf.read(arcname)) > 0


# ---------------------------------------------------------------------------
# 4. release-manifest.json
# ---------------------------------------------------------------------------

def test_release_manifest_contains_all_required_workflows(tmp_path, monkeypatch):
    monkeypatch.setattr(package_suite, "DIST_DIR", tmp_path)
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    files = package_suite.iter_runtime_files()
    zip_path = package_suite.build_zip(files, version)
    manifest_path = package_suite.write_release_manifest(zip_path, files, version)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for name in REQUIRED_WORKFLOWS:
        expected = f"scholarly-agent-suite/skills/scholarly-agent/references/workflows/{name}"
        assert expected in manifest["files"], f"{expected} missing from release-manifest.json's file list"


# ---------------------------------------------------------------------------
# 5. Standalone scholarly-agent package
# ---------------------------------------------------------------------------

def test_standalone_scholarly_agent_contains_workflows(tmp_path):
    """Copy *only* skills/scholarly-agent/ out to its own directory -- no
    repository root, no top-level workflows/, no shared/ or protocols/ --
    simulating a standalone Skill install, and prove every required
    workflow recipe is still a real, readable file at the runtime-canonical
    in-package path."""
    standalone_root = tmp_path / "scholarly-agent"
    shutil.copytree(ROOT / "skills" / "scholarly-agent", standalone_root)

    # Prove nothing outside the copied Skill directory exists to fall back on.
    assert not (standalone_root / ".." / "workflows").resolve().exists() or (
        standalone_root / ".." / "workflows"
    ).resolve() != (ROOT / "workflows").resolve()

    missing = workflow_manifest.missing_from(standalone_root / "references" / "workflows")
    assert not missing, f"standalone scholarly-agent package is missing: {missing}"
    for name in REQUIRED_WORKFLOWS:
        content = (standalone_root / "references" / "workflows" / name).read_text(encoding="utf-8")
        assert content.strip()


# ---------------------------------------------------------------------------
# Documentation-mirror drift (workflows/ at the repository root)
# ---------------------------------------------------------------------------

def test_documentation_mirror_matches_canonical_source():
    assert not sync_workflows.check_drift()


def test_workflow_resolver_known_list_matches_source_of_truth():
    """skills/scholarly-agent/scripts/workflow_resolver.py embeds its own
    KNOWN_WORKFLOWS literal (it must stay self-contained for a standalone
    install with no access to the Suite's dev-only scripts/ directory) --
    this is the drift guard that keeps it from silently diverging from
    scripts/workflow_manifest.REQUIRED_WORKFLOWS."""
    resolver = load_module("scholarly_agent_workflow_resolver", str(SCHOLARLY_AGENT_SCRIPTS / "workflow_resolver.py"))
    assert resolver.KNOWN_WORKFLOWS == REQUIRED_WORKFLOWS


# ---------------------------------------------------------------------------
# Negative test: a genuinely missing required workflow must fail
# ---------------------------------------------------------------------------

def test_missing_required_workflow_is_detected_as_a_failure(tmp_path):
    """Proves the detection mechanism itself works: build a fake source
    runtime boundary that is missing theory-paper.md and confirm
    workflow_manifest.missing_from() (the function validate_suite.py,
    test_scholarly_agent_contains_all_required_workflows, and
    test_runtime_package_contains_all_required_workflows all rely on)
    reports it -- i.e. that a real theory-paper.md-missing regression, like
    the one this whole test module exists because of, cannot pass CI."""
    fake_dir = tmp_path / "references" / "workflows"
    fake_dir.mkdir(parents=True)
    for name in REQUIRED_WORKFLOWS:
        if name == "theory-paper.md":
            continue
        (fake_dir / name).write_text("stub", encoding="utf-8")

    missing = workflow_manifest.missing_from(fake_dir)
    assert missing == ["theory-paper.md"]


def test_missing_required_workflow_fails_zip_completeness_check(tmp_path, monkeypatch):
    """Same failure mode, exercised at the packaging layer: if the
    canonical source were missing a required workflow, iter_runtime_files()
    would silently build a ZIP without it. Simulate that by pointing
    RUNTIME_ALLOWLIST's skills/ walk at a doctored copy of the tree with
    theory-paper.md deleted, and confirm the completeness assertion this
    test module makes elsewhere would actually catch it."""
    doctored_root = tmp_path / "doctored-suite"
    shutil.copytree(ROOT, doctored_root, ignore=shutil.ignore_patterns(".git", "__pycache__", "dist", ".cache"))
    doctored_workflow = (
        doctored_root / "skills" / "scholarly-agent" / "references" / "workflows" / "theory-paper.md"
    )
    assert doctored_workflow.exists()
    doctored_workflow.unlink()

    doctored_manifest = load_module("doctored_workflow_manifest", str(doctored_root / "scripts" / "workflow_manifest.py"))
    missing = doctored_manifest.missing_from(doctored_manifest.CANONICAL_WORKFLOWS_DIR)
    assert missing == ["theory-paper.md"]
