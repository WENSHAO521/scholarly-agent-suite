"""peer-review-engine runtime (prv): panel, report validation, decision,
response matrix, second-round check -- and the two new protocols."""
import copy
from pathlib import Path

import pytest
from schema_lite import ValidationError, validate_file

from prv import DECISIONS, READINESS, REVIEW_NOTICE
from prv.decision import DecisionError, check_revision, decide, desk_decision, desk_screen, response_matrix
from prv.panel import PanelError, build_panel, subagent_packet
from prv.reports import validate_report

ROOT = Path(__file__).resolve().parents[3]
PROTOCOLS = ROOT / "skills" / "scholarly-agent" / "protocols"


def concern(rid, n, severity, fixable=True, category="methods"):
    return {
        "id": "%s-C%d" % (rid, n), "severity": severity, "category": category,
        "location": "Section 4, Table 2", "issue": "issue %d" % n,
        "evidence": "Table 2 shows ...", "request": "do %s-%d" % (rid, n), "fixable": fixable,
    }


def report(rid, lens, rec, concerns=(), mode="isolated-subagent"):
    return {
        "protocol": "REVIEW_REPORT_V1", "reviewer_id": rid, "lens": lens,
        "summary": "The paper studies diffusion.", "strengths": ["original data"],
        "concerns": list(concerns), "questions_for_authors": [],
        "recommendation": rec, "confidence": "moderate",
        "independence": {"mode": mode, "saw_other_reports": False},
        "limitations": [],
    }


# --- panel -------------------------------------------------------------------

def test_default_panels_by_article_type():
    lenses = lambda p: [b.lens for b in p]  # noqa: E731
    assert lenses(build_panel({"article_type": "empirical"})) == ["methods", "theory", "literature"]
    assert lenses(build_panel({"article_type": "theory"}, size=2)) == ["theory", "literature"]
    assert lenses(build_panel({"article_type": "commentary"})) == ["field", "generalist", "devils-advocate"]
    assert lenses(build_panel({})) == ["theory", "methods", "literature"]


def test_medical_panel_swaps_in_statistics_and_ethics():
    panel = build_panel({"article_type": "empirical", "discipline": "medicine-health"})
    assert [b.lens for b in panel] == ["methods", "statistics", "ethics-integrity"]
    assert [b.reviewer_id for b in panel] == ["R1", "R2", "R3"]


def test_panel_size_and_override_rules():
    with pytest.raises(PanelError):
        build_panel({"article_type": "empirical"}, size=5)  # router delegation cap
    with pytest.raises(PanelError):
        build_panel({}, size=2, lenses=["methods", "methods"])
    with pytest.raises(PanelError):
        build_panel({}, size=2, lenses=["methods", "astrology"])
    panel = build_panel({}, size=2, lenses=["statistics", "field"])
    assert panel[0].reason == "editor's choice"


def test_subagent_packet_is_isolated_and_complete():
    brief = build_panel({"article_type": "empirical"})[1]
    packet = subagent_packet(brief, "manuscript.docx", "Aims: public administration theory and practice")
    for needle in ("OBJECTIVE:", "Reviewer R2", "lens: theory", "must not ask for other reviews",
                   "do not invent citations", "not a named person", '"saw_other_reports": false'):
        assert needle in packet
    assert "R1" not in packet and "R3" not in packet
    assert "none supplied" in subagent_packet(brief, "m.pdf")


# --- reports -----------------------------------------------------------------

def test_valid_report_passes_and_matches_schema():
    r = report("R1", "methods", "major-revision", [concern("R1", 1, "major")])
    assert validate_report(r) == []
    validate_file(r, PROTOCOLS / "review-report.schema.json")


@pytest.mark.parametrize("mutate,needle", [
    (lambda r: r.pop("summary"), "missing field: summary"),
    (lambda r: r.update(lens="vibes"), "unknown lens"),
    (lambda r: r["independence"].update(saw_other_reports=True), "saw_other_reports"),
    (lambda r: r["concerns"][0].update(id="R9-C1"), "must start with R1-"),
    (lambda r: r["concerns"][0].update(evidence=" "), "has no evidence"),
    (lambda r: r["concerns"][0].update(severity="catastrophic"), "unknown severity"),
    (lambda r: r.update(recommendation="maybe"), "unknown recommendation"),
])
def test_invalid_reports_are_caught(mutate, needle):
    r = report("R1", "methods", "major-revision", [concern("R1", 1, "major")])
    mutate(r)
    assert any(needle in e for e in validate_report(r)), validate_report(r)


