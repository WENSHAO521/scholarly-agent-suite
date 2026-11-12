# Discipline guidance

One section per family of the shared taxonomy (`../../shared/disciplines.md`). Each section starts at an `<a id>` anchor named by the family slug; load only the section(s) the task needs: [natural-sciences](#natural-sciences), [mathematics-formal](#mathematics-formal), [engineering-computing](#engineering-computing), [medicine-health](#medicine-health), [social-sciences](#social-sciences), [business-management](#business-management), [law](#law), [humanities](#humanities), [education](#education), [arts-design](#arts-design), [interdisciplinary](#interdisciplinary).

<a id="natural-sciences"></a>

## Natural Sciences

Physics, chemistry, biology, earth science, environmental science, astronomy,
materials science, neuroscience, ecology, evolutionary biology.

```yaml
discipline_family: natural_sciences
default_claim_style: associational_to_mechanistic  # causal only with controlled design
typical_argument_structures:
  - problem → known mechanism → specific uncertainty → experimental strategy →
    results → mechanistic interpretation → boundary conditions
  - observation → anomaly → mechanism → generalization (field/observational work)
typical_evidence:
  - controlled experiment
  - field observation
  - quantitative measurement
  - figures/data visualization as primary evidentiary objects
citation_behavior: dense_near_specific_claims  # not batched at paragraph end
methods_visibility: high  # replicability requires explicit, checkable detail
acceptable_first_person: yes  # "we measured", "we observed" is standard
common_failure_modes:
  - hypothesis overreach beyond what the design supports
  - treating a single study as settling a mechanism
  - narrative "storytelling" that smooths over genuine uncertainty
  - figure/caption doing argumentative work the prose should do explicitly
recommended_voice_profiles:
  - experimental-mechanistic
  - economical-scientific
book_writing_norms: >
  Monograph-scale natural-science writing (e.g., a synthesis volume) still keeps
  mechanistic restraint per chapter; narrative/historical framing is permitted in
  introductory chapters but should not carry mechanistic claims that the case
  chapters must actually establish.
article_writing_norms: >
  Prioritize hypothesis restraint, explicit observation-vs-mechanism separation,
  quantitative precision, and figure-driven argument that the prose interprets
  rather than merely restates.
```

### Prose guidance

Scientific prose should be clear rather than artificially ornate. Prefer plain,
cumulative sentences that stack evidence before inference (see the Darwin entry
in `voice-profiles.md#historical-voice-profiles`). Keep causal language proportionate: reserve
causal verbs ("causes," "drives," "produces") for designs that support them;
otherwise use associational language ("is associated with," "correlates with,"
"predicts").

### Uncertainty language

```text
is consistent with / supports the possibility that / suggests a role for /
does not exclude / cannot rule out / within the limits of this design
```

### Common terminology to disambiguate in interdisciplinary work

`resilience`, `robustness`, `stability` — see
`references/writing-genres.md#interdisciplinary-writing`.

<a id="mathematics-formal"></a>

## Mathematics and Formal Sciences

Pure mathematics, applied mathematics, statistics, logic, operations research,
theoretical computer science, information theory.

```yaml
discipline_family: mathematics_formal
default_claim_style: formal  # true/false relative to stated axioms, not degrees of confidence
typical_argument_structures:
  - problem → notation → definitions → main theorem → supporting results →
    proof → discussion/corollaries
typical_evidence:
  - proof (the only admissible evidence for a formal claim)
  - worked example / counterexample for illustration, not proof
citation_behavior: sparse_and_precise  # attributed results, prior theorems, precise statement of what is reused
methods_visibility: high  # every step of a proof must be checkable
acceptable_first_person: yes  # "we prove", "we show" is standard; also common: passive/impersonal "it follows that"
common_failure_modes:
  - rhetorical flourish substituting for proof
  - notation drift (same symbol reused with different meaning)
  - hidden assumptions not stated as hypotheses
  - motivation section that overclaims the theorem's scope
recommended_voice_profiles:
  - formal-deductive
book_writing_norms: >
  Textbook and monograph chapters should keep notation stable across the whole
  book (track it in the monograph continuity state's `terminology:` field) and
  should clearly separate motivating intuition (remarks) from the formal
  development (definitions, theorems, proofs).
article_writing_norms: >
  Separate motivation, formal statement, proof, intuition/remark, and corollary
  into distinct, clearly labeled moves. Avoid unnecessary rhetorical amplitude —
  precision and logical economy are the register, not ornamentation.
```

### Prose guidance

Short, declarative sentences; notation carries the argument. Define every symbol
before use; do not redefine a symbol with a different meaning later in the same
document. State hypotheses explicitly rather than leaving them implicit in the
proof. Distinguish clearly:

```text
motivation | formal statement | proof | intuition/remark | corollary
```

Counterarguments in this family take the form of counterexamples and boundary
cases, not prose objections — handle them as such.

<a id="engineering-computing"></a>

## Engineering and Computing

Computer science, artificial intelligence/machine learning, software
engineering, electrical, mechanical, civil, chemical, and biomedical
engineering, robotics, systems engineering, data science, human-computer
interaction (HCI).

```yaml
discipline_family: engineering_computing
default_claim_style: design_and_evaluation  # performance/behavior claims backed by measurement
typical_argument_structures:
  - motivation → design goals/constraints → design choice → implementation →
    evaluation/benchmark → ablation → interpretation → limitations
typical_evidence:
  - benchmark results
  - ablation studies
  - complexity/performance analysis
  - system measurements under stated conditions
citation_behavior: moderate_dense_at_related_work  # dense in related-work, close to specific claims elsewhere
methods_visibility: high  # reproducibility (code/data availability where applicable)
acceptable_first_person: yes  # "we propose", "we evaluate" is standard
common_failure_modes:
  - conflating a benchmark win with a general claim of superiority
  - hiding design choices inside "implementation details"
  - ablations that don't isolate the claimed contribution
  - buzzword-driven framing ("novel," "state-of-the-art") without the evaluation
    to back it
recommended_voice_profiles:
  - analytical-mechanistic
  - economical-scientific
book_writing_norms: >
  Handbook/textbook chapters in this family should separate conceptual
  exposition from worked implementation detail, and keep terminology (e.g., a
  specific architecture or algorithm name) stable across chapters via the
  monograph continuity state.
article_writing_norms: >
  Distinguish paper sub-genres explicitly: system paper, algorithm paper,
  architecture paper, benchmark paper, empirical software engineering study, HCI
  paper, AI/ML paper — each weights design/implementation/evaluation differently.
  Always keep design choice, implementation, benchmark, and interpretation in
  separately identifiable moves.
```

### Prose guidance

State the design goal and constraint before the design choice, so the choice
reads as a decision rather than an arbitrary description. Report benchmark
numbers with the conditions that produced them adjacent to the numbers, not in a
separate appendix the prose never references. Interpret ablations mechanistically
("removing X causes Y because...") rather than only numerically ("X: 0.81, no X:
0.76").

<a id="medicine-health"></a>

## Medicine and Health Sciences

Clinical medicine, public health, epidemiology, nursing, pharmacy, dentistry,
biomedical sciences, health policy, digital health, medical AI, psychiatry.

```yaml
discipline_family: medicine_health
default_claim_style: strict_separation  # observation / association / diagnostic performance / causal efficacy / clinical utility kept distinct
typical_argument_structures:
  - clinical problem → prior evidence → design → population/sample → outcome
    measures → results → clinical interpretation → limitations → implications
    for practice
typical_evidence:
  - clinical trial data
  - cohort/case-control data
  - diagnostic performance metrics
  - systematic review/meta-analytic synthesis
citation_behavior: dense_near_specific_claims  # guideline- and evidence-grade aware
methods_visibility: very_high  # population, design, and measurement must be fully specified for critical appraisal
acceptable_first_person: yes  # "we enrolled", "we found" is standard in clinical/epidemiological writing
common_failure_modes:
  - reporting an association as if it were a causal or efficacy claim
  - reporting diagnostic accuracy as if it implied clinical utility
  - understating limitations of observational design
  - overgeneralizing from a study population to a broader population
recommended_voice_profiles:
  - clinical-evidentiary
  - experimental-mechanistic
book_writing_norms: >
  Handbook/textbook chapters must keep the same strict separation between
  observation, association, diagnostic performance, and causal/efficacy claims
  as article-length work; do not relax this for pedagogical simplicity without
  flagging the simplification explicitly.
article_writing_norms: >
  Maintain rigid separation of: observation, association, diagnostic performance,
  clinical utility, and causal efficacy. State the evidence level supporting each
  claim (e.g., RCT vs. observational vs. case series) rather than letting
  confident prose imply a stronger design than was used.
```

### Prose guidance

Keep method (population, design, measurement, follow-up) visible and close to
the results it produced. State the evidence level explicitly when making a
clinical-implication claim. Do not let a p-value or effect size stand in for a
clinical-significance judgment — name both separately.

### Uncertainty language

```text
is associated with / was observed in this population / does not establish
efficacy / consistent with, but not proof of, a causal effect / diagnostic
performance in this sample does not by itself establish clinical utility
```

<a id="social-sciences"></a>

## Social Sciences

Political science, public administration, public policy, economics, sociology,
psychology, anthropology, international relations, communication, criminology,
human geography, demography, social policy.

```yaml
discipline_family: social_sciences
default_claim_style: mechanism_and_scope_conditioned  # theory + evidence, scope conditions matter as much as the mechanism itself
typical_argument_structures:
  - problem → literature → theoretical mechanism → hypotheses/questions →
    data → methods → results → interpretation → limitations → contribution
  - concept → mechanism → social structure → empirical pattern → scope condition
typical_evidence:
  - survey/observational data
  - quasi-/natural experiments
  - qualitative/interview/archival data
  - case comparison
citation_behavior: dense_at_literature_positioning  # specific to the claim being extended/challenged
methods_visibility: high
acceptable_first_person: yes  # "we argue", "I find" is now standard in most sub-fields
common_failure_modes:
  - generic "gap spotting" replacing a substantive contribution
  - causal language applied to associational/observational designs
  - literature review as undifferentiated list rather than positioned argument
  - mechanism asserted but never actually tested or illustrated
recommended_voice_profiles:
  - institutional-comparative
  - conceptual-sociological
  - strategic-interaction
book_writing_norms: >
  Monograph chapters should each advance a distinct piece of the mechanism/
  argument (see chapter roles in `references/writing-genres.md#book-writing`) rather than
  repeating the same literature review or restating the contribution in every
  chapter.
article_writing_norms: >
  Name the mechanism explicitly, state its scope conditions, and match claim
  strength (descriptive/associational/causal/mechanistic) to the actual research
  design. Prefer a substantive gap type (mechanism, measurement, boundary
  condition, institutional, theoretical contradiction) over generic gap language.
```

### Prose guidance

State scope conditions plainly ("under conditions of low state capacity...")
rather than leaving generalization implicit. Keep evidence close to the specific
claim it supports rather than batching citations. Treat qualitative and
quantitative evidence with genre-appropriate standards — do not narrate
qualitative material as if it carried statistical generalizability, or vice
versa.

### Economics

Economics is grouped with social sciences for routing, but its conventions
are distinctive enough to warrant dedicated treatment: microeconomics,
macroeconomics, political economy, development economics, labor economics,
public economics, behavioral economics, econometrics.

```yaml
subfield: economics
default_claim_style: disciplined_causal  # identification strategy, not just theory, licenses causal language
typical_argument_structure: >
  economic question → model/identification strategy → institutional
  assumptions → estimand → data → results → robustness → mechanism →
  welfare/policy implication (see argument-and-claims.md#argument-architectures §Economics)
typical_evidence:
  - observational/administrative data with an identification strategy (DiD,
    RDD, IV, natural experiment — see argument-and-claims.md#research-design-matrix)
  - structural or reduced-form models
  - lab/field experiments (behavioral and experimental economics)
citation_behavior: dense_at_identification_and_literature_positioning
methods_visibility: very_high  # the identification strategy must be fully inspectable
acceptable_first_person: yes
common_failure_modes:
  - causal language exceeding what the identification strategy actually
    establishes (see argument-and-claims.md#research-design-matrix rows for did/rdd/iv/
    natural_experiment)
  - treating statistical significance as economic/practical significance
  - an estimand stated loosely enough that it's unclear what parameter is
    actually being estimated
  - policy implications drawn beyond the studied population/market
recommended_voice_profiles:
  - strategic-interaction
  - economical-scientific
prose_guidance: >
  State the estimand and identification strategy explicitly before reporting
  results. Keep the model's institutional assumptions visible rather than
  buried in a footnote. Reserve causal verbs for designs that support them;
  otherwise report the coefficient/association plainly and let the
  robustness section do the work of building confidence, not the prose's
  tone.
```

<a id="business-management"></a>

## Business and Management

Management, organization studies, strategy, marketing, finance, accounting,
entrepreneurship, human resource management, operations management, innovation
studies.

```yaml
discipline_family: business_management
default_claim_style: construct_and_mechanism_disciplined
typical_argument_structures:
  - problem → literature → theoretical mechanism → hypotheses → data → methods
    → results → interpretation → limitations → contribution
  - practice problem → conceptual framework → case/comparative analysis →
    managerial/theoretical implication
typical_evidence:
  - firm-level/archival data
  - survey data
  - case studies
  - experiments (lab or field)
citation_behavior: dense_at_theory_and_construct_definition
methods_visibility: high
acceptable_first_person: yes  # "we test", "we find" is standard
common_failure_modes:
  - managerial buzzword prose substituting for defined constructs
  - constructs used inconsistently across a paper (e.g., "innovation" shifting
    meaning mid-argument)
  - mechanism asserted rhetorically without being tested or illustrated
  - overclaiming generalizability from a single-firm or single-industry sample
recommended_voice_profiles:
  - conceptual-sociological
  - institutional-comparative
  - strategic-interaction
book_writing_norms: >
  Practitioner-facing or textbook chapters may use plainer prose and more
  worked examples, but constructs must still be defined once and used
  consistently — track definitions in the monograph continuity state.
article_writing_norms: >
  Define every construct explicitly before using it in a hypothesis; demand
  explicit mechanism rather than letting a correlational result imply a
  managerial causal story. Avoid buzzwords ("synergy," "leverage," "disruptive")
  standing in for a defined construct.
```

### Prose guidance

Prefer precise, defined constructs over trend vocabulary. State the mechanism a
hypothesis is testing before reporting whether it was supported. Keep
generalizability claims proportionate to sample scope (industry, firm size,
geography, time period).

<a id="law"></a>

## Law

Public law, private law, international law, comparative law, constitutional law,
administrative law, criminal law, legal theory, law and society, empirical
legal studies.

```yaml
discipline_family: law
default_claim_style: doctrinal  # what the law is, distinct from what it ought to be
typical_argument_structures:
  - legal problem → doctrine/authority → conflict or ambiguity → interpretation
    → comparative or normative analysis → consequence
typical_evidence:
  - statutes, case law, and other primary legal authority
  - secondary scholarly authority
  - comparative jurisdictional analysis
  - empirical legal data (for empirical legal studies sub-genre)
citation_behavior: very_dense_and_precise  # pinpoint citation to authority is often obligatory, not optional
methods_visibility: high_for_doctrinal_reasoning  # the interpretive steps must be traceable to authority
acceptable_first_person: variable  # many doctrinal traditions avoid first person; empirical legal studies and legal theory permit "we/I argue"
common_failure_modes:
  - collapsing "what the law is" into "what the law ought to be" without marking
    the shift
  - citing authority for a proposition it does not actually support
  - treating a single jurisdiction's rule as if it were universal without
    marking the comparative scope
  - resolving genuine doctrinal ambiguity by assertion rather than argument
recommended_voice_profiles:
  - doctrinal-legal
  - normative-systematic
book_writing_norms: >
  Treatise/monograph chapters should keep the same rigorous separation of
  descriptive doctrine from normative argument as articles; track how a rule is
  characterized across chapters in the monograph continuity state to avoid
  contradicting an earlier chapter's characterization of the same doctrine.
article_writing_norms: >
  Separate explicitly: what the law is, what courts have held, what
  interpretation is plausible given the authority, and what the law ought to be.
  Provide pinpoint citation to primary authority for doctrinal claims.
```

### Prose guidance

Mark the shift from descriptive to normative explicitly ("the better view is
that...," "as a matter of policy, this rule should..."). When authority is
ambiguous or conflicting, say so rather than resolving it silently in the prose.
In comparative work, name the jurisdiction for every doctrinal claim rather than
letting "the law" imply universality.

<a id="humanities"></a>

## Humanities

Philosophy, history, literature, linguistics, religious studies, classics, art
history, cultural studies, intellectual history, ethics, political thought.

```yaml
discipline_family: humanities
default_claim_style: interpretive  # readings argued for, not "proven" in the scientific sense
typical_argument_structures:
  - interpretive problem → existing reading → text/source evidence → conceptual
    intervention → close analysis → implication (literature/cultural studies)
  - question → sources → chronological reconstruction → interpretation →
    historiographical positioning → implication (history)
  - thesis → key distinction → argument → strongest objection →
    response/qualification → refined thesis (philosophy)
typical_evidence:
  - primary text/source close reading
  - archival material
  - historiographical/critical tradition
  - conceptual argument (philosophy)
citation_behavior: moderate_to_dense  # attributed readings, engaged rather than listed
methods_visibility: moderate  # source/interpretive method made explicit, not a "methods section" in the scientific sense
acceptable_first_person: yes  # "I argue", "this reading suggests" is standard and often necessary to mark interpretive stance
common_failure_modes:
  - treating one's own reading as the only possible one without engaging
    competing readings
  - anachronism (importing a later concept into an earlier text/period without
    marking the move)
  - source evidence disconnected from the interpretive claim it is meant to
    support
  - forcing scientific-style claim calibration onto genuinely interpretive work
recommended_voice_profiles:
  - interpretive-humanistic
  - historical-structural
  - normative-systematic
book_writing_norms: >
  Do not force scientific article structure onto book chapters. Narrative and
  interpretive presence may be stronger here than in empirical disciplines; keep
  terminology (especially contested concepts) stable across chapters via the
  monograph continuity state, or explicitly flag and justify a chapter's
  refinement of an earlier definition.
article_writing_norms: >
  Support close reading, archival argument, historical contextualization,
  conceptual interpretation, historiographical intervention, and philosophical
  argument as first-class architectures — do not impose IMRaD. Allow stronger
  authorial presence where the genre permits it.
```

### Prose guidance

Mark interpretive stance explicitly ("may be read as," "this interpretation
emphasizes," "a competing reading would") rather than asserting a reading as
the only possible one. Keep source evidence physically close to the claim it is
adduced for. Distinguish observation (what the text/source says), interpretation
(what it plausibly means), and speculation (what it might mean, more tentatively)
as three distinct registers.

### Philosophy

Grouped with humanities for routing, but distinctive enough for dedicated
treatment: analytic philosophy, continental philosophy, ethics, political
philosophy, philosophy of science, epistemology, metaphysics.

```yaml
subfield: philosophy
default_claim_style: argued_thesis  # a position defended against its strongest objection, not "proven" empirically
typical_argument_structure: >
  problem → conceptual distinction → argument → strongest objection →
  counterexample → refinement → bounded conclusion
typical_evidence:
  - argument from consequence, counterexample, and thought experiment
  - close engagement with the primary and secondary philosophical literature
  - conceptual analysis
citation_behavior: dense_and_engaged  # attributed, argued with, not merely listed
acceptable_first_person: yes  # "I argue," "I will show" is standard
common_failure_modes:
  - engaging a weaker version of an objection than its strongest form
  - fake profundity — rhetorical amplitude standing in for an actual argument
  - treating a continental-tradition text with analytic-style claim
    calibration or vice versa without acknowledging the difference in method
  - a key term used inconsistently across the piece's central argument
recommended_voice_profiles:
  - normative-systematic
prose_guidance: >
  Take the strongest form of an opposing view seriously before responding to
  it (see the Popper entry in voice-profiles.md#historical-voice-profiles). High definition
  and counterargument density are appropriate here in a way they would be
  excessive elsewhere — but every distinction earns its place by doing
  argumentative work, not by performing rigor.
```

### History

Grouped with humanities for routing, but distinctive enough for dedicated
treatment: political history, social history, economic history, intellectual
history, cultural history, global history, microhistory, history of science.

```yaml
subfield: history
default_claim_style: interpretive_reconstruction  # argued from available sources, not proven the way a formal claim is
typical_argument_structure: >
  historical problem → historiography → source base → context → episode →
  interpretation → comparison → historical significance
typical_evidence:
  - primary sources (archival, documentary, material)
  - secondary historiographical literature, positioned rather than merely
    cited
  - comparative historical cases
citation_behavior: dense_and_source_grounded
acceptable_first_person: variable  # common in historiographical positioning, less so in pure narrative reconstruction
common_failure_modes:
  - treating a single source as settling a contested chronology
  - anachronism — importing a later concept into an earlier period without
    marking the move
  - narrating a historical episode as inevitable in hindsight rather than as
    it was contingently experienced
  - historiographical positioning skipped, so the piece reads as if no one
    has written on the topic before
recommended_voice_profiles:
  - historical-structural
prose_guidance: >
  Make source reliability explicit rather than treating all sources as
  equally probative. Position the account against the existing
  historiography by name — not "historians have studied this topic" but
  which interpretive tradition this account extends, revises, or breaks
  from. Do not force hypothesis-testing language onto a genuinely
  interpretive reconstruction.
```

<a id="education"></a>

## Education

Education policy, curriculum studies, higher education, educational psychology,
pedagogy, comparative education, teacher education, educational technology.

```yaml
discipline_family: education
default_claim_style: evidence_aligned_pedagogical  # pedagogical claims must track the evidence actually available
typical_argument_structures:
  - problem of practice → literature/theory → research question → design
    (quantitative/qualitative/mixed) → findings → implications for practice/policy
  - policy problem → context → theoretical framework → analysis → policy
    implication
typical_evidence:
  - classroom/institutional data
  - survey and assessment data
  - qualitative classroom or policy case studies
  - comparative cross-system data
citation_behavior: dense_at_literature_and_framework
methods_visibility: high
acceptable_first_person: yes  # "we designed", "I observed" is standard, especially in qualitative/practitioner research
common_failure_modes:
  - recommending a pedagogical practice beyond what the cited evidence supports
  - treating a small qualitative study as generalizable policy evidence
  - conflating curriculum theory with empirical effectiveness claims
  - policy recommendations disconnected from the stated evidence base
recommended_voice_profiles:
  - conceptual-sociological
  - clinical-evidentiary
  - institutional-comparative
book_writing_norms: >
  Textbook and handbook chapters should keep worked classroom/policy examples
  consistent with the pedagogical claims being illustrated; track terminology
  (e.g., a specific pedagogical framework's key terms) across chapters.
article_writing_norms: >
  Require explicit alignment between the strength of a pedagogical or policy
  claim and the design that produced the evidence for it (do not let a
  qualitative classroom study support a system-wide policy claim without
  marking the scope difference).
```

### Prose guidance

State the evidence base for a pedagogical or policy recommendation explicitly
("based on this classroom-level qualitative study..." vs. "system-wide data
indicate..."). Keep comparative-education claims scoped to the systems actually
studied.

<a id="arts-design"></a>

## Arts and Practice-Based Research

Music, performance studies, fine arts, design research, architecture, film
studies, theatre, creative practice research.

```yaml
discipline_family: arts_design
default_claim_style: interpretive_and_reflective  # critical/interpretive claims and practitioner reflection legitimately coexist with systematic evidence
typical_argument_structures:
  - work/practice → critical or historical context → close analysis/reading of
    the work → conceptual intervention → implication
  - design/practice problem → process documentation → reflective analysis →
    contribution to practice or theory
typical_evidence:
  - close analysis of the work (score, performance, image, building, film, text)
  - process documentation (practice-based research)
  - critical/historical context
  - reception/reflective evidence
citation_behavior: moderate  # engaged with critical/historical tradition, not citation-dense in the empirical-science sense
methods_visibility: moderate_to_high  # practice-based research must document process rigorously even where the output is a work, not a dataset
acceptable_first_person: yes  # reflective/practitioner voice is often central, not a lapse from objectivity
common_failure_modes:
  - reflective/practitioner prose left un-anchored to critical or historical
    context
  - treating personal creative intention as if it settled interpretive meaning
  - practice-based process documentation too thin to be evaluated as research
  - forcing empirical-science claim calibration onto genuinely interpretive
    practice-based work
recommended_voice_profiles:
  - interpretive-humanistic
  - historical-structural
book_writing_norms: >
  Monograph/handbook chapters may combine sustained close analysis with
  reflective practitioner voice; keep the critical/historical framework and key
  terms consistent across chapters via the monograph continuity state.
article_writing_norms: >
  Recognize that reflective and interpretive writing may legitimately coexist
  with systematic process documentation — do not force a scientific
  hypothesis/results structure onto practice-based research; instead require
  the process documentation to be rigorous enough to support the reflective
  claims made about it.
```

### Prose guidance

Ground interpretive claims about a work in specific, cited features of the work
(a passage, a frame, a detail, a structural choice) rather than general
impression. In practice-based research, keep process documentation detailed
enough that the reflective analysis built on it is actually checkable by a
reader.

<a id="interdisciplinary"></a>

## Interdisciplinary Fields

Science and technology studies, digital humanities, computational social
science, environmental humanities, bioethics, health humanities, urban studies,
development studies, sustainability studies, complexity science, AI governance.

```yaml
discipline_family: interdisciplinary
default_claim_style: reconciled_across_home_and_secondary_disciplines
typical_argument_structures:
  - varies by home discipline; select from `references/argument-and-claims.md#argument-architectures`
    using the home discipline's family, then layer secondary-discipline moves in
    explicitly (see `references/writing-genres.md#interdisciplinary-writing`)
typical_evidence:
  - mixed: whatever the home and secondary disciplines each license, kept
    explicitly attributed to the standard that licenses it
citation_behavior: dense_and_field_attributed  # cite in a way that signals which field's standard a claim is drawing on
methods_visibility: high  # especially important here because reviewers may come from either contributing field
acceptable_first_person: yes  # generally standard across the contributing fields listed above
common_failure_modes:
  - blending evidentiary standards from two fields without flagging the move
    (see `references/writing-genres.md#interdisciplinary-writing`)
  - a term drifting between its meanings in different fields across the same
    document
  - writing that satisfies neither field's reviewers because it hedges on both
    fields' core commitments simultaneously
  - treating "interdisciplinary" as license to skip a genuine argument
    architecture altogether
recommended_voice_profiles:
  - determined by home discipline; add a secondary-discipline inflection rather
    than replacing the home voice
book_writing_norms: >
  Use `references/writing-genres.md#book-writing`'s continuity state to track terminology
  ownership decisions (see `references/writing-genres.md#interdisciplinary-writing`) across
  chapters — this is the most common source of inconsistency in interdisciplinary
  monographs.
article_writing_norms: >
  Establish home and secondary discipline explicitly (internally, and to the
  reader where it affects interpretation), and resolve every cross-disciplinary
  term's intended meaning on first use. See
  `references/writing-genres.md#interdisciplinary-writing` for the full procedure.
```

### Prose guidance

State plainly, early, which discipline's evidentiary standard is being applied to
which part of the argument (e.g., "the empirical claims in this section follow
standard epidemiological practice; the normative claims follow the bioethics
literature cited above"). This is the single highest-value move for
interdisciplinary credibility with mixed audiences.
