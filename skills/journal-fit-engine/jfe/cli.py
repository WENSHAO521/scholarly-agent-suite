"""Developer CLI. Not required for normal Agent Skill usage -- a host
invokes SKILL.md's instructions directly; this is for development, live
verification, and debugging. JSON output throughout.

Commands:
    lookup-journal        --query "..." | --issn ISSN
    evaluate-fit           --manuscript-json PATH (--query "..." | --issn ISSN)
    build-style-context     --query "..." | --issn ISSN [--official-requirements-json PATH]
                            [--observed-patterns-json PATH] [--article-type TYPE]
    build-journal-profile   --query "..." | --issn ISSN [--manuscript-json PATH]
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from jfe.apc_oa import classify as classify_apc_oa
from jfe.fit_dimensions import assess_all as assess_fit_dimensions
from jfe.fit_model import compute_fit
from jfe.hard_filters import apply_all as apply_hard_filters, eliminated
from jfe.http_client import HttpClient, HttpError
from jfe.indexing import assess_indexing
from jfe.integrity import screen as integrity_screen
from jfe.journal_evidence import EvidenceLookupError, lookup_by_issn, lookup_by_name
from jfe.manuscript_profile import ManuscriptProfile, ProfileError
from jfe.style_context import StyleContextError, from_journal_evidence
from jfe.target_journal_profile import TargetJournalProfileError, build_target_journal_profile


def _to_jsonable(obj):
    if dataclasses.is_dataclass(obj):
        return {k: _to_jsonable(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    return obj


def _print_json(obj) -> None:
    print(json.dumps(_to_jsonable(obj), indent=2, default=str))


def _client() -> HttpClient:
    return HttpClient(user_agent="journal-fit-engine-cli/1.0 (mailto:research@example.com)")


def _resolve_evidence(client: HttpClient, args) -> "JournalEvidenceT":  # noqa: F821
    if args.issn:
        return lookup_by_issn(client, args.issn)
    if args.query:
        return lookup_by_name(client, args.query)
    raise SystemExit("provide --query or --issn")


def cmd_lookup_journal(args: argparse.Namespace) -> int:
    client = _client()
    try:
        evidence = _resolve_evidence(client, args)
    except (EvidenceLookupError, HttpError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    apc = classify_apc_oa(evidence)
    _print_json({"evidence": evidence, "apc_classification": apc})
    return 0


def cmd_evaluate_fit(args: argparse.Namespace) -> int:
    manuscript_data = json.loads(Path(args.manuscript_json).read_text(encoding="utf-8"))
    try:
        manuscript = ManuscriptProfile.from_dict(manuscript_data)
    except ProfileError as exc:
        print(json.dumps({"error": f"invalid manuscript profile: {exc}"}))
        return 1

    client = _client()
    try:
        evidence = _resolve_evidence(client, args)
    except (EvidenceLookupError, HttpError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    apc = classify_apc_oa(evidence)
    filters = apply_hard_filters(manuscript, evidence, apc.state)
    is_eliminated = eliminated(filters)
    fit = compute_fit(manuscript, evidence, is_eliminated)
    dimensions = assess_fit_dimensions(manuscript, evidence)
    integrity = integrity_screen(evidence)
    indexing = assess_indexing(evidence)

    _print_json({
        "manuscript_keywords": manuscript.keywords(),
        "evidence": evidence,
        "apc_classification": apc,
        "hard_filters": filters,
        "fit": fit,
        "fit_dimensions": dimensions,
        "integrity": integrity,
        "indexing": indexing.as_dict(),
    })
    return 0


def cmd_build_style_context(args: argparse.Namespace) -> int:
    client = _client()
    try:
        evidence = _resolve_evidence(client, args)
    except (EvidenceLookupError, HttpError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    official = (json.loads(Path(args.official_requirements_json).read_text(encoding="utf-8"))
                if args.official_requirements_json else None)
    observed = (json.loads(Path(args.observed_patterns_json).read_text(encoding="utf-8"))
                if args.observed_patterns_json else None)
    try:
        context = from_journal_evidence(
            evidence, official_requirements=official, observed_patterns=observed,
            article_type=args.article_type,
        )
    except StyleContextError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    _print_json(context)
    return 0


def cmd_build_journal_profile(args: argparse.Namespace) -> int:
    client = _client()
    try:
        evidence = _resolve_evidence(client, args)
    except (EvidenceLookupError, HttpError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    apc = classify_apc_oa(evidence)
    indexing = assess_indexing(evidence)
    integrity = integrity_screen(evidence)

    fit = None
    if args.manuscript_json:
        manuscript_data = json.loads(Path(args.manuscript_json).read_text(encoding="utf-8"))
        try:
            manuscript = ManuscriptProfile.from_dict(manuscript_data)
        except ProfileError as exc:
            print(json.dumps({"error": f"invalid manuscript profile: {exc}"}))
            return 1
        filters = apply_hard_filters(manuscript, evidence, apc.state)
        fit = compute_fit(manuscript, evidence, eliminated(filters))

    try:
        profile = build_target_journal_profile(
            evidence,
            fit_result=fit,
            apc_classification=apc,
            indexing_assessment=indexing,
            integrity=integrity,
        )
    except TargetJournalProfileError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1

    _print_json(profile)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    lookup_p = sub.add_parser("lookup-journal", help="Look up live journal evidence")
    lookup_p.add_argument("--query")
    lookup_p.add_argument("--issn")
    lookup_p.set_defaults(func=cmd_lookup_journal)

    fit_p = sub.add_parser("evaluate-fit", help="Evaluate manuscript-journal fit against live evidence")
    fit_p.add_argument("--manuscript-json", required=True)
    fit_p.add_argument("--query")
    fit_p.add_argument("--issn")
    fit_p.set_defaults(func=cmd_evaluate_fit)

    style_p = sub.add_parser("build-style-context",
                              help="Build a JOURNAL_STYLE_CONTEXT_V1 envelope for scholarly-voice-engine")
    style_p.add_argument("--query")
    style_p.add_argument("--issn")
    style_p.add_argument("--official-requirements-json",
                          help="Path to a JSON file of caller-verified official author-guideline facts")
    style_p.add_argument("--observed-patterns-json",
                          help="Path to a JSON file of corpus-derived observed style patterns")
    style_p.add_argument("--article-type")
    style_p.set_defaults(func=cmd_build_style_context)

    profile_p = sub.add_parser("build-journal-profile",
                                help="Build a TARGET_JOURNAL_PROFILE_V1 envelope against live evidence")
    profile_p.add_argument("--query")
    profile_p.add_argument("--issn")
    profile_p.add_argument("--manuscript-json",
                            help="Optional: evaluate fit_assessment against this manuscript profile; "
                                 "omitted, fit_assessment is NOT_ASSESSED")
    profile_p.set_defaults(func=cmd_build_journal_profile)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
