# Fit Model

## Fit dimensions

Not every task requires every dimension — select what's relevant to the
manuscript and the candidate journal.

scope_fit, topic_fit, theory_fit, method_fit, article_type_fit, audience_fit,
contribution_fit, disciplinary_fit, interdisciplinary_fit, regional_fit,
writing_architecture_fit, submission_constraint_fit, career_strategy_fit.

## Hard filters vs. soft fit

**Hard filters** — presence of any of these eliminates a candidate outright:

- journal does not accept this article type
- word limit fundamentally incompatible (not a trim, a different scale)
- journal inactive / discontinued / merged with no successor accepting this work
- manuscript language not supported by the journal
- journal explicitly states this subject is outside scope

**Soft fit** — influences ranking, never eliminates alone:

- topic alignment strength
- method prevalence in the journal's recent corpus
- theoretical orientation match
- audience appropriateness
- writing-architecture / structural convention match

Apply hard filters before any ranking. Do not let a weak soft-fit dimension
function as a silent hard filter, and do not let enthusiasm about topic fit
override an actual hard filter (e.g. "great topic match, wrong article type"
is still eliminated, not just "flagged").

## No fake precision

Never output decimal or percentage fit scores. Use only: `EXCELLENT FIT`,
`STRONG FIT`, `PLAUSIBLE FIT`, `STRETCH`, `WEAK FIT`, `NOT RECOMMENDED`.
Internal numeric heuristics may be used privately to order candidates but must
never be surfaced as a score or probability.

## Conceptual fit model

```
Overall Fit ≈ Intellectual Fit + Methodological Fit + Genre Fit
              + Audience Fit + Practical Submission Fit
```

This is additive in concept only — weighting is never equal across manuscript
types. State which dimensions are driving a given verdict rather than
implying a uniform formula.

## Weighting by manuscript type (illustrative, not exhaustive)

**Empirical quantitative social science:** scope high, topic high, method
high, genre high, audience medium-high, writing architecture medium.

**Philosophy:** argument-tradition fit very high, scope very high, genre
high, method fit low relevance.

**Clinical medicine:** study design very high, clinical relevance very high,
scope high, article type high.

**Mathematics:** subject classification very high, theorem/problem class
high, technical depth high, article length/style medium.

See [disciplines/](../disciplines/) for the full per-family breakdown,
including engineering/computing, humanities, law, management, education, and
interdisciplinary work.

## Theory fit — a specific trap

For theory-oriented journals, check whether the manuscript actually
**develops**, **extends**, or **tests** theory — versus merely citing
theories as background. Citation volume of theoretical work is not itself a
theoretical contribution. Score `theory_fit` on demonstrated theoretical work,
not on how many theory citations appear in the reference list.

## Method and data fit

Relevant methods span: RCT, cohort, cross-sectional, panel data, DiD, RDD,
SEM, machine learning, simulation, ethnography, case comparison, archival
history, doctrinal analysis, formal proof, and more. Relevant data types span:
survey, administrative, clinical, omics, imaging, text, social media,
historical archive, interview, experimental, simulated.

Do not automatically penalize an uncommon methodology for a venue — an
uncommon method can itself be the contribution. Instead assess whether the
journal's actual audience is positioned to evaluate that method (audience
fit), not just whether the method is common in the journal's back catalog.

## Editorial orientation

Where observable from recent issues, journals may lean toward theory,
methods, policy, practice, clinical translation, technical novelty, historical
interpretation, or interdisciplinary breadth. Treat this as an **observed**
orientation (see [journal-profile.md](journal-profile.md)), not as fixed,
immutable editorial policy — it can and does shift with editorial-board
turnover.

## Temporal fit

Fast-moving fields (AI, medical AI, computational biology, and similar) need
recency-weighted profiles — a five-year-old sample of the journal's articles
may no longer represent what it currently publishes. Prefer the most recent
1–3 years of output when assessing method and topic fit in such fields.

## Interdisciplinary manuscripts

Determine home discipline, secondary discipline, and target conversation.
Interdisciplinary manuscripts often fail at submission because they are
somewhat relevant to several fields but central to none. Identify which venue
logic the *primary contribution* actually serves — e.g. an AI+medicine paper
could target medical informatics, a clinical specialty, AI methods venues, or
digital health; the choice follows the primary contribution, not the
keyword overlap. See [disciplines/interdisciplinary.md](../disciplines/interdisciplinary.md).

## Geographic and internationalization fit

Do not automatically penalize a region-specific study. Ask instead: does the
journal publish work from this geography? Is the journal explicitly regional
(and is that a fit or a mismatch)? Does the manuscript derive broader
implications from the local case? A single-country case study can fit an
international journal when it is theoretically portable — but say concretely
*how* to strengthen that portability (case importance, mechanism
generalizability, comparative framing), not just "add international
relevance" as an unexplained instruction.

## Desk-rejection risk signals

Do not predict a probability. Instead surface observable
**DESK-REJECTION RISK FACTORS**: scope mismatch, article-type mismatch, weak
fit to the journal's actual conversation, local-only framing without
portability, methods outside the venue's norms, contribution pitched below
the journal's typical threshold, or format incompatibility.
