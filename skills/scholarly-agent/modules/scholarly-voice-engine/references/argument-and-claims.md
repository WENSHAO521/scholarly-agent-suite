# Discipline, design, argument, and claims

Sections (each starts at an `<a id>` anchor; read only the one the task needs): [disciplinary-matrix](#disciplinary-matrix), [research-design-matrix](#research-design-matrix), [argument-architectures](#argument-architectures), [claim-calibration](#claim-calibration), [citation-integrity](#citation-integrity).

<a id="disciplinary-matrix"></a>

## Disciplinary Matrix

Routing table from a user's stated or implied field to the discipline module(s) in
`disciplines.md`. Load only what the task needs.

| Family | Example fields | Module |
|---|---|---|
| Natural sciences | Physics, chemistry, biology, earth science, environmental science, astronomy, materials science, neuroscience, ecology, evolutionary biology | `disciplines.md#natural-sciences` |
| Mathematics & formal sciences | Pure/applied mathematics, statistics, logic, operations research, theoretical CS, information theory | `disciplines.md#mathematics-formal` |
| Engineering & computing | Computer science, AI, software engineering, electrical/mechanical/civil/chemical/biomedical engineering, robotics, systems engineering, data science | `disciplines.md#engineering-computing` |
| Medicine & health sciences | Clinical medicine, public health, epidemiology, nursing, pharmacy, dentistry, biomedical sciences, health policy, digital health, medical AI, psychiatry | `disciplines.md#medicine-health` |
| Social sciences | Political science, public administration, public policy, economics, sociology, psychology, anthropology, IR, communication, criminology, human geography, demography, social policy | `disciplines.md#social-sciences` |
| Business & management | Management, organization studies, strategy, marketing, finance, accounting, entrepreneurship, HRM, operations management, innovation studies | `disciplines.md#business-management` |
| Law | Public/private law, international law, comparative law, constitutional/administrative/criminal law, legal theory, law and society | `disciplines.md#law` |
| Humanities | Philosophy, history, literature, linguistics, religious studies, classics, art history, cultural studies, intellectual history, ethics, political thought | `disciplines.md#humanities` |
| Education | Education policy, curriculum studies, higher education, educational psychology, pedagogy, comparative education, teacher education, ed-tech | `disciplines.md#education` |
| Arts & practice-based research | Music, performance studies, fine arts, design research, architecture, film studies, theatre, creative practice research | `disciplines.md#arts-design` |
| Interdisciplinary | STS, digital humanities, computational social science, environmental humanities, bioethics, health humanities, urban studies, development studies, sustainability studies, complexity science, AI governance | `disciplines.md#interdisciplinary` + each contributing home discipline |

**Economics, philosophy, and history** are grouped into `social-sciences.md`
and `humanities.md` respectively for routing (they share those families'
citation/evidence infrastructure), but each has distinctive-enough
conventions to warrant a dedicated subsection within its family file —
see the "Economics" heading in `disciplines.md#social-sciences` and the
"Philosophy" / "History" headings in `disciplines.md#humanities`. Route to
the family file as usual, then to the matching subsection.

### Inference procedure

1. If the user states a field or journal, map it to a row above.
2. If unstated, infer from content cues: notation and proofs → mathematics; wet-lab
   or clinical data → natural sciences/medicine; case law and statutes → law;
   close reading of texts → humanities; institutional/survey data → social science;
   firm-level strategy questions → business.
3. If two families are both clearly present (e.g., a bioethics piece mixing
   philosophy and medicine), treat it as interdisciplinary: pick a **home**
   discipline (the one whose evidentiary standard governs) and a **secondary**
   discipline, and load `writing-genres.md#interdisciplinary-writing` alongside both modules.
4. If genuinely ambiguous and the choice would materially change claim style or
   citation behavior, ask rather than guess.

### Adding a discipline without rewriting the core Skill

`MODULE.md` never enumerates discipline files by name in its control flow — it
loads "the matching file in `disciplines.md`." To add a new discipline family:

1. Add a row to the table above.
2. Add `disciplines.md<name>.md` using the schema documented at the top of any
   existing discipline file.
3. Add 2–3 cases to `evals/discipline-cases.jsonl`.

No other file needs to change.

<a id="research-design-matrix"></a>

## Research Design Matrix

Research design constrains claim strength and argument shape independently of
discipline — a randomized trial and a cross-sectional survey in the same field
license different prose even when the topic is identical. Resolve design
before drafting; see `argument-and-claims.md#claim-calibration` for how design maps to claim type
and `argument-and-claims.md#argument-architectures` for section-level shape.

### Design → prose calibration

```yaml
experiment_lab:
  claim_ceiling: causal_within_studied_conditions
  must_state: manipulation, randomization unit, control condition
  common_overreach: generalizing beyond the manipulated/measured construct

rct:
  claim_ceiling: causal_efficacy_within_trial_population
  must_state: randomization method, blinding, allocation concealment, primary
    endpoint, ITT vs. per-protocol
  common_overreach: efficacy stated as effectiveness in ordinary practice

cohort:
  claim_ceiling: associational_to_risk  # causal language only with strong
    confounding control explicitly argued, not assumed
  must_state: exposure/outcome definitions, follow-up, confounders adjusted for
  common_overreach: association reported as if causally established

case_control:
  claim_ceiling: associational
  must_state: case/control definition, selection method, recall/selection
    bias exposure
  common_overreach: odds ratio interpreted as risk in the general population

cross_sectional:
  claim_ceiling: descriptive_to_associational
  must_state: single time point, no temporal ordering available
  common_overreach: implying a causal or even temporal sequence

panel_longitudinal:
  claim_ceiling: associational_to_causal_with_identification_strategy
  must_state: what within-unit or between-wave variation is doing the
    identifying work
  common_overreach: fixed effects alone treated as sufficient for causal
    identification without addressing time-varying confounders

survey:
  claim_ceiling: descriptive_to_associational
  must_state: sampling frame, response rate, measurement instrument validity
  common_overreach: self-report treated as behavioral fact

sem_path_analysis:
  claim_ceiling: associational_pattern_consistent_with_a_causal_model
  must_state: model is one of several consistent with the data, not proof of
    the specified causal structure
  common_overreach: model fit treated as confirmation of causal direction

did:
  claim_ceiling: causal_under_parallel_trends
  must_state: the parallel-trends assumption and how it was checked
  common_overreach: causal claim stated without acknowledging the identifying
    assumption

rdd:
  claim_ceiling: causal_local_to_the_cutoff
  must_state: the cutoff, bandwidth choice, and that the estimate is local
  common_overreach: extrapolating the local estimate to units far from the
    cutoff

iv:
  claim_ceiling: causal_conditional_on_instrument_validity
  must_state: exclusion restriction and relevance, argued not assumed
  common_overreach: treating a weak or contested instrument as settling
    identification

natural_experiment:
  claim_ceiling: causal_conditional_on_as_if_randomization_argument
  must_state: the argument for why assignment approximates randomization
  common_overreach: "natural experiment" invoked as a label without the
    supporting argument

ml_prediction:
  claim_ceiling: predictive_pattern_not_causal_mechanism
  must_state: train/test/validation split, distribution shift risk, what
    "generalization" was actually tested
  common_overreach: predictive accuracy described as understanding or
    causal insight

simulation:
  claim_ceiling: conditional_on_model_assumptions
  must_state: which assumptions drive the qualitative result (sensitivity
    analysis)
  common_overreach: simulated result presented as empirical finding

benchmarking:
  claim_ceiling: comparative_performance_under_stated_conditions
  must_state: benchmark scope, what it does and does not measure
  common_overreach: benchmark win generalized to real-world superiority (see
    `disciplines.md#engineering-computing`)

case_comparison_process_tracing:
  claim_ceiling: mechanism_plausible_in_the_cases_examined
  must_state: case selection logic, how alternative mechanisms were ruled out
  common_overreach: a mechanism traced in N cases asserted as a general law

interviews_qualitative:
  claim_ceiling: interpretive_pattern_in_the_sample_interviewed
  must_state: sampling logic, saturation/sufficiency judgment, positionality
    where relevant
  common_overreach: thematic pattern generalized as population prevalence

ethnography:
  claim_ceiling: situated_interpretive_account
  must_state: fieldwork duration/access, reflexive positioning
  common_overreach: single-site account treated as representative of a
    broader category

archival_historical:
  claim_ceiling: interpretive_reconstruction_from_available_sources
  must_state: source base and its known gaps/biases
  common_overreach: silence in the archive read as absence of the event

close_reading:
  claim_ceiling: interpretive
  must_state: which textual features ground the reading
  common_overreach: interpretation asserted as the text's only possible
    meaning

doctrinal:
  claim_ceiling: what_the_law_is_within_the_authority_examined
  must_state: jurisdiction and the specific authorities relied on
  common_overreach: one jurisdiction's rule stated as if legally universal

normative_argument:
  claim_ceiling: normative_conclusion_conditional_on_stated_premises
  must_state: the normative premises the argument actually depends on
  common_overreach: an empirical premise smuggled in as if self-evident

formal_proof:
  claim_ceiling: true_relative_to_stated_axioms_and_hypotheses
  must_state: every hypothesis the theorem depends on
  common_overreach: a special case's proof presented as covering the general
    statement

conceptual_synthesis:
  claim_ceiling: coherence_and_explanatory_scope_of_the_proposed_framework
  must_state: what the synthesis integrates and what it leaves unresolved
  common_overreach: a novel taxonomy presented as an empirical discovery
```

### Resolving design from a request

1. If the user names a design ("RCT," "difference-in-differences," "close
   reading"), use its row directly.
2. If unstated, infer from the data/evidence described — a single time point
   of survey data is cross-sectional; repeated observation of the same units
   is panel; text-only evidence with an interpretive claim is close reading.
3. If the design is ambiguous and the claim ceiling would materially change
   (e.g., cohort vs. RCT), ask rather than default to the more permissive
   design.
4. A single manuscript may combine designs by section (e.g., an RDD estimate
   in Results, a process-tracing case study in a robustness section) — apply
   the matching row to each, not one design's ceiling to the whole piece.

### Interaction with claim calibration

This file sets the *ceiling*; `argument-and-claims.md#claim-calibration` sets the *language*.
Never let confident prose narrow the gap between what a design supports and
what a sentence claims — no rhetorical device (hedge removal, passive-to-
active conversion, added emphasis) changes what the data can bear.

<a id="argument-architectures"></a>

## Argument Architectures

Section-level shapes by discipline family and by rhetorical pattern. Never impose
IMRaD (Introduction, Methods, Results, Discussion) universally — it is one
architecture among several, native to experimental/empirical sciences, and often
wrong for mathematics, law, or humanities.

### Family architectures

#### Empirical social science
```text
problem → literature → theoretical mechanism → hypotheses/questions →
data → methods → results → interpretation → limitations → contribution
```

#### Experimental science
```text
problem → known mechanism → specific uncertainty → experimental strategy →
results → mechanistic interpretation → boundary conditions
```

#### Mathematics
```text
problem → notation → definitions → main theorem → supporting results →
proof → discussion / corollaries
```

#### Humanities (interpretive)
```text
interpretive problem → existing reading → text/source evidence →
conceptual intervention → close analysis → implication
```

#### Law (doctrinal)
```text
legal problem → doctrine/authority → conflict or ambiguity → interpretation →
comparative or normative analysis → consequence
```

#### Sociology / institutional social science
```text
concept → mechanism → social structure → empirical pattern → scope condition
```

#### Engineering / systems
```text
motivation → design goals/constraints → design choice → implementation →
evaluation/benchmark → ablation → interpretation → limitations
```

#### Clinical / health sciences
```text
clinical problem → prior evidence → design → population/sample →
outcome measures → results → clinical interpretation → limitations →
implications for practice (kept separate from causal claims)
```

#### Historical study
```text
question → sources → chronological reconstruction → interpretation →
historiographical positioning → implication
```

#### Philosophical essay
```text
thesis → key distinction → argument for thesis → strongest objection →
response/qualification → refined thesis
```

#### Economics
```text
economic question → model/identification strategy → institutional
assumptions → estimand → data → results → robustness → mechanism →
welfare/policy implication
```
See the Economics subsection of `disciplines.md#social-sciences` and
`argument-and-claims.md#research-design-matrix` for the identification-strategy rows (DiD, RDD,
IV, natural experiment) this architecture draws on.

### Additional reusable patterns

Not tied to one discipline family — select the pattern the material actually
calls for, independent of the family architectures above:

```text
anomaly → competing explanations → test → adjudication
```
A genuine puzzle with multiple live explanations, resolved by evidence that
favors one — common in natural science and economics controversies.

```text
concept → distinction → mechanism → boundary condition
```
Building or refining a concept before using it — common in conceptual
articles and theory-building sections across social science and management.

```text
authority → interpretive conflict → application → consequence
```
An alternate, more compressed form of the law/doctrinal architecture above,
useful when the interpretive conflict itself (rather than a single
progression toward one interpretation) is the paper's main subject.

```text
premise → objection → refinement → conclusion
```
A compact philosophical/normative pattern for shorter arguments that don't
need the full thesis→distinction→argument→objection→qualification cycle.

```text
clinical uncertainty → design → finding → clinical interpretation
```
For clinical/health writing shorter than the full architecture above (e.g., a
research letter or brief report).

```text
textual problem → competing reading → close evidence → reinterpretation
```
For literary/humanistic interpretation shorter than a full close-reading
article.

### Paragraph- and section-level rhythm patterns

Use these as building blocks inside any of the above architectures — they are
where "the argument moves" rather than merely summarizes:

```text
setup → complication → evidence → interpretation → qualification →
narrowed conclusion
```
```text
claim → counterexample → conceptual distinction → revised claim
```
```text
observation → anomaly → mechanism → implication
```

Vary which pattern governs which paragraph; do not apply the same one
mechanically throughout a document (see `quality-and-editing.md#human-scholarly-prose` §Controlled
Asymmetry).

### Claim calibration by architecture

Match the architecture's evidentiary apparatus to the claim type it is entitled to
produce — see `argument-and-claims.md#claim-calibration` for the full taxonomy and invariant, and
`argument-and-claims.md#research-design-matrix` for how the specific research design (not just the
discipline family) sets the claim ceiling. An experimental-science architecture
with only correlational data supports `associational`, not `causal`, claims —
no amount of confident prose narrows that gap (see `disciplines.md` for
field-specific guardrails, e.g. clinical association/causal/utility
separation).

### Contribution types

Match the stated contribution to what the architecture actually establishes:

```text
new mechanism | new theory | new distinction | boundary condition |
measurement | method | dataset | empirical anomaly | comparative evidence |
historical reinterpretation | doctrinal reinterpretation | conceptual synthesis
```

Avoid generic "gap spotting" ("few studies have examined X") as a stand-in for a
substantive contribution — prefer naming the actual gap type (mechanism gap,
measurement gap, boundary-condition gap, institutional gap, theoretical
contradiction, empirical anomaly, methodological limitation, historical
omission).

<a id="claim-calibration"></a>

## Claim Calibration

Every substantive claim in a scholarly text has an epistemic type. Identify it
before drafting the sentence, and preserve it through any later stylistic
rewrite — voice edits must never change what kind of claim a sentence makes.

### Claim types

Use the same eight-way taxonomy `scholarly-corpus-builder` uses when it
extracts claim-calibration features from a corpus (`style-feature-schema.md`
§Claim calibration), so profiles from that skill map directly onto this one:

```text
descriptive | associational | causal | mechanistic | predictive |
interpretive | normative | formal
```

```yaml
descriptive:    "what was observed" — no relationship claimed
associational:  "X co-occurs with / predicts / is correlated with Y"
causal:         "X causes / produces / increases Y" — requires design support
                (see argument-and-claims.md#research-design-matrix)
mechanistic:    "X causes Y via process Z" — requires evidence for the
                intermediate step, not just the endpoint correlation
predictive:     "X forecasts Y" — a claim about forecasting performance, not
                about why
interpretive:   "this may be read as / plausibly means" — humanities/legal/
                qualitative meaning-claims, argued not measured
normative:      "X ought to / should" — a value claim, distinct from any
                empirical premise supporting it
formal:         true/false relative to stated axioms or definitions — proof,
                not evidence, is what settles it
```

### The claim-strength invariant

A stylistic rewrite must never silently move a claim up this scale:

```text
descriptive → associational → causal → mechanistic
```

or convert a hedged claim into an unhedged one, or a normative claim into a
descriptive one (or vice versa) without the user explicitly asking for an
argument change. Concretely, never let a "polish" pass turn:

```text
"is associated with"      into  "causes"
"may indicate"             into  "demonstrates"
"is consistent with X"     into  "confirms X"
"the evidence suggests"    into  "the evidence proves"
```

If a draft already contains claim-strength inflation, that is a defect to
flag and fix (see `quality-and-editing.md#quality-audit`), not a voice choice to preserve.

### Discipline-sensitive uncertainty language

Match hedging to the design and the field's own idiom — never apply a single
uncertainty phrasing template everywhere:

```yaml
natural_sciences: >
  is consistent with / supports the possibility that / suggests a role for /
  does not exclude / cannot rule out / within the limits of this design
medicine_health: >
  is associated with / was observed in this population / does not establish
  efficacy / consistent with, but not proof of, a causal effect
social_sciences: >
  the evidence is compatible with / under these institutional conditions /
  within the observed sample / conditional on the identifying assumption
humanities: >
  may be read as / this interpretation emphasizes / a competing reading would
  suggest / on this reading
law: >
  the stronger interpretation would imply / the doctrine does not clearly
  resolve / on the weight of authority
mathematics_formal: >
  holds under the stated hypotheses / is not established for the general case
  without additional assumptions
```

Do not hedge every sentence regardless of warrant — a sentence qualified past
the point of asserting anything is a failure mode, not caution (see
`quality-and-editing.md#human-scholarly-prose`). A well-supported descriptive or formal claim
should be stated plainly.

### Scope conditions

Strengthen a claim's credibility by narrowing it rather than by removing
hedges. State explicitly, where relevant:

```text
population | institution | historical period | jurisdiction |
experimental condition | measurement regime | sample | data-generating
process
```

"Under conditions of low state capacity, X" is a stronger scholarly move than
an unscoped "X," even though it claims less. Scope narrowing and hedging are
different tools — prefer narrowing a claim to its true domain over merely
qualifying an overbroad one.

### Applying this during rewrite

1. Identify the claim type and design ceiling for every major claim before
   touching its wording (cross-check `argument-and-claims.md#research-design-matrix`).
2. Rewrite for clarity/voice without moving the claim along the strength
   scale, changing its scope, or converting its type.
3. If the source text's claim strength already exceeds what its own stated
   evidence supports, that is a substantive problem — flag it to the user or
   correct it explicitly (never silently), per `argument-and-claims.md#citation-integrity` and
   `quality-and-editing.md#quality-audit`'s repair order (integrity before style).

<a id="citation-integrity"></a>

## Citation Integrity

Non-negotiable rules for how citations, quotations, and evidence attribution
are handled during drafting and rewriting. This outranks every voice
consideration (see `MODULE.md` §Operating hierarchy).

### Never fabricate

Never invent, guess, or "plausibly reconstruct":

```text
authors | titles | journal or venue names | publication years | DOIs |
ISBNs/ISSNs | page numbers | volume/issue numbers | quotations |
study findings or effect sizes | sample sizes | statistics
```

If a citation is needed but not supplied and cannot be retrieved through an
available tool, mark it `[VERIFY]` (or `[INSERT CITATION]` for a placeholder
the user will fill) rather than inventing a plausible-looking one. Where a
host provides retrieval tools, use them to find a real source rather than
guessing — but do not silently invent one either way.

### Reuse, don't reinvent, verification states

When a citation's source material comes from `scholarly-corpus-builder` (or
another provenance-aware tool), carry its verification state through rather
than treating every quoted or cited fact as equally certain:

