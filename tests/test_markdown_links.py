"""Every relative Markdown link in the repository resolves to a file.

v2.0.0 moved four Skills into modules/ and renamed each SKILL.md to
MODULE.md; links such as ``[kernel](../SKILL.md)`` kept pointing at files
that no longer existed. This check keeps moves like that from leaving dead
links behind."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r"\]\(([^)\s#]+)(?:#[^)]*)?\)")
SKIP_DIRS = {".git", "node_modules", "__pycache__", "dist", "build"}


def markdown_files():
    for path in ROOT.rglob("*.md"):
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


def test_relative_markdown_links_resolve():
    broken = []
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        for match in LINK_RE.finditer(text):
            target = match.group(1)
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
                continue  # http:, https:, mailto:, ...
            if not (path.parent / target).exists():
                line = text.count("\n", 0, match.start()) + 1
                broken.append(f"{path.relative_to(ROOT)}:{line}: {target}")
    assert not broken, "broken relative links:\n" + "\n".join(broken)


def test_modules_do_not_point_at_a_module_skill_md():
    """Inside a module, its own instructions live in MODULE.md. The only
    SKILL.md is the dispatcher, referenced in each MODULE.md header."""
    modules = ROOT / "skills" / "scholarly-agent" / "modules"
    offenders = []
    for path in modules.rglob("*"):
        if path.suffix not in {".md", ".py"} or "__pycache__" in path.parts:
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        start = 8 if path.name == "MODULE.md" else 0
        for i, line in enumerate(lines[start:], start + 1):
            if "SKILL.md" in line:
                offenders.append(f"{path.relative_to(ROOT)}:{i}")
    assert not offenders, "module files referring to SKILL.md:\n" + "\n".join(offenders)
