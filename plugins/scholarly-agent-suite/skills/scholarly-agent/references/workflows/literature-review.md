# Workflow recipe: literature-review

**Not a Skill.** For a standalone literature review / narrative review
deliverable (not the "background" section embedded inside another workflow).

## When to select this recipe

Trigger example: "Write a literature review on X for [discipline]."

## Stages

```
scholarly-corpus-builder: discipline/topic corpus + SCHOLARLY_PROFILE_V1
  (diversified sampling, explicit corpus-sufficiency gate -- do not proceed
   on a too-small or too-narrow sample without flagging it)
  |
  v
scholarly-voice-engine: review-genre argument architecture
  (synthesis structure, not per-paper summary chaining)
```

journal-fit-engine is not part of this recipe by default -- add
`journal-selection.md` afterward only if the user separately asks where to
publish the review.

## Evidence discipline

A review's entire value is evidence coverage. If corpus-builder's sample is
`PARTIAL` or biased (e.g. OA-only), that limitation must be stated in the
review's own scope section, not buried in a note to the user (rule 74, rule
106).
