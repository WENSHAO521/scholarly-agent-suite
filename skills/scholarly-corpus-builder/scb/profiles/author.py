"""Personal Author Profile builder — maps StyleProfile onto the schema
in references/author-profile.md. Callers are responsible for the
authorization boundary (Tier 1 user-supplied works only — see
references/author-profile.md "Authorization boundary"); this module
only aggregates whatever Documents it is given.
"""

from __future__ import annotations

from typing import Any, Dict, List

from scb.profile_schema import build_style_profile
from scb.text_normalize import Document

DEFAULT_DO_NOT_PRESERVE = ["citation errors", "grammar mistakes", "unsupported claims"]


def build_author_profile(
    documents: List[Document],
    source_scope: str = "",
    do_not_preserve: List[str] = None,
) -> Dict[str, Any]:
    style = build_style_profile("author", source_scope, documents)

    return {
        "profile_type": "author",
        "source_count": style.sample_size,
        "source_scope": source_scope,
        "sentence_style": style.sentence,
        "paragraph_style": style.paragraph,
        "argument_moves": sorted(style.rhetorical_moves, key=style.rhetorical_moves.get, reverse=True),
        "citation_behavior": style.citations,
        "first_person": style.first_person,
        "claim_strength": style.claims.get("dominant_category") or "unclassified",
        "definition_style": style.definition_style,
        "preferred_transitions": [],  # not computed: needs a transition-phrase-specific extractor (future work)
        "section_patterns": style.sections,
        "do_not_preserve": do_not_preserve if do_not_preserve is not None else list(DEFAULT_DO_NOT_PRESERVE),
        "confidence": style.confidence,
        "sample_size_label": style.sample_size_label,
        "generated_at": style.generated_at,
    }
