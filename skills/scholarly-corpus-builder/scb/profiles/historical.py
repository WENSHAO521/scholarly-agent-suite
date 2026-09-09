"""Historical Scholar Profile builder — maps StyleProfile onto the
schema in references/historical-profile.md. Deliberately excludes any
excerpt/quotation storage — see references/copyright-boundary.md and
references/historical-profile.md's "do not build phrase-copying
libraries" rule; only aggregate, non-attributable statistics and named
abstract patterns are retained.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from scb.profile_schema import build_style_profile
from scb.text_normalize import Document


def build_historical_profile(
    documents: List[Document],
    scholar: str,
    discipline: str = "",
    period: str = "",
    source_status: str = "unknown",  # "verified" | "likely" | "unknown" public-domain status
) -> Dict[str, Any]:
    style = build_style_profile("historical_scholar", scholar, documents)

    counterargument_share = style.rhetorical_moves.get("counterargument", 0.0)
    qualification_share = style.rhetorical_moves.get("qualification", 0.0)

    return {
        "scholar": scholar,
        "discipline": discipline,
        "period": period,
        "works_sampled": style.sample_size,
        "source_status": source_status,
        "argument_architecture": style.argument_architecture,
        "definition_style": style.definition_style,
        "evidence_style": style.evidence_style,
        "sentence_architecture": {
            "median_length": style.sentence.get("median_length"),
            "variation": style.sentence.get("variation"),
        },
        "intellectual_rhythm": style.intellectual_rhythm,
        "abstraction_level": "high" if style.lexical.get("nominalization_rate_per_1000", 0) > 30 else "moderate",
        "counterargument_strategy": "frequent" if counterargument_share > 0.15 else "infrequent",
        "qualification_style": "frequent" if qualification_share > 0.15 else style.qualification,
        "transferable_strengths": [
            move for move, share in style.rhetorical_moves.items() if share > 0.2
        ],
        "modern_use_cautions": [
            caution for caution in [
                "derived from a small/illustrative sample" if style.sample_size < 5 else None,
                "source_status is unverified — treat public-domain status conservatively" if source_status != "verified" else None,
            ]
            if caution is not None
        ],
        "confidence": style.confidence,
        "sample_size_label": style.sample_size_label,
        "generated_at": style.generated_at,
    }
