"""Both modules that keep per-discipline guidance use the one shared
discipline taxonomy (skills/scholarly-agent/shared/disciplines.md).

Before v2.1.0 the voice module had 11 discipline files and the journal-fit
module 10, with different names for the same family (business-management vs.
management, mathematics-formal vs. mathematics) and arts folded into
humanities on one side only.

Since v2.4.0 each module keeps its discipline guidance in one
`disciplines.md` file (one `<a id="<slug>">` section per family) instead of
one file per family, to keep the Skill package under the 200-file upload
limit."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "scholarly-agent"
TAXONOMY = SKILL_DIR / "shared" / "disciplines.md"
DISCIPLINE_FILES = [
    SKILL_DIR / "modules" / "scholarly-voice-engine" / "disciplines.md",
    SKILL_DIR / "modules" / "journal-fit-engine" / "disciplines.md",
]
ANCHOR_RE = re.compile(r'^<a id="([a-z-]+)"></a>$', re.M)


def sections(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    marks = list(ANCHOR_RE.finditer(text))
    out = {}
    for i, m in enumerate(marks):
        end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
        out[m.group(1)] = text[m.end():end]
    return out


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


def test_each_discipline_file_matches_the_taxonomy_exactly():
    slugs = [slug for slug, _ in taxonomy_rows()]
    for path in DISCIPLINE_FILES:
        found = list(sections(path))
        assert sorted(found) == sorted(slugs), (
            f"{path.relative_to(ROOT)}: missing {sorted(set(slugs) - set(found))}, "
            f"extra {sorted(set(found) - set(slugs))}"
        )
        assert len(found) == len(set(found)), f"{path.name}: duplicate section"


def test_no_per_family_discipline_directories_remain():
    for path in DISCIPLINE_FILES:
        assert not (path.parent / "disciplines").exists()


def test_voice_discipline_family_ids_match_section_anchors():
    for slug, body in sections(DISCIPLINE_FILES[0]).items():
        m = re.search(r"^discipline_family:\s*(\S+)", body, re.M)
        assert m, f"{slug} has no discipline_family"
        assert m.group(1) == slug.replace("-", "_"), slug
