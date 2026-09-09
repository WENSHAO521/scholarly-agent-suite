---
name: scholarly-corpus-builder
description: Build provenance-aware scholarly corpora and structured writing profiles from user-authorized, public-domain, metadata, abstract, and lawful open-access sources for discipline, journal, historical-scholar, and author-voice analysis.
---

# Scholarly Corpus Builder

## Purpose

Acquire, verify, filter, normalize, analyze, and cache scholarly source material so
that downstream academic-writing systems (a voice engine, a journal-fit engine, a
book-writing workflow) can learn disciplinary, journal, historical, and author-level
writing characteristics **without repeatedly retrieving unnecessary full text**.

This skill is not a web crawler, a paper downloader, a citation generator, a
literature-review writer, a journal recommender, or a direct-imitation engine. Its
product is a compact, reproducible, source-traceable **profile** of how a scholarly
community, journal, tradition, or individual structures academic writing — not a
warehouse of papers.

Central principle: **retrieve the minimum lawful scholarly material necessary to
derive reusable, source-traceable writing and argument features.**

## When to use this skill

Activate for requests like:

- "Build a corpus for [discipline]."
- "Analyze how [journal] writes."
- "Create a historical scholar profile of [scholar]."
- "Learn my academic writing style from these papers."
- "Study current scholarly conventions in [field]."
- "Compare how Journal A and Journal B structure their articles."
- "Refresh the [journal] profile."
- "Prepare a corpus for a book / article I'm writing."

