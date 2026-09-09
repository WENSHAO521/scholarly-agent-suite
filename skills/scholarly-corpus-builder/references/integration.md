# Integration

## Responsibility split

```text
Adaptive Model Router     = how the task should be executed
Scholarly Corpus Builder  = what scholarly material should be acquired and analyzed
Scholarly Voice Engine    = how the academic writing should be structured and voiced
Journal Fit Engine        = where the resulting manuscript may fit
```

## With the Scholarly Voice Engine

The Voice Engine may request a `discipline`, `journal`, `historical`, or
`author` profile. This skill returns:

```text
PROFILE
PROVENANCE SUMMARY
CONFIDENCE
LIMITATIONS
REFRESH STATUS
```

not the raw corpus, by default. Downstream systems should consume derived
features and source pointers, not 50 full papers.

### Voice precedence (recommended downstream priority)

```text
user author profile
  -> discipline conventions
    -> target journal observed profile
      -> selected historical/abstract voice profile
```

A journal profile should not erase author identity. A historical voice
profile should not override modern disciplinary norms.

## With the Adaptive Model Router

The Router decides whether retrieval is necessary at all, whether context
should be reduced, and which model/tool should process the corpus. This skill
decides what sources are needed, how many, from which source tier, and what
profile to derive. Do not embed model-routing logic here, and do not let the
Router make source-tier or copyright decisions — those stay with this skill.

## With the Journal Fit Engine

Journal Fit may use this skill's journal profiles (rhetorical architecture,
genre distribution, methods visibility, argument style) as one input, but must
separately weigh scope, topic, methods, and audience fit. Style similarity
alone is not journal suitability — this skill does not make placement
recommendations.

## Conceptual request/response shape

```text
GET_PROFILE:
  type = journal | discipline | historical | author
  target = ...
  freshness = current | refresh
  purpose = scholarly_voice | ...
```

This is a conceptual contract for how a caller should phrase a request, not a
network API — do not build a network service for this unless a host explicitly
requires one.

## Out of scope for this skill

- Literature-review writing (a style corpus is not an evidence corpus — see
  `corpus-policy.md` § Corpus purpose declaration).
- Journal recommendation/placement decisions.
- Direct phrase-level imitation of any author, living or historical.
- Model/tool routing logic.
