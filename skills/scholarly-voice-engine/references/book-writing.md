# Book Writing

Loaded when the task is book/chapter-scale (see `SKILL.md` §Book vs. article
routing). Book writing is not simply enlarged article prose — it requires
maintaining a coherent argument across chapters that each do different work.

## Model

```text
book thesis
  ↓
chapter function
  ↓
chapter-level argument
  ↓
cross-chapter recurrence
  ↓
intellectual progression
```

## Supported book genres

```text
research monograph | theoretical monograph | historical monograph |
academic textbook | edited-volume chapter | research handbook chapter |
interdisciplinary book
```

Each inflects the model above: a textbook chapter foregrounds pedagogical clarity
over novelty; an edited-volume or handbook chapter must stand alone while still
citing the volume's shared frame if one exists; a research/theoretical/historical
monograph is where full chapter-role differentiation (below) matters most.

## Monograph continuity state

Maintain this compactly across the whole book-writing task — update it as each
chapter is drafted, and consult it before drafting the next one:

```yaml
book_thesis:
central_concepts:
terminology:
major_claims:
chapter_roles:
recurring_examples:
unresolved_questions:
cross_references:
argument_progression:
```

This state exists to prevent: redefining the same term differently in different
chapters; repeating the same literature review; contradicting an earlier
chapter's claim; and re-announcing the book's contribution in every chapter as if
for the first time. When you don't have visibility into earlier chapters (e.g.,
only drafting one chapter of an already-written book), ask the user for a summary
of the relevant continuity state rather than inventing one.

For the detailed mechanics behind this state — separate concept/claim/
evidence/chapter ledgers, terminology-drift auditing, and what to do when
earlier chapters aren't visible to you — see `continuity-ledger.md`.

## Chapter roles

Writing style shifts by function — do not apply one uniform chapter template
throughout the book:

```text
foundation chapter    — establishes terms and stakes; more expository
conceptual chapter    — argument-dense, definition-heavy
historical chapter    — narrative evidence, chronology-driven
methods chapter        — precise, low rhetorical intensity
case chapter           — empirical/textual detail, evidence-first
comparative chapter    — explicit comparative logic across cases
mechanism chapter      — causal/generative argument, close to
                          Analytical-Mechanistic or Experimental-Mechanistic voice
synthesis chapter      — draws threads from prior chapters together
implications chapter   — extends the argument outward (policy, theory, practice)
conclusion             — synthesis and explicit scope of the claim
```

## Book-level voice variation while preserving identity

```text
Introduction → broad intellectual framing
Theory chapter → conceptual density
Historical chapter → narrative evidence
Case chapter → empirical detail
Conclusion → synthesis and scope
```

The core voice profile (primary/secondary/depth from `voice-engine.md`) should
stay recognizable across this variation — local register shifts, authorial
identity does not.

## Chapter openings and conclusions

Do not let every chapter open with "This chapter examines..." or close with
"In conclusion, this chapter has shown..." — that regularity is a generic-AI
tell at book scale (see `human-scholarly-prose.md`). Vary the opening move by
what the chapter actually needs:

```text
a historical scene | a conceptual problem stated cold | an empirical puzzle |
a theoretical contradiction | a case observation | a direct continuation from
the previous chapter's handoff
```

and the closing move similarly:

```text
a bounded synthesis of what this chapter established | a deliberately
unresolved tension carried forward | a conceptual handoff naming the next
chapter's task | a historical transition | an empirical implication
```

Not every chapter needs the same closing move — a case chapter earning an
unresolved tension and a synthesis chapter earning a bounded summary is
correct variation, not inconsistency.

## Practical drafting notes

- Before drafting a new chapter, restate (to yourself) the continuity state and
  this chapter's role; only then apply the discipline module and voice profile.
- When a concept recurs, refer back to its earlier definition rather than
  redefining it, unless the chapter's explicit purpose is to refine or complicate
  that definition (note this explicitly when it happens).
- Track unresolved questions deliberately left open for a later chapter — do not
  let the writing imply false closure.
- Cross-references should name the earlier chapter's specific claim, not just
  gesture at "as discussed above."
