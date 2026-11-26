# Evidence Policy

## Evidence hierarchy

**Tier 1 — Official journal/publisher pages.** Use for aims and scope,
accepted article types, submission rules, APC, word limits, OA model.

**Tier 2 — Trusted scholarly indexes.** E.g. Crossref, OpenAlex, PubMed,
DOAJ, and Scopus- or Web of Science-derived public metadata where lawfully
accessible. Use for identity resolution, indexing status, and metadata
cross-checks.

**Tier 3 — Recent published articles.** Use for topic fit, method fit, genre
fit, and the observed intellectual conversation — not for official-fact
claims.

**Tier 4 — Secondary journal information** (aggregator listings, third-party
summaries, older cached descriptions). Use cautiously; verify any fact that
matters to the recommendation against a higher tier before relying on it.

Prefer higher tiers for anything that functions as a hard filter or a
practical constraint (APC, article types, indexing, word limits) — soft-fit
observations (recurring topics, typical structure) may reasonably draw on
Tier 3.

## Official vs. observed — see also journal-profile.md

Always keep official facts and observed tendencies in clearly separate
buckets in both internal reasoning and user-facing output. See
[journal-profile.md](journal-profile.md) for the schema-level distinction.

## Current-data requirement

Journal information changes over time. Whenever scope, APC, indexing,
submission rules, article types, publisher identity, or journal
title/status are material to the recommendation, prefer freshly verified
information over a stale description and record `verified_at`.

## Current-information failures

If the official source is inaccessible, do not invent current data. Output
`CURRENT_STATUS_NOT_VERIFIED` for the affected fact and downgrade the
practical-recommendation confidence accordingly — do not silently substitute
a plausible-sounding guess.

## Confidence states

Tag recommendation evidence completeness — not acceptance likelihood — as:

- `HIGH_EVIDENCE` — official scope, article types, and a recent-article
  sample were all checked against current sources.
- `MODERATE_EVIDENCE` — some but not all key facts verified, or verified
  from Tier 2/3 rather than Tier 1.
- `LIMITED_EVIDENCE` — verification was largely unavailable; treat the
  recommendation as provisional and say so.

## Recommendation provenance

For each final candidate, keep (and be ready to show) a provenance record:

```json
{
  "journal": "",
  "official_scope_checked": true,
  "recent_articles_checked": true,
  "article_type_checked": true,
  "apc_checked": false,
  "indexing_checked": true,
  "verified_at": ""
}
```

## Recommendation stability

If re-running a similar analysis on the same manuscript produces radically
different journal candidates without new evidence, treat that as a warning
sign of unstable reasoning, not as legitimate variety. Aim for reproducible
candidate logic and record `selection_basis` (why each candidate entered the
pool) so the reasoning is auditable.

## Manuscript evidence integrity

Do not recommend altering results, sample composition, statistics, theorems,
historical evidence, or legal authorities to fit a journal. Only framing,
structure, and presentation may be adapted — never the underlying findings.
See [adaptation-policy.md](adaptation-policy.md) for the full ethical
boundary list.
