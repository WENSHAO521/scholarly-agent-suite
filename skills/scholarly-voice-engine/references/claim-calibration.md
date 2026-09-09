# Claim Calibration

Every substantive claim in a scholarly text has an epistemic type. Identify it
before drafting the sentence, and preserve it through any later stylistic
rewrite — voice edits must never change what kind of claim a sentence makes.

## Claim types

Use the same eight-way taxonomy `scholarly-corpus-builder` uses when it
extracts claim-calibration features from a corpus (`style-feature-schema.md`
§Claim calibration), so profiles from that skill map directly onto this one:

```text
descriptive | associational | causal | mechanistic | predictive |
interpretive | normative | formal
```

```yaml
descriptive:    "what was observed" — no relationship claimed
associational:  "X co-occurs with / predicts / is correlated with Y"
causal:         "X causes / produces / increases Y" — requires design support
                (see research-design-matrix.md)
mechanistic:    "X causes Y via process Z" — requires evidence for the
                intermediate step, not just the endpoint correlation
predictive:     "X forecasts Y" — a claim about forecasting performance, not
                about why
interpretive:   "this may be read as / plausibly means" — humanities/legal/
                qualitative meaning-claims, argued not measured
normative:      "X ought to / should" — a value claim, distinct from any
                empirical premise supporting it
formal:         true/false relative to stated axioms or definitions — proof,
                not evidence, is what settles it
```

## The claim-strength invariant

A stylistic rewrite must never silently move a claim up this scale:

```text
descriptive → associational → causal → mechanistic
```

or convert a hedged claim into an unhedged one, or a normative claim into a
descriptive one (or vice versa) without the user explicitly asking for an
argument change. Concretely, never let a "polish" pass turn:

```text
"is associated with"      into  "causes"
"may indicate"             into  "demonstrates"
"is consistent with X"     into  "confirms X"
"the evidence suggests"    into  "the evidence proves"
```

If a draft already contains claim-strength inflation, that is a defect to
flag and fix (see `quality-audit.md`), not a voice choice to preserve.

## Discipline-sensitive uncertainty language

Match hedging to the design and the field's own idiom — never apply a single
uncertainty phrasing template everywhere:

```yaml
natural_sciences: >
  is consistent with / supports the possibility that / suggests a role for /
  does not exclude / cannot rule out / within the limits of this design
medicine_health: >
  is associated with / was observed in this population / does not establish
  efficacy / consistent with, but not proof of, a causal effect
social_sciences: >
  the evidence is compatible with / under these institutional conditions /
  within the observed sample / conditional on the identifying assumption
humanities: >
  may be read as / this interpretation emphasizes / a competing reading would
  suggest / on this reading
law: >
  the stronger interpretation would imply / the doctrine does not clearly
  resolve / on the weight of authority
mathematics_formal: >
  holds under the stated hypotheses / is not established for the general case
  without additional assumptions
```

Do not hedge every sentence regardless of warrant — a sentence qualified past
the point of asserting anything is a failure mode, not caution (see
`human-scholarly-prose.md`). A well-supported descriptive or formal claim
should be stated plainly.

## Scope conditions

Strengthen a claim's credibility by narrowing it rather than by removing
hedges. State explicitly, where relevant:

```text
population | institution | historical period | jurisdiction |
experimental condition | measurement regime | sample | data-generating
process
```

"Under conditions of low state capacity, X" is a stronger scholarly move than
an unscoped "X," even though it claims less. Scope narrowing and hedging are
different tools — prefer narrowing a claim to its true domain over merely
qualifying an overbroad one.

## Applying this during rewrite

1. Identify the claim type and design ceiling for every major claim before
   touching its wording (cross-check `research-design-matrix.md`).
2. Rewrite for clarity/voice without moving the claim along the strength
   scale, changing its scope, or converting its type.
3. If the source text's claim strength already exceeds what its own stated
   evidence supports, that is a substantive problem — flag it to the user or
   correct it explicitly (never silently), per `citation-integrity.md` and
   `quality-audit.md`'s repair order (integrity before style).
