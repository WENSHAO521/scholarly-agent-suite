# Quality, editing, and continuity

Sections (each starts at an `<a id>` anchor; read only the one the task needs): [quality-audit](#quality-audit), [human-scholarly-prose](#human-scholarly-prose), [editing-modes](#editing-modes), [continuity-ledger](#continuity-ledger).

<a id="quality-audit"></a>

## Quality Audit

The final pass before returning scholarly text, and the vocabulary for
talking about what's still wrong when it isn't ready. This file adds
integrity-focused tests, quality states, repair ordering, and a stop rule on
top of `quality-and-editing.md#human-scholarly-prose`'s own prose-level quality audit (sentence/
paragraph rhythm, transitions, terminology stability) — read that file's
§Quality audit first; this one does not repeat it.

### Redundancy audit

Distinct from useful long-form recurrence (see `quality-and-editing.md#continuity-ledger`
§Repetition control). Flag:

```text
the same claim restated as if new | the same citation cluster reused for an
unrelated point | the same contribution restated in multiple places | the
same definition repeated verbatim rather than referenced back | the same
transition device reused mechanically across sections
```

### Reviewer-aware self-test

Before finalizing, silently ask (do not stage a theatrical fake review in the
output — see `writing-genres.md#article-writing` §Reviewer-aware tightening):

```text
What would a skeptical specialist in this field challenge first?
Which assumption is doing unstated work?
Which claim is broader than the cited evidence actually supports?
Where is a construct or term used unstably?
What alternative explanation survives the evidence presented?
Is a limitation being minimized or hidden rather than stated?
```

### Substantive integrity tests

Run whichever of these apply to the piece's claims:

```yaml
mechanism_test: >
  A claimed mechanism needs an actor/process, a link, an intermediate step,
  and an observable implication. A sequence of correlated variables is not
  automatically a mechanism — if the text asserts "mechanism" but supplies
  only correlation, either supply the missing step or downgrade the claim
  (associational, not mechanistic — see argument-and-claims.md#claim-calibration).
theory_test: >
  A list of variables is not a theory. Theory requires explanatory logic
  connecting constructs, not just their co-occurrence.
causal_test: >
  Verify the research design actually licenses causal language before
  allowing it (argument-and-claims.md#research-design-matrix). If unclear, downgrade rather than
  invent a justification.
humanities_interpretation_test: >
  Interpretive claims need source/text evidence, context, and stated
  reasoning — legitimate interpretive confidence is not the same as
  empirical certainty, and should not be dressed in empirical-certainty
  language.
normative_argument_test: >
  Separate the empirical premise, the normative premise, the value judgment,
  and the institutional consequence — especially in political theory,
  ethics, law, and policy writing. An empirical premise smuggled in as
  self-evident is a defect, not a rhetorical economy.
scientific_mechanism_test: >
  Do not let "mechanism" appear merely because two variables are related in
  a natural-science context either — apply the same field-appropriate
  evidence threshold as the mechanism_test above.
statistical_integrity: >
  Never alter p-values, effect sizes, confidence intervals, sample sizes, or
  model specification during a stylistic pass. Never let prose imply
  practical significance from statistical significance alone.
formal_integrity: >
  Never modify definitions, notation, hypotheses, or proof dependencies to
  improve prose flow in mathematical/formal work.
legal_integrity: >
  Never fabricate case law, statute text, or judgments; keep descriptive
  ("what the law is") and normative ("what it should be") claims visibly
  separate.
historical_integrity: >
  Never invent archives, dates, quotations, events, or actors; historical
  narrative polish stays subordinate to source integrity.
```

### Generic-AI audit

Cross-reference `quality-and-editing.md#human-scholarly-prose`'s checklist. In addition, watch
specifically for:

```text
empty significance claims       — "this is important" with no named stake
                                   (see §Significance guard below)
inflated novelty                — "first-ever," "unprecedented," "completely
                                   new" without evidence-grounded support
excessive topic sentences        — every paragraph telegraphed before it's
                                   made, removing any reason to read the rest
repeated mini-conclusions         — every paragraph re-closing with a summary
                                   sentence
```

### Novelty inflation guard

Replace unsupported superlatives with evidence-grounded contribution
statements:

```text
weak:   "This groundbreaking, unprecedented study reveals a novel mechanism
        never before observed."
better: name the specific prior state of knowledge and what specifically
        this work adds to or revises in it
```

### Significance guard

Replace generic significance claims with a specific answer to: what changes,
for which theory or practice, under what condition, for whom.

```text
weak:   "This is of great theoretical and practical significance."
better: "If the mechanism holds outside the studied sector, it implies X for
        Y theory and Z for practitioners managing W."
```

