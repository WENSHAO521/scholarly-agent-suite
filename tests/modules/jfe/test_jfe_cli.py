"""CLI argument-parsing and error-path tests. No live network calls --
those are covered by the manual live-check workflow."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from jfe import cli


class ParserTests(unittest.TestCase):
    def test_lookup_journal_requires_query_or_issn(self):
        parser = cli.build_parser()
        args = parser.parse_args(["lookup-journal"])
        with self.assertRaises(SystemExit):
            cli._resolve_evidence(mock.Mock(), args)

    def test_evaluate_fit_requires_manuscript_json(self):
        parser = cli.build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["evaluate-fit", "--query", "x"])

    def test_build_journal_profile_requires_query_or_issn(self):
        parser = cli.build_parser()
        args = parser.parse_args(["build-journal-profile"])
        with self.assertRaises(SystemExit):
            cli._resolve_evidence(mock.Mock(), args)

    def test_build_journal_profile_manuscript_json_is_optional(self):
        parser = cli.build_parser()
        args = parser.parse_args(["build-journal-profile", "--query", "x"])
        self.assertIsNone(args.manuscript_json)


class EvaluateFitErrorPathTests(unittest.TestCase):
    def test_invalid_manuscript_json_reports_error_not_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manuscript.json"
            path.write_text(json.dumps({"not_a_real_field": True}), encoding="utf-8")
            parser = cli.build_parser()
            args = parser.parse_args(["evaluate-fit", "--manuscript-json", str(path), "--query", "x"])
            exit_code = cli.cmd_evaluate_fit(args)
            self.assertEqual(exit_code, 1)

    def test_build_journal_profile_invalid_manuscript_json_reports_error_not_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manuscript.json"
            path.write_text(json.dumps({"not_a_real_field": True}), encoding="utf-8")
            parser = cli.build_parser()
            args = parser.parse_args([
                "build-journal-profile", "--manuscript-json", str(path), "--query", "x",
            ])
            with mock.patch.object(cli, "_resolve_evidence") as resolve:
                from jfe.journal_evidence import JournalEvidence
                resolve.return_value = JournalEvidence(
                    display_name="X", checked_at="2026-09-09T00:00:00+00:00", source="openalex",
                )
                exit_code = cli.cmd_build_journal_profile(args)
            self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()
