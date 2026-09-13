# Workflow recipe: theory-paper

**Not a Skill.** Variant of `paper-from-idea.md` for a primarily
theoretical/conceptual contribution (no empirical data collection).

## When to select this recipe

Trigger example: "Develop a theoretical framework paper on X." Distinguish
from `empirical-paper.md` (data-driven) -- theory papers usually need much
less corpus evidence and much more argument-architecture work.

## Stages

```
scholarly-corpus-builder    (light-touch: prior-theory landscape only,
                              not a full empirical-literature corpus)
  |
  v
scholarly-voice-engine: theory-paper argument architecture
  (proposition structure, boundary conditions, contribution-to-theory framing)
  |
  v
journal-fit-engine  (optional)
```

## Context economy

Theory papers are the clearest case for rule 50 ("no unnecessary live
retrieval"): most of the work is argument construction, not evidence
gathering. Do not invoke scholarly-corpus-builder for a full source-hierarchy
sweep when a handful of foundational-theory citations will do.

## Voice Engine emphasis for this recipe

scholarly-voice-engine's argument-architecture work for a theory paper
should emphasize, in roughly this order:

- construct definition
- theoretical mechanism
- proposition architecture
- causal/conceptual chain
- boundary conditions
- rival explanations
- theoretical contribution
- falsifiability, where applicable to the discipline/claim

This is a different emphasis than an empirical paper's argument work (see
`empirical-paper.md`), which centers method/results/claim-calibration
instead.

## Combining with target-journal-adaptation

When the target journal is already selected (not a discovery task), chain
this recipe with `target-journal-adaptation.md` rather than treating them
as alternatives:

1. Run this recipe's stages (light-touch prior-theory corpus, then
   argument-architecture writing above).
2. Run `target-journal-adaptation.md`'s stages against the already-chosen
   journal.

`scholarly-corpus-builder` keeps the light-touch, prior-theory-landscape
strategy from this recipe throughout -- adding the adaptation stage never
triggers a full empirical-literature corpus sweep. `journal-fit-engine`
performs adaptation only (confirm/refresh the profile, produce
`JOURNAL_STYLE_CONTEXT_V1`) -- since the venue is already chosen, it never
runs a fresh journal-discovery/shortlist pass.
