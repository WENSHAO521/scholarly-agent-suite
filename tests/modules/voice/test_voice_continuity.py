import unittest

from scripts.voice.continuity import ContinuityConflict, ContinuityLedger


class ConceptLedgerTests(unittest.TestCase):
    def setUp(self):
        self.ledger = ContinuityLedger()

    def test_same_definition_repeated_is_fine(self):
        self.ledger.add_concept("resilience", "capacity to absorb shock", chapter=2)
        self.ledger.add_concept("resilience", "capacity to absorb shock", chapter=6)
        self.assertEqual(self.ledger.concepts["resilience"].chapter, 6)

    def test_silent_redefinition_raises(self):
        self.ledger.add_concept("resilience", "capacity to absorb shock", chapter=2)
        with self.assertRaises(ContinuityConflict):
            self.ledger.add_concept("resilience", "tendency to return to equilibrium", chapter=6)

    def test_explicit_refinement_is_allowed(self):
        self.ledger.add_concept("resilience", "capacity to absorb shock", chapter=2)
        self.ledger.add_concept(
            "resilience", "capacity to absorb shock without losing core function",
            chapter=6, refinement=True,
        )
        self.assertIn("without losing core function", self.ledger.concepts["resilience"].definition)


class ClaimLedgerTests(unittest.TestCase):
    def setUp(self):
        self.ledger = ContinuityLedger()

    def test_consistent_claim_repeated_is_fine(self):
        self.ledger.add_claim("mechanism_x_operative", "supported", chapter=3)
        self.ledger.add_claim("mechanism_x_operative", "supported", chapter=7)
        self.assertEqual(self.ledger.claims["mechanism_x_operative"].chapter, 7)

    def test_silent_contradiction_raises(self):
        self.ledger.add_claim("mechanism_x_operative", "supported", chapter=3)
        with self.assertRaises(ContinuityConflict):
            self.ledger.add_claim("mechanism_x_operative", "rejected", chapter=7)

    def test_explicit_refinement_of_a_claim_is_allowed(self):
        self.ledger.add_claim("mechanism_x_operative", "supported", chapter=3)
        self.ledger.add_claim(
            "mechanism_x_operative", "supported only under low state capacity",
            chapter=7, refinement=True,
        )
        self.assertEqual(
            self.ledger.claims["mechanism_x_operative"].stance,
            "supported only under low state capacity",
        )


class TerminologyAuditTests(unittest.TestCase):
    def test_variant_terms_flagged(self):
        ledger = ContinuityLedger()
        variants = ledger.check_term_variants("resilience", ["resilience", "Resilience", "robustness"])
        self.assertEqual(variants, ["Resilience", "robustness"])

    def test_no_variants_returns_empty(self):
        ledger = ContinuityLedger()
        self.assertEqual(ledger.check_term_variants("resilience", ["resilience", "resilience"]), [])


class ContinuityStateV1SerializationTests(unittest.TestCase):
    """CONTINUITY_STATE_V1 round-trip (scholarly-agent-suite/protocols/
    continuity-state.schema.json) -- the whole point of that protocol is
    passing this state between chapter-drafting sessions, so a lossy
    round-trip would defeat it."""

    def test_empty_ledger_round_trips(self):
        ledger = ContinuityLedger()
        data = ledger.to_dict()
        self.assertEqual(data["protocol"], "CONTINUITY_STATE_V1")
        self.assertEqual(data["voice_contract"], {})
        self.assertEqual(data["concept_ledger"], [])
        restored = ContinuityLedger.from_dict(data)
        self.assertEqual(restored.concepts, {})
        self.assertEqual(restored.claims, {})

    def test_concepts_and_claims_round_trip(self):
        ledger = ContinuityLedger()
        ledger.add_concept("resilience", "capacity to absorb shock", chapter=2)
        ledger.add_claim("mechanism_x_operative", "supported", chapter=3)
        restored = ContinuityLedger.from_dict(ledger.to_dict())
        self.assertEqual(restored.concepts["resilience"].definition, "capacity to absorb shock")
        self.assertEqual(restored.concepts["resilience"].chapter, 2)
        self.assertEqual(restored.claims["mechanism_x_operative"].stance, "supported")

    def test_conflict_detection_still_works_after_restore(self):
        """A restored ledger must enforce the same continuity rules as the
        original -- serialization must not silently drop the guarantee."""
        ledger = ContinuityLedger()
        ledger.add_concept("resilience", "capacity to absorb shock", chapter=2)
        restored = ContinuityLedger.from_dict(ledger.to_dict())
        with self.assertRaises(ContinuityConflict):
            restored.add_concept("resilience", "a completely different definition", chapter=9)

    def test_pass_through_fields_round_trip_even_when_unused(self):
        data = {
            "protocol": "CONTINUITY_STATE_V1",
            "voice_contract": {"formality": "high"},
            "concept_ledger": [],
            "claim_ledger": [],
            "evidence_ledger": [{"source": "smith2020"}],
            "chapter_ledger": [{"chapter": 1, "title": "Introduction"}],
            "terminology": {"canonical": "resilience"},
            "open_questions": ["does chapter 4 resolve the mechanism debate?"],
        }
        restored = ContinuityLedger.from_dict(data)
        self.assertEqual(restored.to_dict(), data)

    def test_wrong_protocol_rejected(self):
        with self.assertRaises(ValueError):
            ContinuityLedger.from_dict({"protocol": "SOMETHING_ELSE_V1", "voice_contract": {}})

    def test_malformed_concept_ledger_entry_rejected(self):
        with self.assertRaises(ValueError):
            ContinuityLedger.from_dict({
                "protocol": "CONTINUITY_STATE_V1", "voice_contract": {},
                "concept_ledger": [{"term": "resilience"}],  # missing definition/chapter
            })


if __name__ == "__main__":
    unittest.main()
