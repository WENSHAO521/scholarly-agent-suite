# Review Writing

Review articles are not one genre. Differentiate the subtype before drafting
— a systematic review written in narrative-essay voice, or a narrative review
padded with PRISMA-style protocol language it doesn't have, are both failures
of genre discipline. See `genre-matrix.md` for length/feature summary; this
file governs internal architecture and voice.

## Subtypes

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
    genuinely matches it (see `journal-style-adaptation.md` for how a
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

## Choosing a subtype

Use the user's explicit label first. If unstated, infer from purpose: mapping
a broad or emerging field → scoping; answering a specific effect question
reproducibly → systematic (± meta-analysis if effect sizes are pooled);
building an argument about competing explanations → narrative or theoretical
synthesis; challenging a field's assumptions → critical review. If the
distinction would materially change structure and it's genuinely unclear, ask.

## Intellectual progression (all subtypes)

Avoid the flat accumulation pattern this genre is most prone to:

```text
weak:  "Study A found X. Study B also found X. Additionally, Study C found
       a related result. Furthermore, this topic is important."
better: position A → its limitation → position B → the contradiction between
        A and B → the mechanism that would resolve it → what current
        evidence does and doesn't settle
```

See `human-scholarly-prose.md` §Controlled Asymmetry and
`argument-architectures.md` §Paragraph-level rhythm patterns for how to keep
this from flattening into a list even across many cited sources.

## Integrity notes specific to reviews

- Never present a narrative synthesis as if it followed a systematic
  protocol, or vice versa understate a systematic review's actual rigor.
- Never pool studies in a meta-analysis narratively (in prose, without the
  stated model) while implying a formal quantitative synthesis occurred.
- State the search/selection method's limitations honestly — a review is
  only as credible as its stated method for finding what it reviews.
