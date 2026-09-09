# Personal Author Profile

## Purpose

Learn the user's own established scholarly voice from works they provide or
explicitly authorize. This is the highest-personalization-value corpus type.

## Authorization boundary

Do not assume a publicly retrieved paper belongs to the user merely because
the author name matches. Use only:

- user-provided files (uploaded papers, book chapters, manuscripts)
- explicitly identified publication lists the user confirms are theirs
- authorized repositories (e.g. an institutional page the user points to and
  confirms)
- clearly confirmed authorship

Avoid accidental author-name collisions (common names, homonymous authors in
adjacent fields). When in doubt, ask the user to confirm or provide the works
directly rather than guessing from a public search.

## Ideal corpus size

5–20 substantive works. Prioritize quality and coverage of the user's actual
range (article types, venues, career stage) over quantity.

## Derived characteristics

```text
sentence length distribution
paragraph-length distribution
first-person preference
transition habits
claim strength
citation placement
definition frequency
concept recurrence
preferred argument moves
section-opening style
discussion/conclusion style
```

The goal is to **improve consistency**, not mechanically preserve errors or
bad habits. Explicitly separate what should be preserved from what should be
corrected.

## Schema

```json
{
  "profile_type": "author",
  "source_count": 0,
  "source_scope": "",
  "sentence_style": {},
  "paragraph_style": {},
  "argument_moves": [],
  "citation_behavior": {},
  "first_person": "",
  "claim_strength": "",
  "definition_style": "",
  "preferred_transitions": [],
  "section_patterns": {},
  "do_not_preserve": [
    "citation errors",
    "grammar mistakes",
    "unsupported claims"
  ]
}
```

## Example output

```text
Author corpus: 14 user-provided articles

Stable features:
- medium-long sentences with high variation
- concept-first paragraph openings
- low first-person frequency
- frequent mechanism-based transitions
- conclusions tend to narrow claims rather than broaden them

Recommended preservation:
- conceptual density
- cautious causal language

Recommended correction:
- occasional overlong introductions
- repeated literature-summary transitions
```

## Author-vs-journal adaptation

When comparing an author profile against a target journal profile, produce:

```text
shared traits
differences
recommended adaptation points (surface-level, e.g. contribution placement)
features that should NOT be changed (the author's substantive voice)
```

Do not recommend artificially imitating the journal's phrasing — recommend
structural adaptation while preserving the author's own conceptual voice.

## Privacy

- Do not persist user-provided manuscript contents outside authorized,
  project-scoped storage.
- Do not publish or share a personal style profile automatically.
- Do not fold a personal author corpus into any global/shared corpus.

## Freshness

Refresh when new works are added or the user requests recalibration — no
fixed periodic schedule.
