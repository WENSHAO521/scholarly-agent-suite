# Corpus Profile Integration

How this Skill consumes a profile from `scholarly-corpus-builder` when that
Skill is present in the environment. This file does not redefine that
Skill's schemas — it describes how the Voice Engine requests, weighs, and
applies what comes back. See `references/integration.md` for the ecosystem-
level relationship and `journal-style-adaptation.md` for the journal-fit-
engine side of profile integration.

## Requesting a profile

Use `scholarly-corpus-builder`'s own conceptual request shape rather than
inventing a new one:

```text
GET_PROFILE:
  type = journal | discipline | historical | author
  target = <journal name / discipline / scholar / "user">
  freshness = current | refresh
  purpose = scholarly_voice
```

This is a conceptual contract, not a network API — phrase the request this
way to a host or delegate to that Skill; do not build a service around it.
Request the minimum needed: a discipline-family voice question rarely needs a
fresh journal-level pull, and a single-chapter book task rarely needs a full
40–100-source discipline sample.

## What comes back

`scholarly-corpus-builder` returns a derived profile, not raw sources:

```text
PROFILE               the structured feature profile (see that Skill's
                       style-feature-schema.md: sentence/paragraph/argument/
                       evidence/section/claim-calibration/rhythm features)
PROVENANCE SUMMARY     compact source list with verification state
CONFIDENCE             high | medium | low — never a fabricated percentage
LIMITATIONS            explicit caveats (sample size, bias, staleness)
REFRESH STATUS         CURRENT | AGING | STALE | INCOMPLETE
```

Small-corpus honesty carries through: a profile built from `n < 5` sources is
`illustrative`, `5–19` is `limited` — do not draft as if either were a
statistically confident population estimate.

## Voice precedence

Match `scholarly-corpus-builder`'s own stated precedence exactly — do not
invent a competing order:

```text
user author profile
  → discipline conventions
    → target journal observed profile
      → selected historical/abstract voice profile
```

A journal's observed profile must never erase the user's own established
voice, and a historical/abstract profile must never override current
disciplinary norms. See `author-voice-calibration.md` for how the author
layer itself is derived and prioritized.

## OBSERVED, RECOMMENDED, and MANDATORY — never conflate

Three different categories of input, kept visibly separate in your own
reasoning even when not all are surfaced to the user:

```text
OBSERVED     an empirical pattern in a corpus/journal sample
             e.g., "sampled introductions average 900 words"
RECOMMENDED  this Skill's own stylistic suggestion drawn from OBSERVED data
             e.g., "consider a shorter introduction"
MANDATORY    an explicit, authoritative instruction (the author's own
             instruction, or a journal's actual submission requirement)
             e.g., "structured abstract required"
```

An OBSERVED pattern earns, at most, a RECOMMENDED adjustment — never treat it
as MANDATORY. This mirrors `scholarly-corpus-builder`'s own
`OBSERVED_WRITING_PROFILE` vs. `OFFICIAL_REQUIREMENTS` distinction and
`journal-fit-engine`'s `OBSERVED ARTICLE PROFILE` vs. `OFFICIAL JOURNAL DATA`
— do not blur what that Skill has already kept separate.

## Confidence and stability gating

Weight a feature's influence on drafting by its reported confidence, not by
how specific or quotable it sounds:

```text
high confidence, consistent across sample   → may strongly inform drafting
low confidence or small/skewed sample       → weak influence only; note the
                                               uncertainty rather than acting
                                               on it as settled
```

Example: `first_person = medium, confidence = high` may meaningfully shift a
drafting choice. `counterargument_frequency = high, confidence = low` should
not visibly change the output — treat it as a hypothesis, not a rule.

## Conflict resolution

When two inputs disagree (e.g., the author profile shows low first-person use
but the target-journal profile shows medium), do not average them
mechanically. Apply the precedence order above, then look for a principled
compromise at the boundary — e.g., retain the author's restrained first-person
habit but permit it specifically where methodological agency aids clarity —
rather than splitting the difference numerically. See
`scripts/voice/profile_merge.py` for a worked implementation of this
resolution logic.

## Author-profile incremental updates and edit-diff learning

When the corpus-builder skill (or the user directly) supplies updated author
material over time, classify each observed trait as:

```text
stable | strengthening | weakening | new | uncertain
```

A single anomalous manuscript should not overwrite a long-established trait —
require repeated evidence before reclassifying a `stable` trait as
`weakening`.

If the host authorizes comparing an AI draft against the user's own revision
of it, extract recurring preferences from the diff (e.g., consistently
shortened introductions, reduced hedging, more explicit mechanism language,
fewer generic transitions) and fold them into the author profile going
forward. This is calibration to the user's genuine preferences, never framed
or used as AI-detector evasion.

## What must not be preserved

Never preserve, from any profile, an author's or corpus's own defects:
citation errors, unsupported claims, inconsistent terminology, logical gaps,
or grammar mistakes. Separate **voice trait** (preserve) from **quality
defect** (correct) — `scholarly-corpus-builder`'s own author-profile schema
makes exactly this distinction (`do_not_preserve`) and this Skill honors it.

## Standalone fallback

If `scholarly-corpus-builder` is not present or does not return a profile,
proceed using this Skill's own internal discipline/genre defaults
(`disciplinary-matrix.md` / `disciplines/*.md`) rather than blocking the task.
Note to the user, only if it materially matters, that drafting proceeded
without a corpus-derived profile.
