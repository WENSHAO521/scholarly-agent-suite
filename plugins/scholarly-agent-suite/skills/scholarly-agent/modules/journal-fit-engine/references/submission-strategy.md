# Submission Strategy

## Two-stage recommendation

**Stage 1 — intellectual fit.** Ignore prestige, APC, and indexing initially.
Ask only: where does this paper belong? Run the full fit-dimension analysis
([fit-model.md](fit-model.md)) on intellectual/methodological/genre/audience
grounds.

**Stage 2 — strategic fit.** Then layer in indexing, quartile, APC, OA model,
publication timing, word limits, and the user's career objective. This
ordering prevents metrics from distorting the intellectual match — a
high-prestige, poor-fit journal should never outrank a strong-fit journal
just because Stage 2 is evaluated first.

## Strategy modes

Support explicit user goals: best intellectual fit, highest realistic
prestige, balanced, fastest practical route, low/no APC, open access,
conservative acceptance strategy, ambitious/stretch strategy. Never promise
acceptance or a specific speed regardless of mode — describe realistic
tendencies only where there is actual evidence (e.g. published time-to-first-
decision), and label the metric precisely (see [indexing-metrics.md](indexing-metrics.md)
§ Review speed).

## Submission ladder

A useful default output structure:

```
Tier A — ambitious       (Journal 1, Journal 2)
Tier B — strong realistic fit  (Journal 3, Journal 4)
Tier C — conservative fallback (Journal 5)
```

Do not mechanically equate quartile with tier — a Q2 journal can be the
strongest intellectual fit and belong in Tier A; a Q1 journal with weak genre
fit does not automatically belong in Tier A.

## Stretch journals

Label `STRETCH` when fit is plausible but the contribution threshold appears
substantially higher than the manuscript currently clears. Always explain
concretely what would need to strengthen before submission — not just "make
it stronger."

## Journal-specific gap analysis

For every serious candidate, identify: what already fits, what does not fit,
and what needs adaptation before submission. Prefer concrete, evidence-backed
statements:

```
Strong: institutional-governance topic; comparative design; policy audience
Weak:   contribution currently framed too narrowly around one country
Before submission: reframe the mechanism as a broader institutional
  argument; move the institutional contribution earlier
```

This gap analysis is more useful than a bare score and should accompany every
candidate in the final shortlist, not just the top pick.

## Submission readiness vs. journal fit

These are separate axes — a manuscript can fit a journal well but not yet be
ready to submit there. States: `READY`, `MINOR_ADAPTATION`,
`MAJOR_ADAPTATION`, `NOT_READY`. Report both fit and readiness for each
candidate.

## Constraint handling and relaxation

Respect explicit user constraints (SSCI only, SCI only, Q1/Q2, no APC, under
a budget, specific publisher region, medical-journal-only, English only,
etc.), but flag when constraints make the candidate set unusually narrow.

If no journal satisfies every constraint, output
`NO CANDIDATE SATISFIES ALL CONSTRAINTS` and then show the smallest possible
relaxation (e.g. "relax Q1 → Q2") rather than silently dropping or ignoring a
stated constraint.

## Recommendation diversity and tradeoffs

Do not return several near-identical journals unless that genuinely reflects
a narrow field. Where the evidence supports it, diversify across
disciplinary-core, interdisciplinary, method-oriented, and policy-oriented
options while preserving fit — and explain the tradeoff explicitly, e.g.:

```
Journal A: stronger theoretical fit, higher selectivity
Journal B: slightly weaker theory fit, better methodological fit
Journal C: strong policy audience, lower adaptation cost
```

## Submission-sequence optimization and adaptation cost

A good ladder minimizes wasted adaptation work between rejection and
resubmission — prefer sequencing journals with similar formatting and
intellectual framing where practical, rather than requiring a full
manuscript reconstruction at every step. Classify per-candidate adaptation
cost as `LOW`, `MODERATE`, or `HIGH` (see [adaptation-policy.md](adaptation-policy.md)).

Conceptual (not computed) principle for prioritization: fit × career value ÷
adaptation burden. Reason about this qualitatively — do not build or present
a pseudo-quantitative optimizer.

## Simultaneous submission and preprints

Where a journal prohibits simultaneous submission, never recommend violating
it — build a sequential ladder instead. Check current preprint policy from
official sources when relevant rather than assuming universal acceptance or
prohibition (see [evidence-policy.md](evidence-policy.md)).

## Open-science and reporting requirements

Where relevant, check data sharing, code sharing, preregistration, and
reporting-guideline requirements (see [adaptation-policy.md](adaptation-policy.md)
§ Medicine-specific compliance) — these can function as hard submission
constraints, not just recommendations.

## Career objectives and institutional lists

Support optional user priorities (graduation requirement, tenure, grant
compliance, SSCI/SCI requirement, institutional list, high-impact target,
rapid publication, OA compliance) and institution-specific lists (ABS, ABDC,
FT50, CAS ranking, local accreditation lists) as explicit constraints — but
do not treat any such list as a universal quality measure, and never let an
administrative requirement silently override intellectual integrity. Show
the tradeoff instead of resolving it invisibly.

## Existing-target audit and reverse fit

**Target Journal Audit** — if the user already has a chosen journal, return:
`FIT`, `MISMATCHES`, `MANDATORY CHANGES`, `OPTIONAL IMPROVEMENTS`,
`SUBMISSION READINESS`.

**Reverse journal-fit mode** — given a journal, answer "what type of paper
belongs here?" from its official scope, accepted article types, and recent
corpus. Useful for early research planning — but the journal should inform
what kind of contribution is appropriate for that audience, never become a
target to be gamed by inventing a contribution that isn't genuine.

## Compare-journals mode

When comparing named journals (A vs. B vs. C), cover: intellectual fit,
methods, audience, prestige/visibility, APC, OA, submission constraints,
required manuscript changes, and risk factors, side by side.

## No acceptance prediction

Never state or imply a probability of acceptance ("you have a 70% chance").
The Skill does not provide a scientifically defensible acceptance-prediction
model. Use comparative, evidence-grounded language instead: "this is a
stronger fit than the alternatives, for these specific reasons."
