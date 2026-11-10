# Scholarly Agent

**English** · [繁體中文](README.zh-TW.md)

An evidence-first AI research assistant for academic work in any discipline.
It helps you go from an idea, a pile of notes, or a draft manuscript to a
well-argued paper and a defensible submission plan, while keeping every
citation, metric, and claim traceable to a real source.

It is a single Agent Skill, `scholarly-agent`, with six built-in modules:
execution planning, research evidence, scholarly writing, publication
strategy, pre-submission peer review, and prose polishing in any language. A dispatcher reads each request and loads only the modules that
request needs, so a quick paragraph edit stays quick and a full
idea-to-submission project gets the whole pipeline.

![Architecture of the Scholarly Agent: requests enter one Skill whose dispatcher answers directly, loads one module, or runs a multi-module workflow recipe across the Model Router, Corpus Builder, Voice Engine, Journal Fit, Peer Review, and Prose Polish modules, which share versioned protocols and one integrity policy and end at a final quality gate.](assets/scholarly-agent-architecture.svg)

> **What it is not.** It is not a one-click paper generator, it does not
> predict acceptance, and it never invents citations, DOIs, quotations,
> journal metrics, or corpus statistics. See [Integrity
> guarantees](#integrity-guarantees).

## What you can ask it

Ask in plain language. The dispatcher picks the matching workflow recipe and
loads only the modules that recipe actually uses (Corpus = Corpus Builder,
Voice = Voice Engine).

| You want to... | Workflow recipe | Modules used |
|---|---|---|
| Turn a research idea into a manuscript | [paper-from-idea](skills/scholarly-agent/references/workflows/paper-from-idea.md) | (Corpus), Voice, (Journal Fit) |
| Turn notes or fragments into a paper | [paper-from-notes](skills/scholarly-agent/references/workflows/paper-from-notes.md) | (Corpus), Voice, (Journal Fit) |
| Write an empirical paper (IMRaD and variants) | [empirical-paper](skills/scholarly-agent/references/workflows/empirical-paper.md) | Corpus, Voice |
| Write a theoretical or conceptual paper | [theory-paper](skills/scholarly-agent/references/workflows/theory-paper.md) | Corpus, Voice |
| Revise a manuscript, including reviewer responses | [revise-manuscript](skills/scholarly-agent/references/workflows/revise-manuscript.md) | Voice, (Corpus), (Journal Fit) |
| Write a narrative literature review | [literature-review](skills/scholarly-agent/references/workflows/literature-review.md) | Corpus, Voice |
| Run a systematic review (PRISMA-style) | [systematic-review](skills/scholarly-agent/references/workflows/systematic-review.md) | Corpus, Voice |
| Write a short commentary or perspective piece | [nature-commentary](skills/scholarly-agent/references/workflows/nature-commentary.md) | Corpus, Voice |
| Plan and draft a whole book | [book-project](skills/scholarly-agent/references/workflows/book-project.md) | Corpus, Voice |
| Write one monograph chapter | [monograph-chapter](skills/scholarly-agent/references/workflows/monograph-chapter.md) | (Corpus), Voice |
| Find suitable journals for a manuscript | [journal-selection](skills/scholarly-agent/references/workflows/journal-selection.md) | Journal Fit, Corpus |
| Adapt a manuscript to a chosen journal | [target-journal-adaptation](skills/scholarly-agent/references/workflows/target-journal-adaptation.md) | Journal Fit, Voice, (Corpus) |
| Learn your own writing voice from past papers | [author-voice-calibration](skills/scholarly-agent/references/workflows/author-voice-calibration.md) | Corpus, Voice |
| Build a discipline, journal, or historical style profile | [corpus-profile-build](skills/scholarly-agent/references/workflows/corpus-profile-build.md) | Corpus |
| Get peer review and an editorial decision before submitting, then revise and answer the reviewers | [pre-submission-review](skills/scholarly-agent/references/workflows/pre-submission-review.md) | Peer Review, (Voice), (Journal Fit), (Corpus) |
| Polish finished text in any language so it no longer reads templated or machine-made | none needed (single module) | Polish |

Modules in parentheses join only when the request calls for them, and the
Model Router can sit under any recipe as an optional execution layer. The
exact routing rules live in
[`routing-matrix.md`](skills/scholarly-agent/references/routing-matrix.md).
A single-step task, such as polishing one section, needs no recipe: the
agent loads just the one module that owns it.

Example prompts:

- "Help me turn this research idea into a manuscript and find a journal."
- "Revise this draft for *Journal X* and draft a response to reviewers."
- "Build a style profile from my last ten articles, then rewrite this
  introduction in my own voice."
- "Which open-access journals in education policy fit this paper, with no
  APC above 2,000 USD?"
- "Review my paper the way three reviewers at *Journal X* would, and tell me
  what the editor would decide."
- "Here is my Zotero export; use it as the starting corpus for a literature
  review."
- "Polish this discussion section so it stops reading like AI wrote it; don't
  touch the citations." (Works the same in Chinese, Japanese, Spanish, or any
  other language.)

