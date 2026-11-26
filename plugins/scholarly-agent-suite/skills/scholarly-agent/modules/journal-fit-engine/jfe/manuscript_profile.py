"""MANUSCRIPT_PROFILE_V1 (see references/manuscript-profile.md and
scholarly-agent-suite/protocols/manuscript-profile.schema.json). Unknown
fields stay None -- never invented. This is a plain data shape plus shape
validation, not an NLP extractor: a host/LLM populates it from the actual
manuscript.
"""
from __future__ import annotations

import re
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


def tokenize(text: Optional[str]) -> set[str]:
    """Lowercase, alnum-only, stopword-filtered, length>2 tokens. Shared by
    ManuscriptProfile.keywords() and jfe.fit_model's/jfe.fit_dimensions's
    topic-overlap matchers so the same honest bag-of-words rule (no fake
    NLP/embedding) is applied on both the manuscript and journal-topic side.
    """
    if not text:
        return set()
    words: set[str] = set()
    for token in text.lower().replace("-", " ").split():
        cleaned = "".join(ch for ch in token if ch.isalnum())
        if len(cleaned) > 2 and cleaned not in STOPWORDS:
            words.add(cleaned)
    return words


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
            words |= tokenize(text)
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


# --- Shared-protocol interoperability ---------------------------------------
#
# protocols/manuscript-profile.schema.json (MANUSCRIPT_PROFILE_V1) is the
# envelope the voice module or the user hands to this module. Its field
# names and article_type vocabulary differ from ManuscriptProfile's own
# richer shape, so ManuscriptProfile.from_dict() rejects it outright
# ("unknown field: protocol"). from_manuscript_profile_v1() is the explicit
# translation; it never guesses a value the envelope does not carry.

# Envelope article_type -> (this module's article_type, contribution_type).
_V1_ARTICLE_TYPE_MAP = {
    "empirical": ("original-research", None),
    "theory": ("other", "theoretical"),
    "review": ("review", None),
    "commentary": ("commentary", None),
    "case-study": ("case-study", None),
    "book-chapter": ("book-chapter", None),
    "other": ("other", None),
}


def _split_methods(methods) -> list:
    if methods is None:
        return []
    if isinstance(methods, list):
        return [str(m).strip() for m in methods if str(m).strip()]
    parts = re.split(r"[;,]", str(methods))
    return [p.strip() for p in parts if p.strip()]


def from_manuscript_profile_v1(data: dict) -> "ManuscriptProfile":
    """Translate a MANUSCRIPT_PROFILE_V1 envelope into a ManuscriptProfile.

    Raises ProfileError on a wrong protocol, a missing required field
    (discipline, article_type), or an article_type outside the envelope's
    enum. `contribution` maps to central_contribution; a "theory" envelope
    becomes article_type "other" with contribution_type "theoretical", since
    this module has no separate theory article type.
    """
    if not isinstance(data, dict) or data.get("protocol") != "MANUSCRIPT_PROFILE_V1":
        raise ProfileError(f"not a MANUSCRIPT_PROFILE_V1 envelope: protocol={data.get('protocol') if isinstance(data, dict) else None!r}")
    for required in ("discipline", "article_type"):
        if not data.get(required):
            raise ProfileError(f"MANUSCRIPT_PROFILE_V1 missing required field '{required}'")
    mapped = _V1_ARTICLE_TYPE_MAP.get(data["article_type"])
    if mapped is None:
        raise ProfileError(f"unrecognized MANUSCRIPT_PROFILE_V1 article_type: {data['article_type']!r}")
    article_type, contribution_type = mapped
    profile = ManuscriptProfile(
        discipline=data.get("discipline"),
        topic=data.get("topic"),
        research_question=data.get("research_question"),
        central_contribution=data.get("contribution"),
        contribution_type=contribution_type,
        methods=_split_methods(data.get("methods")),
        data=data.get("data"),
        article_type=article_type,
        audience=data.get("audience"),
        geography=data.get("geography"),
        constraints=dict(data.get("constraints") or {}),
    )
    errors = profile.validate()
    if errors:
        raise ProfileError("; ".join(errors))
    return profile
