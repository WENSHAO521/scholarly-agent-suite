# Writing by genre and scale

Sections (each starts at an `<a id>` anchor; read only the one the task needs): [genre-matrix](#genre-matrix), [article-writing](#article-writing), [book-writing](#book-writing), [review-writing](#review-writing), [commentary-writing](#commentary-writing), [interdisciplinary-writing](#interdisciplinary-writing).

<a id="genre-matrix"></a>

## Genre Matrix

Supported genres and the features that distinguish them. Genre determines
structural expectations independent of discipline; discipline then determines how
each structural slot is filled (see `argument-and-claims.md#argument-architectures`).

| Genre | Defining feature | Typical length | Notes |
|---|---|---|---|
| Original research article | New empirical or formal result, own data/derivation | 4,000–10,000 words | Discipline sets internal architecture — never force IMRaD universally |
| Research note / short communication | Small, focused empirical or methodological point | 1,500–3,500 words | No room for extended literature review |
| Theory article | New or refined conceptual/causal account, no new data required | 6,000–10,000 words | Common in social science, philosophy, management |
| Conceptual article | Clarifies, distinguishes, or reframes a concept | 5,000–9,000 words | Heavy on definition and boundary-setting |
| Methods paper | New or improved method/measurement | 4,000–8,000 words | Emphasis on validity, comparison to prior methods |
| Narrative review | Argument-driven synthesis of a literature by theory/mechanism, not study-by-study | 6,000–12,000 words | See `writing-genres.md#review-writing`; not an annotated list |
| Systematic review | Synthesizes literature via documented, reproducible protocol | Variable | PRISMA-style protocol transparency where applicable; see `writing-genres.md#review-writing` |
| Scoping review | Maps the extent/range/nature of evidence on a broad or heterogeneous question | Variable | Descriptive mapping, not effect synthesis — see `writing-genres.md#review-writing` |
| Meta-analysis | Quantitative synthesis across studies | Variable | Statistical methods reporting is load-bearing; see `writing-genres.md#review-writing` |
| Critical review | Evaluates a literature's assumptions, not just its findings | 5,000–10,000 words | Argumentative but evidence-grounded; see `writing-genres.md#review-writing` |
| Theoretical synthesis review | Integrates competing frameworks into a new structure | 6,000–12,000 words | See `writing-genres.md#review-writing` |
| Case study | Deep single-case or small-N analysis | 4,000–8,000 words | Justify case selection and generalization scope |
| Comparative study | Structured comparison across cases/systems | 6,000–10,000 words | Explicit comparative logic (most-similar/most-different, etc.) |
| Historical study | Source-grounded account of a past process | 6,000–12,000 words | Chronology and historiographical positioning |
| Ethnography | Situated, immersive qualitative account | 6,000–12,000 words | Reflexivity, thick description |
| Legal doctrinal article | Analysis of legal rules/authority | 8,000–15,000 words | Rule → authority → interpretation → application |
| Philosophical essay | Sustained argument via distinction and objection | 4,000–10,000 words | Premise transparency, counterexample handling |
| Mathematical paper | Definition/theorem/proof exposition | Variable | Notation discipline, proof economy |
| Engineering paper | System, algorithm, or architecture contribution | 4,000–10,000 words | Design choice vs. implementation vs. evaluation separated |
| Clinical research paper | Patient/population-level intervention or observation | 3,000–6,000 words | Strict association/causal/utility separation |
| Commentary | Short, pointed argument on a live issue | 800–2,000 words | High rhetorical clarity, low hedging where warranted; see `writing-genres.md#commentary-writing` |
| Nature-style commentary essay | One conceptual frame, cross-disciplinary educated-reader audience | 1,000–2,500 words | Not a miniature article — see `writing-genres.md#commentary-writing` |
| Perspective | Author's considered view, less evidence-bound than an article | 1,500–4,000 words | Explicit that it is a perspective, not a finding |
| Editorial | Journal- or field-level, institutional statement | 500–1,500 words | Institutional voice, not personal essay; see `writing-genres.md#commentary-writing` |
| Book review | Evaluates a single book's argument and contribution | 1,000–3,000 words | Summary subordinate to evaluation |
| Policy analysis | Evaluates options against stated criteria | 3,000–8,000 words | Explicit criteria, tractable recommendations |
| Book chapter | Contributes to a larger argument arc | 6,000–12,000 words | Must respect monograph continuity — see `writing-genres.md#book-writing` |
| Monograph | Book-length sustained argument | 70,000–120,000 words | See `writing-genres.md#book-writing` |
| Textbook chapter | Pedagogical exposition of established knowledge | 4,000–10,000 words | Clarity and worked examples over novelty |
| Research handbook chapter | Authoritative field survey for other researchers | 6,000–12,000 words | Balances synthesis with the author's own stance |
| Academic essay | Argumentative but less bound by empirical apparatus | 2,000–6,000 words | Common in humanities |

### Detecting genre

Use explicit cues first ("write a review article," "draft Chapter 3," "this is
for [journal]"). Otherwise infer from purpose: presenting new data/derivation →
research article; synthesizing others' work → review; evaluating a book →
book review; advancing a sustained multi-chapter argument → book/monograph (route
to `writing-genres.md#book-writing` per the "Book vs. article routing" rule in `MODULE.md`).

If the genre is genuinely unclear and materially changes structure (e.g., research
article vs. perspective), ask.

<a id="article-writing"></a>

## Article Writing

Loaded when the task is article-scale (see `MODULE.md` §Book vs. article routing).
Distinguishes major article architectures rather than forcing one universal
template. See `argument-and-claims.md#argument-architectures` for the underlying family shapes and
`writing-genres.md#genre-matrix` for genre-specific length/feature expectations — this file adds
drafting and section-calibration guidance on top of those.

### Architecture selection

Pick the architecture from `argument-and-claims.md#argument-architectures` matching the discipline
family and genre, not by default reflex toward IMRaD. A theory article in public
administration and an experimental article in molecular biology should not share
a section skeleton just because both are "research articles."

### Section-level voice calibration

Within a single article, vary register by function (see also
`quality-and-editing.md#human-scholarly-prose` and `voice-profiles.md#voice-engine`):

```text
Introduction — conceptual, argumentative; earns the reader's attention on the
               stakes and the specific gap, not a generic "importance" claim
Literature   — positions the contribution against specific prior claims, not an
               undifferentiated list
Methods      — precise, low rhetorical intensity, reproducible level of detail
Results      — evidence-first, interpretation minimal and clearly bracketed off
Discussion   — interpretive, qualified, conceptual; where mechanism/implication
               is argued
Limitations  — substantive (design, scope, measurement), not ritual disclaimer
Conclusion   — narrowed, earned claim; not a restatement of the abstract
```

### Contribution framing

State the specific contribution type (see `argument-and-claims.md#argument-architectures`
§Contribution types) early and concretely. Avoid generic gap-spotting language
("few studies have examined X") in favor of the substantive gap actually being
addressed (mechanism, measurement, boundary condition, etc.).

### Reviewer-aware tightening

Before finalizing, silently interrogate the draft:

```text
What would a skeptical specialist challenge?
What assumption is unstated?
Which claim is broader than the evidence supports?
Which term is used unstably across sections?
Which evidence does the argument actually establish, versus merely gesture at?
```

Use the answers to tighten specific sentences — do not perform a theatrical fake
"Reviewer 2" dialogue in the output.

### Claim and citation discipline

- Match claim strength to what the design/evidence supports (see
  `argument-and-claims.md#argument-architectures` §Claim calibration and the relevant
  section of `disciplines.md`).
- Never fabricate citations, quotations, DOIs, or results. Mark missing evidence
  `[VERIFY]` rather than inventing it.
- Keep evidence physically close to the claim it supports (`evidence_proximity`
  in `voice-profiles.md#voice-engine`) rather than batching citations at paragraph end
  disconnected from specific assertions.

### When rewriting an existing article draft

Do not silently alter data, results, causal claims, sample description, or
method — voice edits are subordinate to epistemic accuracy (see `MODULE.md`
§Terminology and integrity). Flag, rather than silently fix, anything that looks
like a substantive (not stylistic) problem — e.g., a claim the results section
doesn't actually support.

<a id="book-writing"></a>

## Book Writing

Loaded when the task is book/chapter-scale (see `MODULE.md` §Book vs. article
routing). Book writing is not simply enlarged article prose — it requires
maintaining a coherent argument across chapters that each do different work.

### Model

```text
book thesis
  ↓
chapter function
  ↓
chapter-level argument
  ↓
cross-chapter recurrence
  ↓
intellectual progression
```

### Supported book genres

```text
research monograph | theoretical monograph | historical monograph |
academic textbook | edited-volume chapter | research handbook chapter |
interdisciplinary book
```

Each inflects the model above: a textbook chapter foregrounds pedagogical clarity
over novelty; an edited-volume or handbook chapter must stand alone while still
citing the volume's shared frame if one exists; a research/theoretical/historical
monograph is where full chapter-role differentiation (below) matters most.

### Monograph continuity state

Maintain this compactly across the whole book-writing task — update it as each
chapter is drafted, and consult it before drafting the next one:

```yaml
book_thesis:
central_concepts:
terminology:
major_claims:
chapter_roles:
recurring_examples:
unresolved_questions:
cross_references:
argument_progression:
```

This state exists to prevent: redefining the same term differently in different
chapters; repeating the same literature review; contradicting an earlier
chapter's claim; and re-announcing the book's contribution in every chapter as if
for the first time. When you don't have visibility into earlier chapters (e.g.,
only drafting one chapter of an already-written book), ask the user for a summary
of the relevant continuity state rather than inventing one.

For the detailed mechanics behind this state — separate concept/claim/
evidence/chapter ledgers, terminology-drift auditing, and what to do when
earlier chapters aren't visible to you — see `quality-and-editing.md#continuity-ledger`.

### Chapter roles

Writing style shifts by function — do not apply one uniform chapter template
throughout the book:

```text
foundation chapter    — establishes terms and stakes; more expository
conceptual chapter    — argument-dense, definition-heavy
historical chapter    — narrative evidence, chronology-driven
methods chapter        — precise, low rhetorical intensity
case chapter           — empirical/textual detail, evidence-first
comparative chapter    — explicit comparative logic across cases
mechanism chapter      — causal/generative argument, close to
                          Analytical-Mechanistic or Experimental-Mechanistic voice
synthesis chapter      — draws threads from prior chapters together
implications chapter   — extends the argument outward (policy, theory, practice)
conclusion             — synthesis and explicit scope of the claim
```

### Book-level voice variation while preserving identity

```text
Introduction → broad intellectual framing
Theory chapter → conceptual density
Historical chapter → narrative evidence
Case chapter → empirical detail
Conclusion → synthesis and scope
```

The core voice profile (primary/secondary/depth from `voice-profiles.md#voice-engine`) should
stay recognizable across this variation — local register shifts, authorial
identity does not.

### Chapter openings and conclusions

Do not let every chapter open with "This chapter examines..." or close with
"In conclusion, this chapter has shown..." — that regularity is a generic-AI
tell at book scale (see `quality-and-editing.md#human-scholarly-prose`). Vary the opening move by
what the chapter actually needs:

```text
a historical scene | a conceptual problem stated cold | an empirical puzzle |
a theoretical contradiction | a case observation | a direct continuation from
the previous chapter's handoff
```

and the closing move similarly:

```text
a bounded synthesis of what this chapter established | a deliberately
unresolved tension carried forward | a conceptual handoff naming the next
chapter's task | a historical transition | an empirical implication
```

Not every chapter needs the same closing move — a case chapter earning an
unresolved tension and a synthesis chapter earning a bounded summary is
correct variation, not inconsistency.

### Practical drafting notes

- Before drafting a new chapter, restate (to yourself) the continuity state and
  this chapter's role; only then apply the discipline module and voice profile.
- When a concept recurs, refer back to its earlier definition rather than
  redefining it, unless the chapter's explicit purpose is to refine or complicate
  that definition (note this explicitly when it happens).
- Track unresolved questions deliberately left open for a later chapter — do not
  let the writing imply false closure.
- Cross-references should name the earlier chapter's specific claim, not just
  gesture at "as discussed above."

<a id="review-writing"></a>

## Review Writing

Review articles are not one genre. Differentiate the subtype before drafting
— a systematic review written in narrative-essay voice, or a narrative review
padded with PRISMA-style protocol language it doesn't have, are both failures
of genre discipline. See `writing-genres.md#genre-matrix` for length/feature summary; this
file governs internal architecture and voice.

### Subtypes

```yaml
narrative_review:
  purpose: argument-driven synthesis of a literature
  architecture: >
    problem space → conceptual organization (by theory/mechanism/school, not
    by study) → competing traditions → evidence synthesis → unresolved
    contradiction → research agenda
  voice: interpretive-synthetic; citations integrated into an argument, not
    listed
  failure_mode: citation dumping / study-by-study annotated-bibliography
    structure standing in for synthesis

systematic_review:
  purpose: reproducible synthesis via a documented protocol
  architecture: >
    research question (often PICO-style) → protocol/registration → search
    strategy → eligibility criteria → screening/selection → study
    characteristics → synthesis → risk-of-bias assessment → limitations
  voice: precise, low-rhetoric, transparent about every methodological choice
  failure_mode: narrative synthesis presented as if it were the documented
    protocol; concealed methodological uncertainty
  reporting_guideline: PRISMA where applicable — follow only when the design
    genuinely matches it (see `integration.md#journal-style-adaptation` for how a
    reporting-guideline requirement interacts with journal targets)

