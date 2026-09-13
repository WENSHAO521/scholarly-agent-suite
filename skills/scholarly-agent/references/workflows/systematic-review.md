# Workflow recipe: systematic-review

**Not a Skill.** For a formal systematic review/meta-analysis deliverable
with an explicit search-and-screening protocol, distinct from a narrative
`literature-review.md`.

## When to select this recipe

Trigger example: "Conduct a systematic review of X following PRISMA."

## Stages

```
scholarly-corpus-builder: protocol-driven corpus construction
  (explicit inclusion/exclusion criteria, deduplication, source hierarchy,
   and an honest record of search coverage -- not just "a corpus")
  |
  v
scholarly-corpus-builder: corpus-stability / sufficiency check
  (rule 106's evidence-integrity gate applies with extra weight here --
   an underpowered or narrow search must be flagged, not hidden)
  |
  v
scholarly-voice-engine: systematic-review genre writing
  (PRISMA-style structure: search strategy, screening, synthesis, limitations)
```

journal-fit-engine is optional and added only on request, same as
`literature-review.md`.

## Non-negotiable disclosure

The search strategy's actual coverage (databases queried, date range,
language restriction, OA-only bias if applicable) must appear in the review's
own methods section -- this is a corpus provenance obligation, not an
optional acknowledgment (`shared/provenance-policy.md`).
