# Voice Engine

Scholarly voice is a **profile across dimensions**, not a label ("academic,"
"formal," "Weberian"). Two texts can both be "formal" and still be completely
different scholarly voices because they differ in claim strength, qualification
density, and mechanism focus. Always think in terms of the profile below, then
render it into prose — never skip straight to vocabulary choices.

## Dimensions

Each dimension takes a value on `very_low | low | medium | high | very_high`
(compact synonyms are fine internally: `vl, l, m, h, vh`).

```yaml
sentence_length:            # mean clause count / length per sentence
concept_density:            # distinct technical concepts per paragraph
rhetorical_intensity:       # amplitude of persuasive/emphatic language
claim_strength:             # how strongly assertions are stated
qualification_density:      # hedges, scope conditions, boundary statements
first_person_usage:         # "I"/"we" frequency
definition_frequency:       # how often terms are explicitly defined
citation_density:           # citations per unit of text
evidence_proximity:         # how close evidence sits to the claim it supports
counterargument_frequency:  # how often objections/alternatives are raised
paragraph_length:           # mean sentences per paragraph
paragraph_architecture:     # claim-first vs. build-up vs. narrative
transition_style:           # mechanical vs. intellectual (see human-scholarly-prose.md)
technicality:               # reliance on field-specific terminology/notation
narrative_presence:         # storytelling / chronological exposition
historical_depth:           # engagement with intellectual lineage
formalization:              # use of formal notation, definitions, theorems
interpretive_density:       # inference/interpretation relative to raw observation
mechanism_focus:            # emphasis on causal/generative mechanism over pattern
causal_language:            # willingness to use causal verbs vs. associational ones
uncertainty_expression:     # how explicitly limits of knowledge are marked
```

Not every dimension is load-bearing for every discipline or genre — set the ones
that matter and leave the rest at a sensible default (`medium`) rather than
enumerating all twenty every time.

## Composing a voice

A voice profile has up to three layers:

- **Primary** — the dominant mechanism (e.g., `analytical-mechanistic`).
- **Secondary** — a complementary mechanism that shapes a subset of moves (e.g.,
  how comparisons are handled).
- **Depth layer** — an optional register that colors historical/contextual
  engagement (e.g., `historical-structural`) without displacing the primary.

```yaml
voice:
  primary: analytical-mechanistic
  secondary: institutional-comparative
  depth: historical-structural

prose:
  sentence_length: medium
  rhetorical_intensity: low
  qualification_density: medium
  mechanism_focus: high
  historical_depth: medium
```

Optional internal weights may be used to reason about blend proportions, but are
a stylistic control, not a scientific measurement, and should not normally be
surfaced to the user:

```yaml
voice_mix:
  analytical: 0.40
  institutional: 0.30
  historical: 0.20
  economical: 0.10
```

## The abstract profile library

Treat these as the operational unit — more important day-to-day than any named
historical figure (see `historical-voice-profiles.md` for where each profile draws
its transferable mechanisms from):

```text
Analytical-Mechanistic     — spare prose, explicit causal/generative mechanism
Institutional-Comparative  — structures around comparison of cases/institutions
Historical-Structural      — long-run, structural, context-first exposition
Formal-Deductive           — definition → proposition → proof economy
Experimental-Mechanistic   — hypothesis restraint, evidence-close interpretation
Clinical-Evidentiary       — diagnostic caution, explicit evidence-to-action gap
Interpretive-Humanistic    — close reading, meaning-centered, tolerant of ambiguity
Normative-Systematic       — premise → distinction → argument → objection → qualification
Doctrinal-Legal            — rule → authority → interpretation → application
Ethnographic-Interpretive  — situated observation, reflexivity, thick description
Conceptual-Sociological    — concept-and-mechanism, scope-conditioned generalization
Strategic-Interaction      — actor incentives, equilibrium/expectation reasoning
Economical-Scientific      — maximal information per sentence, minimal rhetoric
```

## Determining the profile

Output voice is a function of five inputs — always resolve all five before
drafting:

```text
Discipline × Genre × Research design × Audience × Voice profile
```

See `disciplinary-matrix.md` for discipline → module routing, `genre-matrix.md`
for genre features, and the discipline files in `disciplines/` for
`recommended_voice_profiles` per field.

## Section-level and book-level variation

A single document is not one uniform voice throughout:

- **Article sections** — introductions run more conceptual/argumentative, methods
  run precise and low-rhetoric, results run evidence-first with minimal
  interpretation, discussion runs interpretive and qualified. See
  `article-writing.md`.
- **Book chapters** — a monograph's introduction, theory chapter, historical
  chapter, case chapter, and conclusion each shift emphasis while the underlying
  authorial identity (core voice profile) stays recognizable. See
  `book-writing.md`.

Do not apply one prose template uniformly across an entire document — that is
itself a generic-AI tell (see `human-scholarly-prose.md`).

## Readability calibration

Independent of discipline, calibrate for audience:

```text
specialist | advanced_academic | interdisciplinary_academic | educated_general_reader | textbook
```

Sophistication is not the same as maximal complexity — a specialist audience
tolerates dense technicality; an educated-general-reader piece (e.g., a
Nature-style commentary) should carry the same intellectual rigor in plainer
sentences.
