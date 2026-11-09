# Responding to reviewers

## Response matrix

`prv.decision.response_matrix(decision)` turns the decision's required
changes and the upheld concerns into one row per item:

| Column | Filled by |
|---|---|
| `item` | `RC1`, `RC2`, ... (required change) |
| `concern_ids` | The reviewer concerns behind it |
| `request` | What the editor asked for |
| `response` | The author's answer (voice module drafts if asked) |
| `change_location` | Where the manuscript changed |
| `status` | `todo` until answered |

Optional suggestions get rows too, marked `optional`.

## The response letter

The voice module drafts it from the completed matrix. Conventions:

- Answer every required change in order, quoting the request briefly.
- Say what changed and where (section, page, line), or why not.
- A **rebuttal** is legitimate: disagree with evidence and argument, never
  with tone. Concede what is right in the concern before disagreeing.
- Do not claim a change that was not made. The second-round check compares
  the letter with the manuscript.

## Second-round check

`prv.decision.check_revision(decision, responses)` takes, for each required
change, a status the editor role assigned after reading the revision and the
letter:

| Status | Meaning |
|---|---|
| `addressed` | The change was made and resolves the concern |
| `partially-addressed` | Some change, but the concern remains in part |
| `rebutted` | Not changed, with an argument the editor accepts |
| `not-addressed` | Not changed and no acceptable argument |

Outcome:

- Every item `addressed` or `rebutted` → `accept`.
- A fatal item `not-addressed` → `reject`.
- A major item `not-addressed` → `major-revision`, and the letter says this
  is the last revision round.
- A fatal or major item `partially-addressed` → `major-revision`.
- Only minor items `partially-addressed` or `not-addressed` → `minor-revision`.

Only one second round. If problems remain, say so plainly instead of
starting a third.
