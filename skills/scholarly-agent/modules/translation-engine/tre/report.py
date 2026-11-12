"""TRANSLATION_REPORT_V1: build it from a source and its translation,
validate one, and lay the two texts side by side for review. Mirrors
protocols/translation-report.schema.json plus the rules a schema cannot
express (status follows the invariant and glossary checks)."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional

from tre import GLOSSARY_STATUSES, MODES, STATUSES, TRANSLATION_NOTICE
from tre.glossary import check_glossary, normalize
from tre.invariants import check_translation
from tre.languages import detect_language, paragraphs

REQUIRED = ["protocol", "source_language", "target_language", "mode", "paragraphs", "glossary",
            "invariants", "untranslated", "status", "notice"]
NOTE_KINDS = ["quotation", "term", "name", "number", "ambiguity", "culture", "source-error"]
_LANG = re.compile(r"^[a-z]{2,3}(?:-[A-Za-z0-9]{2,8})*$")


def build_translation_report(source: str, target: str, target_language: str,
                             source_language: Optional[str] = None, mode: str = "faithful",
                             variety: Optional[str] = None, glossary: Iterable[Dict[str, Any]] = (),
                             notes: Iterable[Dict[str, str]] = (), escalations: Iterable[str] = (),
                             limitations: Iterable[str] = ()) -> Dict[str, Any]:
    """Check the translation and assemble the report.

    ``glossary`` entries are ``{source, target}`` or ``{source, keep: true}``
    (tre.glossary). ``notes`` is the translator's own log of decisions the
    reader should know about: ``{kind, note}`` with ``kind`` one of
    NOTE_KINDS (``source`` optional, quoting the passage). ``escalations``
    lists problems in the source itself (an unclear claim, a wrong number, a
    citation that does not match its reference) that translation must not
    silently fix.
    """
    if mode not in MODES:
        raise ValueError("unknown mode %r" % mode)
    source_language = source_language or detect_language(source)
    entries = normalize(list(glossary))
    keep = [str(e["source"]) for e in entries if e.get("keep")]
    inv = check_translation(source, target, source_language, target_language, variety, keep)
    gl = check_glossary(source, target, entries)
    failures, warnings = list(inv["failures"]), list(inv["warnings"])
    for r in gl:
        if r["status"] == "missing":
            failures.append("glossary: %r should appear as %r but never does" % (r["source"], r["expected"]))
        elif r["status"] == "count-differs":
            warnings.append("glossary: %r appears %d time(s) in the source, %r %d time(s) in the translation"
                            % (r["source"], r["source_count"], r["expected"], r["target_count"]))
    status = "FAIL" if failures else ("REVIEW" if warnings else "PASS")
    report: Dict[str, Any] = {
        "protocol": "TRANSLATION_REPORT_V1",
        "source_language": source_language,
        "target_language": target_language,
        "mode": mode,
        "paragraphs": {k: inv["paragraphs"][k] for k in ("source", "target", "flagged")},
        "glossary": gl,
        "invariants": {"status": inv["status"], "failures": inv["failures"], "warnings": inv["warnings"]},
        "untranslated": inv["untranslated"],
        "status": status,
        "notice": TRANSLATION_NOTICE,
    }
    if variety:
        report["variety"] = variety
    if notes:
        report["notes"] = [dict(n) for n in notes]
    if escalations:
        report["escalations"] = list(escalations)
    if limitations:
        report["limitations"] = list(limitations)
    return report


def validate_translation_report(report: Dict[str, Any]) -> List[str]:
    """Return a list of problems; empty means the report is usable."""
    if not isinstance(report, dict):
        return ["report is not an object"]
    errors = ["missing field: %s" % k for k in REQUIRED if k not in report]
    if errors:
        return errors
    if report["protocol"] != "TRANSLATION_REPORT_V1":
        errors.append("protocol must be TRANSLATION_REPORT_V1")
    for key in ("source_language", "target_language"):
        if not isinstance(report[key], str) or not _LANG.match(report[key]):
            errors.append("%s must be a language code such as en, zh-Hant, pt-BR: %r" % (key, report[key]))
    if report["mode"] not in MODES:
        errors.append("unknown mode: %r" % report["mode"])
    if report["status"] not in STATUSES:
        errors.append("unknown status: %r" % report["status"])
    if report["notice"] != TRANSLATION_NOTICE:
        errors.append("notice must be tre.TRANSLATION_NOTICE, unchanged")
    inv = report["invariants"]
    if not isinstance(inv, dict) or inv.get("status") not in STATUSES:
        errors.append("invariants.status must be PASS, REVIEW, or FAIL")
    else:
        if inv["status"] == "FAIL" and report["status"] != "FAIL":
            errors.append("a failed invariant check must make the report FAIL")
        if inv["status"] == "REVIEW" and report["status"] == "PASS":
            errors.append("an invariant check needing review cannot be reported as PASS")
    for i, g in enumerate(report["glossary"]):
        if not isinstance(g, dict) or g.get("status") not in GLOSSARY_STATUSES:
            errors.append("glossary[%d] needs a status in %s" % (i, GLOSSARY_STATUSES))
        elif g["status"] == "missing" and report["status"] != "FAIL":
            errors.append("a glossary term missing from the translation must make the report FAIL")
    for i, n in enumerate(report.get("notes", [])):
        if not isinstance(n, dict) or n.get("kind") not in NOTE_KINDS or not n.get("note"):
            errors.append("notes[%d] needs a kind in %s and a note" % (i, NOTE_KINDS))
    return errors


def bilingual(source: str, target: str, source_label: str = "Source", target_label: str = "Translation") -> str:
    """Paragraph-by-paragraph Markdown view for checking a translation:
    each source paragraph followed by its translation. Unequal paragraph
    counts are shown, not hidden."""
    ps, pt = paragraphs(source), paragraphs(target)
    out = []
    for i in range(max(len(ps), len(pt))):
        s = ps[i] if i < len(ps) else "(no paragraph)"
        t = pt[i] if i < len(pt) else "(no paragraph)"
        out.append("**¶%d %s**\n\n%s\n\n**¶%d %s**\n\n%s" % (i + 1, source_label, s, i + 1, target_label, t))
    return "\n\n---\n\n".join(out) + "\n"
