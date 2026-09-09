"""Developer CLI (PART LXXVI). Not required for normal Agent Skill
usage — a host invokes the Skill's instructions directly. This is for
development, scripted acquisition, and debugging. JSON output throughout
so results are machine-readable.

Commands:
    lookup      --adapter NAME --doi/--pmid/--pmcid/--arxiv ID
    search      --adapter NAME QUERY
    acquire     --corpus-type TYPE --purpose PURPOSE --target-records N --adapters a,b,c QUERY
    resolve-oa  reads a canonical record as JSON from stdin, prints AccessResolution
    validate    runs scripts/validate_skill.py in the given mode (thin wrapper)
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from typing import Any, Dict

from scb.acquisition import CorpusRequest, acquire_corpus
from scb.adapters.arxiv import ArxivAdapter
from scb.adapters.crossref import CrossrefAdapter
from scb.adapters.doaj import DoajAdapter
from scb.adapters.openalex import OpenAlexAdapter
from scb.adapters.pmc import PMCAdapter
from scb.adapters.pubmed import PubMedAdapter
from scb.http_client import HttpClient
from scb.oa_resolver import resolve_access
from scb.records import CanonicalRecord

ADAPTER_REGISTRY = {
    "openalex": OpenAlexAdapter,
    "crossref": CrossrefAdapter,
    "pubmed": PubMedAdapter,
    "pmc": PMCAdapter,
    "arxiv": ArxivAdapter,
    "doaj": DoajAdapter,
}


def _to_jsonable(obj: Any) -> Any:
    if dataclasses.is_dataclass(obj):
        return {k: _to_jsonable(v) for k, v in dataclasses.asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    return obj


def _print_json(obj: Any) -> None:
    print(json.dumps(_to_jsonable(obj), indent=2, default=str))


def _make_adapter(name: str):
    if name not in ADAPTER_REGISTRY:
        raise SystemExit("unknown adapter %r; choose from %s" % (name, sorted(ADAPTER_REGISTRY)))
    client = HttpClient(user_agent="scholarly-corpus-builder-cli/1.0")
    return ADAPTER_REGISTRY[name](http_client=client)


def cmd_lookup(args: argparse.Namespace) -> int:
    adapter = _make_adapter(args.adapter)
    record = None
    if args.doi:
        record = adapter.lookup_by_doi(args.doi)
    elif args.pmid:
        record = adapter.lookup_by_pmid(args.pmid)
    elif args.pmcid:
        record = adapter.lookup_by_pmcid(args.pmcid)
    elif args.arxiv:
        record = adapter.lookup_by_arxiv(args.arxiv)
    else:
        print("error: provide one of --doi/--pmid/--pmcid/--arxiv", file=sys.stderr)
        return 2

    if record is None:
        print("error: not found or adapter does not support this lookup", file=sys.stderr)
        return 1
    _print_json(record)
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    adapter = _make_adapter(args.adapter)
    results = adapter.search(args.query)
    _print_json(results)
    return 0


def cmd_acquire(args: argparse.Namespace) -> int:
    adapter_names = [a.strip() for a in args.adapters.split(",") if a.strip()]
    adapters = {name: _make_adapter(name) for name in adapter_names}
    request = CorpusRequest(
        corpus_type=args.corpus_type,
        target=args.query,
        purpose=args.purpose,
        target_records=args.target_records,
        retrieval_depth=args.retrieval_depth,
    )
    result = acquire_corpus(request, adapters)
    output = {
        "manifest": result.manifest.to_dict(),
        "adapter_errors": result.adapter_errors,
        "records": [r.to_dict() for r in result.records] if args.include_records else None,
    }
    _print_json(output)
    return 0 if result.manifest.status not in ("FAILED",) else 1


def cmd_resolve_oa(args: argparse.Namespace) -> int:
    raw = sys.stdin.read()
    data = json.loads(raw)
    record = CanonicalRecord.from_dict(data)
    resolution = resolve_access(record)
    _print_json(resolution)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    import subprocess

    cmd = [sys.executable, "scripts/validate_skill.py", "--mode", args.mode]
    if args.root:
        cmd += ["--root", args.root]
    return subprocess.call(cmd)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="scb", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    lookup_p = sub.add_parser("lookup", help="Look up one work by identifier via an adapter")
    lookup_p.add_argument("--adapter", required=True, choices=sorted(ADAPTER_REGISTRY))
    lookup_p.add_argument("--doi")
    lookup_p.add_argument("--pmid")
    lookup_p.add_argument("--pmcid")
    lookup_p.add_argument("--arxiv")
    lookup_p.set_defaults(func=cmd_lookup)

    search_p = sub.add_parser("search", help="Search via an adapter")
    search_p.add_argument("--adapter", required=True, choices=sorted(ADAPTER_REGISTRY))
    search_p.add_argument("query")
    search_p.set_defaults(func=cmd_search)

    acquire_p = sub.add_parser("acquire", help="Run the full acquisition pipeline (search -> dedup -> OA resolve -> sample -> manifest)")
    acquire_p.add_argument("--corpus-type", required=True, choices=["discipline", "journal", "historical_scholar", "author", "book", "comparison"])
    acquire_p.add_argument("--purpose", required=True)
    acquire_p.add_argument("--adapters", required=True, help="Comma-separated adapter names, e.g. openalex,crossref")
    acquire_p.add_argument("--target-records", type=int, default=30)
    acquire_p.add_argument("--retrieval-depth", default="LEVEL_1_ABSTRACT", choices=["LEVEL_0_METADATA", "LEVEL_1_ABSTRACT", "LEVEL_2_STRUCTURE", "LEVEL_3_FULLTEXT"])
    acquire_p.add_argument("--include-records", action="store_true", help="Include the full selected records in the output (default: manifest + errors only)")
    acquire_p.add_argument("query")
    acquire_p.set_defaults(func=cmd_acquire)

    resolve_p = sub.add_parser("resolve-oa", help="Read a CanonicalRecord as JSON from stdin, print its AccessResolution")
    resolve_p.set_defaults(func=cmd_resolve_oa)

    validate_p = sub.add_parser("validate", help="Thin wrapper around scripts/validate_skill.py")
    validate_p.add_argument("--mode", choices=["source", "runtime"], default="source")
    validate_p.add_argument("--root")
    validate_p.set_defaults(func=cmd_validate)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
