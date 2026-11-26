# Workflow recipe: paper-from-notes

**Not a Skill.** Variant of `paper-from-idea.md` for when the user already has
raw notes, an outline, or partial data rather than a one-line idea.

## When to select this recipe

Trigger example: "Here are my notes/data from the study, turn this into a
manuscript." Distinguish from `paper-from-idea.md` (no material yet) and
`revise-manuscript.md` (a full draft already exists).

## Stages

```
interpret notes/outline/data
  |
  v
scholarly-corpus-builder      (fill evidence gaps the notes don't cover;
                                skip fields the notes already establish)
  |
  v
scholarly-voice-engine
  argument architecture from notes + research design matrix
  |
  v
draft manuscript (VOICE_OUTPUT_V1)
  |
  v
journal-fit-engine  (optional)
```

## Reuse rule

If the notes already contain a clear research question, method, and
contribution, do not re-derive them via corpus building -- pass them directly
into `VOICE_REQUEST_V1.research_idea` and only invoke scholarly-corpus-builder
for genuinely missing evidence (rule 47, rule 50).

## Completion states

Same state model as `paper-from-idea.md`. Report which parts of the notes
were used verbatim vs. required corpus-builder supplementation, so the user
can see where the draft's evidence actually came from.