def test_schema_rejects_a_report_that_saw_other_reviews():
    r = report("R1", "methods", "accept")
    r["independence"]["saw_other_reports"] = True
    with pytest.raises(ValidationError):
        validate_file(r, PROTOCOLS / "review-report.schema.json")


# --- decision ----------------------------------------------------------------

def test_one_fatal_concern_outweighs_a_majority_of_lenient_votes():
    reports = [
        report("R1", "methods", "reject", [concern("R1", 1, "fatal", fixable=False, category="validity")]),
        report("R2", "theory", "minor-revision", [concern("R2", 1, "minor")]),
        report("R3", "literature", "minor-revision", [concern("R3", 1, "minor")]),
    ]
    d = decide(reports)
    validate_file(d, PROTOCOLS / "editorial-decision.schema.json")
    assert d["decision"] == "reject"
    assert d["consensus"] == "majority"
    assert any(x["topic"] == "overall recommendation" for x in d["disagreements"])
    assert d["review_notice"] == REVIEW_NOTICE


@pytest.mark.parametrize("severity,fixable,track,expected,readiness", [
    ("fatal", True, True, "reject-resubmit", "needs-substantial-work"),
    ("fatal", True, False, "major-revision", "ready-after-changes"),
    ("major", True, True, "major-revision", "ready-after-changes"),
    ("minor", True, True, "minor-revision", "ready-to-submit"),
])
def test_rule_table(severity, fixable, track, expected, readiness):
    d = decide([report("R1", "methods", "major-revision", [concern("R1", 1, severity, fixable)]),
                report("R2", "theory", "major-revision")], has_reject_resubmit_track=track)
    assert d["decision"] == expected
    assert d["readiness"] == readiness


def test_every_decision_has_a_readiness_verdict_and_the_notice_avoids_simulation_wording():
    assert set(READINESS) == set(DECISIONS)
    assert "simulat" not in REVIEW_NOTICE.lower()
    assert "not a decision by any journal" in REVIEW_NOTICE


def test_minor_items_move_to_optional_under_major_revision():
    d = decide([report("R1", "methods", "major-revision", [concern("R1", 1, "major"), concern("R1", 2, "minor")]),
                report("R2", "theory", "major-revision")])
    assert [rc["concern_ids"] for rc in d["required_changes"]] == [["R1-C1"]]
    assert d["optional_suggestions"] == ["R1-C2: do R1-2"]


def test_dismissal_needs_reason_and_known_id():
    reports = [report("R1", "methods", "major-revision", [concern("R1", 1, "major")]),
               report("R2", "theory", "minor-revision")]
    with pytest.raises(DecisionError):
        decide(reports, dismissed={"R1-C1": ""})
    with pytest.raises(DecisionError):
        decide(reports, dismissed={"R7-C1": "not ours"})
    d = decide(reports, dismissed={"R1-C1": "asks for a different study; out of scope"})
    assert d["decision"] == "accept" and d["dismissed"][0]["concern_id"] == "R1-C1"
    assert any("unusual" in l for l in d["limitations"])


def test_editor_may_be_stricter_with_reason_never_more_lenient():
    reports = [report("R1", "methods", "major-revision", [concern("R1", 1, "major")]),
               report("R2", "theory", "major-revision", [concern("R2", 1, "major")])]
    with pytest.raises(DecisionError):
        decide(reports, stricter={"decision": "minor-revision", "reason": "I like it"})
    with pytest.raises(DecisionError):
        decide(reports, stricter={"decision": "reject"})
    d = decide(reports, stricter={"decision": "reject-resubmit", "reason": "together the fixes amount to a new study"})
    assert d["decision"] == "reject-resubmit" and d["rule_decision"] == "major-revision"
    assert "stricter" in d["basis"]


def test_sequential_single_model_reviews_are_disclosed():
    d = decide([report("R1", "methods", "accept", mode="sequential-single-model"),
                report("R2", "theory", "accept", mode="sequential-single-model")])
    assert d["consensus"] == "unanimous"
    assert any("not independent" in l for l in d["limitations"])