Do **not** activate for a one-off lookup ("What is the DOI of this article?", "Who
wrote this paper?") — use a normal search/citation tool instead.

## Relationship to other skills

```text
Adaptive Model Router     = how the task should be executed
Scholarly Corpus Builder  = what scholarly material should be acquired and analyzed
Scholarly Voice Engine    = how the academic writing should be structured and voiced
Journal Fit Engine        = where the resulting manuscript may fit
```

This skill contains no model-routing logic and performs no uncontrolled web
crawling on behalf of the voice engine. It hands downstream systems a profile,
a provenance summary, a confidence rating, and a list of limitations — not raw
corpus text. See `references/integration.md`.

## Corpus types

Four corpus types, detailed in their own reference files:

| Type | Purpose | Reference |
|---|---|---|
| Discipline | Current writing conventions of a field | `references/discipline-profile.md` |
| Journal | Observable writing architecture of one venue | `references/journal-profile.md` |
| Historical scholar | Transferable argument mechanics from historical work | `references/historical-profile.md` |
| Author | The user's own established voice | `references/author-profile.md` |

A journal or discipline profile is always an **empirical profile of a sample**,
never a mandatory style — see `references/copyright-boundary.md` and the
Journal Instructions vs Observed Corpus distinction below.

## Workflow

1. **Classify the request** — discipline / journal / historical / author / book /
   comparison / refresh. Determine `purpose` (see `references/corpus-policy.md` §
   Corpus purpose declaration).
2. **Check the Corpus Selection Gate** — is there a cached profile, and is it
   `CURRENT`, `STALE`, `INSUFFICIENT`, or is this a `NEW_TARGET` /
   `USER_REQUESTED_REFRESH`? Reuse a `CURRENT` profile rather than rebuilding.
   See `references/refresh-policy.md`.
3. **Apply the source hierarchy** — Tier 1 user-authorized material first, then
   open metadata, then abstracts, then open full text, then public-domain
   historical sources. Never bypass paywalls or access controls. See
   `references/source-hierarchy.md`.
4. **Apply retrieval minimization** — ask "can metadata answer this?" before
   "can the abstract answer this?" before "is open full text materially
   necessary?" Only escalate tiers when the analytical result would actually
   change.
5. **Sample deliberately** — diversify by year, article type, subfield, and
   author rather than taking the first N results. See sampling ranges in
   `references/corpus-policy.md`.
6. **Verify and record provenance** for every source used — never fabricate a
   DOI, ISSN, year, author list, or license. See
   `references/provenance-schema.md`.
7. **Extract features**, not phrases — sentence, paragraph, argument, evidence,
   section-architecture, claim-calibration, and intellectual-rhythm features.
   See `references/style-feature-schema.md`.
8. **Assemble the profile** using the matching schema in
   `references/journal-profile.md`, `discipline-profile.md`,
   `historical-profile.md`, or `author-profile.md`.
9. **Stop** when the profile is sufficiently supported and additional sources
   would not materially change high-level features (see Stop Rule below).
10. **Return the output contract** (below) — never raw corpus text by default.

## Copyright and access boundary (non-negotiable)

Do not: bypass paywalls or bot protections, use leaked databases, scrape
paywalled full text, store unnecessary full-text corpora, reproduce long
copyrighted passages, build characteristic-phrase imitation libraries, or
construct living-author imitation systems. When access is unavailable, record
metadata, mark `full_text_status = unavailable`, and continue with lawful
evidence. Full policy: `references/copyright-boundary.md`.

## Retrieval minimization and the stop rule

Default is metadata-first, not full-text-first. Stop retrieval when:

```text
requested profile is sufficiently supported
AND additional sources show diminishing feature changes
AND minimum genre/source diversity is achieved
```

Never claim a source count that was not actually retrieved. Track attempted /
retrieved / usable / rejected counts separately (see `references/corpus-policy.md`
§ Corpus build record). Never report fabricated statistics such as "73% of
articles use causal language" unless a real metric was computed from a defined,
recorded corpus — otherwise use descriptive language ("causal claims were
relatively uncommon in the sampled corpus").

## Journal Instructions vs Observed Corpus

Keep these two concepts separate at all times:

- `OFFICIAL_REQUIREMENTS` — word limits, abstract format, reference style,
  article type, as stated in the journal's actual author guidelines.
- `OBSERVED_WRITING_PROFILE` — empirical patterns found in the sampled corpus
  (e.g., "most introductions place the contribution in paragraph 4").

Never present the latter as the former.

## Output contract

Every corpus build or profile retrieval returns:

```text
CORPUS TYPE          e.g. journal
TARGET                e.g. Journal X
PURPOSE                e.g. journal_style
SAMPLE WINDOW           e.g. 2024-2026
SOURCE COUNT            attempted / retrieved / usable
SOURCE TYPES            metadata / abstract / open_full_text / user_supplied / public_domain
SELECTION METHOD        how sampling diversified
PROFILE                  the structured feature profile
PROVENANCE SUMMARY       compact list of sources with verification state
KNOWN BIASES             e.g. OA bias, English-language bias
REFRESH STATUS           CURRENT / AGING / STALE / INCOMPLETE
LIMITATIONS               explicit caveats
```

## Small-corpus honesty

Label profiles built from `n < 5` sources as `illustrative`, and `5–19` as
`limited`. Do not imply statistical certainty from a small or skewed sample.
Record bias factors (OA bias, English-language bias, recency bias, special-issue
bias, author-concentration bias) when material — see `references/corpus-policy.md`.

## Reference index (load only what you need)

- `references/corpus-policy.md` — sampling ranges, sufficiency, build records, biases
- `references/source-hierarchy.md` — tiers 1–5 and escalation rules
- `references/provenance-schema.md` — per-source record schema and verification states
- `references/style-feature-schema.md` — sentence/paragraph/argument/evidence/section/claim/rhythm features
- `references/journal-profile.md` — journal profile schema and sampling rules
- `references/discipline-profile.md` — discipline profile schema
- `references/historical-profile.md` — historical scholar profile schema and safeguards
- `references/author-profile.md` — personal author profile schema and authorization boundary
- `references/copyright-boundary.md` — the hard legal/ethical rules
- `references/refresh-policy.md` — freshness windows, corpus selection gate, incremental refresh, versioning
- `references/integration.md` — how downstream skills (Voice Engine, Journal Fit Engine, Router) should call this skill
- `references/source-adapters.md` — capability matrix and known limitations for the six scholarly-API adapters + user files
- `references/oa-resolution.md` — the access-state resolution sequence and retrieval-depth model
- `references/stability-analysis.md` — the split-corpus stability test and bootstrap resampler

## Tool policy

Use host-native scholarly search/retrieval tools (Crossref, OpenAlex, PubMed,
repository search, web search/fetch) when available rather than implementing
custom scraping. Respect rate limits and tool policies. If a source cannot be
retrieved, classify the failure as `not_found`, `access_restricted`,
`tool_failure`, `metadata_only`, or `license_unknown` and continue — a retrieval
problem is not a reasoning problem, so do not escalate to heavier reasoning to
compensate for it.

## Runtime engine (`scb/`, optional)

When the host provides Python execution, prefer the `scb` package over ad hoc
scraping or hand-rolled parsing — it already implements this file's policy in
code: six adapters (OpenAlex, Crossref, PubMed, PMC, arXiv, DOAJ) plus a local
User File adapter, each declaring only the capabilities it actually supports;
identifier normalization and deduplication; an OA resolver that never probes
hidden URLs or fabricates one; a diversified sampling engine and an explicit
corpus-sufficiency gate; measured style analytics plus a corpus-stability
engine (split-corpus testing, never trusting a profile just because a corpus
exists); profile builders matching every schema in `references/`; and a
Profile Compiler producing `SCHOLARLY_PROFILE_V1` / `VOICE_CONTEXT_V1` /
`JOURNAL_STYLE_CONTEXT_V1` for downstream skills. See `scb/__init__.py` for
the module map, and `scripts/validate_skill.py`'s `check_scb_package` for how
it's kept in sync with the runtime package. Where Python isn't available,
this file's instructions remain fully usable on their own — see README.md
"Runtime requirements".
