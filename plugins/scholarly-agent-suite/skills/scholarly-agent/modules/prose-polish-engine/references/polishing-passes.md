# Polishing passes

Six passes, always in this order, each limited by the level the user
chose (`light`, `standard`, `deep`; see `../MODULE.md`). Doing them in order
matters: deleting residue, defensive qualifiers, and empty frames first often
makes a later connective or rhythm problem disappear on its own.

## 0. Protect (all levels)

Before changing anything, list what must survive unchanged:

- citations in any style: `(Smith, 2020)`, `Smith (2020)`, `[12]`, `[3-5]`,
  `（王，2021）`; footnote markers;
- DOIs, URLs;
- numbers, units, percentages, test statistics, p-values, confidence
  intervals, sample sizes;
- direct quotations (`“…”`, `"…"`, `「…」`, `『…』`) -- including the
  quoted source's own templated phrasing;
- formulas and inline math;
- the author's key terms and defined concepts (ask for them, or infer them
  from definitions in the text, and pass them as `protected_terms`).

`ppe.invariants.extract(text)` lists the mechanical ones. Terms are the
polisher's job: a concept the author defined must keep its exact wording
everywhere, even where a synonym would read more smoothly.

## 1. Residue (all levels)

Delete anything addressed to a chat user rather than a reader: "Certainly!",
"Here is the revised paragraph", "I hope this helps", 「當然可以」「以下是
潤色後的」「希望對你有幫助」, stray Markdown bold or headings in running
prose, and placeholder brackets the author did not intend to keep. Severity
`remove`: none of it may remain.

## 2. Defense (all levels)

Remove defensive writing: qualifiers that answer to no evidence, hedges on
every sentence, caveats nobody asked for, disclaimers, apologies for the
work, and justifications of routine choices. Keep real uncertainty, once,
on the claim it qualifies. Full procedure, the warrant test, and what each
level covers: [defensive-writing.md](defensive-writing.md).

- For every qualifier ask which source of uncertainty it answers to
  (design, statistics, scope, measurement, contested interpretation,
  extrapolation). None: remove it. One: keep one qualifier, specific and on
  the right claim.
- Removing a defensive hedge never makes the claim stronger than the design
  allows. "Is associated with" stays "is associated with".
- Log each decision in the report's `calibration` ledger.

## 3. Words (all levels)

- **Empty emphasis.** Delete the frame and keep the point: "It is important
  to note that X" -> "X". If the importance is real, show it in the claim:
  "X plays a crucial role in Y" -> "Without X, Y fails when …".
- **Inflated vocabulary.** "delve into", "tapestry", "landscape", "realm",
  "pivotal", 「賦能」「深度融合」「抓手」 -> the plain word, or the specific
  thing meant. Keep a technical term even if it is on the list (e.g.
  "landscape" in landscape ecology, "robust" for a robustness check).
- **Stacked hedges.** One hedge per claim, sized to the evidence: "may
  potentially suggest" -> "suggests" or "may indicate", whichever the
  evidence supports. Never remove the only hedge on a claim that needs it
  (pass 2 has already decided which hedges are warranted).

## 4. Connectives (all levels)

For every flagged connective ask: what is the actual relation between this
sentence and the last one?

| Relation | Then |
|---|---|
| none beyond "and also" | delete the connective; adjacency already says it |
| contrast, concession | keep or use the precise one ("however", "yet", "although", 「然而」「但」) |
| cause, consequence | say it ("because", "so", "as a result of the X", 「因此」「所以」) |
| example, specification | "for example", "in particular", 「例如」「具體而言」 or a colon |
| a new step in the argument | name the step: "A second mechanism is …", 「另一個機制是……」 |

Never replace one stock connective with another. If three paragraphs in a
row start with a connective, at least two of them usually need none.

## 5. Sentences (standard and deep)

- **Formulaic frames.** "In today's rapidly evolving world", 「隨著……的快速
  發展」「在……的背景下」: start where the specific problem starts. "This
  study aims to" -> "This article argues / estimates / shows".
- **Nominalizations.** "conduct an examination of" -> "examine";
  「對……進行了分析」 -> 「分析了……」.
- **Contrast templates.** "It is not just X, it is Y" / 「不僅……更……」
  used as a habit: state Y directly, and keep the contrast only where a
  reader would actually assume X.
- **Rhythm.** If every sentence in a paragraph runs the same length, let the
  sentence that carries the paragraph's main claim stand short, and let an
  explanation that needs a qualification run long. Do not break sentences
  at random to create variation.
- **Three-item lists.** Keep a list of three only when there are three
  things. Two is often the honest count; four is fine.

## 6. Paragraphs (standard: openers only; deep: all)

- **Openers.** Paragraphs and consecutive sentences that open the same way
  ("This …", 「此外，」) get a varied entry point: start with the subject
  that matters in that paragraph.
- **Recap endings** (deep). A last sentence that restates the paragraph
  ("Overall, this shows the importance of …", 「綜上所述……」) is cut unless
  it adds the step the next paragraph needs.
- **Sentence order inside a paragraph** (deep). Put the claim before its
  support when the paragraph is an argument, after it when it is a
  narrative of evidence. Do not move sentences between paragraphs; that is
  a structural edit (voice module).

<a id="verify"></a>

## Verify (all levels)

Run `ppe.report.build_polish_report(original, polished, level, changes, lang,
protected_terms, calibration=...)`:

- `invariants.status == "FAIL"` -- something protected was dropped, added, or
  altered. Restore it from the original. This is never acceptable in a
  returned text.
- `"REVIEW"` -- hedges or negations changed in number, or length moved
  outside 55-130 %. Check each: collapsing "may potentially" to "may" is
  fine; losing a "not" or turning "may" into "does" is not. A falling hedge
  count after the defense pass is expected; the `calibration` ledger shows
  each removed hedge had no warrant, and the validator rejects a report
  where hedges fell with no ledger entry and no logged defensive change.
- `after.must_remove > 0` -- residue survived; delete it.
- `remaining` findings at `revise` severity -- either fix them or add a
  `kept_because` (e.g. "'pivotal' is the author's defined term", "quoted
  from the interview transcript").

One repair pass after the first verification. If problems remain, return
the text with them listed under `limitations` rather than looping.

## What success looks like

`after.pattern_load` is `low` or the remaining findings each have a reason;
every hedge left marks an uncertainty the author could name, and every
limitation is said once, specifically;
`invariants.status` is `PASS`, or `REVIEW` with every warning explained;
and the author would recognize every sentence as saying what they meant.
A lower pattern count bought by changing meaning is a failure, not a
partial success.