def test_invalid_or_duplicate_reports_are_refused():
    with pytest.raises(DecisionError):
        decide([])
    with pytest.raises(DecisionError):
        decide([report("R1", "methods", "accept"), report("R1", "theory", "accept")])
    bad = report("R1", "methods", "accept")
    bad["independence"]["saw_other_reports"] = True
    with pytest.raises(DecisionError):
        decide([bad])


def test_desk_screen():
    passed = desk_screen(in_scope=True)
    assert passed["send_to_review"] and passed["decision"] is None
    unknown = desk_screen(in_scope=None)
    assert unknown["send_to_review"] and unknown["limitations"]
    screen = desk_screen(in_scope=False, hard_requirement_failures=["no data availability statement"])
    assert not screen["send_to_review"] and len(screen["reasons"]) == 2
    d = desk_decision(screen)
    validate_file(d, PROTOCOLS / "editorial-decision.schema.json")
    assert d["decision"] == "desk-reject" and d["stage"] == "desk"
    assert d["readiness"] == "needs-substantial-work"
    with pytest.raises(DecisionError):
        desk_decision(passed)


# --- author side ---------------------------------------------------------------

def _major_decision():
    return decide([
        report("R1", "methods", "major-revision", [concern("R1", 1, "fatal"), concern("R1", 2, "major")]),
        report("R2", "theory", "major-revision", [concern("R2", 1, "major"), concern("R2", 2, "minor")]),
    ], has_reject_resubmit_track=False)


def test_response_matrix_lists_every_required_change_then_optional():
    d = _major_decision()
    rows = response_matrix(d)
    assert [r["item"] for r in rows] == ["RC1", "RC2", "RC3", "OS1"]
    assert rows[0]["severity"] == "fatal" and all(r["status"] == "todo" for r in rows)
    assert rows[-1]["required"] is False


@pytest.mark.parametrize("statuses,expected", [
    ({"RC1": "addressed", "RC2": "rebutted", "RC3": "addressed"}, "accept"),
    ({"RC1": "not-addressed", "RC2": "addressed", "RC3": "addressed"}, "reject"),
    ({"RC1": "addressed", "RC2": "not-addressed", "RC3": "addressed"}, "major-revision"),
    ({"RC1": "partially-addressed", "RC2": "addressed", "RC3": "addressed"}, "major-revision"),
])
def test_second_round(statuses, expected):
    d = _major_decision()
    out = check_revision(d, statuses)
    validate_file(out, PROTOCOLS / "editorial-decision.schema.json")
    assert out["decision"] == expected and out["stage"] == "revision"
    assert out["readiness"] == READINESS[expected]
    assert all(rc["status"] not in ("addressed", "rebutted") for rc in out["required_changes"])


def test_minor_leftovers_give_minor_revision():
    d = decide([report("R1", "methods", "minor-revision", [concern("R1", 1, "minor"), concern("R1", 2, "minor")]),
                report("R2", "theory", "minor-revision")])
    assert check_revision(d, {"RC1": "addressed", "RC2": "not-addressed"})["decision"] == "minor-revision"


def test_revision_rounds_are_unlimited_and_stop_only_at_a_final_decision():
    d = _major_decision()
    assert "round" not in d  # first decision: round 1 by default
    current = check_revision(d, {"RC1": "addressed", "RC2": "addressed", "RC3": "partially-addressed"})
    assert current["round"] == 2 and current["decision"] == "major-revision"
    assert [rc["item"] for rc in current["required_changes"]] == ["RC3"]
    for expected_round in range(3, 12):  # no cap on rounds
        current = check_revision(current, {"RC3": "partially-addressed"})
        validate_file(current, PROTOCOLS / "editorial-decision.schema.json")
        assert current["round"] == expected_round and current["stage"] == "revision"
        assert "last revision round" not in current["basis"]
    with pytest.raises(DecisionError):
        check_revision(current, {})  # a later round still needs a status for each open item
    final = check_revision(current, {"RC3": "addressed"})
    assert final["decision"] == "accept" and final["round"] == 12 and final["required_changes"] == []
    with pytest.raises(DecisionError):
        check_revision(final, {})  # nothing follows an accept
    with pytest.raises(DecisionError):
        check_revision(d, {"RC1": "addressed"})  # missing items
    rejected = copy.deepcopy(d)
    rejected["decision"] = "reject"
    with pytest.raises(DecisionError):
        check_revision(rejected, {})
