# Workflow recipe: target-journal-adaptation

**Not a Skill.** For when a target journal is already chosen (or picked in
this same session via `journal-selection.md`) and the manuscript needs to be
adapted to it.

## When to select this recipe

Trigger example: "Improve this paper for Journal X." Distinguish from
`journal-selection.md` (no chosen journal yet, deliverable is a shortlist)
and `revise-manuscript.md` (general revision, no specific venue).

## Stages

```
journal-fit-engine: confirm/refresh target journal profile
  |
  v
scholarly-corpus-builder      (only if the journal's style/requirement
                                evidence is stale -- rule 49)
  |
  v
journal-fit-engine: produce JOURNAL_STYLE_CONTEXT_V1
  (official_requirements kept separate from observed_patterns -- rule 34)
  |
  v
scholarly-voice-engine: targeted adaptation
  (structure, section policies, citation style, length -- driven by the
   style context, not a full rewrite from scratch)
```

## Freshness handling

If the journal profile is `STALE` and the user's request implies current
constraints matter (e.g. asking about APC or word limits), refresh via
scholarly-corpus-builder before adapting. If the profile is merely
non-current historical style evidence with no current-fact dependency,
skip the refresh (rule 49).
