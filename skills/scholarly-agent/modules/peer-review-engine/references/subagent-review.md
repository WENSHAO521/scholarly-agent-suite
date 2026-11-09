# Reviewers as subagents

Real peer review gets its value from reviewers who have not seen each
other's views. Subagents reproduce that: each reviewer starts from a clean
context with only its own briefing.

## When to dispatch

Use subagents when all hold (the router's delegation gate,
`modules/adaptive-model-router/references/delegation-policy.md`):

- The host can dispatch subagents and the user has not asked for a single
  agent.
- There are free slots for the panel (2 reviewers by default; 3 for a full
  panel, which the router allows "exceptionally, for distinct demonstrably
  valuable roles"; distinct lenses qualify).
- The manuscript can be passed to each subagent within its context limit.

Otherwise use the sequential single-model fallback below. Never simulate
dispatch, and never describe single-model reports as independent reviewers.

## The briefing packet

`prv.panel.subagent_packet(brief, manuscript_ref, journal_criteria)` builds it
in the router's minimal-packet shape:

```text
OBJECTIVE: Review this manuscript as Reviewer R2 (lens: theory). Return one REVIEW_REPORT_V1.
RELEVANT INPUT: <manuscript, or a path to it>; journal criteria: <scope, article type, stated review criteria or "none supplied">
CONSTRAINTS: read-only; do not delegate; you have not seen and must not ask for other reviews;
             ground every major or fatal concern in a location and evidence; do not invent citations;
             you are a role, not a named person; this is a simulated pre-submission review.
LENS FOCUS: <the lens's checks from reviewer-lenses.md>
EXPECTED OUTPUT: REVIEW_REPORT_V1 JSON (fields in review-report.md), then nothing else.
```

Give every reviewer the same manuscript text and the same journal criteria.
Differences between reports should come from the lens, not from the inputs.

## Model choice

Reviewers do the hard reading; use a strong standard-tier model (the
router's Sol role) at a reasoning effort suited to the paper. The editor
(root) should be at least as capable as the reviewers. Do not escalate to
the expert tier merely because reviewers disagree; disagreement is a normal
output of review, recorded in the decision, not a reasoning failure.

## Integration (editor = root)

1. Collect all reports before reading any of them closely, so the first
   report read does not anchor the rest.
2. Validate each with `prv.reports.validate_report`; send a malformed report
   back to its reviewer once, or drop it and record the gap.
3. Check `independence.saw_other_reports` is `false` for every report.
4. Decide per [editorial-decision.md](editorial-decision.md).
5. If a reviewer failed or timed out, decide on the remaining reports and
   say the panel was smaller than planned. One replacement reviewer at most.

## Sequential single-model fallback

When subagents are unavailable:

1. Write R1's report completely, then treat it as frozen.
2. Start R2 from the manuscript and its lens brief only. Do not re-read or
   refer to R1's report while writing R2.
3. Repeat for R3, then switch to the editor role and read all reports.
4. Set `independence.mode` to `sequential-single-model` on every report and
   add to the decision's `limitations`: "Reviews were written in sequence by
   one model; they are not independent in the way separate reviewers are."
