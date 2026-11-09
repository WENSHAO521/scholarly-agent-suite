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

Write it the way a handling editor at the target journal would: formal,
direct, collegial. No hedging about AI or simulation in the body.

```
Re: "<manuscript title>"

Dear <author name, or "Dear Author">,

Thank you for submitting your manuscript to <journal, or "the journal">.
It has been read by <n> reviewers, whose reports are below. Based on their
advice and my own reading, my decision is: Major revision.

<2-4 sentences: what the paper does, what the reviewers valued, what stands
between it and publication.>

To be considered further, the revision needs to address:
 1. <change> (Reviewer 1, point 1; Reviewer 2, point 4)
 2. ...

The reviewers differ on <topic>: Reviewer 1 ..., Reviewer 3 .... My view: ...

The reviewers also make suggestions you may take up or decline with a reason:
<minor points>

Please include a point-by-point response with your revision.

Sincerely,
Handling Editor

---
Submission readiness: <Ready to submit | Ready after the listed changes | Needs substantial work first>
<one or two sentences on why>

Prepared by Scholarly Agent before submission; not a decision by any journal.
```

Keep the letter about the paper, not the authors. Required changes are
numbered so the response letter can answer each one. Sign as "Handling
Editor", never as a real person or a named journal's editor.

### Submission readiness

The part after the rule is for the author, not part of the journal-style
letter. Map the decision to a readiness verdict: `accept` or
`minor-revision` → "Ready to submit" (minor items are what real reviewers
ask for anyway); `major-revision` → "Ready after the listed changes";
`reject-resubmit`, `reject`, `desk-reject` → "Needs substantial work first"
(for a desk rejection, name the kind of venue that would fit). This is what
gives an author justified confidence: a clear signal when the paper is
ready, and a concrete list when it is not. `prv.decision` records the verdict in
the decision's `readiness` field (`prv.READINESS`).
