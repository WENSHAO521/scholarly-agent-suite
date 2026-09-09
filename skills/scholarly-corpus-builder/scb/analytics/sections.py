"""Section architecture analytics (PART XXI). Word-share and placement
metrics per normalized section role — applies only where a document
actually has recognizable sections (see text_normalize.py's "never force
IMRaD" rule; a humanities/law/mathematics document with no recognized
IMRaD roles simply reports an empty `role_word_share`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from scb.text_normalize import Document


@dataclass
class SectionArchitectureMetrics:
    section_count: int
    heading_pattern: List[str] = field(default_factory=list)
    role_word_share: Dict[str, float] = field(default_factory=dict)
    has_dedicated_limitations_section: bool = False
    contribution_first_appears_in_section_index: Optional[int] = None


_CONTRIBUTION_CUES = ["this paper", "this study", "we contribute", "our contribution", "we argue that", "we show that"]


def compute_section_metrics(document: Document) -> SectionArchitectureMetrics:
    sections = document.sections
    if not sections:
        return SectionArchitectureMetrics(section_count=0)

    total_words = sum(s.word_count for s in sections) or 1
    role_words: Dict[str, int] = {}
    for s in sections:
        role_words[s.role] = role_words.get(s.role, 0) + s.word_count
    role_share = {role: round(words / total_words, 3) for role, words in role_words.items()}

    has_limitations = any(s.role == "limitations" for s in sections)

    contribution_index = None
    for i, s in enumerate(sections):
        text_lower = s.text.lower()
        if any(cue in text_lower for cue in _CONTRIBUTION_CUES):
            contribution_index = i
            break

    return SectionArchitectureMetrics(
        section_count=len(sections),
        heading_pattern=[s.heading or "(untitled)" for s in sections],
        role_word_share=role_share,
        has_dedicated_limitations_section=has_limitations,
        contribution_first_appears_in_section_index=contribution_index,
    )
