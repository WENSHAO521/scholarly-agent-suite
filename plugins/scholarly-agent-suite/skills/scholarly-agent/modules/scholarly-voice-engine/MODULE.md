<!-- Module of the scholarly-agent Skill (formerly the standalone `scholarly-voice-engine` Skill).
     Loaded on demand by ../../SKILL.md; paths below are relative to this module's directory. -->

> **Module `scholarly-voice-engine`** -- part of the single `scholarly-agent` Skill. Load this file only when the
> dispatcher in `SKILL.md` selects this module. Wherever this file says "this Skill" or names
> another former Skill (e.g. `scholarly-voice-engine`), read it as "this module" / the sibling
> module at `modules/<name>/`. Paths such as `references/...` are relative to `modules/scholarly-voice-engine/`.
>
> Scope: Apply discipline-aware scholarly argument architecture, evidence-disciplined voice synthesis, author calibration, journal-aware adaptation, and long-form academic writing rules for research articles, reviews, commentaries, book chapters, monographs, and interdisciplinary scholarship across the sciences, mathematics, engineering, medicine, social sciences, economics, business, law, humanities, philosophy, history, education, and the arts — including multilingual and corpus/journal-integrated writing. Use for substantive academic drafting or revision; do not use for casual, marketing, or administrative writing.

# Scholarly Voice Engine

Cross-disciplinary scholarly argument architecture, voice synthesis, and
human academic prose.

## What this Skill does

Produces or rewrites scholarly text — articles, reviews, commentaries, book
chapters, monographs, theoretical/empirical writing — so it reads like a
serious human scholar in the target field, not generic AI academic prose. It
calibrates *voice* (how claims are made, hedged, evidenced, and connected)
and *argument architecture* (how the reasoning actually moves), not just
vocabulary.

> Scholarly voice is not a collection of elegant sentences. It is the
> observable relationship between concepts, claims, evidence, uncertainty,
> counterargument, intellectual progression, and authorial judgment.

## Core principle

Learn transferable scholarly writing mechanisms from intellectual traditions
and distinguished scholars, then synthesize them into original,
discipline-appropriate prose. Never imitate a specific living author's style
directly, and never compromise factual/evidentiary integrity for the sake of
voice. This Skill is not a celebrity-phrase generator, an AI-detector-evasion
tool, a citation fabricator, or a verbosity generator — see
`references/integration.md` §Out of scope and `references/quality-and-editing.md#quality-audit`.

## Invocation boundary

Activate for substantive academic drafting/revision: writing or rewriting an
article/review/commentary/chapter/monograph section, strengthening an
argument, adapting prose to a discipline or journal, improving scholarly
voice, or writing multilingual scholarly prose. Translating a finished text
into another language belongs to the sibling module `translation-engine`;
this module drafts and revises in whatever language the user writes in. Do not activate
for ordinary email, casual text, basic non-scholarly translation, a simple
factual question, or social-media copy — unless academic prose is actually
the task's main content.

## Task interpretation

Before drafting, resolve as much of this as the request supports — leave the
rest `unknown` rather than guessing or fabricating:

```yaml
discipline:
subdiscipline:
genre:
research_design:
argument_type:
audience:
language: en
target_venue:
target_length:
current_stage:        # notes/outline, draft, revision, polish
user_goal:
available_evidence:
author_profile_available:
scholarly_profile_available:   # from scholarly-corpus-builder, if present
journal_context_available:     # from journal-fit-engine, if present
```

Ask only when a genuinely ambiguous field would materially change claim
style, citation behavior, or structure (see `references/argument-and-claims.md#disciplinary-matrix`
§Inference procedure); otherwise infer and proceed.

## Operating hierarchy

1. Identify the task (draft vs. rewrite vs. polish) and editing mode — see
   `references/quality-and-editing.md#editing-modes`.
2. Identify **discipline** — `references/argument-and-claims.md#disciplinary-matrix`, then load
   the matching section of `disciplines.md` (and its Economics/Philosophy/History
   subsection where relevant).
3. Identify **genre** — `references/writing-genres.md#genre-matrix`; route to
   `references/writing-genres.md#review-writing` or `references/writing-genres.md#commentary-writing` for
   those families.
4. Identify **research design** — `references/argument-and-claims.md#research-design-matrix` —
   this sets the claim ceiling independent of discipline.
5. Identify argument architecture for discipline × genre × design —
   `references/argument-and-claims.md#argument-architectures`, and `references/writing-genres.md#article-writing`
   or `references/writing-genres.md#book-writing` depending on scale (see Book vs. article
   routing below).
