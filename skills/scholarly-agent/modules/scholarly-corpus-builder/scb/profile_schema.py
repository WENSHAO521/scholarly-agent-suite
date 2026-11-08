"""Style Profile Schema (PART XXIII). Aggregates the analytics engine's
per-document outputs into one corpus-level profile matching the schema
in references/style-feature-schema.md.

Simplification documented honestly: feature confidence here is derived
from sample size alone (n<5 illustrative/low, 5-19 limited/medium, 20+
higher), per PART XXI/LXI's suggested labels — not from the fuller
"consistency + completeness + diversity" formula PART XXVII describes,
which would need cross-document variance analysis (see stability.py for
the piece of that this milestone does implement: split-corpus
consistency testing).
"""

from __future__ import annotations

import datetime
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from scb.analytics.citations import compute_citation_metrics
from scb.analytics.claims import analyze_claims
from scb.analytics.lexical import compute_lexical_metrics
from scb.analytics.paragraph import compute_paragraph_metrics
from scb.analytics.rhetorical import analyze_rhetorical_moves
from scb.analytics.rhythm import analyze_rhythm
from scb.analytics.sections import compute_section_metrics
from scb.analytics.sentence import compute_sentence_metrics
from scb.text_normalize import Document

ILLUSTRATIVE = "illustrative"
LIMITED = "limited"
MODERATE = "moderate"
ROBUST_CANDIDATE = "potentially_robust"


def sample_size_label(n: int) -> str:
    if n < 5:
        return ILLUSTRATIVE
    if n < 20:
        return LIMITED
    if n < 50:
        return MODERATE
    return ROBUST_CANDIDATE


def _confidence_for_sample_size(n: int) -> str:
    if n < 5:
        return "low"
    if n < 20:
        return "medium"
    return "high"


def _label_rate(rate: float, low_cut: float, high_cut: float) -> str:
    if rate <= low_cut:
        return "low"
    if rate >= high_cut:
        return "high"
    return "moderate"


def label_sentence_length(median: float) -> str:
    """Shared bucketing rule so a raw numeric sentence length (e.g. from
    an author profile) and a label-only profile (e.g. a journal
    profile, which deliberately does not expose raw numbers — see
    references/journal-profile.md) can still be compared honestly by
    label rather than by fabricated precision (used by
    scb/profiles/journal.py and scb/comparison.py)."""
    if median <= 15:
        return "short"
    if median >= 25:
        return "long"
    return "moderate"


def label_density(rate: float) -> str:
    """Shared bucketing rule for a per-1000-word rate (e.g. citation
    density) — see label_sentence_length()."""
    if rate <= 5:
        return "low"
    if rate >= 20:
        return "high"
    return "moderate"


