"""Reviewer panel selection and isolated subagent briefings.
See references/reviewer-lenses.md and references/subagent-review.md."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional

from prv import LENSES

LENS_FOCUS: Dict[str, List[str]] = {
    "methods": [
        "Does the design fit the research question?",
        "Is the identification or inference valid? Sampling, measures, analysis, robustness.",
        "Do the results support the claims as stated?",
        "Could someone reproduce this (data, code, materials)?",
    ],
    "statistics": [
        "Model specification and assumptions; are they checked?",
        "Multiple comparisons, effect sizes, uncertainty, power, missing data.",
    ],
    "theory": [
        "Does the question matter, and is the argument coherent?",
        "Are concepts defined and used consistently?",
        "Is the contribution real, stated, and not overstated relative to prior work?",
    ],
    "literature": [
        "Is the paper positioned in the current conversation?",
        "Is key work missing or misread? Is the claimed gap real?",
        "Does it fit the journal's readership?",
    ],
    "field": [
        "Is it substantively accurate for the subfield and its context?",
        "Would specialists or practitioners accept the framing?",
    ],
    "ethics-integrity": [
        "Consent, approvals, data protection, conflicts of interest.",
        "Citation integrity; image or data irregularities.",
        "Compliance with the relevant reporting guideline.",
    ],
    "devils-advocate": [
        "What is the strongest case against the central claim?",
        "Alternative explanations; the most damaging counterexample.",
        "Under what reading does the contribution disappear?",
    ],
    "generalist": [
        "Is it clear to a non-specialist reader?",
        "Do the abstract and introduction promise what the paper delivers?",
    ],
}

# article_type (MANUSCRIPT_PROFILE_V1) -> ordered lenses; the first two are
# the default 2-reviewer panel, the third is added for a full panel.
DEFAULT_PANELS: Dict[str, List[str]] = {
    "empirical": ["methods", "theory", "literature"],
    "theory": ["theory", "literature", "devils-advocate"],
    "review": ["literature", "methods", "theory"],
    "case-study": ["methods", "field", "theory"],
    "commentary": ["field", "generalist", "devils-advocate"],
    "book-chapter": ["theory", "field", "generalist"],
    "other": ["theory", "methods", "literature"],
}

_MEDICAL = {"medicine-health", "medicine_health"}


@dataclass
class ReviewerBrief:
    reviewer_id: str
    lens: str
    focus: List[str] = field(default_factory=list)
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PanelError(ValueError):
    pass


def _family(profile: Dict[str, Any]) -> str:
    fam = profile.get("discipline_family") or profile.get("discipline") or ""
    return str(fam).strip().lower().replace(" ", "-")


def build_panel(
    manuscript_profile: Dict[str, Any],
    size: int = 3,
    lenses: Optional[List[str]] = None,
) -> List[ReviewerBrief]:
    """Choose reviewer lenses for a manuscript.

    `manuscript_profile` is a MANUSCRIPT_PROFILE_V1 dict (only
    `article_type` and `discipline` are read; an optional
    `discipline_family` slug from shared/disciplines.md is honored).
    `lenses` overrides the defaults (the editor's stated choice).
    Size is 2 or 3: the router's delegation cap is 2 agents by default and 3
    exceptionally (references/subagent-review.md).
    """
    if size not in (2, 3):
        raise PanelError("panel size must be 2 or 3 (router delegation cap)")
    if lenses is not None:
        unknown = [l for l in lenses if l not in LENSES]
        if unknown:
            raise PanelError("unknown lens(es): %s" % unknown)
        if len(set(lenses)) != len(lenses):
            raise PanelError("each reviewer needs a distinct lens")
        if len(lenses) != size:
            raise PanelError("got %d lenses for a panel of %d" % (len(lenses), size))
        chosen = list(lenses)
        reasons = ["editor's choice"] * size
    else:
        article_type = manuscript_profile.get("article_type") or "other"
        chosen = list(DEFAULT_PANELS.get(article_type, DEFAULT_PANELS["other"]))
        reasons = ["default for %s" % article_type] * 3
        if _family(manuscript_profile) in _MEDICAL:
            chosen = ["statistics" if l == "theory" else l for l in chosen]
            if "ethics-integrity" not in chosen:
                chosen[2] = "ethics-integrity"
            reasons = ["medicine-health adjustment"] * 3
        chosen = chosen[:size]
        reasons = reasons[:size]
    return [
        ReviewerBrief(reviewer_id="R%d" % (i + 1), lens=lens, focus=list(LENS_FOCUS[lens]), reason=reason)
        for i, (lens, reason) in enumerate(zip(chosen, reasons))
    ]


def subagent_packet(
    brief: ReviewerBrief,
    manuscript_ref: str,
    journal_criteria: Optional[str] = None,
) -> str:
    """Isolated briefing for one reviewer subagent, in the router's
    minimal-packet shape. Contains nothing about other reviewers."""
    criteria = journal_criteria.strip() if journal_criteria else "none supplied; use the discipline's general standards"
    focus = "\n".join("  - %s" % q for q in brief.focus)
    return (
        "OBJECTIVE: Review this manuscript as Reviewer %s (lens: %s). Return one REVIEW_REPORT_V1.\n"
        "RELEVANT INPUT: manuscript: %s; journal criteria: %s\n"
        "CONSTRAINTS: read-only; do not delegate; you have not seen and must not ask for other reviews;\n"
        "  ground every major or fatal concern in a manuscript location and evidence; do not invent citations\n"
        "  (mark any suggested work 'to verify'); you are a role, not a named person; this is a simulated\n"
        "  pre-submission review, not a prediction of any journal's decision.\n"
        "LENS FOCUS:\n%s\n"
        "EXPECTED OUTPUT: REVIEW_REPORT_V1 JSON with reviewer_id \"%s\", lens \"%s\", and\n"
        "  independence {\"mode\": \"isolated-subagent\", \"saw_other_reports\": false}; nothing else."
    ) % (brief.reviewer_id, brief.lens, manuscript_ref, criteria, focus, brief.reviewer_id, brief.lens)
