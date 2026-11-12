"""Structural validation of evals/*.jsonl (spec sections 67, 122, 135
'workflow tests'). These fixtures describe expected orchestration behavior
for a natural-language-triggered Skill -- they are not executed against a
live model here (that requires an eval harness / live host), but this suite
guarantees the fixture set itself is well-formed, IDs are unique, every
referenced workflow_recipe exists, and the minimum category coverage from
the spec (cross-disciplinary + multilingual) is present."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
EVALS_DIR = ROOT / "evals"
WORKFLOWS_DIR = ROOT / "workflows"

REQUIRED_FIELDS = {"id", "category", "task", "workflow_recipe", "expected_components", "expected_orchestrator_invoked", "notes"}

REQUIRED_CROSS_DISCIPLINARY_CATEGORIES = {
    "public_administration", "biomedical", "ai_computer_science", "law",
    "history", "philosophy", "book_project",
}


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def all_fixtures() -> list[dict]:
    rows = []
    for filename in ["orchestration-cases.jsonl", "negative-trigger-cases.jsonl"]:
        rows.extend(load_jsonl(EVALS_DIR / filename))
    return rows


def test_eval_files_exist():
    assert (EVALS_DIR / "orchestration-cases.jsonl").exists()
    assert (EVALS_DIR / "negative-trigger-cases.jsonl").exists()


def test_fixture_count_within_spec_target_range():
    """Spec rule 67/122: ~40-80 suite-level integration fixtures, not 500."""
    fixtures = all_fixtures()
    assert 40 <= len(fixtures) <= 80, f"got {len(fixtures)} fixtures"


def test_every_fixture_has_required_fields_and_unique_id():
    fixtures = all_fixtures()
    seen_ids = set()
    for row in fixtures:
        missing = REQUIRED_FIELDS - row.keys()
        assert not missing, f"{row.get('id')} missing fields: {missing}"
        assert row["id"] not in seen_ids, f"duplicate fixture id: {row['id']}"
        seen_ids.add(row["id"])


def test_every_referenced_workflow_recipe_exists():
    for row in all_fixtures():
        recipe = row["workflow_recipe"]
        if recipe is None:
            continue
        assert (WORKFLOWS_DIR / f"{recipe}.md").exists(), f"{row['id']}: unknown workflow_recipe '{recipe}'"


def test_expected_components_use_known_vocabulary():
    known = {"router", "corpus", "voice", "journal_fit", "peer_review", "polish", "translation"}
    for row in all_fixtures():
        unknown = set(row["expected_components"]) - known
        assert not unknown, f"{row['id']}: unknown component labels {unknown}"


def test_negative_cases_mostly_do_not_invoke_orchestrator():
    negatives = load_jsonl(EVALS_DIR / "negative-trigger-cases.jsonl")
    assert all(not row["expected_orchestrator_invoked"] for row in negatives)


def test_required_cross_disciplinary_categories_covered():
    categories = {row["category"] for row in all_fixtures()}
    missing = REQUIRED_CROSS_DISCIPLINARY_CATEGORIES - categories
    assert not missing, f"missing required cross-disciplinary eval categories: {missing}"


def test_multilingual_coverage_present():
    multilingual = [row for row in all_fixtures() if row["category"] == "multilingual"]
    assert len(multilingual) >= 3, "spec section 148 wants English, Chinese, and cross-language cases"


def test_end_to_end_case_uses_all_four_components():
    endtoend = [row for row in all_fixtures() if row["category"] == "end_to_end"]
    assert endtoend, "no end_to_end fixture found"
    assert set(endtoend[0]["expected_components"]) == {"router", "corpus", "voice", "journal_fit"}


def test_theory_paper_target_journal_fixture_has_expected_specialist_set():
    """Theory-paper routing regression: 'develop a theoretical paper for an
    already-selected target journal' must select scholarly-corpus-builder,
    scholarly-voice-engine, and journal-fit-engine (adaptive-model-router
    remains an optional execution layer, never a required fourth stage --
    see references/routing-matrix.md's 'Why Router is always optional')."""
    matches = [
        row for row in load_jsonl(EVALS_DIR / "orchestration-cases.jsonl")
        if row["category"] == "theory_paper_target_journal"
    ]
    assert matches, "no theory_paper_target_journal fixture found"
    row = matches[0]
    assert row["workflow_recipe"] == "theory-paper"
    assert set(row["expected_components"]) == {"corpus", "voice", "journal_fit"}
    assert "router" not in row["expected_components"]
    assert row["expected_orchestrator_invoked"] is True
    assert "target-journal-adaptation" in row["notes"]


# --- Module evals merged from the former component repositories (v2.0.0) ---

MODULE_EVALS_DIR = ROOT / "evals" / "modules"
MODULE_NAMES = [
    "adaptive-model-router", "scholarly-corpus-builder",
    "scholarly-voice-engine", "journal-fit-engine", "peer-review-engine", "prose-polish-engine", "translation-engine",
]


def test_every_module_has_merged_evals():
    for name in MODULE_NAMES:
        files = sorted((MODULE_EVALS_DIR / name).glob("*.jsonl"))
        assert files, f"evals/modules/{name}/ has no .jsonl eval files"


def test_module_eval_files_are_valid_jsonl():
    for path in sorted(MODULE_EVALS_DIR.rglob("*.jsonl")):
        rows = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert rows, f"{path.relative_to(ROOT)} is empty"
        for i, line in enumerate(rows, 1):
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AssertionError(f"{path.relative_to(ROOT)} line {i}: {exc}") from exc
            assert isinstance(row, dict), f"{path.relative_to(ROOT)} line {i} is not an object"
