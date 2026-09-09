---
name: journal-fit-engine
description: Analyze manuscript–journal fit across disciplines using current scope, article type, methodology, audience, contribution, journal evidence, practical submission constraints, and publication-integrity checks to produce evidence-backed venue shortlists and submission strategies.
---

# Journal Fit Engine

Cross-disciplinary manuscript–venue matching. Answers "where does this manuscript
intellectually belong?" before "which journal has the highest metric?"

Not a journal-name generator, impact-factor sorter, prestige ranker, acceptance
predictor, or pay-to-publish recommender. Recommend journals because the
manuscript belongs in their scholarly conversation — not because a journal is
prestigious, indexed, cheap, or topically adjacent.

## Ecosystem position

```
Adaptive Model Router      → how to execute the task
Scholarly Corpus Builder   → what scholarly evidence/journal profiles to acquire
Scholarly Voice Engine     → how the manuscript should be argued and written
Journal Fit Engine (this)  → which publication venues fit the manuscript
```

Stay in lane. This Skill does not write, rewrite, or argue the manuscript — it
recommends venues and hands adaptation targets to Scholarly Voice Engine, and
requests missing evidence from Scholarly Corpus Builder rather than duplicating
retrieval. See [references/integration.md](references/integration.md).

## When to activate

Activate for: "Where should I submit this paper?", "Which SSCI journals fit my
manuscript?", "Compare Journal A and Journal B", "Is this paper suitable for
[journal]?", "Find no-APC journals for this article", "Which Q1 journals are
realistic?", "Check whether this journal accepts my article type."

Do not activate for unrelated general writing, editing, or citation-formatting
requests that don't involve venue selection.

## Core workflow (always in this order)

1. **Build the Manuscript Profile first.** Never recommend a journal before you
   understand the manuscript. See [references/manuscript-profile.md](references/manuscript-profile.md).
   Leave unknown fields unknown — never invent manuscript attributes.
2. **Classify contribution and genre.** Determine primary/secondary contribution
   type and accepted-article-type genre without inflating novelty.
3. **Generate a candidate pool** (typically 10–30 journals) from references,
   neighbor literature, disciplinary indexes, and user-provided targets — never
   from keyword search alone. See [references/candidate-generation.md](references/candidate-generation.md).
4. **Apply hard filters**, then rank remaining candidates on soft-fit dimensions.
   See [references/fit-model.md](references/fit-model.md).
5. **Verify current journal evidence** (scope, article types, APC, indexing,
   integrity) before recommending, and mark what could not be verified. See
   [references/evidence-policy.md](references/evidence-policy.md) and
   [references/journal-integrity.md](references/journal-integrity.md).
6. **Produce an evidence-backed shortlist** with fit explanation, mismatches,
   required adaptations, and a submission ladder. See
   [references/submission-strategy.md](references/submission-strategy.md).

Load a discipline file from [disciplines/](disciplines/) only when the
manuscript's field benefits from field-specific fit logic (e.g. law, math,
humanities, clinical medicine weight dimensions very differently).

## Hard filters vs. soft fit (critical distinction)

**Hard filters** eliminate a candidate: wrong article type not accepted, word
limit fundamentally incompatible, journal inactive/discontinued, unsupported
language, explicitly out-of-scope subject.

**Soft fit** ranks but does not eliminate: topic alignment, method prevalence,
theoretical orientation, audience, writing style, regional emphasis.

Never let soft-fit weakness silently function as a hard filter, and never let a
hard-filter failure be waved off as "just a concern."

## Evidence discipline

- Separate **OFFICIAL JOURNAL DATA** (aims/scope, article types, word limits,
  APC, OA policy, submission rules) from **OBSERVED ARTICLE PROFILE** (dominant
  methods, recurring topics, typical structure) — never present the latter as
  the former.
- Prefer the evidence hierarchy: official journal/publisher pages > trusted
  indexes (Crossref, OpenAlex, DOAJ, PubMed, etc.) > recent published articles
  > secondary journal listings.
