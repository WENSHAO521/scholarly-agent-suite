"""Scholarly Text Normalizer and section classification (PART XV-XVI).

Splits already-extracted plain text into a Document(sections[...]) shape
and assigns a normalized semantic role to recognized headings — without
forcing every discipline into IMRaD. An unrecognized heading (common in
humanities, law, mathematics, philosophy) keeps its original text and
gets role="other"; nothing is renamed or discarded.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

# Maps a lowercased, recognized heading to a normalized semantic role.
# Deliberately not exhaustive and never mandatory — see module docstring.
HEADING_ROLE_MAP = {
    "abstract": "abstract",
    "introduction": "introduction",
    "background": "introduction",
    "literature review": "literature_review",
    "related work": "literature_review",
    "related literature": "literature_review",
    "theory": "theory",
    "theoretical framework": "theory",
    "conceptual framework": "theory",
    "methods": "methods",
    "methodology": "methods",
    "materials and methods": "methods",
    "data and methods": "methods",
    "results": "results",
    "findings": "results",
    "results and discussion": "results_and_discussion",
    "discussion": "discussion",
    "limitations": "limitations",
    "limitations and future research": "limitations",
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    "concluding remarks": "conclusion",
    "implications": "implications",
    "acknowledgments": "acknowledgments",
    "acknowledgements": "acknowledgments",
    "references": "references",
    "bibliography": "references",
    "works cited": "references",
    "appendix": "appendix",
    "supplementary material": "appendix",
}

_MAX_HEADING_WORDS = 12
_SENTENCE_ENDING = (".", "?", "!", ":", ";", ",")


def classify_heading(heading: str) -> str:
    key = re.sub(r"^[\divxlc]+[\.\)]\s*", "", heading.strip().lower())
    return HEADING_ROLE_MAP.get(key, "other")


def _looks_like_heading(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if len(stripped) > 90:
        return False
    if stripped[-1] in _SENTENCE_ENDING:
        return False
    word_count = len(stripped.split())
    if word_count > _MAX_HEADING_WORDS:
        return False
    is_markdown = stripped.startswith("#")
    is_allcaps = stripped.isupper() and word_count > 1
    is_titlecase = sum(1 for w in stripped.split() if w[:1].isupper()) >= max(1, word_count - 2)
    is_numbered = bool(re.match(r"^[\divxlc]+[\.\)]\s+\S", stripped, re.IGNORECASE))
    return is_markdown or is_allcaps or is_titlecase or is_numbered


@dataclass
class Section:
    heading: Optional[str]
    role: str
    paragraphs: List[str] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "\n\n".join(self.paragraphs)

    @property
    def word_count(self) -> int:
        return sum(len(p.split()) for p in self.paragraphs)


@dataclass
class Document:
    title: Optional[str]
    abstract: Optional[str]
    sections: List[Section] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    # PART XLV translation boundary — all optional/None by default so
    # existing single-language callers are unaffected. See scb/multilingual.py.
    language: Optional[str] = None
    original_language: Optional[str] = None
    translation_status: Optional[str] = None

    def all_paragraphs(self) -> List[str]:
        return [p for s in self.sections for p in s.paragraphs]

    def section_by_role(self, role: str) -> List[Section]:
        return [s for s in self.sections if s.role == role]


def normalize_text(
    raw_text: str,
    title: Optional[str] = None,
    abstract: Optional[str] = None,
    language: Optional[str] = None,
    original_language: Optional[str] = None,
    translation_status: Optional[str] = None,
) -> Document:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw_text or "") if p.strip()]

    sections: List[Section] = []
    current = Section(heading=None, role="front_matter")
    sections.append(current)

    for para in paragraphs:
        first_line = para.splitlines()[0] if "\n" in para else para
        if _looks_like_heading(first_line):
            heading_text = first_line.lstrip("#").strip()
            role = classify_heading(heading_text)
            current = Section(heading=heading_text, role=role)
            sections.append(current)
            remainder = "\n".join(para.splitlines()[1:]).strip()
            if remainder:
                current.paragraphs.append(remainder)
            continue
        current.paragraphs.append(para)

    references: List[str] = []
    for s in sections:
        if s.role == "references":
            for p in s.paragraphs:
                references.extend(line.strip() for line in p.splitlines() if line.strip())

    sections = [s for s in sections if not (s.heading is None and not s.paragraphs)]
    sections = [s for s in sections if s.role != "references"]

    return Document(
        title=title,
        abstract=abstract,
        sections=sections,
        references=references,
        language=language,
        original_language=original_language,
        translation_status=translation_status,
    )
