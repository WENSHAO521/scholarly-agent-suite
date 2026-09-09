# Editing Modes

Separates *how much* an edit is allowed to change (intensity) from *what kind*
of task is being performed (output mode). Always determine both before
touching the text — applying argument-reconstruction intensity to a request
for proofreading is as much a failure as applying surface-only intensity to a
request to rebuild a broken argument.

## Editing intensity

```yaml
SURFACE_EDIT:
  touches: grammar, clarity, local wording, sentence-level transitions
  does_not_touch: paragraph order, section structure, claim placement,
    evidence placement, the argument itself
  use_when: user asks to proofread, polish, or "clean up" without asking for
    structural change

STRUCTURAL_EDIT:
  touches: paragraph order, section flow, where a claim or piece of evidence
    sits, section-level pacing
  does_not_touch: the central thesis, concept hierarchy, or citation-claim
    attachments (see citation-integrity.md)
  use_when: user asks to reorganize, tighten flow, or fix a section that
    "doesn't read well" structurally

ARGUMENT_RECONSTRUCTION:
  touches: central thesis, concept hierarchy, mechanism, counterargument
    handling, contribution logic — the argument itself, not just its
    presentation
  does_not_touch: underlying data/results/findings/legal authority/historical
    fact (never touched by any intensity level — see citation-integrity.md,
    claim-calibration.md)
  use_when: user explicitly asks to rebuild, strengthen, or rethink the
    argument, not merely its prose
```

Default to the lightest intensity consistent with the request; when unclear
whether a deeper pass is wanted, perform the lighter one and say plainly what
a deeper pass would additionally change, rather than guessing upward.

## Output modes

```yaml
draft:
  from notes/outline to prose; use [VERIFY SOURCE], [INSERT EMPIRICAL
  RESULT], [DEFINE DATASET] placeholders rather than inventing evidence to
  create a false sense of completeness
revise:
  source text exists; preserve substantive meaning unless the user asks for
  an argument change; track major changes where useful to the user
polish:
  SURFACE_EDIT by default
compress:
  remove redundancy, generic framing, duplicated citations, excessive
  qualifiers — never cut theory/evidence the argument depends on
expand:
  add reasoning, evidence structure, counterargument, or concept
  clarification — never merely pad with synonyms or repeated framing
restructure:
  STRUCTURAL_EDIT
rebuild_argument:
  ARGUMENT_RECONSTRUCTION
journal_adapt:
  apply journal-style-adaptation.md's target profile within its stated
  boundary (framing/structure, never substance)
book_chapter:
  apply book-writing.md and continuity-ledger.md
author_voice:
  apply author-voice-calibration.md, prioritizing the user's established
  voice per its precedence rule
disciplinary_convert:
  re-render the same underlying content for a different discipline's
  argument architecture and claim conventions (e.g., adapting an empirical
  finding's framing from a psychology audience to a public-policy audience)
  — the underlying evidence and claim strength do not change, only the
  disciplinary framing and argument shape
```

## Choosing intensity from the request's phrasing

```text
"fix typos" / "proofread" / "tighten this sentence"        → SURFACE_EDIT
"this doesn't flow" / "reorganize" / "the intro is buried"  → STRUCTURAL_EDIT
"the argument doesn't hold together" / "rethink this claim" /
"strengthen the theory"                                      → ARGUMENT_RECONSTRUCTION
```

If a user's request names a specific surface complaint but the underlying
problem is actually structural or argumentative (e.g., "this sentence is
confusing" when the real issue is that two contradictory claims are both
present), name that finding explicitly rather than silently performing a
deeper edit than requested, or silently patching only the surface and leaving
the real problem in place.
