# Defensive writing (防禦性寫作)

Defensive writing is prose written to protect the author from criticism
rather than to tell the reader something. It hedges claims the evidence
already carries, apologizes for the work before presenting it, fences off
objections nobody raised, and justifies routine choices at length. Editors
and reviewers read it as a lack of confidence, and it does a second,
quieter kind of damage: when every sentence is qualified, the reader can no
longer see which uncertainties are real. A defensive text hides its genuine
limitations among the ritual ones.

This pass removes the ritual and keeps the real uncertainty, stated once,
specifically, on the claim it qualifies. It runs at every level (see the
level table below) as pass 2 of `polishing-passes.md`.

Sections: [the warrant test](#warrant-test), [the six forms](#six-forms),
[procedure](#procedure), [writing a limitation that is not defensive](#limitations),
[levels](#levels), [genre and discipline](#genre), [the calibration ledger](#ledger),
[when it is not a wording problem](#escalate).

<a id="warrant-test"></a>

## The warrant test: real uncertainty or defence?

For every qualifier (hedge, caveat, disclaimer, apology, justification) ask
one question: **which specific source of uncertainty does it answer to?**

| Warrant | Example | What stays |
|---|---|---|
| Design ceiling: the design cannot establish more | observational data, so association, not effect | "is associated with", once, on that claim |
| Statistical uncertainty | a CI that crosses zero, low power, one estimate of several that is fragile | the interval or the specific fragility, not a vague "may" |
| Scope: sample, population, period, setting | one country, one cohort, 2010-2015 | a scope phrase: "in this cohort", "among firms that ..." |
| Measurement | a proxy, self-report, a validated-elsewhere scale | name the measure's weakness where the claim depends on it |
| Contested interpretation | the literature disagrees; another reading fits the evidence | attribute it: "on X's reading (cite) ..." / "a competing reading would ..." |
| Extrapolation beyond the data | out-of-sample prediction, policy implication | mark the step, not every sentence around it |

- **A warrant exists:** keep exactly one qualifier, put it on the claim it
  qualifies, and make it specific. "These results may suggest a possible
  link" becomes "In this cohort, exposure is associated with a 12 % higher
  risk (95 % CI 3-21 %)".
- **No warrant:** remove the qualifier and state the claim at the strength
  the evidence already supports. A well-supported descriptive or formal
  claim is stated plainly.
- **Not sure:** keep it, and record it in the ledger with `decision: kept`
  and the doubt in `note`.

**Removing a defensive hedge never licenses a stronger claim.** The claim
type stays where `modules/scholarly-voice-engine/references/argument-and-claims.md#claim-calibration`
puts it: an association does not become a cause, "is consistent with" does
not become "confirms". The pass makes the warranted uncertainty visible; it
does not delete it, and it does not invent confidence the design cannot
support.

<a id="six-forms"></a>

## The six forms

Category names are the ones `ppe.patterns` and `ppe.diagnose` report
(`python -m ppe diagnose FILE --defensive` lists only these).

### 1. `defensive-hedge` -- qualifiers that answer to nothing

"It could be argued that", "seems to suggest", "may suggest a possible",
"it is not impossible that", "arguably", "in some sense"; 「從某種意義上說」
「或可認為」「似乎可能」「不能說沒有」.

> It could be argued that the reform may have contributed to some extent to
> the decline in turnout.
> -> The reform coincided with an 8-point fall in turnout (Table 3); the
> design cannot separate it from the concurrent redistricting.

Either make the argument and own it, or attribute it with a citation. The
rewrite keeps the real limit (the design) and drops the three empty ones.

### 2. `hedge-blanket` and `hedge-stack` -- hedging everything

Structural (`ppe.diagnose`): a sentence with three or more hedges
(`struct-hedge-pileup`), or a paragraph in which at least three quarters of
the sentences are hedged (`struct-hedge-blanket`). Phrase-level stacks
("may potentially", 「可能或許」) stay in `hedge-stack`.

Sort the paragraph's claims by how well they are supported. State the
well-supported ones plainly; keep one hedge on each claim that has a
warrant. The remaining hedges then mean something.

### 3. `preemptive-caveat` -- conceding before anyone objects

"While this study has some limitations, ...", "It should be noted that",
"These results should be interpreted with caution", "Further research is
needed", "Admittedly, ...", "This is not to say that"; 「本研究也存在一些
不足」「結果應謹慎看待」「有待進一步研究」「當然，……」「這並不是說」.

- A caveat that names a real limitation moves to where it bears on a result
  (or to the limitations section) and is said **once**, specifically
  (see [limitations](#limitations)).
- "Interpret with caution" says nothing until it says which result, why,
  and what reading is still safe.
- "Further research is needed" is cut, or replaced by the study that would
  settle the question: which data, which design.
- A concession ("Of course", 「當然」「誠然」) stays only if it answers an
  objection a reader would actually raise.

### 4. `disclaimer` -- fencing off the reader

"This review is by no means exhaustive", "does not claim to be
comprehensive", "beyond the scope of this paper" (repeated); 「本文無意
窮盡」「限於篇幅」「不在本文討論範圍」.

Replace the negative fence with a positive scope statement:

> This review is by no means exhaustive.
> -> This review covers the 64 randomized trials published 2010-2024 that
> report a mortality endpoint.

> 限於篇幅，本文無意窮盡所有案例。
> -> 本文分析 2015 至 2020 年間的三個縣市案例。

"We do not claim causality" is different: it rules out a reading readers
would actually make, so it stays (once, as a scope statement).

### 5. `apologetic-framing` -- apologizing for the work

"We humbly suggest", "this modest attempt", "a preliminary effort", "we
apologize"; 「拋磚引玉」「不揣淺陋」「才疏學淺」「不當之處在所難免，敬請
批評指正」「筆者學識有限」「粗淺的嘗試」.

Delete the apology and state the contribution at its real size, without
size words: neither "modest" nor "groundbreaking" (the latter is already
`inflated-vocabulary`). Reviewers judge the size; the text describes the
work.

### 6. `over-justification` -- defending routine choices

"It is reasonable to assume that", "there is good reason to believe",
"as is widely accepted", "for the sake of rigour", "to ensure the
robustness of", "carefully designed"; 「為了保證研究的嚴謹性」「為嚴謹
起見」「有理由認為」「學界普遍認為」「不難看出」.

- Give the reason itself instead of announcing that one exists.
- A standard procedure gets a citation, not a defence; justify only the
  choices a reader in the field would question.
- An appeal to consensus is replaced by the sources; if there are no
  sources, there is no consensus to appeal to.
- Adverbs do not make a procedure rigorous: describe the procedure.

<a id="procedure"></a>

## Procedure

1. **Diagnose.** `python -m ppe diagnose FILE --defensive` (or
   `ppe.diagnose.defensive_findings(diagnose(text))`). Note `hedge_rate`, the
   share of hedged sentences: it is a prompt to look, not a target.
2. **List the claims** in each flagged paragraph and their claim type
   (`argument-and-claims.md#claim-calibration`).
3. **Run the warrant test** on every qualifier, flagged or not, in those
   paragraphs. The catalog misses some defensive phrasing and flags some
   warranted phrasing; the test decides, not the match.
4. **Decide** for each qualifier: `kept` (warranted, already well placed),
   `scoped` (warranted, rewritten to sit on the exact claim and name its
   source), `removed` (no warrant), or `consolidated` (several scattered
   caveats about the same limitation become one specific statement).
5. **Rewrite**, keeping every protected item (pass 0) and every claim type.
6. **Log** each decision in the report's `calibration` ledger
   ([below](#ledger)), then verify (`polishing-passes.md#verify`). The hedge
   count will usually fall; the ledger is what makes that `REVIEW` warning
   explainable.

<a id="limitations"></a>

## Writing a limitation that is not defensive

A real limitation, stated well, reads as command of the material, not as
weakness. Four parts, in one or two sentences:

1. **What** the limitation is, concretely (not "some limitations").
2. **Which result** it bears on.
3. **Which way** it would push that result, if known (towards zero,
   upward, unknown).
4. **What still holds** despite it.

> Our study has several limitations, and the results should be interpreted
> with caution.
> -> Turnout is self-reported, which usually inflates levels but not the
> difference between groups; the gap in Table 2 is therefore the more
> reliable estimate.

> 本研究存在一定的局限，結論需謹慎看待。
> -> 樣本僅來自北部三所大學，對技職體系學生的推論需另行驗證；但兩種
> 回饋方式之間的差異在三校方向一致。

Say each limitation once. A limitation already stated in the limitations
section is not repeated as a hedge in every paragraph of the discussion.

<a id="levels"></a>

## Levels

| Level | Defensive pass covers |
|---|---|
| `light` | apologetic framing, disclaimers, defensive hedges and stacked hedges inside a sentence |
| `standard` (default) | everything in light, plus pre-emptive caveats, over-justification, and hedge blankets within a paragraph |
| `deep` | everything in standard, plus consolidating caveats about the same limitation within a paragraph into one specific statement, and deleting a caveat that repeats a limitation the text already states in full elsewhere |

No level moves a caveat into another section: that is a structural edit.
If a manuscript's limitations are scattered across sections and need one
home, record it under `escalations` (voice module).

<a id="genre"></a>

## Genre and discipline

- **Humanities and interpretive work.** "May be read as", "on this
  reading", "a competing reading would suggest" are warranted when the
  claim is interpretive: interpretation is argued, not measured. Keep them;
  remove only the ones stacked on top ("it could perhaps be argued that
  this may be read as ...").
- **Medicine and health.** Reporting guidelines (CONSORT, STROBE, PRISMA)
  require a limitations section. Keep the section; make each item specific
  ([limitations](#limitations)). Never remove "does not establish efficacy"
  or similar design-ceiling language.
- **Law.** "Arguably" and "the better view is" can be terms of art for a
  contested point of doctrine. Keep them where the point is contested and
  attributed.
- **Mathematics and formal work.** "Holds under the stated hypotheses" is
  not a hedge; it is the theorem's scope. A proof needs no "we believe".
- **Chinese academic conventions.** Self-deprecating formulae
  (「拋磚引玉」「不當之處，敬請指正」) can belong in a preface, a 後記, or
  an acknowledgment, where the venue expects them; record them as
  `kept_because` there. In the body of an article they are removed.
- **Response-to-reviewer letters.** Courtesy ("We thank the reviewer for
  this point") is not defensive and stays. What gets cut is the grovelling
  and the over-explanation that hides whether the change was made.
- **The author's considered stance.** If the author tells you a hedge is
  deliberate (a cautious field, an anticipated hostile reviewer), it stays,
  with `kept` and the reason in the ledger.

<a id="ledger"></a>

## The calibration ledger

POLISH_REPORT_V1 carries an optional `calibration` list
(`polish-report.md`). One entry per qualifier the pass examined in a
flagged paragraph:

```json
{"before": "These results may possibly suggest a potential link",
 "after": "In this cohort, exposure is associated with a 12 % higher risk",
 "decision": "scoped",
 "warrant": "observational cohort: design ceiling is association; CI 3-21 % excludes zero"}
```

- `decision`: `kept`, `scoped`, `removed`, or `consolidated`.
- `warrant`: the evidence the qualifier answers to, or, for `removed`, why
  it answers to none ("descriptive count from Table 1; nothing uncertain").
  Never empty.
- `ppe.report.validate_polish_report` rejects a report whose hedge count fell
  with neither a `calibration` entry nor a logged change in a defensive
  category: a hedge the evidence needs must never disappear silently.

In the hand-back, summarize the ledger in one or two lines ("removed nine
defensive hedges and two apologies; kept three hedges on the causal claims,
each now naming the design limit"), not entry by entry.

<a id="escalate"></a>

## When it is not a wording problem

Sometimes the hedging is defensive because the claim is too big for the
evidence: the author senses the overreach and qualifies it everywhere. The
fix is a smaller claim stated plainly, which is an argument change. Do not
make it here. Keep the hedges, record the claim under `escalations` ("the
abstract claims an effect the cross-sectional design cannot carry; the
hedging throughout the discussion follows from that"), and tell the author
it needs a revision pass (voice module).
