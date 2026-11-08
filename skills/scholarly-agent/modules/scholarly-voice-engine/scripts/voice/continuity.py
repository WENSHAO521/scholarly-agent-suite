"""A small, heuristic continuity ledger for long-form (book/monograph) work,
operationalizing references/continuity-ledger.md's concept and claim
ledgers. Not NLP — it catches exact-key redefinition and direct stance
contradiction, which is most of what actually goes wrong across chapters
drafted in separate passes.

to_dict()/from_dict() serialize to/from a CONTINUITY_STATE_V1 envelope
(scholarly-agent-suite/protocols/continuity-state.schema.json) so this
ledger can actually be "passed between chapter-drafting sessions" as that
protocol's own description requires -- previously this class was
in-memory only. concept_ledger/claim_ledger round-trip through this
class's own active conflict-checking; voice_contract/evidence_ledger/
chapter_ledger/terminology/open_questions are stored and round-tripped
opaquely (this class does not yet validate or act on them) -- see
references/integration.md's compatibility notes for what remains open.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class ContinuityConflict(Exception):
    """Raised when a concept is redefined or a claim is contradicted without
    being explicitly marked as a refinement."""


@dataclass
class ConceptEntry:
    definition: str
    chapter: int


@dataclass
class ClaimEntry:
    stance: str
    chapter: int


class ContinuityLedger:
    def __init__(self) -> None:
        self.concepts: dict[str, ConceptEntry] = {}
        self.claims: dict[str, ClaimEntry] = {}
        # Opaque pass-through state (see module docstring): not validated
        # or acted on by this class yet, but preserved across a
        # to_dict()/from_dict() round trip rather than silently dropped.
        self.voice_contract: dict = {}
        self.evidence_ledger: list = []
        self.chapter_ledger: list = []
        self.terminology: dict = {}
        self.open_questions: list = []

    def add_concept(self, term: str, definition: str, chapter: int, *, refinement: bool = False) -> None:
        """Record a concept's definition. Raises ContinuityConflict if the
        term was previously defined differently and this isn't marked as a
        deliberate refinement (see continuity-ledger.md §Concept ledger).
        """
        existing = self.concepts.get(term)
        if existing is not None and existing.definition != definition and not refinement:
            raise ContinuityConflict(
                f"term {term!r} redefined in chapter {chapter} "
                f"(chapter {existing.chapter} defined it as {existing.definition!r}, "
                f"chapter {chapter} defines it as {definition!r})"
            )
        self.concepts[term] = ConceptEntry(definition, chapter)

    def add_claim(self, claim_key: str, stance: str, chapter: int, *, refinement: bool = False) -> None:
        """Record a claim's stance (e.g. "supported", "rejected", or any
        short label meaningful to the caller). Raises ContinuityConflict on
        a direct contradiction not marked as a refinement (see
        continuity-ledger.md §Claim ledger).
        """
        existing = self.claims.get(claim_key)
        if existing is not None and existing.stance != stance and not refinement:
            raise ContinuityConflict(
                f"claim {claim_key!r} contradicted in chapter {chapter} "
                f"(chapter {existing.chapter} stated {existing.stance!r}, "
                f"chapter {chapter} states {stance!r})"
            )
        self.claims[claim_key] = ClaimEntry(stance, chapter)

    def check_term_variants(self, canonical: str, seen_terms: list[str]) -> list[str]:
        """Return any terms in seen_terms that are not the canonical term
        registered for a concept — a lightweight terminology-drift check
        (continuity-ledger.md §Terminology audit). Case-sensitive by design:
        capitalization drift is itself a flagged pattern.
        """
        return [t for t in seen_terms if t != canonical]

    def to_dict(self) -> dict:
        """Serialize to a CONTINUITY_STATE_V1 envelope. `voice_contract` is
        required by that protocol; an empty dict is valid (means "no fixed
        voice decisions recorded yet"), never omitted."""
        return {
            "protocol": "CONTINUITY_STATE_V1",
            "voice_contract": dict(self.voice_contract),
            "concept_ledger": [
                {"term": term, "definition": entry.definition, "chapter": entry.chapter}
                for term, entry in self.concepts.items()
            ],
            "claim_ledger": [
                {"claim_key": key, "stance": entry.stance, "chapter": entry.chapter}
                for key, entry in self.claims.items()
            ],
            "evidence_ledger": list(self.evidence_ledger),
            "chapter_ledger": list(self.chapter_ledger),
            "terminology": dict(self.terminology),
            "open_questions": list(self.open_questions),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ContinuityLedger":
        """Reconstruct a ledger from a CONTINUITY_STATE_V1 envelope (see
        to_dict()). Raises ValueError on a wrong/missing protocol field or a
        concept_ledger/claim_ledger entry with the wrong shape -- never
        silently drops or guesses at malformed entries."""
        if data.get("protocol") != "CONTINUITY_STATE_V1":
            raise ValueError(f"not a CONTINUITY_STATE_V1 envelope: protocol={data.get('protocol')!r}")

        ledger = cls()
        ledger.voice_contract = dict(data.get("voice_contract") or {})
        for entry in data.get("concept_ledger") or []:
            missing = {"term", "definition", "chapter"} - set(entry)
            if missing:
                raise ValueError(f"concept_ledger entry missing fields: {sorted(missing)}")
            ledger.concepts[entry["term"]] = ConceptEntry(entry["definition"], entry["chapter"])
        for entry in data.get("claim_ledger") or []:
            missing = {"claim_key", "stance", "chapter"} - set(entry)
            if missing:
                raise ValueError(f"claim_ledger entry missing fields: {sorted(missing)}")
            ledger.claims[entry["claim_key"]] = ClaimEntry(entry["stance"], entry["chapter"])
        ledger.evidence_ledger = list(data.get("evidence_ledger") or [])
        ledger.chapter_ledger = list(data.get("chapter_ledger") or [])
        ledger.terminology = dict(data.get("terminology") or {})
        ledger.open_questions = list(data.get("open_questions") or [])
        return ledger
