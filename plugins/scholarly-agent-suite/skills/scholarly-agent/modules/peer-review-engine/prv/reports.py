"""REVIEW_REPORT_V1 validation without a JSON Schema dependency. Mirrors
protocols/review-report.schema.json plus the cross-field rules a schema
cannot express (concern ids prefixed by the reviewer id, grounded major and
fatal concerns, independence)."""

from __future__ import annotations

import re
from typing import Any, Dict, List

from prv import CATEGORIES, LENSES, RECOMMENDATIONS, SEVERITIES

REQUIRED = ["protocol", "reviewer_id", "lens", "summary", "strengths", "concerns",
            "recommendation", "confidence", "independence"]
CONCERN_REQUIRED = ["id", "severity", "category", "location", "issue", "evidence", "request", "fixable"]


def validate_report(report: Dict[str, Any]) -> List[str]:
    """Return a list of problems; empty means the report is usable."""
    errors: List[str] = []
    if not isinstance(report, dict):
        return ["report is not an object"]
    for key in REQUIRED:
        if key not in report:
            errors.append("missing field: %s" % key)
    if errors:
        return errors
    if report["protocol"] != "REVIEW_REPORT_V1":
        errors.append("protocol must be REVIEW_REPORT_V1")
    rid = report["reviewer_id"]
    if not isinstance(rid, str) or not re.match(r"^R\d+$", rid):
        errors.append("reviewer_id must look like R1, R2, ...")
    if report["lens"] not in LENSES:
        errors.append("unknown lens: %r" % report["lens"])
    if not str(report["summary"]).strip():
        errors.append("summary is empty")
    if report["recommendation"] not in RECOMMENDATIONS:
        errors.append("unknown recommendation: %r" % report["recommendation"])
    if report["confidence"] not in ("low", "moderate", "high"):
        errors.append("confidence must be low, moderate, or high")
    ind = report["independence"]
    if not isinstance(ind, dict) or ind.get("mode") not in ("isolated-subagent", "sequential-single-model"):
        errors.append("independence.mode must be isolated-subagent or sequential-single-model")
    elif ind.get("saw_other_reports") is not False:
        errors.append("independence.saw_other_reports must be false")
    seen = set()
    for i, c in enumerate(report["concerns"] or []):
        where = "concerns[%d]" % i
        if not isinstance(c, dict):
            errors.append("%s is not an object" % where)
            continue
        missing = [k for k in CONCERN_REQUIRED if k not in c]
        if missing:
            errors.append("%s missing %s" % (where, missing))
            continue
        if not str(c["id"]).startswith("%s-" % rid):
            errors.append("%s id %r must start with %s-" % (where, c["id"], rid))
        if c["id"] in seen:
            errors.append("%s duplicate id %r" % (where, c["id"]))
        seen.add(c["id"])
        if c["severity"] not in SEVERITIES:
            errors.append("%s unknown severity %r" % (where, c["severity"]))
        if c["category"] not in CATEGORIES:
            errors.append("%s unknown category %r" % (where, c["category"]))
        if not isinstance(c["fixable"], bool):
            errors.append("%s fixable must be true or false" % where)
        if c["severity"] in ("fatal", "major"):
            for key in ("location", "evidence"):
                if not str(c[key]).strip():
                    errors.append("%s is %s but has no %s" % (where, c["severity"], key))
    return errors
