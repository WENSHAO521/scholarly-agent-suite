# Voice profiles and calibration

Sections (each starts at an `<a id>` anchor; read only the one the task needs): [voice-engine](#voice-engine), [author-voice-calibration](#author-voice-calibration), [historical-voice-profiles](#historical-voice-profiles), [era-calibration](#era-calibration), [multilingual-writing](#multilingual-writing).

<a id="voice-engine"></a>

## Voice Engine

Scholarly voice is a **profile across dimensions**, not a label ("academic,"
"formal," "Weberian"). Two texts can both be "formal" and still be completely
different scholarly voices because they differ in claim strength, qualification
density, and mechanism focus. Always think in terms of the profile below, then
render it into prose — never skip straight to vocabulary choices.

### Dimensions

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
transition_style:           # mechanical vs. intellectual (see quality-and-editing.md#human-scholarly-prose)
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

### Composing a voice

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

### The abstract profile library

Treat these as the operational unit — more important day-to-day than any named
historical figure (see `voice-profiles.md#historical-voice-profiles` for where each profile draws
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

### Determining the profile

Output voice is a function of five inputs — always resolve all five before
drafting:

```text
Discipline × Genre × Research design × Audience × Voice profile
```

See `argument-and-claims.md#disciplinary-matrix` for discipline → module routing, `writing-genres.md#genre-matrix`
for genre features, and the discipline files in `disciplines.md` for
`recommended_voice_profiles` per field.

### Section-level and book-level variation

A single document is not one uniform voice throughout:

- **Article sections** — introductions run more conceptual/argumentative, methods
  run precise and low-rhetoric, results run evidence-first with minimal
  interpretation, discussion runs interpretive and qualified. See
  `writing-genres.md#article-writing`.
- **Book chapters** — a monograph's introduction, theory chapter, historical
  chapter, case chapter, and conclusion each shift emphasis while the underlying
  authorial identity (core voice profile) stays recognizable. See
  `writing-genres.md#book-writing`.

Do not apply one prose template uniformly across an entire document — that is
itself a generic-AI tell (see `quality-and-editing.md#human-scholarly-prose`).

### Readability calibration

Independent of discipline, calibrate for audience:

```text
specialist | advanced_academic | interdisciplinary_academic | educated_general_reader | textbook
```

Sophistication is not the same as maximal complexity — a specialist audience
tolerates dense technicality; an educated-general-reader piece (e.g., a
Nature-style commentary) should carry the same intellectual rigor in plainer
sentences.

<a id="author-voice-calibration"></a>

## Author Voice Calibration

When the user supplies their own prior writing, infer a high-level style profile
from it and let it take priority over any historical or abstract voice profile.

### Priority hierarchy

```text
user's established scholarly voice
  +
disciplinary conventions
  +
selected scholarly profile (for gaps the user's sample doesn't cover)
```

Never: "historical scholar overrides user." The historical/abstract profile fills
in only what the user's own sample does not establish, and only in a way
consistent with what it does establish.

### What to infer from a writing sample

```text
average sentence length
paragraph length
first-person usage (frequency and construction: "I argue" vs "we show")
transition style (mechanical vs. intellectual; which connectives recur)
claim strength (typical hedging level)
citation placement (parenthetical vs. narrative; density)
definition habits (does the author define terms explicitly, and how often)
concept density
preferred rhetorical moves (how they open sections, how they close them,
  how they introduce counterarguments)
```

### What not to do

- Do not copy the user's errors (grammatical slips, inconsistent terminology,
  citation-format mistakes) forward into new text — fix these silently unless the
  user is specifically asking for a diagnostic of their own habits.
- Do not flatten genuine stylistic idiosyncrasy toward a generic "correct
  academic" register if it is a deliberate, functioning choice (e.g., an author
  who consistently opens sections with a rhetorical question, or who prefers
  short paragraphs even in a discipline that trends toward long ones).
- Do not infer a profile from too small a sample (a single paragraph) with false
  confidence — note the uncertainty and lean more heavily on disciplinary
  convention until more sample is available.

### Applying the calibration

1. Extract the profile using the dimension list in `voice-profiles.md#voice-engine`.
2. Cross-check against the discipline's `recommended_voice_profiles` — flag (to
   yourself, and to the user if it's a substantial mismatch) any place the
   author's habits diverge sharply from field convention, e.g. a first-person-free
   author writing in a sub-field where "we show" is now standard.
3. Draft/rewrite using the author's profile as the default; use the discipline
   module and abstract voice profile only to fill gaps (a construction the sample
   never exercises, e.g. how to open a limitations section).
