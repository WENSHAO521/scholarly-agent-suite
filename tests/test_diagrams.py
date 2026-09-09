"""README diagrams: valid SVG, referenced from README, and excluded from the
runtime package (they are documentation assets, not part of the rule-81
runtime allowlist)."""
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from conftest import load_module

ROOT = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT / "assets"
package_suite = load_module("package_suite", "package_suite.py")

DIAGRAMS = ["suite-architecture-diagram.svg", "orchestration-flowchart.svg"]


@pytest.mark.parametrize("filename", DIAGRAMS)
def test_diagram_is_well_formed_svg(filename):
    path = ASSETS_DIR / filename
    assert path.exists()
    root = ET.parse(path).getroot()
    assert root.tag.endswith("svg")
    assert root.get("viewBox")


@pytest.mark.parametrize("filename", DIAGRAMS)
def test_diagram_referenced_from_readme(filename):
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert f"assets/{filename}" in readme


def test_assets_dir_not_in_runtime_package():
    files = package_suite.iter_runtime_files()
    assert not any(f.relative_to(ROOT).parts[0] == "assets" for f in files)
