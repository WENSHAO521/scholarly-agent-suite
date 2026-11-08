import unittest

from scripts.voice.journal_context import (
    PROTOCOL,
    JournalContextError,
    apply_journal_style_context,
    from_journal_style_context_v1,
)


def _envelope(**overrides):
    base = {
        "protocol": PROTOCOL,
        "journal_name": "Journal of Example Studies",
        "official_requirements": {"word_limit": 8000},
        "observed_patterns": {"tone": "formal"},
        "freshness": "current",
    }
    base.update(overrides)
    return base


class FromJournalStyleContextV1Tests(unittest.TestCase):
    def test_valid_envelope_round_trips(self):
        context = from_journal_style_context_v1(_envelope())
        self.assertEqual(context.journal_name, "Journal of Example Studies")
        self.assertEqual(context.official_requirements, {"word_limit": 8000})
        self.assertEqual(context.observed_patterns, {"tone": "formal"})
        self.assertEqual(context.freshness, "current")

    def test_wrong_protocol_rejected(self):
        with self.assertRaises(JournalContextError):
            from_journal_style_context_v1(_envelope(protocol="SOMETHING_ELSE_V1"))

    def test_missing_required_field_rejected(self):
        envelope = _envelope()
        del envelope["observed_patterns"]
        with self.assertRaises(JournalContextError):
            from_journal_style_context_v1(envelope)

    def test_non_dict_official_requirements_rejected(self):
        with self.assertRaises(JournalContextError):
            from_journal_style_context_v1(_envelope(official_requirements=["word_limit"]))

    def test_invalid_freshness_rejected(self):
        with self.assertRaises(JournalContextError):
            from_journal_style_context_v1(_envelope(freshness="brand-new"))

    def test_missing_freshness_is_allowed_and_flagged_as_a_limitation(self):
        envelope = _envelope()
        del envelope["freshness"]
        context = from_journal_style_context_v1(envelope)
        self.assertIsNone(context.freshness)
        self.assertTrue(any("did not state freshness" in note for note in context.limitations))

    def test_stale_freshness_flagged_as_a_limitation(self):
        context = from_journal_style_context_v1(_envelope(freshness="stale"))
        self.assertTrue(any("stale" in note for note in context.limitations))

    def test_empty_official_requirements_flagged_as_a_limitation(self):
        context = from_journal_style_context_v1(_envelope(official_requirements={}))
        self.assertTrue(any("no official_requirements" in note for note in context.limitations))

    def test_caller_supplied_limitations_are_preserved_not_replaced(self):
        context = from_journal_style_context_v1(_envelope(limitations=["upstream note"]))
        self.assertIn("upstream note", context.limitations)

    def test_optional_fields_pass_through(self):
        context = from_journal_style_context_v1(_envelope(
            journal_identifiers={"issn_l": "1234-5678"}, article_type="empirical",
            evidence=[{"identity": "1234-5678", "access_status": "metadata-only"}],
        ))
        self.assertEqual(context.journal_identifiers, {"issn_l": "1234-5678"})
        self.assertEqual(context.article_type, "empirical")
        self.assertEqual(len(context.evidence), 1)


class ApplyJournalStyleContextTests(unittest.TestCase):
    def test_current_freshness_lets_journal_beat_historical(self):
        context = from_journal_style_context_v1(_envelope(observed_patterns={"tone": "formal"}))
        layers = {"historical": {"tone": "informal"}}
        resolved, conflicts, hard_requirements, limitations = apply_journal_style_context(context, layers)
        self.assertEqual(resolved["tone"], "formal")
        self.assertEqual(hard_requirements, {"word_limit": 8000})

    def test_stale_freshness_yields_to_historical(self):
        """Regression: a stale observed pattern must not silently outrank a
        lower-precedence layer the way a current one legitimately would."""
        context = from_journal_style_context_v1(_envelope(freshness="stale", observed_patterns={"tone": "formal"}))
        layers = {"historical": {"tone": "informal"}}
        resolved, _conflicts, _hard, _lim = apply_journal_style_context(context, layers)
        self.assertEqual(resolved["tone"], "informal")

    def test_missing_freshness_is_gated_the_same_as_stale(self):
        envelope = _envelope(observed_patterns={"tone": "formal"})
        del envelope["freshness"]
        context = from_journal_style_context_v1(envelope)
        layers = {"historical": {"tone": "informal"}}
        resolved, _conflicts, _hard, _lim = apply_journal_style_context(context, layers)
        self.assertEqual(resolved["tone"], "informal")

    def test_author_layer_still_beats_journal_regardless_of_freshness(self):
        context = from_journal_style_context_v1(_envelope(observed_patterns={"first_person": "high"}))
        layers = {"author": {"first_person": "low"}}
        resolved, conflicts, _hard, _lim = apply_journal_style_context(context, layers)
        self.assertEqual(resolved["first_person"], "low")
        self.assertEqual(conflicts[0]["chosen_layer"], "author")

    def test_official_requirements_never_confidence_gated(self):
        """Even when observed_patterns is gated away for being stale,
        official_requirements (hard constraints) must still come through
        verbatim -- these are not part of the precedence-resolved layers at
        all."""
        context = from_journal_style_context_v1(_envelope(
            freshness="stale", official_requirements={"word_limit": 8000, "citation_style": "APA7"},
        ))
        _resolved, _conflicts, hard_requirements, _lim = apply_journal_style_context(context, {})
        self.assertEqual(hard_requirements, {"word_limit": 8000, "citation_style": "APA7"})

    def test_limitations_propagate_through(self):
        context = from_journal_style_context_v1(_envelope(freshness="stale"))
        _resolved, _conflicts, _hard, limitations = apply_journal_style_context(context, {})
        self.assertTrue(any("stale" in note for note in limitations))


class ContaminationSurvivesRoundTripTests(unittest.TestCase):
    """E2E-04-style regression: corpus-derived observed evidence must never
    land in hard_requirements, and a stated official rule must never end up
    silently confidence-gated away inside observed_patterns resolution."""

    def test_observed_patterns_never_appear_in_hard_requirements(self):
        context = from_journal_style_context_v1(_envelope(
            official_requirements={"word_limit": 8000},
            observed_patterns={"mean_paragraph_length": 120, "tone": "formal"},
        ))
        _resolved, _conflicts, hard_requirements, _lim = apply_journal_style_context(context, {})
        self.assertNotIn("mean_paragraph_length", hard_requirements)
        self.assertNotIn("tone", hard_requirements)

    def test_official_requirements_never_appear_in_resolved_soft_style(self):
        context = from_journal_style_context_v1(_envelope(
            official_requirements={"word_limit": 8000},
            observed_patterns={"tone": "formal"},
        ))
        resolved, _conflicts, _hard, _lim = apply_journal_style_context(context, {})
        self.assertNotIn("word_limit", resolved)


if __name__ == "__main__":
    unittest.main()