### Quality states

```text
PASS                              — ready to return
PASS_WITH_LIMITATIONS             — ready to return; state the limitations
                                     explicitly rather than silently
REPAIR_REQUIRED                   — a fixable defect found; repair before
                                     returning
BLOCKED_BY_MISSING_EVIDENCE       — cannot complete without evidence the
                                     user/host must supply
BLOCKED_BY_CITATION_UNCERTAINTY   — a citation cannot be verified and the
                                     claim depends on it
BLOCKED_BY_ARGUMENT_INCONSISTENCY — the source material contains a genuine
                                     contradiction that must be resolved by
                                     the user, not silently by this Skill
```

### Repair order

When a defect is found, fix in this order — do not polish prose sitting on
top of a broken argument or an unverified claim:

```text
1. factual/citation repair       (argument-and-claims.md#citation-integrity)
2. argument repair                (the integrity tests above)
3. discipline/genre repair        (disciplines.md, argument-and-claims.md#argument-architectures)
4. voice repair                   (voice-profiles.md#voice-engine, quality-and-editing.md#human-scholarly-prose)
5. surface repair                 (grammar, local wording)
```

### Stop rule

Stop revising when all of the following hold — do not keep polishing past
this point:

```text
the requested deliverable is complete
AND factual/citation integrity is acceptable
AND the argument architecture is coherent
AND disciplinary conventions are satisfied
AND no critical issue remains unresolved
```

If a genuine unresolved issue remains (missing evidence, an unverifiable
citation, a contradiction only the user can resolve), report it as the
relevant `BLOCKED_BY_*` state rather than shipping prose that papers over it.

<a id="human-scholarly-prose"></a>

## Human Scholarly Prose

This module's purpose is **not** to defeat AI-detection tools. It exists to remove
generic, machine-like academic prose and replace it with the intellectual
variation that characterizes writing by a practicing scholar.

### Transitions to avoid overusing

Not banned outright — flag when they substitute for actual argumentative
connection rather than expressing one:

```text
Furthermore. Moreover. Additionally. It is important to note that.
It is worth noting that. In today's rapidly changing world.
This study aims to. The results highlight the importance of.
From this perspective. In conclusion.
```

### Prefer transitions with argumentative function

Use only where the relationship they name is actually true of the surrounding
text — do not decorate with these either:

```text
The difficulty lies elsewhere.
This explanation, however, leaves one question unresolved.
The distinction matters for two reasons.
The evidence supports a narrower claim.
At first sight, these findings appear inconsistent.
The institutional explanation changes once time is introduced.
A competing interpretation is possible.
The stronger claim does not follow from these results.
```

### Controlled asymmetry

Genuine scholarly prose is not geometrically uniform. Permit:

- short, decisive paragraphs beside long conceptual ones where each is earned;
- occasional very short sentences for emphasis;
- uneven evidence density (some claims need one citation, others need five);
- recurring concepts revisited rather than redefined from scratch each time;
- different rhythms across sections of the same piece.

Do **not** mechanically force uniform paragraph length, uniform sentence length,
a fixed citation count per paragraph, or a restated mini-conclusion at the end of
every paragraph — that regularity is itself a generic-AI signature. Do not,
however, introduce actual mistakes to fake this variation (see Integrity, below).

### Anti-generic-AI checklist

Before finalizing, scan the draft for these patterns and revise any that fired
mechanically rather than substantively:

```text
transition repetition           — same connective word reused across paragraphs
over-signposting                — "In this section, we will..." / "As shown above..."
                                   used more than the structure actually requires
parallel paragraph symmetry     — every paragraph same length/shape
excessive recap                 — restating prior points instead of advancing
generic importance claims       — "this is an important area of study" with no
                                   specific stake named
inflated contribution language  — "novel," "unprecedented," "groundbreaking"
                                   applied to incremental contributions
uniform sentence length         — no rhythmic variation across a paragraph
mechanical three-part lists     — reflexive rule-of-three where two or four items
                                   are the true count
citation dumping                — strings of citations not tied to a specific claim
abstract noun overload          — nominalizations ("utilization," "implementation
                                   of methodologies") replacing direct verbs
```

### Claim strength and uncertainty language

Match hedging to what the evidence supports, using field-appropriate phrasing
(see also each section of `disciplines.md`):

```text
Experimental science:  is consistent with / supports the possibility that /
                        suggests a role for / does not exclude
Social science:         the evidence is compatible with / under these
                        institutional conditions / within the observed sample
Humanities:             may be read as / this interpretation emphasizes /
                        a competing reading would
Law:                    the stronger interpretation would imply / the doctrine
                        does not clearly resolve
```