scoping_review:
  purpose: map the extent, range, and nature of existing evidence on a
    question too broad or heterogeneous for a systematic review's effect
    synthesis
  architecture: >
    research question → search/selection (broad, documented) → charting of
    evidence types and gaps → thematic map → identified gaps for future
    research
  voice: descriptive-mapping, not effect-synthesizing — do not pool or imply
    a quantitative summary the design doesn't support
  failure_mode: presented as if it answers an effectiveness question rather
    than mapping a field

meta_analysis:
  purpose: quantitative synthesis across studies
  architecture: >
    research question → study identification/selection → effect-size
    extraction and model choice → heterogeneity assessment → pooled
    estimate → sensitivity/publication-bias analysis → interpretation
  voice: statistical precision; every reported number tied to its model and
    assumptions
  failure_mode: pooling heterogeneous studies without addressing
    heterogeneity; treating the pooled estimate as more certain than the
    input studies warrant

critical_review:
  purpose: evaluative assessment of a literature's assumptions, not just its
    findings
  architecture: >
    field's dominant assumption → where it originates → evidence and
    counter-evidence → what the assumption obscures → alternative framing
  voice: argumentative, comparable to a theory article; still evidence-
    grounded, not polemical

theoretical_synthesis_review:
  purpose: integrate competing frameworks into a new structure, not just
    summarize them
  architecture: >
    conceptual conflict between frameworks → mechanism integration →
    taxonomy/typology → boundary conditions → proposed unified framework
  voice: conceptual-sociological or analytical-mechanistic; the contribution
    is the synthesis itself
  failure_mode: source-by-source summary that never actually integrates
    anything into a new structure
