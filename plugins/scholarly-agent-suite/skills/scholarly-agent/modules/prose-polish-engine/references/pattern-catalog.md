# English pattern catalog

The phrasing `ppe.patterns.EN_PATTERNS` flags, grouped by category, with
the rewrite each one usually needs. Severity: `remove` (never in a
manuscript), `revise` (almost always a template), `watch` (fine in
moderation; act when it recurs or does no work). The list is deliberately
short and literal. Anything not on it can still be templated; anything on
it can still be right in context.

Chinese patterns are in `chinese-academic-prose.md`. Defensive writing
(defensive hedges, hedge blankets, pre-emptive caveats, disclaimers,
apologetic framing, over-justification) has its own page with English and
Chinese examples: `defensive-writing.md`.

## chat-residue (remove)

"Certainly!", "Sure,", "Here is the revised version", "I hope this helps",
"Let me know if you …", "Feel free to …", "As an AI language model".
Delete. None of it was ever addressed to a reader of the paper.

## stock-connective (watch)

"Furthermore", "Moreover", "Additionally", "In addition", "Notably,",
"Importantly,".

> Moreover, the effect was larger in rural districts.
> -> The effect was larger in rural districts.
> -> The effect was larger in rural districts, where turnout was already low.

Name the relation (`polishing-passes.md`, pass 4) or delete the word.

## empty-emphasis (revise / watch)

"It is important to note that", "It is worth noting that", "plays a
crucial / pivotal / vital / key role", "cannot be overstated", "of
paramount importance", "underscores".

> It is important to note that the sample excludes migrants.
> -> The sample excludes migrants, so the estimates speak only to citizens.

> Trust plays a crucial role in compliance.
> -> Where trust in tax officials is low, compliance falls by a third (Table 2).

## inflated-vocabulary (revise / watch)

"delve into", "tapestry", "intricate interplay", "ever-evolving
landscape", "in the realm of", "multifaceted", "pivotal", "showcase",
"leverage", "harness the power of", "seamless", "navigate the complexities
of", "groundbreaking", "unprecedented", "revolutionize".

> This paper delves into the multifaceted landscape of platform labour.
> -> This paper examines how platforms set drivers' pay and hours.

Keep a word when it is a term of art in the field and used in that sense.

## formulaic-frame (revise / watch)

"In today's rapidly evolving world", "This study aims to", "sheds light
on", "paves the way for", "opens new avenues", "provides valuable
insights", "highlights the importance of".

> In today's rapidly changing world, remote work has become increasingly
> important. This study aims to shed light on its effects on promotion.
> -> Remote workers are promoted less often than office-based colleagues
> doing the same job. This article asks why.

## stock-summary (watch)

"In conclusion,", "In summary,", "Overall,", "To sum up,", "Taken
together,". In a section titled Conclusion the heading already says it.
At the end of a body paragraph, cut the recap unless it adds a step.

## hedge-stack (revise / watch)

"may potentially", "could possibly", "might perhaps", "to some extent".
One hedge, sized to the evidence. Say to what extent, or drop "to some
extent".

## contrast-template (watch / revise)

"not only … but also" as a habit; "It is not just X, it is Y."

> It is not just a technical problem; it is a political one.
> -> The problem is political: who pays for the upgrade decides whether it happens.

## nominalization (watch)

"the implementation of", "the utilization of", "the examination of",
"utilize". Use the verb.

## Defensive writing (revise / watch)

Six categories, with the warrant test that decides each case, are on
their own page: [defensive-writing.md](defensive-writing.md). The English
catalog flags, among others:

| Category | Examples |
|---|---|
| defensive-hedge | "it could be argued that", "seems to suggest", "may suggest a possible", "it is not impossible that", "arguably" |
| preemptive-caveat | "While this study has some limitations, ...", "It should be noted that", "should be interpreted with caution", "further research is needed", "Admittedly," |
| disclaimer | "is by no means exhaustive", "does not claim to be comprehensive", "beyond the scope of this paper" (when it recurs) |
| apologetic-framing | "we humbly suggest", "this modest attempt", "a preliminary effort", "we apologize" |
| over-justification | "it is reasonable to assume that", "as is widely accepted", "for the sake of rigour", "carefully designed" |

> While this study has some limitations, it could be argued that the
> findings may suggest a possible role for peer feedback.
> -> In the two courses studied, students who received peer feedback
> revised more (Table 2); the courses were not randomized, so this is an
> association.

## Structural habits (from `ppe.diagnose`)

| id | Category | What fired | Usual fix |
|---|---|---|---|
| `struct-paragraph-opener` | repeated-opener | several paragraphs open with the same word, or more than one with the same connective | start with the paragraph's real subject |
| `struct-sentence-opener-run` | repeated-opener | three sentences in a row open the same way ("This … This … This …") | vary by putting the new information first |
| `struct-uniform-rhythm` | uniform-rhythm | five or more sentences in a paragraph with nearly identical length | let the key claim stand short; let the qualified explanation run long |
| `struct-triplet` | triplet-habit | "X, Y, and Z" (counts once three appear in the text) | keep only if there are three things |
| `struct-dash` | dash-habit | em dashes or `--` (counts once more than three appear) | comma, colon, parentheses, or a new sentence |
| `struct-hedge-pileup` | hedge-blanket | three or more hedges in one sentence | keep the one the evidence needs, on the claim it qualifies |
| `struct-hedge-blanket` | hedge-blanket | at least three quarters of a paragraph's sentences (three or more) are hedged | state the well-supported claims plainly so the remaining hedges mark real uncertainty |

## Not on the list on purpose

"however", "therefore", "thus", "first … second …", "we argue", "this
suggests": these do real work. Flag them only when they recur so often
they stop doing it (the paragraph-opener check catches most cases).
