import unittest

from scripts.voice.profile_merge import resolve_voice_precedence


class PrecedenceTests(unittest.TestCase):
    def test_author_beats_everything(self):
        layers = {
            "author": {"first_person": "low"},
            "discipline": {"first_person": "medium"},
            "journal": {"first_person": "high"},
            "historical": {"first_person": "very_high"},
        }
        resolved, conflicts = resolve_voice_precedence(layers)
        self.assertEqual(resolved["first_person"], "low")
        self.assertEqual(conflicts[0]["chosen_layer"], "author")
        self.assertEqual(len(conflicts[0]["overridden"]), 3)

    def test_discipline_fills_gap_author_does_not_cover(self):
        layers = {
            "author": {"first_person": "low"},
            "discipline": {"qualification_density": "medium"},
        }
        resolved, conflicts = resolve_voice_precedence(layers)
        self.assertEqual(resolved["first_person"], "low")
        self.assertEqual(resolved["qualification_density"], "medium")
        self.assertEqual(conflicts, [])

    def test_journal_beats_historical_by_default(self):
        layers = {
            "journal": {"tone": "formal"},
            "historical": {"tone": "informal"},
        }
        resolved, _ = resolve_voice_precedence(layers)
        self.assertEqual(resolved["tone"], "formal")


class ConfidenceGatingTests(unittest.TestCase):
    def test_low_confidence_journal_yields_to_historical(self):
        layers = {
            "journal": {"tone": "formal"},
            "historical": {"tone": "informal"},
        }
        resolved, conflicts = resolve_voice_precedence(layers, confidence={"journal": "low"})
        self.assertEqual(resolved["tone"], "informal")
        self.assertEqual(conflicts[0]["chosen_layer"], "historical")

    def test_low_confidence_journal_still_used_if_sole_source(self):
        layers = {"journal": {"tone": "formal"}}
        resolved, conflicts = resolve_voice_precedence(layers, confidence={"journal": "low"})
        self.assertEqual(resolved["tone"], "formal")
        self.assertEqual(conflicts, [])

    def test_high_confidence_journal_not_gated(self):
        layers = {
            "journal": {"tone": "formal"},
            "historical": {"tone": "informal"},
        }
        resolved, _ = resolve_voice_precedence(layers, confidence={"journal": "high"})
        self.assertEqual(resolved["tone"], "formal")

    def test_confidence_never_promotes_a_lower_precedence_layer_over_author(self):
        # A low-confidence journal profile must never outrank the author's
        # own established voice, even though confidence gating exists.
        layers = {
            "author": {"first_person": "low"},
            "journal": {"first_person": "medium"},
        }
        resolved, conflicts = resolve_voice_precedence(layers, confidence={"journal": "high"})
        self.assertEqual(resolved["first_person"], "low")
        self.assertEqual(conflicts[0]["chosen_layer"], "author")


if __name__ == "__main__":
    unittest.main()
