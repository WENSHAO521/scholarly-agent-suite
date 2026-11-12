# Profile types and style features

Sections (each starts at an `<a id>` anchor; read only the one the task needs): [discipline-profile](#discipline-profile), [journal-profile](#journal-profile), [historical-profile](#historical-profile), [author-profile](#author-profile), [style-feature-schema](#style-feature-schema), [stability-analysis](#stability-analysis).

<a id="discipline-profile"></a>

## Discipline Profile

### Purpose

Learn the current writing conventions of a field. The core skill logic is
discipline-neutral; discipline-specific conventions live here and in
supplementary notes rather than in `MODULE.md`.

### Supported disciplinary coverage (non-exhaustive)

```text
Natural sciences
Mathematics and formal sciences
Engineering
Computer science and AI
Medicine and health sciences
Social sciences
Business and management
Law
Humanities
Education
Arts and design
Interdisciplinary fields
```

Examples of discipline granularity: public administration, molecular biology,
machine learning, constitutional law, intellectual history, clinical
medicine, economics, sociology, education, mathematics.

### Sampling rules

- Default size: 40–100 representative works.
- Default freshness: refresh every 12–24 months, shorter for rapidly changing
  fields (e.g. ML/AI).
- Diversify across subfields, methods, and venues rather than sampling one
  dominant journal.

### Derived output

```text
argument patterns
typical genre structures
evidence conventions
claim calibration
citation placement
paragraph rhythm
section architecture
methods visibility
first-person usage
uncertainty conventions
```

### Schema

```text
discipline
subdiscipline
sample_window
dominant_genres
claim_conventions
argument_architectures
methods_visibility
citation_behavior
uncertainty_conventions
first_person_norms
section_conventions
recommended_scholarly_voice_profiles
confidence
```

### Do not

- Treat one subfield's conventions as representative of the whole discipline
  without noting the narrower scope.
- Turn a discipline profile into a stereotype ("economists always...") —
  ground every claim in the sampled evidence and note confidence.

<a id="journal-profile"></a>

## Journal Profile

### Purpose

Learn the observable writing architecture of a target journal from a sampled
corpus of its articles. This is an **empirical profile of sampled articles**,
never a claim about the journal's mandatory style — see the Journal
Instructions vs Observed Corpus distinction in `MODULE.md`.

### Sampling rules

- Default window: last 2–3 years, adapted to publication volume, field
  stability, and user request. Always record the actual sampling period used.
- Default size: 20–50 articles. A small, diversified corpus is usually more
  useful than hundreds of undifferentiated papers.
- Diversify by: year, article type, subfield/topic, methods, issue, and
  author. Avoid overrepresenting one special issue, one prolific author, one
  laboratory, or one article genre.
- **Article type discipline**: a special issue is not the whole journal, an
  editorial is not an empirical article, and a review article is not original
  research. Sample within a clearly recorded article-type scope, and record
  that scope in the manifest.

### Extractable characteristics

```text
title length
abstract architecture and length
introduction structure
literature placement
contribution placement
section naming
methods visibility
results/discussion separation
policy-implication frequency
first-person usage
sentence variation
citation density
limitations placement
```

### Schema

```json
{
  "journal": "",
  "issn": [],
  "sample_window": "",
  "sample_size": 0,
  "article_types": [],
  "profile_generated_at": "",
  "source_provenance": [],
  "abstract": {
    "typical_structure": [],
    "contribution_position": ""
  },
  "introduction": {
    "dominant_architecture": "",
    "literature_density": "",
    "contribution_position": ""
  },
  "prose": {
    "sentence_length": "",
    "sentence_variation": "",
    "first_person": "",
    "rhetorical_intensity": "",
    "qualification_density": ""
  },
  "citations": {
    "density": "",
    "dominant_placement": ""
  },
  "sections": {
    "common_patterns": []
  },
  "limitations": [],
  "confidence": "medium"
}
```

### Example output

```text
Target: Journal X
Corpus: 32 original research articles, 2024-2026

Observed profile:
- Contribution typically appears in the first third of the introduction.
- Literature review is integrated rather than fully separated.
- First-person plural is moderately common.
- Discussion sections frequently distinguish empirical findings from policy
  implications.

Limitations:
- Open-access sample overrepresented.
- Special issues excluded.
```

### Freshness

Refresh approximately every 6–12 months; 3–6 months for fast-moving
computing/AI venues where current style materially matters. See
`corpus-policy.md#refresh-policy` for the Corpus Selection Gate and incremental refresh.

### Do not

- Present observed patterns as formal submission requirements.
- Infer that a higher-impact journal has "better" prose — this skill is
  descriptive, not evaluative.
- Rebuild the corpus from scratch on every request when a `CURRENT` cached
  profile already exists.

<a id="historical-profile"></a>

## Historical Scholar Profile

### Purpose

Derive transferable scholarly-writing *mechanisms* from deceased or historical
scholars — argument architecture, not phrasing.

### Focus areas

```text
argument architecture
definition strategy
conceptual progression
counterargument
examples
evidentiary structure
sentence rhythm
abstraction
qualification
```

### Hard limits

- **Do not build phrase-copying libraries.** No compilation of the scholar's
  distinctive sentences intended for reuse.
- **Do not generate substantial reproductions of copyrighted texts.** Prefer
  verified or reasonably believed public-domain sources (Tier 5); record
  `public_domain_status: verified / likely / unknown` per work — see
  `corpus-policy.md#copyright-boundary`. Public domain is jurisdiction-dependent; do not
  assume it globally.
- Record edition, source, and publication date for every work used.

### Schema

```text
scholar
discipline
period
works_sampled
source_status
argument_architecture
definition_style
evidence_style
sentence_architecture
intellectual_rhythm
abstraction_level
counterargument_strategy
qualification_style
transferable_strengths
modern_use_cautions
```

Do not include large excerpts of the source text in the profile.

### Example output

```text
Profile: Historical institutional-analytical tradition
Derived from: verified public-domain / lawfully accessible historical sources

Transferable traits:
- strong conceptual definitions
- progressive qualification
- mechanism-centered examples
- disciplined abstraction

Do not reproduce:
- archaic diction
- characteristic quotations
- obsolete citation conventions
```

### Era comparison

Support broad era bands for comparative work:

```text
pre-1945
1945-1980
1980-2005
2005-present
```

Ground every era profile in actually sampled evidence; do not let era labels
calcify into unsupported stereotypes.

### Freshness

Historical scholar profiles normally need no periodic refresh unless better
source material becomes available (a newly digitized edition, a more reliable
public-domain text).

<a id="author-profile"></a>

## Personal Author Profile

### Purpose

Learn the user's own established scholarly voice from works they provide or
explicitly authorize. This is the highest-personalization-value corpus type.

### Authorization boundary

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

### Ideal corpus size

5–20 substantive works. Prioritize quality and coverage of the user's actual
range (article types, venues, career stage) over quantity.

### Derived characteristics

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

### Schema

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

### Example output

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

### Author-vs-journal adaptation

When comparing an author profile against a target journal profile, produce:

```text
shared traits
differences
recommended adaptation points (surface-level, e.g. contribution placement)
features that should NOT be changed (the author's substantive voice)
```

Do not recommend artificially imitating the journal's phrasing — recommend
structural adaptation while preserving the author's own conceptual voice.

### Privacy

- Do not persist user-provided manuscript contents outside authorized,
  project-scoped storage.
- Do not publish or share a personal style profile automatically.
- Do not fold a personal author corpus into any global/shared corpus.

### Freshness

Refresh when new works are added or the user requests recalibration — no
fixed periodic schedule.

<a id="style-feature-schema"></a>

## Style Feature Schema

The primary output of this skill is a structured feature profile, not the
corpus. This file defines the feature categories every profile type draws
from. Treat all features as sampled heuristics, not exact linguistic
measurements — describe them descriptively ("relatively uncommon in the
sampled corpus") rather than with false statistical precision, unless a real
metric was actually computed over a defined, recorded corpus.

### Sentence-level features

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

### Paragraph-level features

```text
median paragraph length
paragraph-length variation
dominant paragraph architecture (claim-first vs. evidence-first)
citation concentration
paragraph-final synthesis frequency
topic-sentence explicitness
```

### Argument-level features

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

### Evidence features

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

### Section architecture

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

### Claim calibration

Classify observed claims into:

```text
descriptive | associational | causal | mechanistic | predictive | interpretive | normative | formal
```

Record common hedge *patterns* (e.g., "hedges before causal claims, direct on
descriptive claims") without building a phrase-copy library of exact hedging
language.

### Intellectual rhythm

Abstract, higher-level rhetorical patterns, e.g.:

```text
claim -> evidence -> qualification
problem -> mechanism -> implication
observation -> anomaly -> explanation
premise -> objection -> revised claim
historical episode -> structural interpretation
```

### Feature confidence

Each feature carries a confidence rating:

```text
high | medium | low
```

based on `source_count`, consistency across sources, data completeness, and
genre diversity. Do not present pseudo-calibrated probabilities (e.g. "73%") —
use confidence bands and descriptive language instead, unless a genuine
computed statistic exists for the recorded corpus.

### Citation feature extraction — scope limit

Citation density, position, clustering, self-citation proportion (if
determinable), and reference recency may be analyzed as *style* signals. Do
not use citation counts to evaluate research quality — that is out of scope
for this skill.

<a id="stability-analysis"></a>

## Corpus Stability Analysis

Implementation reference for `scb/stability.py`. A profile should not
be trusted merely because a corpus exists — this module actually runs
a comparison, it does not assume stability.

### Split-corpus test

`run_stability_check(documents)`:

1. Below 10 documents: `INSUFFICIENT_SAMPLE` — no test is run.
2. Otherwise, `split_corpus()` deterministically alternates documents
   into two halves (reproducible without a seed — no randomness needed
   for a simple alternating split).
3. A `StyleProfile` is built for each half (`scb/profile_schema.py`).
4. Five numeric features are compared (sentence/paragraph length,
   first-person rate, hedge rate, citation density) using a **35%
   relative-difference tolerance** — an explicit, documented threshold,
   not a fitted statistical model.
5. `stable_feature_share >= 0.8` → `STABLE`; `>= 0.5` → `MOSTLY_STABLE`;
   otherwise `UNSTABLE`.

`STABLE` means the two halves of *this* corpus agree with each other —
it is a statement about internal consistency, not external validation
against ground truth, and not a claim that the corpus is representative
of the wider discipline/journal/author it was sampled from.

### Bootstrap resampling

`bootstrap_sentence_median_length(documents, iterations, seed)`
resamples documents with replacement (Python's stdlib `random`, no
third-party statistics package — PART XXV: "do not turn this into a
complex statistical package") and recomputes the sentence-length
median each time, reporting the spread (mean/stdev/min/max) across
resamples. Deterministic given a fixed seed — verified reproducible in
`tests/test_stability.py`.

### What this does not do

- No cross-disciplinary, human-QA'd validation of whether "stable"
  profiles actually match expert judgment (see the benchmark-honesty
  fixtures in `evals/production-hardening.jsonl`).
- No confidence interval or p-value — the module reports a descriptive
  spread, not an inferential statistic, deliberately avoiding false
  precision (see `references/profiles.md#style-feature-schema`).
