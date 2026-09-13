# Workflow recipe: revise-manuscript

**Not a Skill.** For when a complete (or near-complete) manuscript already
exists and needs structural/argument revision, optionally with a target
venue.

## When to select this recipe

Trigger example: "Improve this paper and tell me where to submit."
Not for: a single-sentence/paragraph polish that scholarly-voice-engine can
do alone (rule 17) -- only select this recipe when revision is genuinely
structural or multi-stage.

## Stages

```
read manuscript
  |
  v
scholarly-voice-engine: structural audit
  (argument architecture, section balance, claim calibration)
  |
  v
citation/argument integrity check
  (scholarly-voice-engine; flags unverified citations per VOICE_OUTPUT_V1)
  |
  v
scholarly-corpus-builder     (only for evidence gaps the audit surfaced,
                               or evidence that has gone stale)
  |
  v
journal-fit-engine           (only if a target venue was supplied or asked for)
  |
  v
scholarly-voice-engine: targeted adaptation
  (only the sections the audit + journal fit actually flagged)
```

## Explicit non-goal

scholarly-voice-engine must not rewrite the whole manuscript "while it's in
there" -- only the sections the audit flagged and, if a venue is targeted,
the sections journal-fit-engine's style context calls for (rule 22, rule 56).

## Failure propagation

If scholarly-corpus-builder returns `PARTIAL` evidence, the final adaptation
must state which claims remain evidence-gapped rather than presenting the
revision as fully evidence-verified (rule 73).
