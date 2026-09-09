# Integration

## Ecosystem responsibilities

```
Adaptive Model Router      → how to execute the task (model/reasoning/tool/delegation)
Scholarly Corpus Builder   → what scholarly evidence and journal profiles to acquire
Scholarly Voice Engine     → how the manuscript should be argued and written
Journal Fit Engine (this)  → which publication venues fit the manuscript
```

Keep these separated. Journal Fit Engine must not become a general
paper-writing Skill, must not duplicate the Router's execution-strategy
decisions, and must not perform full-manuscript rewrites itself.

## Scholarly Corpus Builder integration

When journal evidence is missing or stale, request only the specific missing
information rather than broad retrieval:

```
Need:
  recent Journal X profile
  2024–2026
  original research articles
  method + introduction architecture
```

Do not request hundreds of full texts by default — request what's needed to
fill the specific evidence gap (e.g. article-type distribution, method
profile, recent sample). Reuse cached profiles when `CURRENT` (see
[journal-profile.md](journal-profile.md)) instead of re-requesting.

## Scholarly Voice Engine integration

When the manuscript has a strong target journal, Journal Fit Engine may
return a compact adaptation-target profile for the Voice Engine to act on —
it does not perform the rewrite itself:

```yaml
target_voice_adjustment:
  contribution_position: earlier
  mechanism_visibility: higher
  policy_implication: medium
  sentence_density: moderate
```

or, in the fuller integration form:

```yaml
journal_target:
  genre: empirical_social_science
  contribution_position: early
  theory_density: medium_high
  policy_implications: high
  methods_transparency: high
  introduction_length: moderate
```

Send only this compact target profile downstream — never the entire journal
corpus or full manuscript rewrite instructions.

## Adaptive Model Router integration

If the Router is active, it owns execution-strategy decisions (which model,
how much reasoning, which tools, whether to delegate). Journal Fit Engine
owns only the candidate/fit decision logic and should not restate or
override routing instructions.

## Standalone operation

All of the above integrations are optional. When Corpus Builder or Voice
Engine are not present in the environment, Journal Fit Engine operates
standalone: it gathers evidence directly (via available search/fetch tools)
and stops at producing the adaptation-target profile rather than performing
the rewrite itself — the user can act on that profile manually.