```

### Choosing a subtype

Use the user's explicit label first. If unstated, infer from purpose: mapping
a broad or emerging field → scoping; answering a specific effect question
reproducibly → systematic (± meta-analysis if effect sizes are pooled);
building an argument about competing explanations → narrative or theoretical
synthesis; challenging a field's assumptions → critical review. If the
distinction would materially change structure and it's genuinely unclear, ask.

### Intellectual progression (all subtypes)

Avoid the flat accumulation pattern this genre is most prone to:

```text
weak:  "Study A found X. Study B also found X. Additionally, Study C found
       a related result. Furthermore, this topic is important."
better: position A → its limitation → position B → the contradiction between
        A and B → the mechanism that would resolve it → what current
        evidence does and doesn't settle
```

See `quality-and-editing.md#human-scholarly-prose` §Controlled Asymmetry and
`argument-and-claims.md#argument-architectures` §Paragraph-level rhythm patterns for how to keep
this from flattening into a list even across many cited sources.

### Integrity notes specific to reviews

- Never present a narrative synthesis as if it followed a systematic
  protocol, or vice versa understate a systematic review's actual rigor.
- Never pool studies in a meta-analysis narratively (in prose, without the
  stated model) while implying a formal quantitative synthesis occurred.
- State the search/selection method's limitations honestly — a review is
  only as credible as its stated method for finding what it reviews.

