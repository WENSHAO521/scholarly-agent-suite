---
name: scholarly-voice-engine
description: Apply discipline-aware scholarly argument architecture, evidence-disciplined voice synthesis, author calibration, journal-aware adaptation, and long-form academic writing rules for research articles, reviews, commentaries, book chapters, monographs, and interdisciplinary scholarship across the sciences, mathematics, engineering, medicine, social sciences, economics, business, law, humanities, philosophy, history, education, and the arts — including multilingual and corpus/journal-integrated writing. Use for substantive academic drafting or revision; do not use for casual, marketing, or administrative writing.
---

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
`references/integration.md` §Out of scope and `references/quality-audit.md`.

## Invocation boundary

Activate for substantive academic drafting/revision: writing or rewriting an
article/review/commentary/chapter/monograph section, strengthening an
argument, adapting prose to a discipline or journal, improving scholarly
voice, or translating/writing multilingual scholarly prose. Do not activate
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
style, citation behavior, or structure (see `references/disciplinary-matrix.md`
§Inference procedure); otherwise infer and proceed.

## Operating hierarchy

1. Identify the task (draft vs. rewrite vs. polish) and editing mode — see
   `references/editing-modes.md`.
2. Identify **discipline** — `references/disciplinary-matrix.md`, then load
   the matching file in `disciplines/` (and its Economics/Philosophy/History
   subsection where relevant).
3. Identify **genre** — `references/genre-matrix.md`; route to
   `references/review-writing.md` or `references/commentary-writing.md` for
   those families.
4. Identify **research design** — `references/research-design-matrix.md` —
   this sets the claim ceiling independent of discipline.
5. Identify argument architecture for discipline × genre × design —
   `references/argument-architectures.md`, and `references/article-writing.md`
   or `references/book-writing.md` depending on scale (see Book vs. article
   routing below).
6. Identify audience/readability level and language — `references/voice-engine.md`
   §Readability calibration; load `references/multilingual-writing.md` for
   non-English or translation tasks.
7. Choose a **voice profile** — primary + secondary + depth — from
   `references/historical-voice-profiles.md` (abstracted, composite; never
   named-author imitation) and calibrate era with `references/era-calibration.md`.
8. If the user supplies their own prior writing, run
   `references/author-voice-calibration.md`; if `scholarly-corpus-builder` is
   available, consume its profile via `references/corpus-profile-integration.md`
   — apply the stated voice precedence in either case.
9. If a target venue/journal is known and `journal-fit-engine` is available,
   apply `references/journal-style-adaptation.md` within its adaptation
   boundary (framing/structure, never substance).
10. Apply `references/human-scholarly-prose.md` for natural rhythm and
    controlled asymmetry.
11. Run the citation-integrity guard (`references/citation-integrity.md`) and
    the claim-calibration check (`references/claim-calibration.md`) — these
    outrank every voice consideration.
12. Draft or rewrite, respecting the resolved editing intensity
    (`references/editing-modes.md`).
13. Run the argument-integrity tests and final quality audit
    (`references/quality-audit.md`), which also governs long-form continuity
    via `references/continuity-ledger.md` for book-scale work.
14. Resolve to a quality state (`PASS` / `PASS_WITH_LIMITATIONS` /
    `REPAIR_REQUIRED` / `BLOCKED_BY_*`) and apply the repair order before
    returning text, per the stop rule in `references/quality-audit.md`.

Do not narrate this pipeline to the user; just apply it.

## Book vs. article routing

- Cues like "chapter," "monograph," "book," "Chapter N" → load
  `references/book-writing.md` and `references/continuity-ledger.md`. Do not
  also load the full article module.
- Cues like "article," "paper," "manuscript," "journal submission" → load
  `references/article-writing.md`.
- Cues like "review article," "systematic review," "meta-analysis" → also
  load `references/review-writing.md`.
- Cues like "commentary," "perspective," "editorial," "Nature-style essay" →
  also load `references/commentary-writing.md`.
- If ambiguous, ask, or infer from context (e.g., stated word count, journal
  name).

## Discipline modules

Load only the module(s) needed from `disciplines/`: `natural-sciences.md`,
`mathematics-formal.md`, `engineering-computing.md`, `medicine-health.md`,
`social-sciences.md` (includes an Economics subsection),
`business-management.md`, `law.md`, `humanities.md` (includes Philosophy and
History subsections), `education.md`, `arts-design.md`,
`interdisciplinary.md`. Each specifies claim style, argument structures,
evidence norms, citation behavior, first-person conventions, common failure
modes, and recommended voice profiles. See `references/disciplinary-matrix.md`
for routing and for adding a new discipline without touching this file.

