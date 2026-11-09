"""The editor's bookkeeping: desk screen, decision from upheld concerns,
response matrix, and second-round check. See references/editorial-decision.md
and references/responding-to-reviewers.md.

The decision follows from upheld concerns, never from counting reviewer
recommendations. The editor may be stricter than the rules (with a reason);
to be more lenient the editor must dismiss concerns explicitly, with reasons.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Dict, Iterable, List, Optional

from prv import DECISIONS, SIMULATION_DISCLAIMER
from prv.reports import validate_report

# Strictness order, strictest first.
_ORDER = ["desk-reject", "reject", "reject-resubmit", "major-revision", "minor-revision", "accept"]


class DecisionError(ValueError):
    pass


def _stricter(a: str, b: str) -> str:
    return a if _ORDER.index(a) <= _ORDER.index(b) else b


def desk_screen(
    in_scope: Optional[bool],
    article_type_accepted: Optional[bool] = True,
    hard_requirement_failures: Iterable[str] = (),
    fatal_flaws: Iterable[str] = (),
    integrity_flags: Iterable[str] = (),
) -> Dict[str, Any]:
    """Editor's desk screen. `None` for scope means it could not be judged
    (no journal criteria); that is reported, not treated as a pass or fail."""
    reasons: List[str] = []
    limitations: List[str] = []
    if in_scope is False:
        reasons.append("outside the journal's stated aims and scope")
    elif in_scope is None:
        limitations.append("scope not assessed: no journal aims and scope supplied")
    if article_type_accepted is False:
        reasons.append("the journal does not publish this article type")
    reasons += ["hard requirement: %s" % r for r in hard_requirement_failures]
    reasons += ["fatal flaw on reading: %s" % r for r in fatal_flaws]
    reasons += ["integrity: %s" % r for r in integrity_flags]
    return {
        "send_to_review": not reasons,
        "decision": "desk-reject" if reasons else None,
        "reasons": reasons,
        "limitations": limitations,
    }


def _consensus(recs: List[str]) -> str:
    if not recs:
        return "split"
    top = Counter(recs).most_common(1)[0][1]
    if top == len(recs):
        return "unanimous"
    if top * 2 > len(recs):
        return "majority"
    return "split"


def decide(
    reports: List[Dict[str, Any]],
    dismissed: Optional[Dict[str, str]] = None,
    stricter: Optional[Dict[str, str]] = None,
    disagreements: Optional[List[Dict[str, Any]]] = None,
    has_reject_resubmit_track: bool = True,
    optional_suggestions: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Build an EDITORIAL_DECISION_V1 from reviewer reports.

    dismissed: {concern_id: reason} -- every concern not listed is upheld.
    stricter: {"decision": ..., "reason": ...} -- the editor's stricter call.
    disagreements: [{"topic", "positions", "editor_resolution"}] as recorded
      by the editor; reviewer splits on recommendation are added
      automatically when the panel is not unanimous.
    """
    if not reports:
        raise DecisionError("no reviewer reports to decide on")
    dismissed = dict(dismissed or {})
    problems = []
    for r in reports:
        problems += ["%s: %s" % (r.get("reviewer_id", "?"), e) for e in validate_report(r)]
    if problems:
        raise DecisionError("invalid report(s): " + "; ".join(problems))
    ids = [r["reviewer_id"] for r in reports]
    if len(set(ids)) != len(ids):
        raise DecisionError("duplicate reviewer ids: %s" % ids)

    all_concerns = {c["id"]: c for r in reports for c in r["concerns"]}
    unknown = sorted(set(dismissed) - set(all_concerns))
    if unknown:
        raise DecisionError("dismissed concern ids not in any report: %s" % unknown)
    missing_reason = sorted(cid for cid, why in dismissed.items() if not str(why).strip())
    if missing_reason:
        raise DecisionError("every dismissal needs a reason: %s" % missing_reason)
    upheld = [c for cid, c in all_concerns.items() if cid not in dismissed]

    severities = {c["severity"] for c in upheld}
    if any(c["severity"] == "fatal" and not c["fixable"] for c in upheld):
        rule = "reject"
    elif "fatal" in severities:
        rule = "reject-resubmit" if has_reject_resubmit_track else "major-revision"
    elif "major" in severities:
        rule = "major-revision"
    elif "minor" in severities:
        rule = "minor-revision"
    else:
        rule = "accept"

    decision = rule
    basis = "upheld concerns"
    if stricter:
        wanted = stricter.get("decision")
        if wanted not in DECISIONS or wanted == "desk-reject":
            raise DecisionError("stricter decision must be one of %s" % _ORDER[1:])
        if not str(stricter.get("reason", "")).strip():
            raise DecisionError("a stricter decision needs a reason")
        if _stricter(wanted, rule) != wanted:
            raise DecisionError(
                "%s is more lenient than the upheld concerns allow (%s); dismiss concerns with reasons instead"
                % (wanted, rule))
        decision = wanted
        if wanted != rule:
            basis = "editor stricter than upheld concerns: %s" % stricter["reason"]

    recs = [{"reviewer_id": r["reviewer_id"], "lens": r["lens"], "recommendation": r["recommendation"],
             "confidence": r["confidence"]} for r in reports]
    consensus = _consensus([r["recommendation"] for r in reports])
    disagreements = list(disagreements or [])
    if consensus != "unanimous":
        disagreements.append({
            "topic": "overall recommendation",
            "positions": ["%s (%s): %s" % (r["reviewer_id"], r["lens"], r["recommendation"]) for r in reports],
            "editor_resolution": "decision follows the upheld concerns: %s" % decision,
        })

    sev_rank = {"fatal": 0, "major": 1, "minor": 2}
    required = []
    for c in sorted(upheld, key=lambda c: (sev_rank[c["severity"]], c["id"])):
        if c["severity"] == "minor" and decision in ("major-revision", "reject-resubmit", "reject"):
            continue  # listed under optional suggestions instead
        required.append({"item": "RC%d" % (len(required) + 1), "concern_ids": [c["id"]],
                         "severity": c["severity"], "change": c["request"]})
    optional = list(optional_suggestions or [])
    optional += ["%s: %s" % (c["id"], c["request"]) for c in upheld
                 if c["severity"] == "minor" and decision in ("major-revision", "reject-resubmit", "reject")]

    limitations = []
    modes = {r["independence"]["mode"] for r in reports}
    if "sequential-single-model" in modes:
        limitations.append("Reviews were written in sequence by one model; they are not independent "
                           "in the way separate reviewers are.")
    for r in reports:
        limitations += ["%s: %s" % (r["reviewer_id"], l) for l in r.get("limitations", [])]
    if decision == "accept":
        limitations.append("No upheld concerns on a first round is unusual; re-check for missed issues "
                           "before relying on this outcome.")

    return {
        "protocol": "EDITORIAL_DECISION_V1",
        "stage": "after-review",
        "decision": decision,
        "basis": basis,
        "rule_decision": rule,
        "reviewer_recommendations": recs,
        "consensus": consensus,
        "upheld_concern_ids": sorted(c["id"] for c in upheld),
        "dismissed": [{"concern_id": k, "reason": v} for k, v in sorted(dismissed.items())],
        "required_changes": required,
        "optional_suggestions": optional,
        "disagreements": disagreements,
        "limitations": limitations,
        "simulation_disclaimer": SIMULATION_DISCLAIMER,
    }


