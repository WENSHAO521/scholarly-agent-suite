# Integration

Sections (each starts at an `<a id>` anchor; read only the one the task needs): [integration](#integration), [corpus-profile-integration](#corpus-profile-integration), [journal-style-adaptation](#journal-style-adaptation).

<a id="integration"></a>

## Integration

### Ecosystem responsibilities

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

### With the Adaptive Model Router

If a router is active in the environment, it owns model choice, reasoning
effort, context management, and delegation. This Skill only reports needs
that might affect those decisions — e.g., "this is a long-context book-
continuity task," "this step requires citation verification via a retrieval
tool," "this step needs a fresh journal profile" — it never selects a model or
overrides routing instructions itself.

### With the Scholarly Corpus Builder

Request profiles using that Skill's own conceptual contract
(`type=journal|discipline|historical|author`, `target`, `freshness`,
`purpose=scholarly_voice`) and consume what it returns (`PROFILE`,
`PROVENANCE SUMMARY`, `CONFIDENCE`, `LIMITATIONS`, `REFRESH STATUS`) rather
than retrieving or fabricating a corpus profile itself. Full consumption
rules — precedence, OBSERVED/RECOMMENDED/MANDATORY, confidence gating,
standalone fallback — live in `integration.md#corpus-profile-integration`.

### With the Journal Fit Engine

Consume the compact `target_voice_adjustment` or fuller `journal_target`
block that skill hands over — never the full journal corpus, and never a
placement recommendation (this Skill does not decide "where," only "how
written"). Full rules live in `integration.md#journal-style-adaptation`.

### This Skill's own conceptual interface

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
shapes. `quality-and-editing.md#quality-audit` defines the `integrity_status` states in full.

### Optional scholarly-agent-suite protocol compatibility

This Skill's own conceptual interface above is authoritative and works fully
standalone. `scripts/voice/profile_schema.py` additionally provides
`from_voice_request_v1()` and `to_voice_output_v1()`: an optional, additive
translation layer for a host speaking the Suite's narrower orchestration
envelopes (`VOICE_REQUEST_V1`, `VOICE_OUTPUT_V1` —
`scholarly-agent-suite/protocols/`). This Skill never requires the Suite or
these protocols; a direct/standalone caller uses this Skill's own richer
fields instead.

Known, audited compatibility state (2026-09):

- **VOICE_REQUEST_V1 / VOICE_OUTPUT_V1** — bridged by the adapters above.
  `VOICE_REQUEST_V1`'s `task` enum maps onto this Skill's own `OUTPUT_MODES`
  (adding `audit` as a mode: a read-only quality-audit pass, distinct from
  the audit step every other mode already runs before returning text). This
  Skill's two citation/argument-specific `integrity_status` values collapse
  onto the nearest `VOICE_OUTPUT_V1` `validation_state`, recorded in
  `limitations` so nothing is silently lost.
- **SCHOLARLY_PROFILE_V1** — `profile_schema.py`'s `CONFIDENCE_LEVELS` uses
  `high | moderate | low`, matching both this protocol and
  `scholarly-corpus-builder`'s actual output (an earlier `medium` value here
  was a real defect: it would have rejected genuine corpus-builder profiles).
- **VOICE_CONTEXT_V1** — compatible in substance (`discipline`/`genre`/
  `research_design` align); the protocol's `author_voice` field name maps to
  this Skill's `author_profile`.
- **JOURNAL_STYLE_CONTEXT_V1** — **reconciled (2026-09).** `journal-fit-engine`
  v0.3.0 now emits this protocol directly (`jfe.style_context`); this Skill
  consumes it via `scripts/voice/journal_context.py`
  (`from_journal_style_context_v1()` / `apply_journal_style_context()`),
  rather than deriving an adaptation-target shape from it. The two buckets
  are handled on two different paths, matching
  `integration.md#corpus-profile-integration`'s precedence order exactly:
  `official_requirements` becomes `hard_requirements` — returned verbatim,
  never confidence-gated, never merged into the layered voice-precedence
  resolution; `observed_patterns` is fed into
  `profile_merge.resolve_voice_precedence()` as the existing "journal"
  layer, confidence-gated by the envelope's `freshness`
  (`current`→high, `aging`→moderate, `stale`/absent→low — never silently
  treated as current). See `integration.md#journal-style-adaptation` for the full
  consumption rules. This Skill's older `journal_context`
  (`validate_journal_target()`, the compact/full adaptation-target shape)
  remains supported unchanged for a caller that has already derived
  writing-level adjustments itself and wants to hand those over directly —
  the two input shapes are not mutually exclusive.
- **CONTINUITY_STATE_V1** — implemented (2026-09). `scripts/voice/
  continuity.py`'s `ContinuityLedger.to_dict()`/`from_dict()` serialize to
  and restore from a `CONTINUITY_STATE_V1` envelope, so it can genuinely be
  saved and passed between chapter-drafting sessions. `concept_ledger`/
  `claim_ledger` round-trip through this class's own active
  redefinition/contradiction checking (a restored ledger still raises
  `ContinuityConflict` the same way); `voice_contract`/`evidence_ledger`/
  `chapter_ledger`/`terminology`/`open_questions` round-trip opaquely --
  stored and returned unchanged, not yet validated or acted on by this
  class.

### Out of scope for this Skill

- Acquiring, retrieving, or caching corpus material (that's Corpus Builder).
- Recommending or ranking journals/venues (that's Journal Fit Engine).
- Model/tool routing logic (that's the Router).
- Direct phrase-level imitation of any author, living or historical.
- AI-detector evasion — the human-scholarly-prose rules exist to remove
  generic cadence, not to defeat a classifier.

### Standalone operation

Every integration above is optional. When none of the sibling skills are
present, this Skill drafts and revises scholarly prose using its own
`argument-and-claims.md#disciplinary-matrix`, `writing-genres.md#genre-matrix`, `argument-and-claims.md#research-design-matrix`, and
`voice-profiles.md#voice-engine` defaults, and states plainly when a decision would have
benefited from a corpus or journal profile it did not have access to.

<a id="corpus-profile-integration"></a>

## Corpus Profile Integration

How this Skill consumes a profile from `scholarly-corpus-builder` when that
Skill is present in the environment. This file does not redefine that
Skill's schemas — it describes how the Voice Engine requests, weighs, and
applies what comes back. See `references/integration.md` for the ecosystem-
level relationship and `integration.md#journal-style-adaptation` for the journal-fit-
engine side of profile integration.

### Requesting a profile

Use `scholarly-corpus-builder`'s own conceptual request shape rather than
inventing a new one:

```text
GET_PROFILE:
  type = journal | discipline | historical | author
  target = <journal name / discipline / scholar / "user">
  freshness = current | refresh
  purpose = scholarly_voice
```

This is a conceptual contract, not a network API — phrase the request this
way to a host or delegate to that Skill; do not build a service around it.
Request the minimum needed: a discipline-family voice question rarely needs a
fresh journal-level pull, and a single-chapter book task rarely needs a full
40–100-source discipline sample.

### What comes back

`scholarly-corpus-builder` returns a derived profile, not raw sources:

```text
PROFILE               the structured feature profile (see that Skill's
                       style-feature-schema.md: sentence/paragraph/argument/
                       evidence/section/claim-calibration/rhythm features)
PROVENANCE SUMMARY     compact source list with verification state
CONFIDENCE             high | moderate | low — never a fabricated percentage
LIMITATIONS            explicit caveats (sample size, bias, staleness)
REFRESH STATUS         CURRENT | AGING | STALE | INCOMPLETE
```

Small-corpus honesty carries through: a profile built from `n < 5` sources is
`illustrative`, `5–19` is `limited` — do not draft as if either were a
statistically confident population estimate.

### Voice precedence

Match `scholarly-corpus-builder`'s own stated precedence exactly — do not
invent a competing order:

```text
user author profile
  → discipline conventions
    → target journal observed profile
      → selected historical/abstract voice profile
```

A journal's observed profile must never erase the user's own established
voice, and a historical/abstract profile must never override current
disciplinary norms. See `voice-profiles.md#author-voice-calibration` for how the author
layer itself is derived and prioritized.

### OBSERVED, RECOMMENDED, and MANDATORY — never conflate

Three different categories of input, kept visibly separate in your own
reasoning even when not all are surfaced to the user:

```text
OBSERVED     an empirical pattern in a corpus/journal sample
             e.g., "sampled introductions average 900 words"
RECOMMENDED  this Skill's own stylistic suggestion drawn from OBSERVED data
             e.g., "consider a shorter introduction"
MANDATORY    an explicit, authoritative instruction (the author's own
             instruction, or a journal's actual submission requirement)
             e.g., "structured abstract required"
```

An OBSERVED pattern earns, at most, a RECOMMENDED adjustment — never treat it
as MANDATORY. This mirrors `scholarly-corpus-builder`'s own
`OBSERVED_WRITING_PROFILE` vs. `OFFICIAL_REQUIREMENTS` distinction and
`journal-fit-engine`'s `OBSERVED ARTICLE PROFILE` vs. `OFFICIAL JOURNAL DATA`
— do not blur what that Skill has already kept separate.

### Confidence and stability gating

Weight a feature's influence on drafting by its reported confidence, not by
how specific or quotable it sounds:

```text
high confidence, consistent across sample   → may strongly inform drafting
low confidence or small/skewed sample       → weak influence only; note the
                                               uncertainty rather than acting
                                               on it as settled
```

Example: `first_person = medium, confidence = high` may meaningfully shift a
drafting choice. `counterargument_frequency = high, confidence = low` should
not visibly change the output — treat it as a hypothesis, not a rule.

### Conflict resolution

When two inputs disagree (e.g., the author profile shows low first-person use
but the target-journal profile shows medium), do not average them
mechanically. Apply the precedence order above, then look for a principled
compromise at the boundary — e.g., retain the author's restrained first-person
habit but permit it specifically where methodological agency aids clarity —
rather than splitting the difference numerically. See
`scripts/voice/profile_merge.py` for a worked implementation of this
resolution logic.

### Author-profile incremental updates and edit-diff learning

When the corpus-builder skill (or the user directly) supplies updated author
material over time, classify each observed trait as:

```text
stable | strengthening | weakening | new | uncertain
```

A single anomalous manuscript should not overwrite a long-established trait —
require repeated evidence before reclassifying a `stable` trait as
`weakening`.

If the host authorizes comparing an AI draft against the user's own revision
of it, extract recurring preferences from the diff (e.g., consistently
shortened introductions, reduced hedging, more explicit mechanism language,
fewer generic transitions) and fold them into the author profile going
forward. This is calibration to the user's genuine preferences, never framed
or used as AI-detector evasion.

### What must not be preserved

Never preserve, from any profile, an author's or corpus's own defects:
citation errors, unsupported claims, inconsistent terminology, logical gaps,
or grammar mistakes. Separate **voice trait** (preserve) from **quality
defect** (correct) — `scholarly-corpus-builder`'s own author-profile schema
makes exactly this distinction (`do_not_preserve`) and this Skill honors it.

### Standalone fallback

If `scholarly-corpus-builder` is not present or does not return a profile,
proceed using this Skill's own internal discipline/genre defaults
(`argument-and-claims.md#disciplinary-matrix` / `disciplines.md`) rather than blocking the task.
Note to the user, only if it materially matters, that drafting proceeded
without a corpus-derived profile.

<a id="journal-style-adaptation"></a>

## Journal Style Adaptation

How this Skill consumes an adaptation target from `journal-fit-engine` when
that Skill is present. Journal Fit Engine decides *where* a manuscript might
belong and hands this Skill a compact target profile; it does not perform the
rewrite itself — that is this Skill's job. See `references/integration.md`
for the ecosystem-level relationship.

### What journal-fit-engine sends

As of journal-fit-engine v0.3.0, the primary handoff is a
`JOURNAL_STYLE_CONTEXT_V1` envelope (`jfe.style_context`,
`scholarly-agent-suite/protocols/journal-style-context.schema.json`),
consumed here via `scripts/voice/journal_context.py`:

```yaml
protocol: JOURNAL_STYLE_CONTEXT_V1
journal_name: Journal of Example Studies
official_requirements: { word_limit: 8000, citation_style: APA7 }
observed_patterns: { tone: formal, contribution_placement_observed: early }
freshness: current | aging | stale
```

`official_requirements` becomes a `hard_requirements` block: apply it as
stated, never confidence-gated, never silently dropped or overridden by
anything else in this reference. `observed_patterns` is fed into the
existing author→discipline→journal→historical precedence resolution
(`integration.md#corpus-profile-integration`) as the "journal" layer, with its
confidence set from `freshness` — a `stale` or absent freshness gates it
down to low confidence exactly as an already-low-confidence journal
profile would be gated (`integration.md#corpus-profile-integration` §Conflict
resolution), so it yields to a lower-precedence layer rather than silently
winning on stale evidence.

Older callers (or a caller that has already derived writing-level
adjustments itself, e.g. from its own reasoning over a
`JOURNAL_STYLE_CONTEXT_V1`) may instead hand over the compact form:

```yaml
target_voice_adjustment:
  contribution_position: earlier
  mechanism_visibility: higher
  policy_implication: medium
  sentence_density: moderate
```

or the fuller form:

```yaml
journal_target:
  genre: empirical_social_science
  contribution_position: early
  theory_density: medium_high
  policy_implications: high
  methods_transparency: high
  introduction_length: moderate
```

Treat these field names as authoritative — do not rename them or invent
additional fields on this Skill's side. If a host or user supplies a journal
name without going through `journal-fit-engine`, either request the profile
from that Skill (if present) or ask the user for the journal's actual
instructions rather than guessing its house style from the name alone.

### Adaptation boundary — framing and structure only

Journal adaptation may change:

```text
contribution placement | section order | abstract architecture | technical
density | policy/clinical-implication emphasis | discussion structure |
word count | reference style
```

It must never change:

```text
results | data | findings | study design | sample | statistical values |
historical facts | legal authority | theorem statements | definitions
```

This matches `journal-fit-engine`'s own adaptation policy verbatim ("never
recommend changing the scientific findings, data, results, sample, or
legal/historical evidence to fit a journal") — this Skill enforces the same
line at the point where the actual rewrite happens.

### Observed style is not destiny

A `journal_target` reflects an **observed** pattern in that journal's own
recent articles (see `integration.md#corpus-profile-integration` §OBSERVED, RECOMMENDED,
MANDATORY). Compress toward it when doing so doesn't damage the argument —
but do not gut a theoretical section the manuscript genuinely needs merely to
match a shorter median article length. If following the target would require
cutting something the argument depends on, say so rather than silently
complying.

### Precedence against author and discipline

A journal-observed target sits below the user's own established voice and
current disciplinary convention in the overall precedence order (see
`integration.md#corpus-profile-integration` §Voice precedence). Use the journal target to
adjust structure and emphasis; do not let it flatten the author's genuine
voice or override a discipline's non-negotiable evidentiary norms (e.g., a
journal's typically shorter methods section never licenses omitting
information a clinical design requires for critical appraisal).

### What this Skill returns

After adapting, report back (conceptually, for a caller like
`journal-fit-engine` or the user) which target fields were actually applied,
which were not applied and why (usually: would have required changing
substance), and any residual mismatch the user should know about before
submitting.

### Standalone fallback

If `journal-fit-engine` is not present, adapt only from explicit information
the user supplies (e.g., a pasted "Instructions for Authors" page) and mark
anything else as unknown rather than inferring a journal's house style from
its name or reputation.