4. When calibration is high-confidence (large sample, consistent patterns),
   prefer fidelity to the author's voice even where it's mildly unconventional,
   as long as it doesn't violate discipline-specific integrity norms (e.g., a
   journal that strictly forbids first person).

### Incremental updates

When new author material arrives over time (a new manuscript, a corpus-
builder refresh — see `integration.md#corpus-profile-integration`), classify each trait
as:

```text
stable | strengthening | weakening | new | uncertain
```

Require repeated, consistent evidence before reclassifying a `stable` trait
as `weakening` or dropping it — a single anomalous manuscript (a co-authored
piece, a deliberately different register for one venue) should not overwrite
a long-established voice.

### Learning from user edits (edit-diff learning)

When the host authorizes comparing an AI-drafted passage against the user's
own revision of it, extract recurring preferences from the diff rather than
treating each edit as a one-off correction — e.g., the user consistently
shortens introductions, consistently removes a specific hedge, consistently
adds mechanism language, or consistently cuts a generic transition. Fold
confirmed, repeated preferences into the working author profile for the rest
of the task. This is calibration to the user's genuine preferences; it is not
and must not be framed as evading any kind of detection.

<a id="historical-voice-profiles"></a>

## Historical Voice Profiles

Historical scholars are modeled here as sources of **transferable writing
mechanisms** — sentence architecture, argument architecture, how they define
terms, how evidence enters the text, how they handle counterargument — never as
sources of characteristic phrases or quotations to copy. Do not fabricate or
reproduce any quotation attributed to a figure below. The abstract profiles in
`voice-profiles.md#voice-engine` (Analytical-Mechanistic, Institutional-Comparative, etc.) are
the operational unit; the entries below explain where each abstraction draws its
mechanisms from and, importantly, what *not* to imitate mechanically (period-bound
vocabulary, dated terminology, or now-outdated conventions).

### Profile entry schema

```text
Scholar
Discipline
Period
Primary writing genres
Sentence architecture
Argument architecture
Definition style
Evidence style
Citation style
Use of examples
Use of counterargument
Level of abstraction
Typical intellectual rhythm
Strengths worth transferring
Traits not to imitate mechanically
Best-fit modern genres
```

### Illustrative entries

#### Max Weber — sociology, comparative-historical (feeds Institutional-Comparative)
```text
Sentence architecture:   long, subordinate-clause-heavy, qualification embedded
                          mid-sentence rather than appended
Argument architecture:   ideal type → comparative variation → causal adequacy
Definition style:        explicit, stipulative, revisited across a text
Evidence style:          comparative-historical illustration, not statistical
Counterargument:         addressed by narrowing scope conditions, not refutation
Strengths to transfer:   scope-conditioned generalization; ideal types as
                          analytical tools rather than descriptions of reality
Not to imitate:          the sheer sentence length itself — modern journals
                          require shorter units carrying the same precision
Best-fit modern genres:  theory articles, comparative institutional analysis
```

#### Charles Darwin — natural history (feeds Experimental-Mechanistic / Economical-Scientific)
```text
Sentence architecture:   plain, cumulative, evidence stacked before inference
Argument architecture:   observation → anomaly → mechanism → generalization
Definition style:        minimal; concepts built through examples rather than
                          stipulated definitions
Evidence style:          dense concrete particulars, patient accumulation
Counterargument:         anticipated objections addressed one at a time, in the
                          author's own voice, before conclusions are drawn
Strengths to transfer:   restraint in inference; letting accumulated observation
                          carry the argument's weight
Not to imitate:          Victorian-era diction; anecdotal sample sizes acceptable
                          then are not acceptable evidentiary practice now
Best-fit modern genres:  natural-history and field-biology synthesis, review
                          articles building toward a mechanism
```

#### David Hilbert — mathematics (feeds Formal-Deductive)
```text
Sentence architecture:   short, declarative, notation doing most of the work
Argument architecture:   problem → axioms/definitions → theorem → proof
Definition style:        maximally precise, minimal redundancy
Evidence style:          proof as the only evidence; no rhetorical support
Counterargument:         handled as boundary cases and counterexamples, not prose
                          objection
Strengths to transfer:   notation discipline; refusal to let prose substitute
                          for proof
Not to imitate:          period-specific notation conventions superseded by
                          modern standard notation
Best-fit modern genres:  mathematical papers, formal sections of any discipline
```

