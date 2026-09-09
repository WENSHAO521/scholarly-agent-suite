"""Developer CLI. Not required for normal Agent Skill usage -- a host
invokes SKILL.md's instructions directly; this is for development, live
verification, and debugging. JSON output throughout.

Commands:
    lookup-journal   --query "..." | --issn ISSN
    evaluate-fit     --manuscript-json PATH (--query "..." | --issn ISSN)
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

from jfe.apc_oa import classify as classify_apc_oa
from jfe.fit_model import compute_fit
from jfe.hard_filters import apply_all as apply_hard_filters, eliminated
from jfe.http_client import HttpClient, HttpError
from jfe.journal_evidence import EvidenceLookupError, lookup_by_issn, lookup_by_name
from jfe.manuscript_profile import ManuscriptProfile, ProfileError


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

    _print_json({
        "manuscript_keywords": manuscript.keywords(),
        "evidence": evidence,
        "apc_classification": apc,
        "hard_filters": filters,
        "fit": fit,
    })
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

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
