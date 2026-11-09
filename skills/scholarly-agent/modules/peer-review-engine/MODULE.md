<!-- Module of the scholarly-agent Skill (native module, added in v2.1.0).
     Loaded on demand by ../../SKILL.md; paths below are relative to this module's directory. -->

> **Module `peer-review-engine`** -- part of the single `scholarly-agent` Skill. Load this file only when the
> dispatcher in `SKILL.md` selects this module. Sibling modules are at `modules/<name>/`.
> Paths such as `references/...` are relative to `modules/peer-review-engine/`.
>
> Scope: Pre-submission journal peer review of a manuscript, written the way real reviewers and editors write: an editor desk screen, a panel of independent reviewer reports (run as isolated subagents when the host can dispatch), and an editorial decision letter with required changes; then check a revision and response-to-reviewers letter against that decision. It gives authors the review they would likely get, early enough to act on it, without claiming to be any journal's decision.

# Peer Review Engine

Gives an author the review their manuscript is likely to get, early enough to
act on it. Three roles, kept apart on purpose:

```
Handling editor   desk screen -> picks the panel -> weighs reports -> decision letter
Reviewers (2-3)   each reads the manuscript alone, through one lens, and writes a report
Author side       response matrix -> revision -> second-round check (optional)
```

## Ecosystem position

```
Adaptive Model Router      how to execute (subagent dispatch, caps, validation)
Scholarly Corpus Builder   evidence a reviewer's concern needs checked
Scholarly Voice Engine     writes the revision and the response letter
Journal Fit Engine         the target journal's scope, article types, criteria
Peer Review Engine (this)  what reviewers and an editor would say, and what must change
```

Stay in lane. This module critiques and decides; it does not rewrite the
manuscript (voice), choose journals (journal fit), or retrieve literature
(corpus). A reviewer who says "the literature on X is missing" names the gap;
the corpus module, not the reviewer, finds and verifies the sources.

## When to use

- "Review my paper like a reviewer at *Journal X* would." / "幫我審稿" / "投稿前審稿"
- "What would the editor decide?" / "Give me reviewer comments before I submit."
- "Check whether my revision answers the reviewers." (second round)
- A workflow stage: the dispatcher's `pre-submission-review` workflow
  recipe (review, then revision and response letter).

Not for: a one-paragraph polish (voice), "is my paper good?" with no
manuscript to read, or reviewing someone else's confidential submission (see
Integrity).

## Workflow

1. **Intake.** Read the manuscript once. Build or reuse a
   `MANUSCRIPT_PROFILE_V1` (discipline, article type, methods, contribution).
   Note the target journal if given; ask journal fit for its scope, article
   types, and stated review criteria only if they are not already in hand.
   Without a target journal, review against the discipline's general
   standards and say so.
2. **Desk screen (editor).** Out of scope, wrong article type, a hard
   requirement violated (length, structure, missing ethics or data
   statement), or an obvious fatal flaw → `desk-reject` with reasons. Stop
   here unless the user asks for full reviews anyway. See
   [references/editorial-decision.md](references/editorial-decision.md).
3. **Assemble the panel (editor).** Choose 2–3 reviewer lenses from
   [references/reviewer-lenses.md](references/reviewer-lenses.md) for this
   article type and discipline (`prv.panel.build_panel`). Lenses differ on
   purpose: methods, theory/contribution, literature/field, and optionally a
   devil's advocate. Never name or imitate a real person as a reviewer.
4. **Independent reviews.** Each reviewer produces a `REVIEW_REPORT_V1`
   ([references/review-report.md](references/review-report.md)). Independence
   is the point of having a panel:
   - **Host can dispatch subagents:** run each reviewer as an isolated,
     read-only leaf subagent with only its briefing packet
     (`prv.panel.subagent_packet`): the manuscript, its lens, the journal's
     criteria, and the report format. No reviewer sees another's report.
     Follow the router's delegation caps (default 2, exceptionally 3 agents;
     `modules/adaptive-model-router/references/delegation-policy.md`).
     See [references/subagent-review.md](references/subagent-review.md).
   - **No dispatch:** write the reports one at a time in the active model,
     finishing and freezing each before starting the next, and record
     `independence.mode = "sequential-single-model"`. Do not claim the
     reports are independent in the way separate reviewers would be.