#### Claude Bernard — experimental physiology (feeds Clinical-Evidentiary)
```text
Sentence architecture:   medium length, method and result kept in close
                          proximity within the same paragraph
Argument architecture:   hypothesis → controlled intervention → observed effect
                          → mechanistic interpretation → explicit limits
Definition style:        operational — defined by how a variable was measured
Evidence style:          the experiment itself narrated as evidence
Counterargument:         alternative explanations tested experimentally rather
                          than argued away in prose
Strengths to transfer:   explicit separation of what was observed from what is
                          inferred; distrust of unearned generalization
Not to imitate:          single-investigator, uncontrolled-comparison norms of
                          the period, superseded by modern controlled-trial design
Best-fit modern genres:  experimental biology/medicine articles, clinical
                          research papers
```

#### Marc Bloch — history (feeds Historical-Structural)
```text
Sentence architecture:   moderate length, source and interpretation interleaved
Argument architecture:   question → source critique → chronological
                          reconstruction → interpretation → historiographical
                          positioning
Definition style:        concepts defined through their historical variation,
                          not fixed once and reused unchanged
Evidence style:          primary-source grounded, source reliability made
                          explicit
Counterargument:         engaged as alternative readings of the same sources
Strengths to transfer:   source skepticism; treating a concept's historical
                          instability as itself informative
Not to imitate:          absence of the citation apparatus expected in current
                          historical scholarship
Best-fit modern genres:  historical studies, intellectual-history chapters
```

#### Karl Popper — philosophy of science (feeds Normative-Systematic / Analytical)
```text
Sentence architecture:   short to medium, high logical connective density
Argument architecture:   thesis → distinction → argument → objection →
                          qualification → sharpened thesis
Definition style:        adversarial — defined partly by contrast with rejected
                          alternatives
Evidence style:          argument from consequence and counterexample rather
                          than empirical citation
Counterargument:         central to the method, not an afterthought section
Strengths to transfer:   taking the strongest form of an opposing view seriously
                          before responding to it
Not to imitate:          polemical tone where a gentler register better serves
                          the target venue
Best-fit modern genres:  philosophical essays, theoretical/normative articles
```

#### John von Neumann — mathematics/game theory (feeds Formal-Deductive / Strategic-Interaction)
```text
Sentence architecture:   dense, terse, assumes reader fluency with formalism
Argument architecture:   formalize the situation → derive consequence → interpret
Definition style:        axiomatic, minimal appeal to intuition once formalized
Evidence style:          formal derivation; intuition offered only as a gloss
Strengths to transfer:   translating an informal problem into a formal structure
                          before arguing about it
Not to imitate:          terseness that assumes away necessary exposition for a
                          non-specialist target audience
Best-fit modern genres:  formal theory articles, economics/game-theory papers
```

### Using this library

