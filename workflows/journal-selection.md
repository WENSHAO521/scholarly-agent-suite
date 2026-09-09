# Workflow recipe: journal-selection

**Not a Skill.** For a manuscript that is already reasonably final and the
deliverable is purely "where should this go," not further writing.

## When to select this recipe

Trigger example: "Find Q1/Q2 SSCI journals with no mandatory APC for this
paper." Not for a request that also wants the manuscript rewritten -- that is
`revise-manuscript.md` or `target-journal-adaptation.md`.

## Stages

```
manuscript profile (MANUSCRIPT_PROFILE_V1 -- from the user or a quick
                     scholarly-voice-engine audit, not a full rewrite)
  |
  v
journal-fit-engine: candidate generation
  |
  v
scholarly-corpus-builder: current candidate evidence
  (journal profiles / JOURNAL_STYLE_CONTEXT_V1 for shortlisted candidates
   only -- not the whole field)
  |
  v
journal-fit-engine: ranking + hard-constraint filtering
  |
  v
submission ladder (ordered candidates with fit rationale)
```

## Explicit non-goal

scholarly-voice-engine is not invoked to rewrite the manuscript unless the
user explicitly asks (rule 23). This recipe's deliverable is a ranked
shortlist plus rationale, not prose changes.

## Constraint conflicts

If hard constraints (e.g. "Q1 only" + "no APC" + a narrow subfield) leave no
candidate, report `NO CANDIDATE SATISFIES ALL HARD CONSTRAINTS` and suggest
the smallest relaxation rather than silently dropping a constraint (rule 112).