@dataclass
class StyleProfile:
    profile_type: str
    target: str
    sample_size: int
    sample_size_label: str
    sentence: Dict[str, Any] = field(default_factory=dict)
    paragraph: Dict[str, Any] = field(default_factory=dict)
    lexical: Dict[str, Any] = field(default_factory=dict)
    citations: Dict[str, Any] = field(default_factory=dict)
    sections: Dict[str, Any] = field(default_factory=dict)
    claims: Dict[str, Any] = field(default_factory=dict)
    rhetorical_moves: Dict[str, Any] = field(default_factory=dict)
    intellectual_rhythm: List[str] = field(default_factory=list)
    first_person: str = "unknown"
    qualification: str = "unknown"
    definition_style: str = "unknown"
    evidence_style: str = "unknown"
    argument_architecture: List[str] = field(default_factory=list)
    confidence: Dict[str, str] = field(default_factory=dict)
    known_biases: List[str] = field(default_factory=list)
    generated_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def build_style_profile(
    profile_type: str,
    target: str,
    documents: List[Document],
    known_biases: Optional[List[str]] = None,
) -> StyleProfile:
    n = len(documents)
    if n == 0:
        return StyleProfile(
            profile_type=profile_type,
            target=target,
            sample_size=0,
            sample_size_label=ILLUSTRATIVE,
            confidence={"overall": "low"},
            known_biases=known_biases or [],
            generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        )

    all_text_parts = []
    all_paragraphs: List[str] = []
    for doc in documents:
        paras = doc.all_paragraphs()
        all_paragraphs.extend(paras)
        all_text_parts.append("\n\n".join(paras))
    full_text = "\n\n".join(all_text_parts)

    sentence_metrics = compute_sentence_metrics(full_text)
    paragraph_metrics = compute_paragraph_metrics(all_paragraphs)
    lexical_metrics = compute_lexical_metrics(full_text)
    citation_metrics = compute_citation_metrics(all_paragraphs)
    claim_analysis = analyze_claims(full_text)
    rhetorical_analysis = analyze_rhetorical_moves(all_paragraphs)
    rhythm_analysis = analyze_rhythm(all_paragraphs)

    section_role_shares: Dict[str, List[float]] = {}
    limitations_docs = 0
    for doc in documents:
        sm = compute_section_metrics(doc)
        if sm.has_dedicated_limitations_section:
            limitations_docs += 1
        for role, share in sm.role_word_share.items():
            section_role_shares.setdefault(role, []).append(share)
    avg_role_share = {role: round(sum(shares) / len(shares), 3) for role, shares in section_role_shares.items()}

    confidence_level = _confidence_for_sample_size(n)

    argument_architecture = sorted(rhythm_analysis.pattern_counts, key=rhythm_analysis.pattern_counts.get, reverse=True)

    return StyleProfile(
        profile_type=profile_type,
        target=target,
        sample_size=n,
        sample_size_label=sample_size_label(n),
        sentence={
            "median_length": sentence_metrics.median_length,
            "mean_length": sentence_metrics.mean_length,
            "length_iqr": sentence_metrics.length_iqr,
            "short_sentence_share": sentence_metrics.short_sentence_share,
            "long_sentence_share": sentence_metrics.long_sentence_share,
            "variation": _label_rate(sentence_metrics.length_iqr, 4, 10),
        },
        paragraph={
            "median_length_words": paragraph_metrics.median_length_words,
            "mean_sentences_per_paragraph": paragraph_metrics.mean_sentences_per_paragraph,
        },
        lexical={
            "unique_word_ratio": lexical_metrics.unique_word_ratio,
            "first_person_rate_per_1000": lexical_metrics.first_person_rate_per_1000,
            "passive_voice_rate_per_1000": lexical_metrics.passive_voice_rate_per_1000,
            "hedge_rate_per_1000": lexical_metrics.hedge_rate_per_1000,
            "certainty_rate_per_1000": lexical_metrics.certainty_rate_per_1000,
            "transition_rate_per_1000": lexical_metrics.transition_rate_per_1000,
        },
        citations={
            "citations_per_1000_words": citation_metrics.citations_per_1000_words,
            "sentence_final_citation_share": citation_metrics.sentence_final_citation_share,
            "citation_free_paragraph_share": citation_metrics.citation_free_paragraph_share,
        },
        sections={
            "role_word_share": avg_role_share,
            "limitations_section_share": round(limitations_docs / n, 3),
        },
        claims={
            "category_shares": claim_analysis.category_shares,
            "dominant_category": claim_analysis.dominant_category,
            "hedge_cooccurrence_rate": claim_analysis.hedge_cooccurrence_rate,
        },
        rhetorical_moves=rhetorical_analysis.move_shares,
        intellectual_rhythm=argument_architecture,
        first_person=_label_rate(lexical_metrics.first_person_rate_per_1000, 2, 10),
        qualification=_label_rate(lexical_metrics.hedge_rate_per_1000, 2, 8),
        definition_style="explicit" if rhetorical_analysis.move_shares.get("definition", 0) > 0.1 else "implicit_or_rare",
        evidence_style="citation_dense" if citation_metrics.citations_per_1000_words > 15 else "citation_sparse",
        argument_architecture=argument_architecture,
        confidence={
            "sentence": confidence_level,
            "paragraph": confidence_level,
            "lexical": confidence_level,
            "citations": confidence_level,
            "claims": confidence_level if n >= 5 else "low",
            "rhetorical_moves": confidence_level if n >= 5 else "low",
            "intellectual_rhythm": "low",  # PART XXII pattern matching is always low-confidence
        },
        known_biases=known_biases or [],
        generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    )