1. Identify the mechanism the task actually needs (e.g., "scope-conditioned
   generalization," "evidence-close mechanistic interpretation") rather than
   picking a name first.
2. Route to the corresponding abstract profile in `voice-profiles.md#voice-engine`.
3. Combine primary/secondary/depth layers as needed; do not import an entire
   named figure's voice wholesale.
4. Never quote, paraphrase into a "signature phrase," or otherwise reproduce a
   named figure's actual wording.

### Living and contemporary scholars

Do not build named profiles for living scholars. If a request references one,
extract only high-level, discipline-general traits (e.g., "mechanism-centered
prose," "economical causal argument," "comparative institutional analysis,"
"narrative theoretical exposition," "highly formal methodological writing") and
synthesize a composite, original voice from those traits — never a stylistic copy.
See `MODULE.md` §Voice profiles for the operational rule and
`disciplines.md#interdisciplinary` / eval file `anti-generic-ai-cases.jsonl` for
the corresponding safeguard tests.

<a id="era-calibration"></a>

## Era Calibration

Broad intellectual-era characteristics that subtly influence prose. Use these to
tune register when a task calls for it (e.g., "write this as a classical
theoretical exposition" or when a historical/humanities piece must sound
period-appropriate) — never to produce archaic pastiche in an ordinary
contemporary piece, and never as an excuse to skip current citation and
evidentiary norms.

### Classical / pre-1945 scholarship
```text
Greater rhetorical amplitude; longer conceptual sentences; less standardized
article architecture; exposition often historical or philosophical in mode even
within the sciences; citation apparatus lighter and less standardized.
```

### 1945–1980
```text
Strong theory-building; large conceptual systems; growing formalization;
mechanistic explanation prized; article architecture standardizing but still
flexible.
```

### 1980–2005
```text
Middle-range theory over grand system-building; empirical specialization;
structured literature positioning ("this paper extends X by..."); increasing
methodological explicitness.
```

### 2005–present
```text
Clearer, front-loaded contribution statements; identification/causal-inference
awareness; robustness checks; structured limitations sections; open-science
practices (preregistration, data/code availability) where relevant to the field.
```

### How to apply

- Calibrate subtly: shift sentence amplitude, argument pacing, and how explicitly
  contribution is stated — do not swap in period vocabulary or spelling.
- Default to the 2005–present register unless the task specifies otherwise or the
  genre is explicitly historical/retrospective.
- Never let era calibration override current standards for evidentiary rigor,
  citation practice, or claim calibration — those come from `disciplines.md`
  and are non-negotiable regardless of the era being stylistically evoked.
- For historical or intellectual-history writing *about* an earlier era, keep the
  analytical prose in contemporary register even while the subject matter is
  historical — do not confuse "writing about the past" with "writing like the
  past."

<a id="multilingual-writing"></a>

## Multilingual Writing

English-language academic writing is the primary, most-developed target of
this Skill. This file governs architecture-level support for other languages
and translation between them — it does not assume English rhetorical
structure transfers mechanically to another language, and it does not build
out full language-specific prose rulebooks to the same depth as English.

### Language-independent voice vs. language-specific realization

Keep two layers separate:

```yaml
language_independent:   # carries across languages unchanged
  - discipline/genre argument architecture
  - claim type and claim strength (argument-and-claims.md#claim-calibration)
  - mechanism focus, definition discipline, scope conditions
  - citation integrity and evidence proximity

language_specific:      # realized differently per language
  - sentence order and clause structure
  - pronoun/subject-drop conventions
  - transition frequency and connective vocabulary
  - punctuation and citation-integration conventions
  - register markers (formality levels, honorifics where applicable)
```

A translation or non-English draft should preserve the language-independent
layer exactly and re-realize the language-specific layer natively — not
transliterate English sentence structure into another language's grammar.

### Supported languages (architecture-level)

```text
Chinese | German | French | Spanish | Japanese | Korean
```

For each, apply the discipline/genre architecture from
`argument-and-claims.md#argument-architectures` and `disciplines.md` as usual, but let sentence
rhythm, connective choice, and formality register follow that language's own
scholarly convention rather than a word-for-word rendering of the English
version.

### Chinese academic writing

Avoid mechanical translationese — connective words such as 因此, 此外,
与此同时, 值得注意的是 used reflexively in nearly every paragraph read the
same way "Furthermore/Moreover" overuse reads in English (see
`quality-and-editing.md#human-scholarly-prose`). Chinese scholarly prose still needs genuine
argumentative transitions; the fix is the same principle as the English
anti-generic-AI rules, realized in Chinese connective choices rather than
suppressing transitions altogether.

### English academic writing — avoid pseudo-formality

Prefer precise verbs, clear subjects, and bounded claims over unnecessary
nominalization ("the utilization of," "the implementation of methodologies")
— see `quality-and-editing.md#human-scholarly-prose` §Anti-generic-AI checklist §abstract noun
overload. Formality is not measured by syllable count.

### Translation mode

Translating a finished text is the `translation-engine` module's job (its
glossary, invariant check, and `TRANSLATION_REPORT_V1`). The principles
below are shared with it, and apply here when a draft mixes languages or
when revising a text that was translated. When translating existing
scholarly prose, preserve:

```text
claim strength | concept hierarchy | which citation supports which claim |
authorial stance | argument progression | uncertainty expression
```

Do not mirror the source language's sentence structure mechanically — a
faithful translation re-expresses the same claims and argument moves in the
target language's native scholarly register, not a clause-by-clause mirror.
Where a source-language rhetorical device has no natural target-language
equivalent, replace it with the target language's own device for
accomplishing the same argumentative work rather than a literal rendering
that reads as foreign.

### Cross-language author profile

If a user writes in more than one language, maintain:

```text
author_intellectual_profile      # language-independent: mechanism focus,
                                   claim style, definitional habits
language_specific_profiles:      # one per language, its own realization
  en: {...}
  zh: {...}
  ...
```

Do not infer a user's English sentence-level style from their Chinese (or
other language) writing, or vice versa — sentence-level habits are
language-specific; only the intellectual profile (what kind of claims they
make, how they handle counterargument, their definitional discipline)
transfers across languages. See `voice-profiles.md#author-voice-calibration` for how the
intellectual profile itself is derived.

### Standalone note

This file documents architecture-level guidance, not a full rhetorical-
structure module per language. For deep, idiomatic non-English scholarly
prose beyond what this file specifies, rely on the model's own fluency in
that language's scholarly register, applying the language-independent
constraints above as the invariant.
