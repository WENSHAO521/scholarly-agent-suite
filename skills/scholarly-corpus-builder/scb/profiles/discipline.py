"""Discipline Profile builder — maps StyleProfile onto the schema in
references/discipline-profile.md.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from scb.profile_schema import build_style_profile
from scb.text_normalize import Document


def build_discipline_profile(
    documents: List[Document],
    discipline: str,
    subdiscipline: str = "",
    sample_window: str = "",
) -> Dict[str, Any]:
    style = build_style_profile("discipline", discipline, documents)

    methods_share = style.sections.get("role_word_share", {}).get("methods", 0.0)

    return {
        "discipline": discipline,
        "subdiscipline": subdiscipline,
        "sample_window": sample_window,
        "sample_size": style.sample_size,
        "dominant_genres": [],  # not computed: requires article-type metadata from the acquisition manifest
        "claim_conventions": style.claims.get("category_shares", {}),
        "argument_architectures": style.argument_architecture,
        "methods_visibility": "high" if methods_share > 0.2 else ("low" if methods_share == 0 else "moderate"),
        "citation_behavior": style.citations,
        "uncertainty_conventions": style.qualification,
        "first_person_norms": style.first_person,
        "section_conventions": sorted(
            style.sections.get("role_word_share", {}),
            key=style.sections.get("role_word_share", {}).get,
            reverse=True,
        ),
        "recommended_scholarly_voice_profiles": [],  # downstream Voice Engine concern, not derived here
        "confidence": style.confidence,
        "known_biases": style.known_biases,
        "sample_size_label": style.sample_size_label,
        "generated_at": style.generated_at,
    }