def desk_decision(screen: Dict[str, Any]) -> Dict[str, Any]:
    """EDITORIAL_DECISION_V1 for a desk rejection from desk_screen()."""
    if screen.get("send_to_review"):
        raise DecisionError("the desk screen sent this manuscript to review")
    return {
        "protocol": "EDITORIAL_DECISION_V1",
        "stage": "desk",
        "decision": "desk-reject",
        "basis": "desk screen",
        "rule_decision": "desk-reject",
        "reviewer_recommendations": [],
        "consensus": "none",
        "upheld_concern_ids": [],
        "dismissed": [],
        "required_changes": [],
        "optional_suggestions": [],
        "disagreements": [],
        "desk_reasons": list(screen["reasons"]),
        "limitations": list(screen.get("limitations", [])),
        "simulation_disclaimer": SIMULATION_DISCLAIMER,
    }


def response_matrix(decision: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows = [{"item": rc["item"], "concern_ids": rc["concern_ids"], "severity": rc["severity"],
             "request": rc["change"], "response": "", "change_location": "", "status": "todo",
             "required": True} for rc in decision["required_changes"]]
    for i, text in enumerate(decision.get("optional_suggestions", []), 1):
        rows.append({"item": "OS%d" % i, "concern_ids": [], "severity": "minor", "request": text,
                     "response": "", "change_location": "", "status": "todo", "required": False})
    return rows


_REVISION_STATUSES = {"addressed", "partially-addressed", "rebutted", "not-addressed"}


def check_revision(decision: Dict[str, Any], statuses: Dict[str, str]) -> Dict[str, Any]:
    """Second-round check. `statuses` maps each required-change item (RC1,
    ...) to the status the editor assigned after reading the revision."""
    if decision.get("stage") == "revision":
        raise DecisionError("only one second round; report remaining problems instead of a third")
    if decision["decision"] in ("desk-reject", "reject", "accept"):
        raise DecisionError("no revision round follows a %s" % decision["decision"])
    items = {rc["item"]: rc for rc in decision["required_changes"]}
    missing = sorted(set(items) - set(statuses))
    if missing:
        raise DecisionError("no status for required change(s): %s" % missing)
    bad = {k: v for k, v in statuses.items() if v not in _REVISION_STATUSES}
    if bad:
        raise DecisionError("unknown status(es): %s" % bad)

    not_addr = [items[k] for k, v in statuses.items() if k in items and v == "not-addressed"]
    partial = [items[k] for k, v in statuses.items() if k in items and v == "partially-addressed"]
    if any(rc["severity"] == "fatal" for rc in not_addr):
        outcome, note = "reject", "a fatal concern was not addressed"
    elif any(rc["severity"] == "major" for rc in not_addr):
        outcome, note = "major-revision", "major concerns remain unaddressed; this is the last revision round"
    elif any(rc["severity"] != "minor" for rc in partial):
        outcome, note = "major-revision", "fatal or major concerns only partially addressed"
    elif not_addr or partial:
        outcome, note = "minor-revision", "minor items remain"
    else:
        outcome, note = "accept", "every required change addressed or convincingly rebutted"
    return {
        "protocol": "EDITORIAL_DECISION_V1",
        "stage": "revision",
        "decision": outcome,
        "basis": note,
        "rule_decision": outcome,
        "reviewer_recommendations": decision.get("reviewer_recommendations", []),
        "consensus": decision.get("consensus", "none"),
        "upheld_concern_ids": decision.get("upheld_concern_ids", []),
        "dismissed": decision.get("dismissed", []),
        "required_changes": [dict(rc, status=statuses[rc["item"]]) for rc in decision["required_changes"]
                             if statuses[rc["item"]] not in ("addressed", "rebutted")],
        "optional_suggestions": [],
        "disagreements": decision.get("disagreements", []),
        "limitations": decision.get("limitations", []),
        "simulation_disclaimer": SIMULATION_DISCLAIMER,
    }
