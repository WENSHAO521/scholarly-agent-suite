"""Indexing/quartile evidence assessment (references/indexing-metrics.md).

No paid or authenticated index (Scopus, Web of Science/JCR, SCIE, SSCI,
AHCI, ESCI) is reachable from this Skill's two free, keyless adapters
(OpenAlex Sources, Crossref Journals) -- every such claim is honestly
`cannot_verify`, never inferred from a publisher's own claim or from
model recall of a journal's reputation. Never returns a bare "Q1"; a
quartile always needs its ranking system, category, and year, none of
which this module can supply, so it never fabricates one.

DOAJ inclusion is the one real, freely queryable indexing signal available
(already fetched by jfe.journal_evidence as evidence.is_in_doaj) and is
reported as `officially_verified` accordingly, with source and freshness
attached.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from jfe.journal_evidence import JournalEvidence

OFFICIALLY_VERIFIED = "officially_verified"
CANNOT_VERIFY = "cannot_verify"

# Indexes/metrics this Skill's adapters cannot check at all -- listed
# explicitly so a caller sees exactly what was not checked, rather than a
# silent gap that could be mistaken for "not indexed."
UNCHECKABLE_INDEXES = ("Scopus", "Web of Science", "SCIE", "SSCI", "AHCI", "ESCI")
UNCHECKABLE_METRICS = ("JCR quartile", "CiteScore quartile", "Impact Factor", "SJR")


@dataclass
class IndexingEntry:
    name: str
    state: str  # officially_verified | cannot_verify
    value: object
    source: Optional[str]
    freshness: Optional[str]
    note: str


@dataclass
class IndexingAssessment:
    entries: list

    def as_dict(self) -> dict:
        return {
            e.name: {"state": e.state, "value": e.value, "source": e.source,
                      "freshness": e.freshness, "note": e.note}
            for e in self.entries
        }


def assess_indexing(evidence: JournalEvidence, freshness: Optional[str] = None) -> IndexingAssessment:
    entries = [
        IndexingEntry(
            name="DOAJ",
            state=OFFICIALLY_VERIFIED if evidence.is_in_doaj is not None else CANNOT_VERIFY,
            value=evidence.is_in_doaj,
            source=evidence.source,
            freshness=freshness,
            note=("DOAJ inclusion flag from the index's own record."
                  if evidence.is_in_doaj is not None else
                  "Index did not report a DOAJ inclusion flag for this source."),
        ),
    ]
    for name in UNCHECKABLE_INDEXES:
        entries.append(IndexingEntry(
            name, CANNOT_VERIFY, None, None, None,
            f"{name} requires an authenticated/paid index this Skill's adapters do not query; "
            f"verify directly against {name}'s own listing.",
        ))
    for name in UNCHECKABLE_METRICS:
        entries.append(IndexingEntry(
            name, CANNOT_VERIFY, None, None, None,
            f"{name} is not resolvable from OpenAlex/Crossref; verify against the metric's own "
            "authoritative source and always name the year and category -- a bare quartile letter "
            "is meaningless (see references/indexing-metrics.md).",
        ))
    return IndexingAssessment(entries)
