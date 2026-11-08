import unittest

from scripts.voice import profile_schema as ps


class ClaimTypeTests(unittest.TestCase):
    def test_valid_claim_type(self):
        self.assertEqual(ps.validate_claim_type("mechanistic"), [])

    def test_invalid_claim_type(self):
        errors = ps.validate_claim_type("proven")
        self.assertEqual(len(errors), 1)
        self.assertIn("proven", errors[0])

    def test_none_is_valid(self):
        self.assertEqual(ps.validate_claim_type(None), [])


class ConfidenceTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(ps.validate_confidence("high"), [])

    def test_moderate_is_valid(self):
        # Matches scholarly-corpus-builder's actual vocabulary and the
        # Suite's SCHOLARLY_PROFILE_V1 schema (confidence enum), not "medium".
        self.assertEqual(ps.validate_confidence("moderate"), [])

    def test_medium_is_rejected(self):
        # "medium" was this module's own earlier (incorrect) term; a real
        # corpus-builder profile never sends it, so it must not validate.
        errors = ps.validate_confidence("medium")
        self.assertEqual(len(errors), 1)

    def test_invalid_percentage_rejected(self):
        errors = ps.validate_confidence("73%")
        self.assertEqual(len(errors), 1)


class AuthorProfileTests(unittest.TestCase):
    def test_minimal_valid_profile(self):
        profile = {"profile_type": "author", "source_count": 14}
        self.assertEqual(ps.validate_author_profile(profile), [])

    def test_unknown_field_flagged(self):
        profile = {"profile_type": "author", "made_up_field": True}
        errors = ps.validate_author_profile(profile)
        self.assertTrue(any("made_up_field" in e for e in errors))

    def test_wrong_profile_type_flagged(self):
        profile = {"profile_type": "journal"}
        errors = ps.validate_author_profile(profile)
        self.assertTrue(any("profile_type" in e for e in errors))

    def test_do_not_preserve_must_be_list(self):
        profile = {"profile_type": "author", "do_not_preserve": "citation errors"}
        errors = ps.validate_author_profile(profile)
        self.assertTrue(any("do_not_preserve" in e for e in errors))


class JournalTargetTests(unittest.TestCase):
    def test_compact_shape_valid(self):
        target = {"contribution_position": "earlier", "mechanism_visibility": "higher"}
        self.assertEqual(ps.validate_journal_target(target), [])

    def test_full_shape_valid(self):
        target = {"genre": "empirical_social_science", "theory_density": "medium_high"}
        self.assertEqual(ps.validate_journal_target(target), [])

    def test_unknown_field_flagged(self):
        target = {"contribution_position": "earlier", "acceptance_probability": "93%"}
        errors = ps.validate_journal_target(target)
        self.assertTrue(any("acceptance_probability" in e for e in errors))


class VoiceRequestOutputTests(unittest.TestCase):
    def test_default_request_is_valid(self):
        self.assertEqual(ps.VoiceRequest().validate(), [])

    def test_invalid_editing_mode_flagged(self):
        req = ps.VoiceRequest(editing_mode="full_rewrite")
        errors = req.validate()
        self.assertTrue(any("editing_mode" in e for e in errors))

    def test_request_validates_nested_author_profile(self):
        req = ps.VoiceRequest(author_profile={"profile_type": "journal"})
        errors = req.validate()
        self.assertTrue(any("profile_type" in e for e in errors))

    def test_default_output_is_valid(self):
        self.assertEqual(ps.VoiceOutput(mode="draft").validate(), [])

    def test_invalid_integrity_status_flagged(self):
        out = ps.VoiceOutput(mode="draft", integrity_status="LOOKS_FINE")
        errors = out.validate()
        self.assertTrue(any("integrity_status" in e for e in errors))