For work spanning more than one discipline, load
`references/interdisciplinary-writing.md` alongside each home/secondary
discipline module.

## Voice profiles

Voice is a multi-dimensional profile (sentence length, claim strength,
qualification density, mechanism focus, historical depth, etc.), never a
single label. See `references/voice-engine.md` for the dimension list and how
to combine primary/secondary/depth into a coherent composite. Historical
profiles in `references/historical-voice-profiles.md` describe transferable
*mechanisms* abstracted from named scholars — never characteristic phrases or
quotations to copy.

**Living or contemporary scholars:** never imitate directly. Abstract only
high-level, discipline-general traits into a composite profile. If asked to
"write exactly like [living scholar]," comply with the spirit (channel the
requested traits) but produce an original voice, not a stylistic copy.

## Author voice and external profiles

If the user provides their own prior writing, infer their profile via
`references/author-voice-calibration.md` — it takes priority over any
historical or corpus/journal-derived profile, with disciplinary convention
filling gaps the sample doesn't cover. When `scholarly-corpus-builder` and/or
`journal-fit-engine` are present, consume their outputs via
`references/corpus-profile-integration.md` and
`references/journal-style-adaptation.md` respectively — full precedence
order lives in the former. Do not copy the user's errors forward; do copy
their genuine stylistic choices.

## Terminology and integrity

- When a term (e.g., "institution," "resilience," "validity," "robustness")
  carries different meanings across disciplines, name which meaning is
  intended — see `references/interdisciplinary-writing.md`.
- Never fabricate citations, DOIs, page numbers, quotations, authors,
  statistics, or results — see `references/citation-integrity.md`.
- Never invent quotations attributed to historical or living scholars.
- Never inflate claim strength, novelty, or contribution beyond what the
  material supports — see `references/claim-calibration.md`.
- When rewriting existing scholarship, never silently alter data, results,
  causal claims, sample, method, legal rule, historical fact, definitions, or
  theorem statements — voice edits are subordinate to epistemic accuracy.
- Do not "humanize" prose by degrading it: no deliberately inserted errors,
  typos, logical gaps, or bad citations — see
  `references/human-scholarly-prose.md`.

## Editing modes and output modes

Intensity (`SURFACE_EDIT` / `STRUCTURAL_EDIT` / `ARGUMENT_RECONSTRUCTION`)
and output mode (draft / revise / polish / compress / expand / restructure /
rebuild_argument / journal_adapt / book_chapter / author_voice /
disciplinary_convert) are resolved separately — see
`references/editing-modes.md`. Default to the lightest intensity consistent
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

| File | Loads when you need... |
|---|---|
| `references/voice-engine.md` | The voice-dimension schema and how to compose profiles |
| `references/disciplinary-matrix.md` | Routing to the right discipline module(s) |
| `references/genre-matrix.md` | The genre list and its defining features |
| `references/research-design-matrix.md` | Design-driven claim ceilings, independent of discipline |
| `references/argument-architectures.md` | Section-by-section argument shapes per genre family |
| `references/claim-calibration.md` | Claim types, the claim-strength invariant, uncertainty language |
| `references/citation-integrity.md` | No-fabrication rules, citation preservation, quotation discipline |
| `references/human-scholarly-prose.md` | Anti-generic-AI prose rules, rhythm, transitions |
| `references/quality-audit.md` | Integrity tests, quality states, repair order, stop rule |
| `references/historical-voice-profiles.md` | Abstracted historical scholarly profiles and composite voices |
| `references/era-calibration.md` | Adjusting prose for the intellectual era being emulated |
| `references/author-voice-calibration.md` | Inferring and prioritizing the user's own voice |
| `references/corpus-profile-integration.md` | Consuming a scholarly-corpus-builder profile |
| `references/journal-style-adaptation.md` | Consuming a journal-fit-engine adaptation target |
| `references/article-writing.md` | Article-scale drafting/rewriting |
| `references/review-writing.md` | Narrative/systematic/scoping/meta-analysis/critical/synthesis reviews |
| `references/commentary-writing.md` | Commentary, perspective, editorial, Nature-style essays |
| `references/book-writing.md` | Book/chapter-scale drafting, monograph continuity |
| `references/continuity-ledger.md` | Concept/claim/evidence/chapter ledger mechanics |
| `references/multilingual-writing.md` | Non-English and translation-mode scholarly writing |
| `references/editing-modes.md` | Editing intensity and output-mode definitions |
| `references/interdisciplinary-writing.md` | Combining disciplines without collision |
| `references/integration.md` | Ecosystem contract with the Router, Corpus Builder, Journal Fit Engine |

See `evals/` for worked test cases and `scripts/validate_skill.py` for
structural validation of this Skill's own files.
