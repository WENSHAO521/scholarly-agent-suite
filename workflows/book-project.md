# Workflow recipe: book-project

**Not a Skill.** For a full academic monograph/book project spanning
multiple chapters and sessions.

## When to select this recipe

Trigger example: "Help me build and write a research monograph."

## Stages

```
book thesis
  |
  v
scholarly-corpus-builder: research corpus (book-scale)
  |
  v
scholarly-voice-engine: book architecture
  (chapter map, argument spine, book-writing genre policy)
  |
  v
CONTINUITY_STATE_V1 initialized
  (voice contract, concept/claim/evidence/chapter ledgers, terminology,
   open questions)
  |
  v
chapter drafting/revision (repeat per chapter, continuity state updated
                            after each chapter)
  |
  v
continuity audit
  (before considering the book "complete" for this session -- check the
   voice contract and ledgers are internally consistent across chapters)
```

## Explicit non-goal

journal-fit-engine is normally excluded from this recipe entirely -- books
are not journal submissions (rule 24). If the user separately asks about a
book proposal / publisher fit, that is out of scope for the Suite's current
five specialists (see rule 131, "future extensibility").

## Privacy

No private book content is written into any Suite-level file. Continuity
state stays in the user's own session/project artifacts, never in this
repository (rule 35, rule 113).
