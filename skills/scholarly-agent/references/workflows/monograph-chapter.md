# Workflow recipe: monograph-chapter

**Not a Skill.** For drafting/revising a single chapter within an
already-established book project (continuity state already exists).

## When to select this recipe

Trigger example: "Draft chapter 4 using the continuity state we built."
Distinguish from `book-project.md` (initial, whole-book setup).

## Stages

```
load existing CONTINUITY_STATE_V1
  |
  v
scholarly-corpus-builder    (only for evidence this specific chapter needs
                              that the existing corpus doesn't cover)
  |
  v
scholarly-voice-engine: chapter drafting/revision
  (must honor the existing voice_contract and terminology ledger --
   not re-derive style choices per chapter)
  |
  v
continuity state update
  (append to concept/claim/evidence/chapter ledgers; do not overwrite
   prior chapters' entries)
```

## Reuse rule

Never rebuild the book's research corpus from scratch for a single chapter
(rule 47). Query the existing corpus profile first; only extend it for
genuinely new evidence needs.