6. Identify audience/readability level and language — `references/voice-profiles.md#voice-engine`
   §Readability calibration; load `references/voice-profiles.md#multilingual-writing` for
   non-English writing (a translation of finished text goes to `translation-engine`).
7. Choose a **voice profile** — primary + secondary + depth — from
   `references/voice-profiles.md#historical-voice-profiles` (abstracted, composite; never
   named-author imitation) and calibrate era with `references/voice-profiles.md#era-calibration`.
8. If the user supplies their own prior writing, run
   `references/voice-profiles.md#author-voice-calibration`; if `scholarly-corpus-builder` is
   available, consume its profile via `references/integration.md#corpus-profile-integration`
   — apply the stated voice precedence in either case.
9. If a target venue/journal is known and `journal-fit-engine` is available,
   apply `references/integration.md#journal-style-adaptation` within its adaptation
   boundary (framing/structure, never substance).
10. Apply `references/quality-and-editing.md#human-scholarly-prose` for natural rhythm and
    controlled asymmetry.
11. Run the citation-integrity guard (`references/argument-and-claims.md#citation-integrity`) and
    the claim-calibration check (`references/argument-and-claims.md#claim-calibration`) — these
    outrank every voice consideration.
12. Draft or rewrite, respecting the resolved editing intensity
    (`references/quality-and-editing.md#editing-modes`).
13. Run the argument-integrity tests and final quality audit
    (`references/quality-and-editing.md#quality-audit`), which also governs long-form continuity
    via `references/quality-and-editing.md#continuity-ledger` for book-scale work.
14. Resolve to a quality state (`PASS` / `PASS_WITH_LIMITATIONS` /
    `REPAIR_REQUIRED` / `BLOCKED_BY_*`) and apply the repair order before
    returning text, per the stop rule in `references/quality-and-editing.md#quality-audit`.

Do not narrate this pipeline to the user; just apply it.

## Book vs. article routing

- Cues like "chapter," "monograph," "book," "Chapter N" → load
  `references/writing-genres.md#book-writing` and `references/quality-and-editing.md#continuity-ledger`. Do not
  also load the full article module.
- Cues like "article," "paper," "manuscript," "journal submission" → load
  `references/writing-genres.md#article-writing`.
- Cues like "review article," "systematic review," "meta-analysis" → also
  load `references/writing-genres.md#review-writing`.
- Cues like "commentary," "perspective," "editorial," "Nature-style essay" →
  also load `references/writing-genres.md#commentary-writing`.
- If ambiguous, ask, or infer from context (e.g., stated word count, journal
  name).

## Discipline modules

Load only the section(s) needed from `disciplines.md` (one section per family,
anchored by slug): `natural-sciences`, `mathematics-formal`,
`engineering-computing`, `medicine-health`, `social-sciences` (includes an
Economics subsection), `business-management`, `law`, `humanities` (includes
Philosophy and History subsections), `education`, `arts-design`,
`interdisciplinary`. Each specifies claim style, argument structures,
evidence norms, citation behavior, first-person conventions, common failure
modes, and recommended voice profiles. See `references/argument-and-claims.md#disciplinary-matrix`
for routing and for adding a new discipline without touching this file.

For work spanning more than one discipline, load
`references/writing-genres.md#interdisciplinary-writing` alongside each home/secondary
discipline module.

## Voice profiles

Voice is a multi-dimensional profile (sentence length, claim strength,
qualification density, mechanism focus, historical depth, etc.), never a
single label. See `references/voice-profiles.md#voice-engine` for the dimension list and how
to combine primary/secondary/depth into a coherent composite. Historical
profiles in `references/voice-profiles.md#historical-voice-profiles` describe transferable
*mechanisms* abstracted from named scholars — never characteristic phrases or
quotations to copy.

**Living or contemporary scholars:** never imitate directly. Abstract only
high-level, discipline-general traits into a composite profile. If asked to
"write exactly like [living scholar]," comply with the spirit (channel the
requested traits) but produce an original voice, not a stylistic copy.

## Author voice and external profiles

If the user provides their own prior writing, infer their profile via
`references/voice-profiles.md#author-voice-calibration` — it takes priority over any
historical or corpus/journal-derived profile, with disciplinary convention
filling gaps the sample doesn't cover. When `scholarly-corpus-builder` and/or
`journal-fit-engine` are present, consume their outputs via
`references/integration.md#corpus-profile-integration` and
`references/integration.md#journal-style-adaptation` respectively — full precedence
order lives in the former. Do not copy the user's errors forward; do copy
their genuine stylistic choices.

## Terminology and integrity