class VoiceRequestV1CompatibilityTests(unittest.TestCase):
    def test_draft_task_maps_through(self):
        req = ps.from_voice_request_v1({
            "protocol": "VOICE_REQUEST_V1", "task": "draft", "genre": "research-article",
        })
        self.assertEqual(req.task, "draft")
        self.assertEqual(req.genre, "research-article")

    def test_adapt_to_journal_maps_to_journal_adapt(self):
        req = ps.from_voice_request_v1({
            "protocol": "VOICE_REQUEST_V1", "task": "adapt-to-journal", "genre": "research-article",
        })
        self.assertEqual(req.task, "journal_adapt")

    def test_calibrate_author_voice_maps_to_author_voice(self):
        req = ps.from_voice_request_v1({
            "protocol": "VOICE_REQUEST_V1", "task": "calibrate-author-voice", "genre": "book-chapter",
        })
        self.assertEqual(req.task, "author_voice")

    def test_continue_chapter_maps_to_book_chapter(self):
        req = ps.from_voice_request_v1({
            "protocol": "VOICE_REQUEST_V1", "task": "continue-chapter", "genre": "book-chapter",
        })
        self.assertEqual(req.task, "book_chapter")

    def test_audit_task_maps_to_audit_mode(self):
        req = ps.from_voice_request_v1({
            "protocol": "VOICE_REQUEST_V1", "task": "audit", "genre": "research-article",
        })
        self.assertEqual(req.task, "audit")
        self.assertEqual(req.validate(), [])

    def test_wrong_protocol_rejected(self):
        with self.assertRaises(ps.SchemaError):
            ps.from_voice_request_v1({"protocol": "SOMETHING_ELSE_V1", "task": "draft"})

    def test_unrecognized_task_rejected(self):
        with self.assertRaises(ps.SchemaError):
            ps.from_voice_request_v1({"protocol": "VOICE_REQUEST_V1", "task": "summarize"})

    def test_constraints_pass_through(self):
        req = ps.from_voice_request_v1({
            "protocol": "VOICE_REQUEST_V1", "task": "draft", "genre": "review",
            "constraints": {"word_limit": 4000},
        })
        self.assertEqual(req.constraints, {"word_limit": 4000})


class VoiceOutputV1CompatibilityTests(unittest.TestCase):
    def test_pass_state_maps_through(self):
        envelope = ps.to_voice_output_v1(ps.VoiceOutput(mode="draft", output="Some prose."))
        self.assertEqual(envelope, {
            "protocol": "VOICE_OUTPUT_V1",
            "output_text": "Some prose.",
            "validation_state": "PASS",
            "limitations": [],
        })

    def test_citation_uncertainty_collapses_to_blocked_by_missing_evidence(self):
        out = ps.VoiceOutput(mode="revise", integrity_status="BLOCKED_BY_CITATION_UNCERTAINTY")
        envelope = ps.to_voice_output_v1(out)
        self.assertEqual(envelope["validation_state"], "BLOCKED_BY_MISSING_EVIDENCE")
        self.assertTrue(any("BLOCKED_BY_CITATION_UNCERTAINTY" in limitation
                             for limitation in envelope["limitations"]))

    def test_argument_inconsistency_collapses_to_repair_required(self):
        out = ps.VoiceOutput(mode="revise", integrity_status="BLOCKED_BY_ARGUMENT_INCONSISTENCY")
        envelope = ps.to_voice_output_v1(out)
        self.assertEqual(envelope["validation_state"], "REPAIR_REQUIRED")

    def test_existing_limitations_are_preserved(self):
        out = ps.VoiceOutput(mode="draft", limitations=["small sample corpus profile"])
        envelope = ps.to_voice_output_v1(out)
        self.assertIn("small sample corpus profile", envelope["limitations"])

    def test_invalid_output_rejected(self):
        with self.assertRaises(ps.SchemaError):
            ps.to_voice_output_v1(ps.VoiceOutput(mode="draft", integrity_status="NOT_A_STATE"))


if __name__ == "__main__":
    unittest.main()