Avoid both overclaiming and excessive hedging — a sentence qualified past the
point of making a claim at all is a failure mode, not caution.

### First-person calibration

Do not universally ban or universally require "I"/"we." Determine appropriateness
from discipline, genre, and specific journal convention (see
`disciplines.md` → `acceptable_first_person`). "We show...", "we estimate...",
"I argue...", "we interpret..." are legitimate scholarly prose in the right
context (most empirical sciences, much social science, philosophy) and jarring in
others (some legal doctrinal writing, some formal mathematics).

### Section-level voice calibration

Within one document, vary register by function rather than applying one template
throughout:

```text
Introduction — more conceptual, more argumentative
Methods      — precise, low rhetorical intensity
Results      — evidence-first, minimal interpretation
Discussion   — interpretive, qualified, conceptual
```

### Integrity constraints on "humanizing"

Naturalness comes from genuine intellectual variation — never from deliberately
degrading quality. Never introduce, for the sake of sounding human:

```text
grammar errors, typos, logical gaps, incorrect citations,
random punctuation, awkward wording
```

### Quality audit (run before returning text)

```text
Does this sound like a scholar in this field?
Does the argument move rather than merely summarize?
Are claims calibrated to the evidence actually presented?
Are transitions intellectual rather than mechanical?
Does evidence sit near the claim it supports?
Does the prose vary naturally in rhythm across paragraphs/sections?
Does terminology remain stable across the document?
Does the writing preserve the author's actual position (not silently drifted)?
```

If any answer is no, revise that specific part rather than regenerating the whole
document.

<a id="editing-modes"></a>

## Editing Modes

Separates *how much* an edit is allowed to change (intensity) from *what kind*
of task is being performed (output mode). Always determine both before
touching the text — applying argument-reconstruction intensity to a request
for proofreading is as much a failure as applying surface-only intensity to a
request to rebuild a broken argument.

### Editing intensity

```yaml
SURFACE_EDIT:
  touches: grammar, clarity, local wording, sentence-level transitions
  does_not_touch: paragraph order, section structure, claim placement,
    evidence placement, the argument itself
  use_when: user asks to proofread, polish, or "clean up" without asking for
    structural change

STRUCTURAL_EDIT:
  touches: paragraph order, section flow, where a claim or piece of evidence
    sits, section-level pacing
  does_not_touch: the central thesis, concept hierarchy, or citation-claim
    attachments (see argument-and-claims.md#citation-integrity)
  use_when: user asks to reorganize, tighten flow, or fix a section that
    "doesn't read well" structurally

ARGUMENT_RECONSTRUCTION:
  touches: central thesis, concept hierarchy, mechanism, counterargument
    handling, contribution logic — the argument itself, not just its
    presentation
  does_not_touch: underlying data/results/findings/legal authority/historical
    fact (never touched by any intensity level — see argument-and-claims.md#citation-integrity,
    argument-and-claims.md#claim-calibration)
  use_when: user explicitly asks to rebuild, strengthen, or rethink the
    argument, not merely its prose
```

Default to the lightest intensity consistent with the request; when unclear
whether a deeper pass is wanted, perform the lighter one and say plainly what
a deeper pass would additionally change, rather than guessing upward.

### Output modes

```yaml
draft:
  from notes/outline to prose; use [VERIFY SOURCE], [INSERT EMPIRICAL
  RESULT], [DEFINE DATASET] placeholders rather than inventing evidence to
  create a false sense of completeness
revise:
  source text exists; preserve substantive meaning unless the user asks for
  an argument change; track major changes where useful to the user
polish:
  SURFACE_EDIT by default
compress:
  remove redundancy, generic framing, duplicated citations, excessive
  qualifiers — never cut theory/evidence the argument depends on
expand:
  add reasoning, evidence structure, counterargument, or concept
  clarification — never merely pad with synonyms or repeated framing
restructure:
  STRUCTURAL_EDIT
rebuild_argument:
  ARGUMENT_RECONSTRUCTION
journal_adapt:
  apply integration.md#journal-style-adaptation's target profile within its stated
  boundary (framing/structure, never substance)
book_chapter:
  apply writing-genres.md#book-writing and quality-and-editing.md#continuity-ledger
author_voice:
  apply voice-profiles.md#author-voice-calibration, prioritizing the user's established
  voice per its precedence rule
disciplinary_convert:
  re-render the same underlying content for a different discipline's
  argument architecture and claim conventions (e.g., adapting an empirical
  finding's framing from a psychology audience to a public-policy audience)
  — the underlying evidence and claim strength do not change, only the
  disciplinary framing and argument shape
```

### Choosing intensity from the request's phrasing

