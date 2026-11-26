"""POLISH_REPORT_V1: build it from an original and a polished text, and
validate one. Mirrors protocols/polish-report.schema.json plus the rules a
schema cannot express (status follows the invariant check; residue left in
the polished text always fails; a polish that removed hedges must say why,
in ``calibration`` or in a logged change of a defensive category)."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

import re

from ppe import CALIBRATION_DECISIONS, CATEGORIES, DEFENSIVE_CATEGORIES, LEVELS, POLISH_NOTICE, STATUSES
from ppe.diagnose import detect_language, diagnose, summary
from ppe.invariants import check_invariants
from ppe.languages import has_catalog, supported_note

REQUIRED = ["protocol", "language", "catalog", "level", "before", "after", "changes", "remaining",
            "invariants", "status", "notice"]
CHANGE_REQUIRED = ["category", "before", "after"]
CALIBRATION_REQUIRED = ["before", "after", "decision", "warrant"]


def build_polish_report(original: str, polished: str, level: str = "standard",
                        changes: Iterable[Dict[str, str]] = (), lang: Optional[str] = None,
                        protected_terms: Iterable[str] = (), escalations: Iterable[str] = (),
                        limitations: Iterable[str] = (),
                        calibration: Iterable[Dict[str, str]] = ()) -> Dict[str, Any]:
    """Diagnose both versions, check invariants, and assemble the report.

    ``changes`` is the polisher's own log: one ``{category, before, after}``
    entry per edit worth showing the author (``note`` optional).
    ``escalations`` lists argument- or structure-level problems noticed
    but deliberately not fixed here (they belong to the voice module).
    ``calibration`` is the defensive-writing ledger: one ``{before, after,
    decision, warrant}`` entry per qualifier the polisher kept, scoped,
    removed, or consolidated, where ``warrant`` names the evidence the
    hedge answers to, or says why it answers to none
    (references/defensive-writing.md).
    """
    if level not in LEVELS:
        raise ValueError("unknown level %r" % level)
    lang = lang or detect_language(original)
    d0, d1 = diagnose(original, lang), diagnose(polished, lang)
    inv = check_invariants(original, polished, lang, protected_terms)
    remaining = [
        {k: f[k] for k in ("id", "category", "severity", "excerpt", "hint")}
        for f in d1["findings"] if f["severity"] in ("remove", "revise")
    ]
    status = inv["status"]
    if d1["must_remove"]:
        status = "FAIL"
    report = {
        "protocol": "POLISH_REPORT_V1",
        "language": lang,
        "catalog": has_catalog(lang),
        "level": level,
        "before": summary(d0),
        "after": summary(d1),
        "changes": [dict(c) for c in changes],
        "remaining": remaining,
        "invariants": {"status": inv["status"], "failures": inv["failures"], "warnings": inv["warnings"],
                       "length_ratio": inv["length_ratio"]},
        "status": status,
        "notice": POLISH_NOTICE,
    }
    if "hedges" in inv["checks"]:
        report["invariants"]["hedges"] = dict(inv["checks"]["hedges"])
    calibration = [dict(c) for c in calibration]
    if calibration:
        report["calibration"] = calibration
    if escalations:
        report["escalations"] = list(escalations)
    limitations = supported_note(lang) + list(limitations)
    if limitations:
        report["limitations"] = limitations
    return report


def validate_polish_report(report: Dict[str, Any]) -> List[str]:
    """Return a list of problems; empty means the report is usable."""
    if not isinstance(report, dict):
        return ["report is not an object"]
    errors = ["missing field: %s" % k for k in REQUIRED if k not in report]
    if errors:
        return errors
    if report["protocol"] != "POLISH_REPORT_V1":
        errors.append("protocol must be POLISH_REPORT_V1")
    if not isinstance(report["language"], str) or not re.match(r"^[a-z]{2,3}$", report["language"]):
        errors.append("language must be an ISO 639 code such as en, zh, ja: %r" % report["language"])
    elif report["catalog"] != has_catalog(report["language"]):
        errors.append("catalog must say whether ppe.patterns has a catalog for %r" % report["language"])
    if report["level"] not in LEVELS:
        errors.append("unknown level: %r" % report["level"])
    if report["status"] not in STATUSES:
        errors.append("unknown status: %r" % report["status"])
    if report["notice"] != POLISH_NOTICE:
        errors.append("notice must be ppe.POLISH_NOTICE, unchanged")
    for i, c in enumerate(report["changes"]):
        missing = [k for k in CHANGE_REQUIRED if k not in c] if isinstance(c, dict) else CHANGE_REQUIRED
        if missing:
            errors.append("changes[%d] missing %s" % (i, missing))
        elif c["category"] not in CATEGORIES:
            errors.append("changes[%d] unknown category %r" % (i, c["category"]))
    inv = report["invariants"]
    if not isinstance(inv, dict) or inv.get("status") not in STATUSES:
        errors.append("invariants.status must be PASS, REVIEW, or FAIL")
    else:
        if inv["status"] == "FAIL" and report["status"] != "FAIL":
            errors.append("a failed invariant check must make the report FAIL")
        if inv["status"] == "REVIEW" and report["status"] == "PASS":
            errors.append("an invariant check needing review cannot be reported as PASS")
    after = report["after"]
    if isinstance(after, dict) and after.get("must_remove") and report["status"] != "FAIL":
        errors.append("chat residue left in the polished text must make the report FAIL")
    calibration = report.get("calibration", [])
    for i, c in enumerate(calibration):
        missing = [k for k in CALIBRATION_REQUIRED if k not in c] if isinstance(c, dict) else CALIBRATION_REQUIRED
        if missing:
            errors.append("calibration[%d] missing %s" % (i, missing))
            continue
        if c["decision"] not in CALIBRATION_DECISIONS:
            errors.append("calibration[%d] unknown decision %r" % (i, c["decision"]))
        if not str(c["warrant"]).strip():
            errors.append("calibration[%d] needs a warrant: the evidence the hedge answers to, or why none" % i)
    hedges = inv.get("hedges") if isinstance(inv, dict) else None
    if isinstance(hedges, dict) and hedges.get("polished", 0) < hedges.get("original", 0):
        logged = any(isinstance(c, dict) and c.get("category") in DEFENSIVE_CATEGORIES for c in report["changes"])
        if not calibration and not logged:
            errors.append("hedges fell from %d to %d with no calibration entry or defensive-category change "
                          "saying why; a hedge the evidence needs must never be dropped silently"
                          % (hedges["original"], hedges["polished"]))
    return errors
