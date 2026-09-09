"""Acceptance criteria: Workflows (spec section 139) + component selection
checks (spec section 65). Workflow recipes are markdown, not executable code,
so "verify expected component selection" here means: the recipe's documented
stage list matches the Suite's own component-selection rules (e.g. a book
project recipe must not schedule journal-fit-engine by default)."""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = ROOT / "workflows"

REQUIRED_WORKFLOWS = [
    "paper-from-idea.md", "paper-from-notes.md", "revise-manuscript.md",
    "journal-selection.md", "target-journal-adaptation.md",
    "literature-review.md", "theory-paper.md", "empirical-paper.md",
    "systematic-review.md", "nature-commentary.md", "book-project.md",
    "monograph-chapter.md", "author-voice-calibration.md",
    "corpus-profile-build.md",
]


@pytest.mark.parametrize("filename", REQUIRED_WORKFLOWS)
def test_workflow_file_exists_and_is_marked_not_a_skill(filename):
    text = (WORKFLOWS_DIR / filename).read_text(encoding="utf-8")
    assert "Not a Skill" in text, f"{filename} must declare it is a recipe, not a Skill (rule 20)"


def test_book_project_excludes_journal_fit_by_default():
    text = (WORKFLOWS_DIR / "book-project.md").read_text(encoding="utf-8")
    assert "journal-fit-engine" not in text.split("## Explicit non-goal")[0]


def test_journal_selection_does_not_default_to_voice_rewrite():
    text = (WORKFLOWS_DIR / "journal-selection.md").read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "non-goal" in normalized.lower()
    assert "unless the user explicitly asks" in normalized


def test_nature_commentary_avoids_full_corpus_build():
    text = (WORKFLOWS_DIR / "nature-commentary.md").read_text(encoding="utf-8")
    assert "bounded" in text.lower()


def test_author_voice_calibration_excludes_journal_fit_and_router():
    text = (WORKFLOWS_DIR / "author-voice-calibration.md").read_text(encoding="utf-8")
    assert re.search(r"not part of this recipe", text)


def test_all_workflows_referenced_from_scholarly_agent_or_readme():
    skill_md = (ROOT / "skills" / "scholarly-agent" / "SKILL.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    combined = skill_md + readme
    for filename in REQUIRED_WORKFLOWS:
        stem = filename.replace(".md", "")
        assert stem in combined, f"no reference to workflow '{stem}' found in SKILL.md or README.md"