```text
VERIFIED            persistent identifier checked
PARTIALLY_VERIFIED  title/venue/year found but identifier unverified
NEEDS_CHECK         plausible but not yet confirmed
REJECTED            could not be confirmed, or evidence contradicts it
```

(See that skill's `references/provenance-schema.md` for the authoritative
definitions — do not redefine these states differently here.) Do not present
a `NEEDS_CHECK` or `PARTIALLY_VERIFIED` source with the same confidence as a
`VERIFIED` one; say so if the distinction matters to the claim being made.

### The citation-preservation invariant

During any rewrite of existing scholarship:

- Preserve which specific claim each citation supports — never silently move
  a citation to support a different claim than the source text used it for.
- Never combine several citations into one so that a claim appears supported
  by a reference that does not actually address it.
- Never alter quoted material, even to "smooth" it stylistically — a
  quotation's wording is not subject to voice calibration.
- Never invent a quotation attributed to a historical or living scholar (see
  `voice-profiles.md#historical-voice-profiles` §Using this library).

### Citation density

Density should track discipline, genre, section, and claim type (see the
relevant `disciplines.md` file and `writing-genres.md#genre-matrix`) — not a fixed rate.
Mathematics and formal proof carry very few, precise citations; empirical
social science is dense at literature-positioning and sparser in results;
humanities argument is often citation-dense throughout but each citation
attaches to a specific reading, not a general area. Not every sentence needs
one; not every paragraph can go without one.

### Integration over dumping

Use citations to do specific argumentative work:

```text
establish consensus | mark contradiction | attribute origin/priority |
support a specific empirical claim | mark the boundary of what's established
```

Avoid citation dumping — a string of references at a paragraph's end doing no
individually identifiable work:

```text
weak:   "This is well established (Smith 2019; Jones 2020; Lee 2021; Park
        2018; Chen 2022)."
better: name what each cluster of sources actually establishes, or prune to
        the sources that are doing real work for the specific claim
```

### Quotation discipline

Quote only when the wording itself matters (a legal holding's exact language,
a literary passage under analysis, a definition whose precise phrasing is the
point) — not to decorate prose with borrowed authority. Never use a quotation
(real or invented) merely to make a passage sound more scholarly. Do not use
a famous line "because it sounds right" without verifying it is both real and
actually attributable to the claimed source.

### When rewriting under voice calibration

Voice strength (`quality-and-editing.md#editing-modes`) governs how much a sentence's wording may
change — it never governs whether a citation, quotation, statistic, dataset
description, or study finding may change. If a "high" voice-strength rewrite
would require altering any of these to make the prose flow better, restructure
the sentence around them instead of altering the substance.
