# Editorial decision (`EDITORIAL_DECISION_V1`)

Schema: `protocols/editorial-decision.schema.json`. Runtime:
`prv.decision.desk_screen`, `prv.decision.decide`.

The editor is the root role. In a multi-agent run, the root agent is the
editor and integrates the reviewer subagents' reports; it never delegates the
decision.

## 1. Desk screen

Before any review, check:

| Check | Desk reject when |
|---|---|
| Scope | The manuscript's question is outside the journal's stated aims and scope |
| Article type | The journal does not publish this article type |
| Hard requirements | Length far over the limit, required sections or statements missing (ethics approval, data availability, trial registration, reporting checklist) |
| Fatal flaw on reading | The central claim visibly cannot follow from the design |
| Integrity | Signs of plagiarism, duplicate publication, or fabricated references |

A desk rejection lists each reason with its evidence and, where useful, the
kind of venue that would fit (journal fit can suggest some).

## 2. From reports to a decision

The decision follows from **upheld concerns**, not from counting reviewer
votes. For each concern the editor records `upheld` or `dismissed`, and
every dismissal has a reason (for example: "R3-C2 asks for a different
paper; out of scope for this submission"). Then, as `prv.decision.decide`
applies:

| Upheld concerns | Decision |
|---|---|
| Any `fatal` with `fixable: false` | `reject` |
| Any `fatal` with `fixable: true` | `reject-resubmit` (or `major-revision` if the journal has no reject-and-resubmit track) |
| Any `major` | `major-revision` |
| Only `minor` | `minor-revision` |
| None | `accept` (flag as unusual on a first round) |

Rules around the table:

- The editor may decide **more strictly** than the table with a stated
  reason (for example, five major concerns that together amount to a new
  study). The editor may not decide more leniently than the upheld concerns
  allow; to be more lenient, dismiss concerns explicitly, with reasons.
- When reviewers disagree on a concern (one calls it fatal, another
  addresses the same point as fine), record it under `disagreements` with
  both positions and the editor's resolution. Never hide a split panel
  behind a single verdict.
- `consensus` reports the reviewers' own recommendations: `unanimous`,
  `majority`, or `split`. It is context for the author, not the basis of the
  decision.
- A concern raised by only one reviewer counts as much as one raised by all
  three, if upheld. Agreement is not evidence of correctness (the router's
  rule: do not majority-vote factual truth).

## 3. The decision letter

```
Simulated editorial decision -- not a prediction of any journal's actual decision.

Decision: Major revision

Summary of the assessment: <2-4 sentences: what the paper does, what the
panel valued, what stands between it and publication>

Required changes:
 1. <change> (R1-C1, R2-C4)
 2. ...

Points of disagreement among reviewers and how to handle them:
 - <topic>: R1 ..., R3 ...; the editor's view: ...

Optional suggestions: <minor points; the authors may decline with a reason>

Reviewer reports follow.
```

Keep the letter about the paper, not the authors. Required changes are
numbered so the response letter can answer each one.
