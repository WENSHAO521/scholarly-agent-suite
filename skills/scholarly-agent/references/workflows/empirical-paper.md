# Workflow recipe: empirical-paper

**Not a Skill.** Variant of `paper-from-idea.md` / `paper-from-notes.md` for a
data-driven empirical study (quantitative, qualitative, or mixed methods).

## When to select this recipe

Trigger example: "Write up these results as an empirical paper."

## Stages

```
scholarly-corpus-builder: prior-empirical-literature corpus
  + discipline profile (methods conventions, reporting norms)
  |
  v
scholarly-voice-engine: empirical argument architecture
  (hypotheses/RQs -> methods -> results -> discussion, per research-design
   matrix and discipline-specific reporting conventions)
  |
  v
journal-fit-engine  (optional)
```

## Claim calibration

Empirical papers carry the highest risk of statistical claim inflation (rule
12, `shared/integrity-policy.md`). scholarly-voice-engine's claim-calibration
pass must not upgrade correlational findings to causal language or overstate
effect sizes even when it would make the manuscript read more persuasively.
