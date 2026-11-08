# Continuity Ledger

Detailed mechanics for the monograph continuity state introduced in
`book-writing.md`. Load this file for long-form work (multi-chapter books,
multi-part reports, any task spanning more sections than fit in one drafting
pass). Keep the ledger task-local/project-local — it is not global memory and
does not need to persist beyond the current book-writing task unless the host
environment provides project-scoped storage.

## Why a ledger, not just "keep it in mind"

Long-form drafting fails in specific, recurring ways without an explicit
ledger: a term gets redefined slightly differently in chapter 6 than chapter
2; a claim made in chapter 3 is quietly contradicted in chapter 8; the same
piece of evidence is presented as supporting two incompatible claims; a
chapter's opening re-announces the book's contribution as if for the first
time. The ledger exists to catch these before the reader does.

## Concept ledger

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

## Claim ledger

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

## Evidence ledger

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
`citation-integrity.md`).

## Chapter ledger

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

### Chapter roles

```text
introduction | foundation | conceptual | historical | methods | empirical |
case | comparative | mechanism | normative | synthesis | implications |
conclusion
```

Writing register should vary by role (see `book-writing.md` §Chapter roles);
the ledger's `chapter_role` field is what determines which register applies
when drafting that chapter.

## Terminology audit

Before finalizing a chapter, or periodically across a long-running book task,
scan for:

```text
a construct renamed partway through | abbreviation inconsistency |
capitalization inconsistency | British/US spelling mixed | a variable or
concept name used inconsistently
```

## Repetition control

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

## When continuity is not visible to you

If you are drafting one chapter of an already-partly-written book without
access to earlier chapters, ask the user for the relevant parts of this
ledger (central concepts and their definitions, major claims so far, this
chapter's role) rather than inventing a plausible-sounding continuity state.