5. **Editorial decision (editor).** Read all reports, uphold or dismiss each
   concern with a reason, record disagreements, and decide
   (`prv.decision.decide`). The decision follows from the upheld concerns,
   not from counting votes. Output an `EDITORIAL_DECISION_V1` and a decision
   letter. See [references/editorial-decision.md](references/editorial-decision.md).
6. **Hand back.** Give the author the letter, the reports, and a response
   matrix (`prv.decision.response_matrix`) listing every required change.
   The voice module drafts the revision and response letter if asked
   ([references/responding-to-reviewers.md](references/responding-to-reviewers.md)).
7. **Second round (optional).** Check the revision and response letter
   against the first-round decision: each required change is `addressed`,
   `partially-addressed`, `rebutted` (with a reasoned argument), or
   `not-addressed` (`prv.decision.check_revision`). One second round only,
   matching the dispatcher's bounded repair loop.

## Decision vocabulary

`desk-reject`, `reject`, `reject-resubmit`, `major-revision`,
`minor-revision`, `accept`. A first-round `accept` with no changes is rare
in real journals; if the rules produce it, say so and look again for
concerns the panel missed before reporting it.

## Integrity (non-negotiable)

`shared/integrity-policy.md` applies in full. In addition:

- **Real in voice, honest in origin.** Reports and the decision letter read
  exactly like a real journal's: an anonymous reviewer's first-person
  report, an editor's letter, no hedging about being an AI or a
  simulation in the body. The letter ends with one line, `prv.REVIEW_NOTICE`,
  saying it was prepared before submission and is not a decision by any
  journal. Never remove that line, never present the result as coming from
  the named journal or its editors, and never state an acceptance
  probability or a predicted outcome.
- **Confidence from substance.** The way to give an author confidence is a
  review that is specific and fair: real strengths named, every required
  change concrete, and a readiness verdict (see
  `references/editorial-decision.md`) that says plainly when a paper is
  ready to submit. Do not soften concerns to make the author feel better;
  a problem found here is one a journal's reviewers will not find first.
- **No impersonation.** Reviewers are roles ("Reviewer 2, methods"), never a
  real, named scholar or editor, living or dead.
- **Grounded criticism.** Every major or fatal concern points to a location
  in the manuscript and states the evidence for it. A reviewer may say a
  literature is missing; any specific work it suggests must be a real,
  checkable citation or be marked "to verify" (corpus module), never invented.
- **Confidential manuscripts.** If the user is a journal's reviewer and the
  manuscript is someone else's submission, stop and say: most journals and
  funders forbid uploading a confidential manuscript to an AI tool, and the
  reviewer remains responsible for their own report. Offer only help that
  does not need the manuscript (for example, how to structure a report) unless
  the user confirms the journal's policy allows it.
- **No gaming.** Do not help write a manuscript aimed at a reviewer's
  weaknesses, suggest reviewers with conflicts of interest, or draft fake
  reviews for any real submission system.

## Runtime code

`prv/` is a small standard-library package (Python 3.10+), importable by
putting this module's directory on `sys.path`:

- `prv.panel` -- `build_panel(manuscript_profile, size)` chooses reviewer
  lenses; `subagent_packet(brief, ...)` builds an isolated reviewer briefing.
- `prv.reports` -- `validate_report(report)` checks a `REVIEW_REPORT_V1`.
- `prv.decision` -- `desk_screen(...)`, `decide(reports, ...)` producing an
  `EDITORIAL_DECISION_V1`, `response_matrix(decision)`, and
  `check_revision(decision, responses)` for the second round.

The rules in `prv/` are deterministic bookkeeping over the reports. The
judgment (what is a fatal flaw, whether a rebuttal holds) stays with the
reviewer and editor roles.

## References

- `references/reviewer-lenses.md` -- the reviewer roles, what each checks, and which panel to pick per article type
- `references/review-report.md` -- `REVIEW_REPORT_V1` fields, severity scale, and a worked example
- `references/editorial-decision.md` -- desk screen, how concerns turn into a decision, letter template
- `references/subagent-review.md` -- running reviewers as isolated subagents, and the single-model fallback
- `references/responding-to-reviewers.md` -- response matrix, response letter, and the second-round check
