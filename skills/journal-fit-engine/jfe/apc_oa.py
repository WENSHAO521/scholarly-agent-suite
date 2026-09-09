"""APC/OA classification (references/apc-open-access.md). Distinguishes
mandatory APC, optional hybrid OA charge, diamond OA, and unknown -- never
confuses an optional hybrid fee with a mandatory publication fee (SKILL.md
Evidence discipline).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from jfe.journal_evidence import JournalEvidence

MANDATORY_APC = "MANDATORY_APC"
DIAMOND_OA = "DIAMOND_OA"
HYBRID_OA_OPTIONAL = "HYBRID_OA_OPTIONAL"
UNKNOWN = "UNKNOWN"


@dataclass
class APCClassification:
    state: str
    apc_usd: Optional[int]
    is_oa: Optional[bool]
    is_in_doaj: Optional[bool]
    note: str


def classify(evidence: JournalEvidence) -> APCClassification:
    apc, is_oa, in_doaj = evidence.apc_usd, evidence.is_oa, evidence.is_in_doaj

    if is_oa is None:
        return APCClassification(UNKNOWN, apc, is_oa, in_doaj,
                                  "OA status not resolved by the index; verify on the journal's own page before assuming a fee state.")

    if is_oa and (apc is None or apc == 0):
        return APCClassification(DIAMOND_OA, apc, is_oa, in_doaj,
                                  "Fully open access with no APC recorded by the index (diamond/no-fee OA) -- confirm on the journal's own page, index coverage of fee data is incomplete.")

    if is_oa and apc and apc > 0:
        return APCClassification(MANDATORY_APC, apc, is_oa, in_doaj,
                                  f"Fully open access with a recorded APC of ${apc} USD -- a gold-OA fee is mandatory to publish here.")

    if not is_oa and apc and apc > 0:
        return APCClassification(HYBRID_OA_OPTIONAL, apc, is_oa, in_doaj,
                                  f"Subscription journal with an optional hybrid-OA fee of ${apc} USD -- publishing here does NOT require paying this; it only applies if the author chooses hybrid OA.")

    return APCClassification(UNKNOWN, apc, is_oa, in_doaj,
                              "Not enough index data to classify APC/OA state confidently.")


def violates_no_apc_constraint(classification: APCClassification) -> bool:
    """A user's stated 'no mandatory APC' constraint is violated only by
    MANDATORY_APC -- never by HYBRID_OA_OPTIONAL (which the author is free
    to decline) or UNKNOWN (absence of evidence is not evidence of a fee)."""
    return classification.state == MANDATORY_APC