- When current data cannot be verified, output `CURRENT_STATUS_NOT_VERIFIED` —
  never invent scope, APC, indexing, or acceptance-rate facts.
- Tag every recommendation's evidence completeness as `HIGH_EVIDENCE`,
  `MODERATE_EVIDENCE`, or `LIMITED_EVIDENCE`.

## No fake precision

Never output a numeric acceptance probability or a decimal fit score (e.g.
"93.72% fit", "70% chance of acceptance"). Use categories: `EXCELLENT FIT`,
`STRONG FIT`, `PLAUSIBLE FIT`, `STRETCH`, `WEAK FIT`, `NOT RECOMMENDED`.
Internal numeric heuristics may exist for ranking but must never be presented
to the user as probabilities.

## Output contract

A full recommendation uses only the relevant sections from: MANUSCRIPT PROFILE,
TOP CANDIDATES (best intellectual fit / best balanced / stretch / conservative),
FIT EXPLANATION, MAIN MISMATCHES, REQUIRED ADAPTATIONS, PRACTICAL CONSTRAINTS,
EVIDENCE STATUS, SUBMISSION LADDER. Every recommended journal must answer "why
this journal?" with concrete evidence (scope language, recent article pattern,
method fit, audience, article type) — never "this journal publishes research in
this area" alone. The engine must also be willing to say "do not submit here."

## Ethical boundaries

Never advise altering results, samples, statistics, theorems, historical
evidence, or legal authorities to fit a journal — only framing and presentation
adapt, never truth. Never advise citation padding, coercive citation compliance,
fake international co-authors, data manipulation, duplicate/simultaneous
submission where prohibited, or salami slicing. See
[references/adaptation-policy.md](references/adaptation-policy.md).

## Reference implementation

`jfe/` is a real, tested, live-verified Python implementation of the
mechanical parts of this workflow -- live journal evidence lookup
(OpenAlex Sources, Crossref Journals), APC/OA classification, hard
filters, and a categorical topic-overlap fit dimension. It supplements
this SKILL.md's reasoning workflow; it does not replace the LLM's own
judgment on soft fit beyond topic overlap, candidate generation,
integrity screening, indexing/quartile verification, or submission
strategy, none of which are implemented in code yet (see CHANGELOG's
"Still not implemented"). Where `jfe/` cannot verify something (e.g.
accepted article types, language policy), it returns `CANNOT_VERIFY`
honestly rather than guessing -- the LLM's own reasoning is still
required to fill those gaps from other evidence. See
`references/evidence-policy.md` for how CANNOT_VERIFY should be handled.

## Reference index

- [references/manuscript-profile.md](references/manuscript-profile.md) — manuscript profile schema, contribution/genre classification
- [references/journal-profile.md](references/journal-profile.md) — journal profile schema, identity resolution
- [references/fit-model.md](references/fit-model.md) — fit dimensions, hard filters, weighting by manuscript type
- [references/candidate-generation.md](references/candidate-generation.md) — candidate discovery and reference-neighborhood analysis
- [references/evidence-policy.md](references/evidence-policy.md) — official vs. observed, evidence hierarchy, provenance, confidence states
- [references/journal-integrity.md](references/journal-integrity.md) — predatory/integrity screening, discontinuation status
- [references/submission-strategy.md](references/submission-strategy.md) — two-stage recommendation, ladders, strategy modes, constraint relaxation
- [references/indexing-metrics.md](references/indexing-metrics.md) — SSCI/SCIE/Scopus/quartile verification, impact metrics
- [references/apc-open-access.md](references/apc-open-access.md) — APC, OA models, no-APC mode
- [references/adaptation-policy.md](references/adaptation-policy.md) — adaptation types, cost, submission readiness, ethics
- [references/integration.md](references/integration.md) — Corpus Builder / Voice Engine / Router integration contracts
- [disciplines/](disciplines/) — per-discipline-family fit emphasis (natural sciences, mathematics, engineering/computing, medicine/health, social sciences, management, law, humanities, education, interdisciplinary)
