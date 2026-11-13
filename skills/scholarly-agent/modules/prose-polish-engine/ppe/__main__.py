"""Command line: ``python -m ppe diagnose FILE [--defensive]`` or
``python -m ppe check ORIGINAL POLISHED [--term TERM ...]``.

Run with this module's directory on ``sys.path`` (``cd`` into it, or set
``PYTHONPATH``). Prints JSON.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ppe.diagnose import defensive_findings, detect_language, diagnose
from ppe.report import build_polish_report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m ppe")
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("diagnose", help="list templated phrasing in a text")
    d.add_argument("file")
    d.add_argument("--lang", help="ISO 639-1 code; detected when omitted")
    d.add_argument("--defensive", action="store_true",
                   help="list only defensive-writing findings (references/defensive-writing.md)")
    c = sub.add_parser("check", help="compare a polished text with its original (POLISH_REPORT_V1)")
    c.add_argument("original")
    c.add_argument("polished")
    c.add_argument("--lang", help="ISO 639-1 code; detected when omitted")
    c.add_argument("--level", default="standard", choices=["light", "standard", "deep"])
    c.add_argument("--term", action="append", default=[], help="a term that must keep its exact form")
    args = ap.parse_args(argv)

    read = lambda p: Path(p).read_text(encoding="utf-8")  # noqa: E731
    if args.cmd == "diagnose":
        text = read(args.file)
        out = diagnose(text, args.lang or detect_language(text))
        if args.defensive:
            out["findings"] = defensive_findings(out)
        rc = 0
    else:
        out = build_polish_report(read(args.original), read(args.polished), args.level,
                                  lang=args.lang, protected_terms=args.term)
        rc = 1 if out["status"] == "FAIL" else 0
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