<a id="commentary-writing"></a>

## Commentary Writing

Commentaries, perspectives, and editorials need stronger authorial judgment
than an empirical article, but the same evidence discipline. This is the
genre family most prone to drifting into hype or into a miniature literature
review — both are failures here.

### Subtypes

```yaml
nature_style_commentary:
  purpose: a scholarly essay for an educated cross-disciplinary academic
    audience, built around one conceptual frame and its significance
  architecture: >
    a clear intellectual problem → one memorable conceptual frame →
    concrete evidence/examples grounding the frame → restrained authorial
    voice → practical or field-level implication
  voice: educated_general_reader register — plainer sentences, same rigor;
    concrete examples over abstract claims; jargon reduced, not eliminated
  avoid: mechanical sectioning (no "Introduction/Discussion" headers); an
    embedded mini-literature-review; over-citation; hyperbolic advocacy

career_or_field_commentary:
  purpose: reflection on a field's trajectory, a career milestone, or a
    disciplinary turning point
  architecture: similar to nature_style_commentary, with more narrative
    presence and first-person legitimacy
  voice: narrative-analytical; personal stake may be explicit

policy_perspective:
  purpose: argue for a specific stance on a live policy question from
    scholarly expertise
  architecture: >
    the decision at stake → the evidence base → competing considerations →
    the author's own weighing → a specific, actionable position
  voice: normative-systematic; state the normative premise explicitly rather
    than letting it hide inside "policymakers should..."

academic_editorial:
  purpose: an institutional (journal/field-level) statement, not a personal
    essay
  architecture: the issue → why it matters to this venue/field → the
    editorial position → what follows from it
  voice: institutional, restrained; avoid first-person unless the editorial
    board's convention explicitly permits it

conceptual_perspective:
  purpose: propose or defend a way of seeing a problem, short of a full
    theory article
  architecture: >
    the received framing → its limitation → the proposed reframing →
    what it would change if adopted
  voice: analytical-mechanistic or normative-systematic depending on field
```