- When a term (e.g., "institution," "resilience," "validity," "robustness")
  carries different meanings across disciplines, name which meaning is
  intended — see `references/writing-genres.md#interdisciplinary-writing`.
- Never fabricate citations, DOIs, page numbers, quotations, authors,
  statistics, or results — see `references/argument-and-claims.md#citation-integrity`.
- Never invent quotations attributed to historical or living scholars.
- Never inflate claim strength, novelty, or contribution beyond what the
  material supports — see `references/argument-and-claims.md#claim-calibration`.
- When rewriting existing scholarship, never silently alter data, results,
  causal claims, sample, method, legal rule, historical fact, definitions, or
  theorem statements — voice edits are subordinate to epistemic accuracy.
- Do not "humanize" prose by degrading it: no deliberately inserted errors,
  typos, logical gaps, or bad citations — see
  `references/quality-and-editing.md#human-scholarly-prose`.

## Editing modes and output modes

Intensity (`SURFACE_EDIT` / `STRUCTURAL_EDIT` / `ARGUMENT_RECONSTRUCTION`)
and output mode (draft / revise / polish / compress / expand / restructure /
rebuild_argument / journal_adapt / book_chapter / author_voice /
disciplinary_convert) are resolved separately — see
`references/quality-and-editing.md#editing-modes`. Default to the lightest intensity consistent
with the request.

## Ecosystem position

```text
Adaptive Model Router     = how the task should be executed
Scholarly Corpus Builder  = what scholarly writing evidence and profiles are
                             available
Scholarly Voice Engine    = how the argument and prose should be constructed
Journal Fit Engine        = where the manuscript belongs and how it should be
                             adapted
```

This Skill is standalone and does not perform model routing, corpus
retrieval, or venue recommendation. See `references/integration.md` for the
full ecosystem contract, including this Skill's own conceptual
`VOICE_REQUEST` / `VOICE_OUTPUT` shape for callers.

## Reference index

Reference files are grouped (five files); each section starts at an `<a id>`
anchor, so read only the section you need.

| Section | Loads when you need... |
|---|---|
| `references/voice-profiles.md#voice-engine` | The voice-dimension schema and how to compose profiles |
| `references/argument-and-claims.md#disciplinary-matrix` | Routing to the right discipline module(s) |
| `references/writing-genres.md#genre-matrix` | The genre list and its defining features |
| `references/argument-and-claims.md#research-design-matrix` | Design-driven claim ceilings, independent of discipline |
| `references/argument-and-claims.md#argument-architectures` | Section-by-section argument shapes per genre family |
| `references/argument-and-claims.md#claim-calibration` | Claim types, the claim-strength invariant, uncertainty language |
| `references/argument-and-claims.md#citation-integrity` | No-fabrication rules, citation preservation, quotation discipline |
| `references/quality-and-editing.md#human-scholarly-prose` | Anti-generic-AI prose rules, rhythm, transitions |
| `references/quality-and-editing.md#quality-audit` | Integrity tests, quality states, repair order, stop rule |
| `references/voice-profiles.md#historical-voice-profiles` | Abstracted historical scholarly profiles and composite voices |
| `references/voice-profiles.md#era-calibration` | Adjusting prose for the intellectual era being emulated |
| `references/voice-profiles.md#author-voice-calibration` | Inferring and prioritizing the user's own voice |
| `references/integration.md#corpus-profile-integration` | Consuming a scholarly-corpus-builder profile |
| `references/integration.md#journal-style-adaptation` | Consuming a journal-fit-engine adaptation target |
| `references/writing-genres.md#article-writing` | Article-scale drafting/rewriting |
| `references/writing-genres.md#review-writing` | Narrative/systematic/scoping/meta-analysis/critical/synthesis reviews |
| `references/writing-genres.md#commentary-writing` | Commentary, perspective, editorial, Nature-style essays |
| `references/writing-genres.md#book-writing` | Book/chapter-scale drafting, monograph continuity |
| `references/quality-and-editing.md#continuity-ledger` | Concept/claim/evidence/chapter ledger mechanics |
| `references/voice-profiles.md#multilingual-writing` | Non-English scholarly writing; translation principles (full translation: `translation-engine`) |
| `references/quality-and-editing.md#editing-modes` | Editing intensity and output-mode definitions |
| `references/writing-genres.md#interdisciplinary-writing` | Combining disciplines without collision |
| `references/integration.md` | Ecosystem contract with the Router, Corpus Builder, Journal Fit Engine |

Worked test cases live in the Suite repository's `evals/modules/scholarly-voice-engine/`,
and `tests/modules/voice/` plus `scripts/validate_suite.py` validate this module
(repository only, not shipped in the runtime ZIP).
