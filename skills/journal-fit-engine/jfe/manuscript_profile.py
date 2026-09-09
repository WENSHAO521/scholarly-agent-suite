"""MANUSCRIPT_PROFILE_V1 (see references/manuscript-profile.md and
scholarly-agent-suite/protocols/manuscript-profile.schema.json). Unknown
fields stay None -- never invented. This is a plain data shape plus shape
validation, not an NLP extractor: a host/LLM populates it from the actual
manuscript.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# Common short connector words that would otherwise pass the length>2
# filter and show up as fake "topic overlap" evidence (e.g. "and" matching
# because both the manuscript text and a journal topic name contain it).
STOPWORDS = frozenset({
    "the", "and", "for", "with", "from", "into", "onto", "this", "that",
    "these", "those", "are", "was", "were", "been", "being", "have", "has",
    "had", "not", "but", "its", "their", "our", "your", "his", "her",
    "who", "whom", "which", "what", "how", "why", "when", "where",
})

ARTICLE_TYPES = (
    "original-research", "review", "systematic-review", "meta-analysis",
    "case-study", "commentary", "perspective", "letter", "book-chapter",
    "conference-paper", "short-communication", "other",
)


class ProfileError(ValueError):
    """Raised when a profile field has an invalid shape/value."""


@dataclass
class ManuscriptProfile:
    discipline: Optional[str] = None
    subdiscipline: Optional[str] = None
    topic: Optional[str] = None
    research_question: Optional[str] = None
    central_contribution: Optional[str] = None
    contribution_type: Optional[str] = None
    theory: Optional[str] = None
    research_design: Optional[str] = None
    methods: list = field(default_factory=list)
    data: Optional[str] = None
    article_type: Optional[str] = None
    audience: Optional[str] = None
    geography: Optional[str] = None
    language: str = "en"
    word_count: Optional[int] = None
    constraints: dict = field(default_factory=dict)

    def keywords(self) -> list[str]:
        """Free-text fields flattened into a lowercase keyword bag, used by
        the topic-overlap fit dimension. Not a semantic embedding -- an
        honest, transparent bag-of-words signal only."""
        text_fields = (self.discipline, self.subdiscipline, self.topic,
                       self.research_question, self.central_contribution,
                       self.theory)
        words: set[str] = set()
        for text in text_fields:
            if not text:
                continue
            for token in text.lower().replace("-", " ").split():
                cleaned = "".join(ch for ch in token if ch.isalnum())
                if len(cleaned) > 2 and cleaned not in STOPWORDS:
                    words.add(cleaned)
        return sorted(words)

    def validate(self) -> list[str]:
        errors: list[str] = []
        if self.article_type is not None and self.article_type not in ARTICLE_TYPES:
            errors.append(f"article_type: {self.article_type!r} not in {ARTICLE_TYPES}")
        if self.word_count is not None and (not isinstance(self.word_count, int) or self.word_count < 0):
            errors.append("word_count: must be a non-negative integer")
        if not isinstance(self.methods, list):
            errors.append("methods: must be a list")
        if not isinstance(self.constraints, dict):
            errors.append("constraints: must be a dict")
        return errors

    @classmethod
    def from_dict(cls, data: dict) -> "ManuscriptProfile":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        unknown = set(data) - known
        if unknown:
            raise ProfileError(f"unknown manuscript profile fields: {sorted(unknown)}")
        profile = cls(**{k: v for k, v in data.items() if k in known})
        errors = profile.validate()
        if errors:
            raise ProfileError("; ".join(errors))
        return profile