```text
"fix typos" / "proofread" / "tighten this sentence"        → SURFACE_EDIT
"this doesn't flow" / "reorganize" / "the intro is buried"  → STRUCTURAL_EDIT
"the argument doesn't hold together" / "rethink this claim" /
"strengthen the theory"                                      → ARGUMENT_RECONSTRUCTION
```

If a user's request names a specific surface complaint but the underlying
problem is actually structural or argumentative (e.g., "this sentence is
confusing" when the real issue is that two contradictory claims are both
present), name that finding explicitly rather than silently performing a
deeper edit than requested, or silently patching only the surface and leaving
the real problem in place.

<a id="continuity-ledger"></a>

## Continuity Ledger

Detailed mechanics for the monograph continuity state introduced in
`writing-genres.md#book-writing`. Load this file for long-form work (multi-chapter books,
multi-part reports, any task spanning more sections than fit in one drafting
pass). Keep the ledger task-local/project-local — it is not global memory and
does not need to persist beyond the current book-writing task unless the host
environment provides project-scoped storage.

### Why a ledger, not just "keep it in mind"

Long-form drafting fails in specific, recurring ways without an explicit
ledger: a term gets redefined slightly differently in chapter 6 than chapter
2; a claim made in chapter 3 is quietly contradicted in chapter 8; the same
piece of evidence is presented as supporting two incompatible claims; a
chapter's opening re-announces the book's contribution as if for the first
time. The ledger exists to catch these before the reader does.

### Concept ledger

```yaml
central_concepts: []       # the book's load-bearing terms
definitions: {}            # term -> current authoritative definition
preferred_terms: {}        # concept -> the one term used for it
deprecated_terms: {}       # concept -> earlier terms no longer used, and why
related_terms: {}          # term -> nearby terms it must not be confused with
concept_relationships: []  # e.g. "mechanism X is a subtype of concept Y"
```

Rules:
- One concept, one preferred term, used consistently — do not let three
  labels drift into use for the same construct.
- One term, one meaning within the book — if a term must shift meaning
  across chapters (e.g., refined in light of a later chapter's evidence),
  say so explicitly at the point of refinement rather than letting it drift
  silently.

### Claim ledger

```yaml
major_claims: []
supporting_claims: []
evidence_status: {}         # claim -> what currently supports it
chapter_first_introduced: {} # claim -> chapter number
later_refinements: {}       # claim -> how a later chapter narrowed/extended it
scope_conditions: {}        # claim -> its stated boundary
```

Before drafting a chapter that touches an existing major claim, check this
ledger — a later chapter may narrow or extend an earlier claim (record it as
a refinement) but must never silently contradict it. If a genuine
contradiction is intended (the book's argument changes its own mind partway
through), that is itself a claim the text must make explicit, not something
to leave for the reader to notice.

### Evidence ledger

```yaml
evidence_items: []
source: {}            # evidence item -> its source
claim_supported: {}   # evidence item -> which claim(s) it's adduced for
evidence_type: {}      # e.g. archival, statistical, textual, experimental
strength: {}           # a plain-language strength note, not a fake score
limitations: {}
```

Never invent an evidence item to fill a narrative gap between chapters — a
gap in the evidence base is a limitation to state, not a reason to
manufacture a citation, dataset, or archival source (see
`argument-and-claims.md#citation-integrity`).

### Chapter ledger

Maintain one entry per chapter:

```yaml
chapter_number:
chapter_role:            # see roles below
chapter_question:
chapter_claim:
new_concepts: []
reused_concepts: []
evidence: []
open_questions: []
handoff_to_next_chapter:
```

#### Chapter roles

```text
introduction | foundation | conceptual | historical | methods | empirical |
case | comparative | mechanism | normative | synthesis | implications |
conclusion
```

Writing register should vary by role (see `writing-genres.md#book-writing` §Chapter roles);
the ledger's `chapter_role` field is what determines which register applies
when drafting that chapter.

### Terminology audit

Before finalizing a chapter, or periodically across a long-running book task,
scan for:

```text
a construct renamed partway through | abbreviation inconsistency |
capitalization inconsistency | British/US spelling mixed | a variable or
concept name used inconsistently
```

### Repetition control

Useful long-form repetition (keep):

```text
concept recurrence | thesis reminders at natural junctures | cross-chapter
transitions that name the specific earlier claim
```

Repetition to avoid:

```text
re-summarizing the full literature review each chapter | redefining a term
identically each time it appears | re-announcing the book's contribution as
if novel in every chapter
```

### When continuity is not visible to you

If you are drafting one chapter of an already-partly-written book without
access to earlier chapters, ask the user for the relevant parts of this
ledger (central concepts and their definitions, major claims so far, this
chapter's role) rather than inventing a plausible-sounding continuity state.
