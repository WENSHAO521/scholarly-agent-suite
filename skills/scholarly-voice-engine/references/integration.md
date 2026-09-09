# Integration

## Ecosystem responsibilities

```text
Adaptive Model Router     = how the task should be executed
Scholarly Corpus Builder  = what scholarly writing evidence and profiles are
                             available
Scholarly Voice Engine    = how the argument and prose should be constructed
Journal Fit Engine        = where the manuscript belongs and how it should be
                             adapted
```

Do not merge these. This Skill does not decide model/reasoning/delegation
strategy, does not retrieve or build corpora itself when a corpus skill is
available, and does not decide venue placement.

## With the Adaptive Model Router

If a router is active in the environment, it owns model choice, reasoning
effort, context management, and delegation. This Skill only reports needs
that might affect those decisions — e.g., "this is a long-context book-
continuity task," "this step requires citation verification via a retrieval
tool," "this step needs a fresh journal profile" — it never selects a model or
overrides routing instructions itself.

## With the Scholarly Corpus Builder

Request profiles using that Skill's own conceptual contract
(`type=journal|discipline|historical|author`, `target`, `freshness`,
`purpose=scholarly_voice`) and consume what it returns (`PROFILE`,
`PROVENANCE SUMMARY`, `CONFIDENCE`, `LIMITATIONS`, `REFRESH STATUS`) rather
than retrieving or fabricating a corpus profile itself. Full consumption
rules — precedence, OBSERVED/RECOMMENDED/MANDATORY, confidence gating,
standalone fallback — live in `corpus-profile-integration.md`.

## With the Journal Fit Engine

Consume the compact `target_voice_adjustment` or fuller `journal_target`
block that skill hands over — never the full journal corpus, and never a
placement recommendation (this Skill does not decide "where," only "how
written"). Full rules live in `journal-style-adaptation.md`.

## This Skill's own conceptual interface

For a host, orchestrator, or another skill invoking the Voice Engine
directly, the conceptual request/response shape is:

```text
VOICE_REQUEST:
  task = draft | revise | polish | compress | expand | restructure |
         rebuild_argument | journal_adapt | book_chapter | author_voice |
         disciplinary_convert
  discipline = ... | unknown
  genre = ... | unknown
  research_design = ... | unknown
  audience = ... | unknown
  language = en | ...
  editing_mode = surface | structural | argument_reconstruction
  voice_strength = low | medium | high
  author_profile = ... | none
  scholarly_profile = ... | none
  journal_context = ... | none
  constraints = { ... }

VOICE_OUTPUT:
  mode = <task actually performed>
  discipline = ...
  genre = ...
  voice_profile = { primary, secondary, depth }
  integrity_status = PASS | PASS_WITH_LIMITATIONS | REPAIR_REQUIRED |
                      BLOCKED_BY_MISSING_EVIDENCE | BLOCKED_BY_CITATION_UNCERTAINTY
                      | BLOCKED_BY_ARGUMENT_INCONSISTENCY
  limitations = [ ... ]
  output = "<the prose>"
```

This is a conceptual contract for how a caller should phrase a request and
how this Skill should structure its answer internally — not a network API and
not something to serialize or expose in an ordinary user-facing reply; see
`scripts/voice/profile_schema.py` for a lightweight validator over these
shapes. `quality-audit.md` defines the `integrity_status` states in full.

## Out of scope for this Skill

- Acquiring, retrieving, or caching corpus material (that's Corpus Builder).
- Recommending or ranking journals/venues (that's Journal Fit Engine).
- Model/tool routing logic (that's the Router).
- Direct phrase-level imitation of any author, living or historical.
- AI-detector evasion — the human-scholarly-prose rules exist to remove
  generic cadence, not to defeat a classifier.

## Standalone operation

Every integration above is optional. When none of the sibling skills are
present, this Skill drafts and revises scholarly prose using its own
`disciplinary-matrix.md`, `genre-matrix.md`, `research-design-matrix.md`, and
`voice-engine.md` defaults, and states plainly when a decision would have
benefited from a corpus or journal profile it did not have access to.