## The six modules

| Module | Owns | What it does |
|---|---|---|
| [Model Router](skills/scholarly-agent/modules/adaptive-model-router/MODULE.md) | Execution planning | Decides how a large task is executed: model tier, reasoning effort, when to delegate to subagents, and when escalation is justified. Its roles map onto OpenAI/Codex, Claude, Gemini, or local models. Used only when the host can actually dispatch. |
| [Corpus Builder](skills/scholarly-agent/modules/scholarly-corpus-builder/MODULE.md) | Research evidence | Retrieves open scholarly literature (OpenAlex, Crossref, PubMed/PMC, arXiv, DOAJ, your own files) with provenance, imports and exports reference-manager libraries (Zotero, Mendeley, EndNote via BibTeX, RIS, or CSL-JSON), and builds discipline, journal, historical, and author-voice style profiles. |
| [Voice Engine](skills/scholarly-agent/modules/scholarly-voice-engine/MODULE.md) | Writing and argument | Writes and edits discipline-aware, genre-aware academic prose, calibrates claims, checks citation integrity, and keeps long projects such as books consistent. |
| [Journal Fit](skills/scholarly-agent/modules/journal-fit-engine/MODULE.md) | Publication strategy | Profiles the manuscript, generates candidate journals, applies hard filters (scope, APC, open access, indexing), assesses fit with evidence, and produces a submission strategy. Can read open [POSI](https://github.com/WENSHAO521/posi-data) journal data (citation ranking for about 158,000 journals) as an extra, clearly labelled evidence source. |
| [Peer Review](skills/scholarly-agent/modules/peer-review-engine/MODULE.md) | Pre-submission peer review | An editor desk-screens the manuscript, picks 2–3 reviewers with different lenses (methods, theory, literature, and so on), runs each as an isolated subagent when the host can dispatch, and issues a decision letter from the upheld concerns (not a vote count) with numbered required changes. It can then check your revision and response letter, for as many rounds as you want. Reports and letters read like a real journal's, end with a plain submission-readiness verdict, and carry one closing line saying they were prepared before submission, so they are never mistaken for a journal's decision. |
| [Polish](skills/scholarly-agent/modules/prose-polish-engine/MODULE.md) | Prose polishing (潤色) | Removes the "language watermark" of templated writing in any language: stock connectives, empty emphasis ("plays a crucial role", 「具有重要意義」), inflated vocabulary, formulaic openings and closings, stacked hedges, repeated sentence openers, uniform rhythm. Nine languages have built-in phrase catalogs (English, Chinese, Japanese, Korean, Spanish, French, German, Portuguese, Russian); every other language gets the structural checks and the same procedure. Light, standard, or deep. A check confirms every citation, number, quotation, and formula survived unchanged and flags any hedge or negation that moved. It improves the writing; it does not score text for AI authorship or promise anything about AI detectors. |

The dispatcher itself lives in
[`SKILL.md`](skills/scholarly-agent/SKILL.md). Modules keep separate
responsibilities even inside one Skill: the corpus module never recommends
journals, the voice module never picks models, and so on
([`capability-boundaries.md`](skills/scholarly-agent/shared/capability-boundaries.md)).
Corpus Builder, Voice Engine, Journal Fit, Peer Review, and Polish also ship
tested Python engines (`scb/`, `scripts/voice/`, `jfe/`, `prv/`, `ppe/`) for
the mechanical parts.

## How it works

For every request the dispatcher chooses one of three paths: answer a
trivial question directly, load a single module, or run a multi-module
workflow recipe. In a workflow it reuses fresh results from earlier steps,
carries hard constraints (APC limits, word counts, open-access
requirements) forward, allows one bounded repair pass, and ends in one of
three honest states: `COMPLETE`, `COMPLETE_WITH_LIMITATIONS`, or `BLOCKED`.

![How a request is handled: the dispatcher asks what the deliverable is and which modules it needs, then answers directly, loads one module, or runs a multi-module workflow that selects a recipe, reuses fresh artifacts, carries hard constraints, runs the stages through versioned protocols, and ends at a six-check quality gate with at most one repair pass and an outcome of COMPLETE, COMPLETE_WITH_LIMITATIONS, or BLOCKED.](assets/orchestration-flowchart.svg)

Modules hand work to each other through thirteen versioned JSON Schemas in
[`protocols/`](skills/scholarly-agent/protocols/): `EXECUTION_POLICY_V1`,
`SCHOLARLY_PROFILE_V1`, `VOICE_REQUEST_V1`, `VOICE_CONTEXT_V1`,
`VOICE_OUTPUT_V1`, `MANUSCRIPT_PROFILE_V1`, `TARGET_JOURNAL_PROFILE_V1`,
`JOURNAL_STYLE_CONTEXT_V1`, `CONTINUITY_STATE_V1`, `PROVENANCE_RECORD_V1`,
`REVIEW_REPORT_V1`, `EDITORIAL_DECISION_V1`, and `POLISH_REPORT_V1`. For example, Journal Fit produces a
`JOURNAL_STYLE_CONTEXT_V1` that the Voice Engine consumes, so a journal's
official requirements and its merely observed house style never get mixed
up.

## Install

**As a plugin.** Install this repository through
[`.codex-plugin/plugin.json`](.codex-plugin/plugin.json), or unzip a
release package (`scholarly-agent-suite-v<version>.zip`).

**As a plain Skill.** Copy `skills/scholarly-agent/` into your host's skills
directory. It is self-contained: modules, protocols, shared policy, and
workflow recipes all live inside that one folder.

To check a local checkout:

```bash
pip install pytest jsonschema
python scripts/validate_suite.py   # acceptance checks
pytest tests/                      # tests
```

## Integrity guarantees

These rules apply to every module and are enforced by the final quality
gate
([`integrity-policy.md`](skills/scholarly-agent/shared/integrity-policy.md)):

- No fabricated citations, DOIs, quotations, journal metrics, corpus
  counts, or acceptance probabilities. Anything unverified is labelled as
  such.
- No paywall bypassing or shadow libraries; only open or user-supplied
  sources.
- No imitation of a living author's voice; author-voice calibration is for
  your own writing.
- No AI-detector evasion as a goal.
- A module's unresolved integrity flag is never silently dropped on the way
  to a "complete" result.

## Repository layout

```
skills/scholarly-agent/   the one Skill
  SKILL.md                dispatcher
  modules/                the six modules (MODULE.md + references + engines)
  references/             routing matrix, orchestration state, workflow recipes
  protocols/              JSON Schemas for module handoffs
  shared/                 integrity, provenance, terminology, boundaries
workflows/                generated read-only mirror of the workflow recipes
assets/                   README diagrams (not shipped in the runtime package)
scripts/                  validation, packaging, and workflow-mirror tools
tests/, evals/            tests and dispatch fixtures
docs/                     maintainer documentation
```

## Development and releases

Everything, including all six modules, is developed in this repository.
Until v1.2.1 the modules were separate Skills synced from their own
repositories; v2.0.0 merged them (see [`CHANGELOG.md`](CHANGELOG.md)).
Layout rules, versioning, testing, packaging, and known limitations are in
[`docs/development.md`](docs/development.md). Releases are packaged and
published automatically: merging a new `VERSION` to `master` builds the
runtime ZIP and publishes it as a GitHub release (see
[`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md)).

## Roadmap

New capabilities (next candidates: grant and research-proposal writing) are
added as new modules when each has a
distinct responsibility and enough policy of its own, not merely because a
feature could be split out.

## License

[MIT](LICENSE)
