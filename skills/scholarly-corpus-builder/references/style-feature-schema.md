# Style Feature Schema

The primary output of this skill is a structured feature profile, not the
corpus. This file defines the feature categories every profile type draws
from. Treat all features as sampled heuristics, not exact linguistic
measurements — describe them descriptively ("relatively uncommon in the
sampled corpus") rather than with false statistical precision, unless a real
metric was actually computed over a defined, recorded corpus.

## Sentence-level features

```text
median sentence length
sentence-length variation
complex-sentence frequency
short decisive-sentence frequency
passive-voice tendency
first-person tendency
nominalization density
technical-vocabulary density
parenthetical usage
colon/semicolon usage
```

## Paragraph-level features

```text
median paragraph length
paragraph-length variation
dominant paragraph architecture (claim-first vs. evidence-first)
citation concentration
paragraph-final synthesis frequency
topic-sentence explicitness
```

## Argument-level features

```text
problem framing
gap type
mechanism use
definition strategy
hypothesis style
counterargument frequency
scope-condition use
qualification pattern
contribution placement
limitation placement
```

## Evidence features

```text
citation density
citation position
evidence proximity to claims
quantitative evidence density
case evidence density
quotation frequency
figure/table dependence
source diversity
```

## Section architecture

```text
title pattern
abstract structure
introduction length
literature-review position
theory-section presence
methods-section presence
results/discussion separation
conclusion structure
limitations section presence/position
appendix/supplement reliance
```

## Claim calibration

Classify observed claims into:

```text
descriptive | associational | causal | mechanistic | predictive | interpretive | normative | formal
```

Record common hedge *patterns* (e.g., "hedges before causal claims, direct on
descriptive claims") without building a phrase-copy library of exact hedging
language.

## Intellectual rhythm

Abstract, higher-level rhetorical patterns, e.g.:

```text
claim -> evidence -> qualification
problem -> mechanism -> implication
observation -> anomaly -> explanation
premise -> objection -> revised claim
historical episode -> structural interpretation
```

## Feature confidence

Each feature carries a confidence rating:

```text
high | medium | low
```

based on `source_count`, consistency across sources, data completeness, and
genre diversity. Do not present pseudo-calibrated probabilities (e.g. "73%") —
use confidence bands and descriptive language instead, unless a genuine
computed statistic exists for the recorded corpus.

## Citation feature extraction — scope limit

Citation density, position, clustering, self-citation proportion (if
determinable), and reference recency may be analyzed as *style* signals. Do
not use citation counts to evaluate research quality — that is out of scope
for this skill.
