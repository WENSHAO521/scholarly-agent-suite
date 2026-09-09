# Author Voice Calibration

When the user supplies their own prior writing, infer a high-level style profile
from it and let it take priority over any historical or abstract voice profile.

## Priority hierarchy

```text
user's established scholarly voice
  +
disciplinary conventions
  +
selected scholarly profile (for gaps the user's sample doesn't cover)
```

Never: "historical scholar overrides user." The historical/abstract profile fills
in only what the user's own sample does not establish, and only in a way
consistent with what it does establish.

## What to infer from a writing sample

```text
average sentence length
paragraph length
first-person usage (frequency and construction: "I argue" vs "we show")
transition style (mechanical vs. intellectual; which connectives recur)
claim strength (typical hedging level)
citation placement (parenthetical vs. narrative; density)
definition habits (does the author define terms explicitly, and how often)
concept density
preferred rhetorical moves (how they open sections, how they close them,
  how they introduce counterarguments)
```

## What not to do

- Do not copy the user's errors (grammatical slips, inconsistent terminology,
  citation-format mistakes) forward into new text — fix these silently unless the
  user is specifically asking for a diagnostic of their own habits.
- Do not flatten genuine stylistic idiosyncrasy toward a generic "correct
  academic" register if it is a deliberate, functioning choice (e.g., an author
  who consistently opens sections with a rhetorical question, or who prefers
  short paragraphs even in a discipline that trends toward long ones).
- Do not infer a profile from too small a sample (a single paragraph) with false
  confidence — note the uncertainty and lean more heavily on disciplinary
  convention until more sample is available.

## Applying the calibration

1. Extract the profile using the dimension list in `voice-engine.md`.
2. Cross-check against the discipline's `recommended_voice_profiles` — flag (to
   yourself, and to the user if it's a substantial mismatch) any place the
   author's habits diverge sharply from field convention, e.g. a first-person-free
   author writing in a sub-field where "we show" is now standard.
3. Draft/rewrite using the author's profile as the default; use the discipline
   module and abstract voice profile only to fill gaps (a construction the sample
   never exercises, e.g. how to open a limitations section).
4. When calibration is high-confidence (large sample, consistent patterns),
   prefer fidelity to the author's voice even where it's mildly unconventional,
   as long as it doesn't violate discipline-specific integrity norms (e.g., a
   journal that strictly forbids first person).

## Incremental updates

When new author material arrives over time (a new manuscript, a corpus-
builder refresh — see `corpus-profile-integration.md`), classify each trait
as:

```text
stable | strengthening | weakening | new | uncertain
```

Require repeated, consistent evidence before reclassifying a `stable` trait
as `weakening` or dropping it — a single anomalous manuscript (a co-authored
piece, a deliberately different register for one venue) should not overwrite
a long-established voice.

## Learning from user edits (edit-diff learning)

When the host authorizes comparing an AI-drafted passage against the user's
own revision of it, extract recurring preferences from the diff rather than
treating each edit as a one-off correction — e.g., the user consistently
shortens introductions, consistently removes a specific hedge, consistently
adds mechanism language, or consistently cuts a generic transition. Fold
confirmed, repeated preferences into the working author profile for the rest
of the task. This is calibration to the user's genuine preferences; it is not
and must not be framed as evading any kind of detection.
