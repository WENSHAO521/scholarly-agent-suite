"""Both modules that keep per-discipline guidance use the one shared
discipline taxonomy (skills/scholarly-agent/shared/disciplines.md).

Before v2.1.0 the voice module had 11 discipline files and the journal-fit
module 10, with different names for the same family (business-management vs.
management, mathematics-formal vs. mathematics) and arts folded into
humanities on one side only."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "scholarly-agent"
TAXONOMY = SKILL_DIR / "shared" / "disciplines.md"
DISCIPLINE_DIRS = [
    SKILL_DIR / "modules" / "scholarly-voice-engine" / "disciplines",
    SKILL_DIR / "modules" / "journal-fit-engine" / "disciplines",
]


def taxonomy_rows() -> list[tuple[str, str]]:
    rows = []
    for line in TAXONOMY.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| `([a-z-]+)` \| `([a-z_]+)` \|", line)
        if m:
            rows.append((m.group(1), m.group(2)))
    return rows


def test_taxonomy_has_eleven_families_with_matching_ids():
    rows = taxonomy_rows()
    assert len(rows) == 11
    for slug, ident in rows:
        assert ident == slug.replace("-", "_")


def test_each_discipline_dir_matches_the_taxonomy_exactly():
    slugs = {slug for slug, _ in taxonomy_rows()}
    for directory in DISCIPLINE_DIRS:
        files = {p.stem for p in directory.glob("*.md")}
        assert files == slugs, (
            f"{directory.relative_to(ROOT)}: missing {sorted(slugs - files)}, "
            f"extra {sorted(files - slugs)}"
        )


def test_voice_discipline_family_ids_match_file_names():
    voice_dir = DISCIPLINE_DIRS[0]
    for path in voice_dir.glob("*.md"):
        m = re.search(r"^discipline_family:\s*(\S+)", path.read_text(encoding="utf-8"), re.M)
        assert m, f"{path.name} has no discipline_family"
        assert m.group(1) == path.stem.replace("-", "_"), path.name
