# Workflow recipe: peer-review-simulation

**Not a Skill.** For a pre-submission review of a complete manuscript: what
an editor and two or three independent reviewers would likely say, the
decision that follows, and what must change. Optionally followed by the
revision, the response letter, and one second-round check.

## When to select this recipe

Trigger examples: "Review my paper like a reviewer at this journal would
and tell me what the editor would decide." / "Simulate peer review, then
help me revise and write the response letter."
Not for: "review my paper" meaning a single editing pass (voice alone), or
a peer review only (no revision, no venue work), which is a single-module
request to peer-review-engine without this recipe.

## Stages

```
read manuscript; reuse or build MANUSCRIPT_PROFILE_V1
  |
  v
journal-fit-engine          (only if a target journal is named and its scope,
                             article types, or review criteria are not in hand)
  |
  v
peer-review-engine: editor desk screen
  |  desk-reject -> stop: report reasons (journal-fit-engine may suggest other venues)
  v
peer-review-engine: panel of 2-3 lenses -> independent REVIEW_REPORT_V1s
  (isolated reviewer subagents when the host can dispatch, under
   adaptive-model-router's delegation caps; otherwise sequential single-model)
  |
  v
peer-review-engine: editor -> EDITORIAL_DECISION_V1 + letter + response matrix
  |
  v
scholarly-corpus-builder    (only for evidence gaps reviewers named, e.g. missing literature)
  |
  v
scholarly-voice-engine      (only if the user asks: revise the flagged sections,
                             draft the response letter from the matrix)
  |
  v
peer-review-engine: second-round check of revision + letter (once)
```

## Explicit non-goal

No stage predicts a real journal's decision or an acceptance probability,
and the voice module revises only what the decision letter requires, not
the whole manuscript (rule 22). Reviewers never write the revision; the
editor never rewrites the paper.

## Failure propagation

If fewer reviewers report than planned, or reviews were written
sequentially by one model, the decision's `limitations` say so and the
assembled output carries them. If a second round still leaves fatal or
major items unaddressed, report that; do not start a third round (the
dispatcher's bounded repair loop).
