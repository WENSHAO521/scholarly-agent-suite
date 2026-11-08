"""Hard filters eliminate a candidate outright; they never silently
function as soft-fit weakness and are never waved off as "just a concern"
(SKILL.md §Hard filters vs. soft fit). Every filter that cannot be verified
from available evidence returns CANNOT_VERIFY, never a fabricated pass.
"""
from __future__ import annotations

import datetime
from dataclasses import dataclass
from typing import Optional

from jfe.journal_evidence import JournalEvidence
from jfe.manuscript_profile import ManuscriptProfile

PASS = "PASS"
FAIL = "FAIL"
CANNOT_VERIFY = "CANNOT_VERIFY"

# A source with no indexed output in this many years is flagged as a
# possibly-inactive/discontinued candidate. Conservative on purpose: this
# is a hard-elimination signal, so false positives (wrongly excluding a
# live journal) are worse than a missed true positive.
INACTIVITY_THRESHOLD_YEARS = 4


@dataclass
class FilterResult:
    name: str
    result: str
    reason: str


def check_inactive(evidence: JournalEvidence, current_year: Optional[int] = None) -> FilterResult:
    current_year = current_year or datetime.date.today().year
    if evidence.last_publication_year is None:
        return FilterResult("journal_inactive", CANNOT_VERIFY,
                             "Index has no last_publication_year for this source.")
    gap = current_year - evidence.last_publication_year
    if gap >= INACTIVITY_THRESHOLD_YEARS:
        return FilterResult("journal_inactive", FAIL,
                             f"No indexed output since {evidence.last_publication_year} ({gap} years) -- "
                             "possibly discontinued or absorbed; verify directly before excluding entirely.")
    return FilterResult("journal_inactive", PASS,
                         f"Indexed output as recently as {evidence.last_publication_year}.")


def check_language(manuscript: ManuscriptProfile, evidence: JournalEvidence) -> FilterResult:
    # The index adapters here do not carry a journal's accepted-language
    # list, so this filter is honestly unverifiable from this evidence
    # source alone -- never guessed from the journal's display name.
    return FilterResult("language_unsupported", CANNOT_VERIFY,
                         "Accepted-language policy is not available from OpenAlex/Crossref index data; "
                         "check the journal's own submission guidelines.")


def check_article_type(manuscript: ManuscriptProfile, evidence: JournalEvidence) -> FilterResult:
    # Same honesty constraint: neither index reliably exposes an accepted-
    # article-type list at the source level.
    return FilterResult("wrong_article_type", CANNOT_VERIFY,
                         "Accepted article types are not available from OpenAlex/Crossref index data; "
                         "check the journal's own author guidelines.")


def check_no_apc_constraint(manuscript: ManuscriptProfile, apc_state: str) -> FilterResult:
    from jfe.apc_oa import MANDATORY_APC

    if not manuscript.constraints.get("no_mandatory_apc"):
        return FilterResult("mandatory_constraint_violated", PASS, "No no_mandatory_apc constraint stated.")
    if apc_state == MANDATORY_APC:
        return FilterResult("mandatory_constraint_violated", FAIL,
                             "User requires no mandatory APC; this journal has one.")
    return FilterResult("mandatory_constraint_violated", PASS,
                         "No mandatory-APC conflict found with available evidence.")


def apply_all(manuscript: ManuscriptProfile, evidence: JournalEvidence, apc_state: str,
               current_year: Optional[int] = None) -> list[FilterResult]:
    return [
        check_inactive(evidence, current_year),
        check_language(manuscript, evidence),
        check_article_type(manuscript, evidence),
        check_no_apc_constraint(manuscript, apc_state),
    ]


def eliminated(results: list[FilterResult]) -> bool:
    """A candidate is hard-eliminated only by an actual FAIL, never by
    CANNOT_VERIFY -- unverifiable is not the same as failing."""
    return any(r.result == FAIL for r in results)
