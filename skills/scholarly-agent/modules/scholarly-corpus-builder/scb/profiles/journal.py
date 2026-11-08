"""Journal Profile builder — maps StyleProfile onto the schema in
references/journal-profile.md. Fields this module cannot honestly
derive yet (e.g. abstract-only architecture, precise contribution
*position*) are left as `null`/"not_computed" rather than guessed —
see references/journal-profile.md's explicit distinction between
OFFICIAL_REQUIREMENTS and OBSERVED_WRITING_PROFILE, which this profile
is entirely the latter half of.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from scb.profile_schema import build_style_profile, label_density, label_sentence_length
from scb.text_normalize import Document


def build_journal_profile(
    documents: List[Document],
    journal: str,
    issn: Optional[List[str]] = None,
    sample_window: str = "",
    article_types: Optional[List[str]] = None,
    source_provenance: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    style = build_style_profile("journal", journal, documents)

    common_patterns = sorted(style.sections.get("role_word_share", {}), key=style.sections.get("role_word_share", {}).get, reverse=True)
    contribution_share = style.rhetorical_moves.get("contribution", 0.0)
    literature_share = style.rhetorical_moves.get("literature_positioning", 0.0)

    return {
        "journal": journal,
        "issn": issn or [],
        "sample_window": sample_window,
        "sample_size": style.sample_size,
        "article_types": article_types or [],
        "profile_generated_at": style.generated_at,
        "source_provenance": source_provenance or [],
        "abstract": {
            "typical_structure": [],  # not computed: needs abstract-only sub-corpus analysis (future work)
            "contribution_position": "not_computed",
        },
        "introduction": {
            "dominant_architecture": style.argument_architecture[0] if style.argument_architecture else "unclear",
            "literature_density": "high" if literature_share > 0.3 else ("low" if literature_share < 0.1 else "moderate"),
            "contribution_position": (
                "commonly state the contribution explicitly" if contribution_share > 0.3 else "rarely state the contribution explicitly"
            ),
        },
        "prose": {
            "sentence_length": label_sentence_length(style.sentence.get("median_length", 0)),
            "sentence_variation": style.sentence.get("variation", "unknown"),
            "first_person": style.first_person,
            "rhetorical_intensity": "assertive" if style.lexical.get("certainty_rate_per_1000", 0) > style.lexical.get("hedge_rate_per_1000", 0) else "qualified",
            "qualification_density": style.qualification,
        },
        "citations": {
            "density": label_density(style.citations.get("citations_per_1000_words", 0)),
            "dominant_placement": "sentence_final" if style.citations.get("sentence_final_citation_share", 0) > 0.5 else "distributed",
        },
        "sections": {"common_patterns": common_patterns},
        "limitations": (
            [] if style.sections.get("limitations_section_share", 0) > 0
            else ["no dedicated Limitations section observed in the sampled corpus"]
        ),
        "confidence": style.confidence.get("sentence", "low"),
        "known_biases": style.known_biases,
        "sample_size_label": style.sample_size_label,
    }
