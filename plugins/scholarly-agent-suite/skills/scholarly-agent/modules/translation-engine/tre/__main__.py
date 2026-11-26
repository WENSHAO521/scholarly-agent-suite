"""Command line (run with this module's directory on ``sys.path``):

    python -m tre terms SOURCE [--lang zh]
    python -m tre check SOURCE TARGET --to en [--from zh] [--variety zh-Hant]
                        [--mode faithful|academic|bilingual] [--glossary FILE] [--keep TERM ...]
    python -m tre bilingual SOURCE TARGET

``terms`` and ``check`` print JSON; ``bilingual`` prints Markdown. ``check``
exits 1 when the report status is FAIL.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tre import MODES
from tre.glossary import load_glossary, term_candidates
from tre.languages import detect_language
from tre.report import bilingual, build_translation_report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m tre")
    sub = ap.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("terms", help="list terms worth fixing in a glossary before translating")
    t.add_argument("source")
    t.add_argument("--lang", help="source language; detected when omitted")
    c = sub.add_parser("check", help="check a translation against its source (TRANSLATION_REPORT_V1)")
    c.add_argument("source")
    c.add_argument("target")
    c.add_argument("--to", dest="target_language", required=True, help="e.g. en, zh-Hant, ja, pt-BR")
    c.add_argument("--from", dest="source_language", help="detected when omitted")
    c.add_argument("--variety", help="zh-Hant / zh-Hans are checked character by character")
    c.add_argument("--mode", default="faithful", choices=MODES)
    c.add_argument("--glossary", help="JSON or two-column TSV glossary")
    c.add_argument("--keep", action="append", default=[], help="a term to leave exactly as written")
    b = sub.add_parser("bilingual", help="source and translation, paragraph by paragraph")
    b.add_argument("source")
    b.add_argument("target")
    args = ap.parse_args(argv)

    read = lambda p: Path(p).read_text(encoding="utf-8")  # noqa: E731
    if args.cmd == "bilingual":
        sys.stdout.write(bilingual(read(args.source), read(args.target)))
        return 0
    if args.cmd == "terms":
        text = read(args.source)
        out = term_candidates(text, args.lang or detect_language(text))
        rc = 0
    else:
        glossary = load_glossary(args.glossary) if args.glossary else []
        glossary += [{"source": k, "keep": True} for k in args.keep]
        out = build_translation_report(read(args.source), read(args.target), args.target_language,
                                       args.source_language, args.mode, args.variety, glossary)
        rc = 1 if out["status"] == "FAIL" else 0
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
