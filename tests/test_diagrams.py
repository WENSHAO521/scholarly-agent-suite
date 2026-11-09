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

DIAGRAMS = ["scholarly-agent-architecture.svg", "orchestration-flowchart.svg"]
ZH_DIAGRAMS = ["scholarly-agent-architecture.zh-TW.svg", "orchestration-flowchart.zh-TW.svg"]


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


@pytest.mark.parametrize("filename", ZH_DIAGRAMS)
def test_zh_tw_diagram_is_valid_and_used_by_zh_readme(filename):
    root = ET.parse(ASSETS_DIR / filename).getroot()
    assert root.tag.endswith("svg") and root.get("viewBox")
    readme = (ROOT / "README.zh-TW.md").read_text(encoding="utf-8")
    assert f"assets/{filename}" in readme


@pytest.mark.parametrize("en,zh", list(zip(DIAGRAMS, ZH_DIAGRAMS)))
def test_zh_tw_diagram_keeps_the_english_layout(en, zh):
    """The zh-TW diagrams are translations: same canvas and same number of
    shapes, so a layout change to one must be made to both."""
    a = ET.parse(ASSETS_DIR / en).getroot()
    b = ET.parse(ASSETS_DIR / zh).getroot()
    assert a.get("viewBox") == b.get("viewBox")
    count = lambda r, tag: sum(1 for e in r.iter() if e.tag.endswith(tag))  # noqa: E731
    for tag in ("rect", "line", "path", "text"):
        assert count(a, tag) == count(b, tag), tag