### What distinguishes commentary from an article

A commentary earns stronger, more direct authorial claims than an empirical
article would license from the same evidence — but "stronger voice" is not
license to overstate what the evidence shows. Keep:

```text
claim strength → still calibrated to actual evidence (argument-and-claims.md#claim-calibration)
novelty language → still proportionate (no "unprecedented" without warrant)
citation density → lower than an article, but real claims still cited
```

### Common failure modes

```text
journal_article_miniature      — full IMRaD-style sectioning imposed on an
                                  800-2000 word piece
literature_review_creep        — commentary turns into an under-cited
                                  survey instead of a pointed argument
hyperbolic_advocacy             — rhetorical intensity exceeds what the
                                  evidence or reasoning supports
vague_significance_claim        — "this has important implications" without
                                  naming what changes, for whom, under what
                                  condition (see quality-and-editing.md#quality-audit §Significance
                                  guard)
```

### Drafting checklist

1. State the one conceptual frame the piece is built around before drafting
   — a commentary with three equally weighted ideas usually needs to become
   three commentaries or lose two ideas.
2. Ground the frame in at least one concrete, specific example or piece of
   evidence early — abstract argument alone reads as generic in this genre.
3. Keep sentences plainer than an article's without losing precision (see
   `voice-profiles.md#voice-engine` §Readability calibration, `educated_general_reader`).
4. End with a real implication, not a restated importance claim.

<a id="interdisciplinary-writing"></a>

## Interdisciplinary Writing

Prevents disciplinary collision when a task genuinely spans more than one field
(e.g., bioethics, STS, digital humanities, computational social science,
environmental humanities, health humanities, urban studies, development studies,
sustainability studies, complexity science, AI governance).

### Setup

Before drafting, establish:

```text
home discipline        — whose evidentiary standard governs the piece overall
secondary discipline    — the contributing field(s) supplying concepts/methods
borrowed concepts        — which concepts cross from secondary into home
borrowed methods         — which methods cross, and whether they're used natively
                           or adapted
terminology conflicts    — terms that mean different things in each field
evidentiary standards    — reconcile: e.g., a philosophy-of-science argument
                           embedded in an empirical health-policy paper must be
                           explicit about which claims are conceptual and which
                           are empirical
```

Load the home discipline's module as primary and the secondary discipline's
module for its specific contributions — do not blend them into an undifferentiated
voice.

### Terminology ownership

When a term carries different meanings across the fields in play, name the
intended meaning explicitly on first use rather than letting it float:

```text
institution    — (economics: rules of the game) vs. (sociology: durable social
                  pattern) vs. (political science: formal organization)
resilience     — (ecology: return to equilibrium) vs. (engineering: capacity to
                  absorb shock) vs. (psychology: individual adaptive capacity)
complexity     — (complexity science: emergent system behavior) vs. (colloquial:
                  "complicated")
agency         — (sociology/philosophy: capacity for independent action) vs.
                  (principal-agent economics: a specific contractual relationship)
representation — (political theory: standing for constituents) vs. (statistics:
                  sample reflecting a population) vs. (humanities: depiction)
validity        — (measurement: construct/internal/external validity) vs. (logic:
                  soundness of an argument) vs. (law: legal effect)
robustness      — (statistics: insensitivity to specification) vs. (engineering:
                  tolerance to failure) vs. (evolutionary biology: phenotypic
                  stability)
```

State the chosen meaning once, then use it consistently for the rest of the
document — do not let it silently drift back to a different field's sense.

### Avoiding incompatible mixing

Do not combine concepts from different fields as if they were interchangeable
without explanation. If a claim requires borrowing an evidentiary standard from
one field into a text otherwise governed by another (e.g., invoking statistical
significance inside a doctrinal legal argument), flag the borrowing explicitly
rather than letting the standards blur.

### Genre and continuity

Interdisciplinary work still follows `writing-genres.md#article-writing` or `writing-genres.md#book-writing`
for its scale; this file only governs how the disciplinary content within that
architecture is kept coherent. For book-length interdisciplinary work, record
terminology choices in the monograph continuity state's `terminology:` field so
later chapters don't redefine a cross-disciplinary term inconsistently.
