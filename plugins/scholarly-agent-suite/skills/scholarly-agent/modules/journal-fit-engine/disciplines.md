# Discipline fit emphasis

One section per family of the shared taxonomy (`../../shared/disciplines.md`). Each section starts at an `<a id>` anchor named by the family slug; load only the section(s) the task needs: [natural-sciences](#natural-sciences), [mathematics-formal](#mathematics-formal), [engineering-computing](#engineering-computing), [medicine-health](#medicine-health), [social-sciences](#social-sciences), [business-management](#business-management), [law](#law), [humanities](#humanities), [education](#education), [arts-design](#arts-design), [interdisciplinary](#interdisciplinary).

<a id="natural-sciences"></a>

## Natural Sciences

Covers: physics, chemistry, biology, astronomy, earth sciences, environmental
sciences, ecology, materials science, neuroscience.

### Fit emphasis

- **Method/data fit is high-stakes.** Experimental design, instrumentation,
  and statistical treatment must match what the journal's recent corpus
  actually publishes — a purely computational paper submitted to a
  primarily-experimental journal is a method mismatch even on-topic.
- **Novelty and priority matter more here than in most fields** — check
  whether the journal's scope statement and recent issues emphasize
  first-report/priority claims vs. incremental/confirmatory work, and match
  the manuscript's actual contribution type honestly.
- **Subfield specificity is often narrow.** "Biology" is rarely a useful
  discipline granularity — match at the subfield level (e.g. molecular
  ecology vs. population ecology vs. behavioral ecology) since these often
  have distinct venue ecosystems.
- **Reproducibility/data-sharing requirements** are increasingly common hard
  constraints (raw data deposition, code availability, pre-registration in
  some subfields) — check current official policy, don't assume.
- **Multi-author, multi-lab manuscripts** should check authorship-order and
  contribution-statement requirements, which vary by journal and can affect
  submission readiness independent of scientific fit.

### Genre notes

Distinguish Letters/Rapid Communications (short, high-novelty), full Articles,
Reviews (often invited-only at high-tier venues — verify before treating as
an open submission route), and Registered Reports (a distinct, pre-results
review model in some subfields) as genuinely different submission tracks,
not interchangeable labels.

<a id="mathematics-formal"></a>

## Mathematics and Formal Sciences

Covers: pure mathematics, applied mathematics, statistics, logic, operations
research, information theory, theoretical computer science.

### Fit emphasis (from spec: subject area very high, problem-class high,
technical depth high, prose style secondary)

- **Subject classification is the primary fit signal.** Use the field's
  standard classification scheme (e.g. MSC codes in mathematics) as the
  anchor for matching, more than free-text topic description.
- **Problem-class and technical depth dominate over topical description.**
  Two papers on "graph theory" can belong in entirely different journals
  depending on whether the contribution is a new proof technique, a
  computational result, an applied modeling contribution, or a survey of
  existing results.
- **Writing/prose style is a secondary concern.** Unlike social sciences or
  humanities, argument architecture and narrative framing carry little
  weight in fit; rigor, proof completeness, and problem significance to the
  target community dominate.
- **Audience specialization matters more than breadth.** A highly technical
  proof-based contribution needs a venue whose readership can evaluate the
  proof — a broad "applied math" journal may be a poor audience fit even if
  topically adjacent.
- **Length and format conventions vary widely** (some venues favor short,
  dense notes; others long expository papers) — check actual length norms
  from the journal's recent corpus, not just the stated limit.
- **Preprint culture (e.g. arXiv-first norms)** is often the default in this
  family — verify the journal's preprint policy rather than assuming either
  universal acceptance or prohibition.

### Contribution types most relevant here

theorem/proof contribution, new method, dataset/benchmark (applied
statistics/OR), algorithm, measurement. Theory contributions require genuine
proof or formal development — citing a theorem is not a theoretical
contribution (see [fit-model.md](references/fit-model.md) §Theory fit).

<a id="engineering-computing"></a>

## Engineering and Computing

Covers: computer science, AI/ML, software engineering, electrical
engineering, mechanical engineering, civil engineering, chemical
engineering, biomedical engineering, robotics, data science, HCI.

### Venue-type distinction (critical for this family)

Distinguish journal, conference, workshop, and transactions venues
explicitly before recommending. In several CS/AI subfields (ML, systems,
HCI, robotics, security), top-tier conferences function as the *primary*
venue — a journal-only recommendation can be actively wrong strategic advice
for these subfields. This Skill is journal-first by default (see
[integration.md](references/integration.md) roadmap), but must flag when
a conference-first strategy is actually the field norm rather than silently
defaulting to journals.

### Fit emphasis

- **Benchmark/dataset/algorithm contributions** need venues that explicitly
  publish and evaluate such contributions (reproducibility and evaluation
  rigor expectations vary significantly by venue).
- **System/engineering papers** (a working system, an implementation, an
  applied deployment) fit differently than purely theoretical algorithmic
  contributions — match against the journal's actual accepted-article-type
  taxonomy (engineering/system paper vs. original research).
- **Fast-moving subfields (AI/ML especially)** need recency-weighted journal
  profiles — see [fit-model.md](references/fit-model.md) §Temporal fit.
  A journal's 2019 scope statement may not reflect its 2025–2026 actual
  output in a field moving this fast.
- **Reproducibility artifacts** (code, data, trained models) are increasingly
  hard requirements at some venues — check current official policy.
- **Interdisciplinary computing work** (e.g. AI + medicine, AI + law) should
  be routed by primary contribution, not by which field supplied the
  motivating application — see
  [interdisciplinary.md](#interdisciplinary) and
  [fit-model.md](references/fit-model.md) §Interdisciplinary manuscripts.

### Genre notes

Journal categories in this family often include: Research Article, Technical
Note/Brief, Survey/Review, System Demonstration, Benchmark Paper — verify the
target journal's own taxonomy since "Transactions" journals frequently have
different length/rigor expectations than a same-publisher "Letters" venue.

<a id="medicine-health"></a>

## Medicine and Health Sciences

Covers: clinical medicine, biomedical sciences, epidemiology, public health,
nursing, pharmacy, dentistry, psychiatry, health policy, digital health,
medical AI.

### Fit emphasis (from spec: study design very high, clinical relevance very
high, scope high, article type high)

- **Study design is the dominant fit signal**, often more than topic —
  match RCT, cohort, case-control, cross-sectional, systematic
  review/meta-analysis, case report, or qualitative design against what the
  journal's recent corpus actually publishes and what its stated article
  types accept.
- **Clinical relevance and audience specificity matter acutely.** A finding
  relevant to a narrow clinical subspecialty needs a subspecialty audience,
  not just a general-medicine venue with topical overlap.
- **Reporting-guideline compliance can be a hard submission constraint.**
  Check whether CONSORT (RCTs), STROBE (observational), PRISMA (systematic
  reviews/meta-analyses), CARE (case reports), TRIPOD (prediction models), or
  STARD (diagnostic accuracy) applies, per
  [adaptation-policy.md](references/adaptation-policy.md). Do not force an
  irrelevant guideline onto an unrelated design.
- **Clinical trial registration** is frequently a hard prerequisite for
  publication of trial results — verify current journal/ICMJE-aligned policy
  rather than assuming.
- **Ethics/IRB approval and reporting** requirements are near-universal but
  vary in required detail — check current official instructions.
- **Medical AI / digital health** sits at an interdisciplinary boundary
  (clinical specialty vs. medical informatics vs. AI methods venue) — route
  by primary contribution; see
  [interdisciplinary.md](#interdisciplinary) and
  [fit-model.md](references/fit-model.md) §Interdisciplinary manuscripts.

### Genre notes

Distinguish Original Article, Research Letter, Brief Report, Case Report,
Systematic Review, Meta-analysis, Clinical Practice Guideline, and
Perspective/Viewpoint as genuinely different tracks with different
review/evidence expectations — verify against the specific journal's
taxonomy rather than assuming standardization across the family.

<a id="social-sciences"></a>

## Social Sciences

Covers: political science, public administration, public policy, economics,
sociology, psychology, anthropology, international relations, communication,
criminology, geography, demography, social policy.

### Fit emphasis (from spec: for empirical quantitative work — scope high,
topic high, method high, genre high, audience medium-high, writing
architecture medium)

- **Method fit is a major discriminator within this family.** Quantitative
  (survey, panel, causal-inference designs), qualitative (interview,
  ethnography, case comparison), and mixed-methods traditions often cluster
  in different journals even within the same substantive subfield — verify
  against the journal's recent method mix, not just its topical scope.
- **Theory vs. empirics balance varies significantly by subfield and by
  journal** (e.g. sociology has both heavily theoretical and heavily
  empirical flagship venues) — check the journal's actual balance rather
  than assuming a discipline-wide norm.
- **Geographic/case scope is a recurring fit issue.** A single-country study
  can be a strong fit for an international journal if the manuscript
  develops portable theoretical/mechanism implications — see
  [fit-model.md](references/fit-model.md) §Geographic and
  internationalization fit for how to strengthen this, not just flag it.
- **Policy relevance** is a distinct audience-fit dimension from
  disciplinary-theory relevance — a strong policy contribution may fit a
  policy-audience journal better than a top disciplinary-theory journal even
  on the same topic.
- **Preregistration and open-data norms** vary substantially by subfield
  (strong in much of psychology, more mixed elsewhere) — check current
  journal policy rather than assuming.

### Genre notes

Distinguish Original Research/Empirical Article, Theory/Conceptual Paper,
Research Note (often shorter, narrower-contribution track), Systematic
Review, and Comparative Study as distinct tracks with different length and
evidentiary expectations.

<a id="business-management"></a>

## Business and Management

Covers: management, organization studies, strategy, marketing, finance,
accounting, entrepreneurship, HRM, operations, innovation.

### Fit emphasis

- **Institutional journal lists dominate practical strategy here more than
  in most families** — ABS Academic Journal Guide, ABDC, FT50, and similar
  lists are frequently hard constraints from the user's institution (tenure,
  promotion, doctoral requirements). Treat a stated list as a genuine
  constraint (see
  [submission-strategy.md](references/submission-strategy.md) §Career
  objectives and institutional lists), but never present list membership
  itself as evidence of intellectual fit — it is a career-strategy filter,
  applied in Stage 2, not a Stage 1 fit signal.
- **Theory-building vs. theory-testing vs. practice-oriented contribution
  type** is a major venue discriminator — a rigorous theory-testing empirical
  paper and a normative practitioner-facing piece rarely belong in the same
  journal even on identical topics.
- **Method norms cluster by subfield**: finance/accounting lean heavily
  quantitative/econometric; organization studies and entrepreneurship often
  support qualitative and mixed methods; marketing spans both experimental
  and survey/econometric traditions. Verify against the specific journal's
  recent corpus.
- **Managerial/practical implications sections** are often an explicit,
  checkable requirement distinct from the academic contribution — check
  whether the journal expects a dedicated practitioner-relevance discussion.

### Genre notes

Distinguish Original Research/Empirical Article, Theory/Conceptual Paper
(a legitimate, distinct genre in this family, unlike some sciences),
Literature Review/Meta-analysis, Case Study, and Research Note as separate
tracks.

<a id="law"></a>

## Law

Covers: constitutional law, administrative law, international law,
comparative law, criminal law, private law, legal theory, law and society,
empirical legal studies.

### Venue-type distinction (critical for this family)

Distinguish explicitly between:

- **law reviews** (often student-edited, especially in the US model; article
  selection and editorial process differ substantially from peer review)
- **peer-reviewed legal journals** (faculty/expert peer review, closer to
  the standard academic model used elsewhere in this Skill)
- **doctrinal journals** (focused on legal-rule analysis and interpretation)
- **law-and-society / empirical-legal-studies journals** (social-science
  methodology applied to legal questions, often reviewed and edited more
  like social-science venues)

Do not assume these have identical editorial processes, review timelines, or
evaluation criteria — they are structurally different submission ecosystems,
and this affects both fit and practical strategy (e.g. many US law reviews
accept expedite requests and multi-submission is a normal, expected practice
there, unlike most peer-reviewed venues in this Skill's general policy —
verify current journal-specific submission norms before advising on
simultaneous submission).

### Fit emphasis

- **Contribution type matters strongly**: doctrinal reinterpretation,
  normative argument, comparative evidence, and empirical legal evidence are
  genuinely different contribution types that map to different venues (a
  doctrinal journal is a poor fit for a purely empirical/quantitative
  legal-studies contribution, and vice versa).
- **Jurisdictional and comparative scope** is a first-order fit dimension —
  check whether the journal is jurisdiction-specific, comparative, or
  international in orientation.
- **Argument tradition and citation convention** (e.g. Bluebook vs. OSCOLA
  vs. other systems) is largely a formatting-mismatch issue, not a
  structural one (see
  [adaptation-policy.md](references/adaptation-policy.md)).

### Genre notes

Distinguish Article (full-length), Essay/Response, Case Note/Comment, Book
Review, and (for empirical-legal-studies venues) Original Empirical Research
as separate tracks with very different length and evidentiary norms.

<a id="humanities"></a>

## Humanities

Covers: philosophy, history, literature, linguistics, religious studies,
classics, cultural studies, art history, intellectual history, political
thought.

### Fit emphasis (from spec: emphasize intellectual tradition, archive/text
type, historiography, period, regional specialization, argument genre —
de-emphasize quantitative method matching)

- **Intellectual/argumentative tradition is the primary fit signal**, more
  than topic keywords — e.g. within philosophy, analytic vs. continental
  argument style and tradition often matters more to fit than the subject
  matter itself; within history, historiographical school and methodology
  (social history, intellectual history, cultural history, etc.) is a major
  discriminator.
- **Archive/text type and period specialization** are first-order fit
  dimensions in history, literature, and classics — a journal specializing
  in a specific period, region, or textual corpus is a hard-adjacent
  constraint even when the broader topic overlaps.
- **Argument genre matters**: philosophical article, historical
  reinterpretation, conceptual distinction, and normative argument are
  different contribution types with different expected structures — do not
  apply quantitative-method fit logic (RCT/cohort/etc.) to this family; it is
  largely irrelevant here (see
  [fit-model.md](references/fit-model.md) §Method and data fit).
- **Regional and linguistic specialization** of a journal is often a genuine
  scope boundary, not a soft preference — check explicitly rather than
  assuming a general-sounding journal covers all regions/periods.
- **Book reviews and review essays** are a legitimate, distinct genre with
  their own (often invitation-based) submission norms in this family —
  verify whether unsolicited submissions are even accepted for this genre at
  a given venue.

### Genre notes

Distinguish Article, Review Essay, Book Review, Response/Reply, and (in
philosophy specifically) Discussion Note as separate tracks.

Arts and practice-based research has its own file:
[arts-design.md](#arts-design).

<a id="education"></a>

## Education

Covers: education policy, higher education, curriculum, pedagogy, teacher
education, educational psychology, educational technology.

### Fit emphasis

- **Practice-relevance vs. theory-building orientation** is a major venue
  discriminator — practitioner-facing pedagogy journals and
  theory/measurement-focused educational-psychology journals rarely overlap
  even on the same topic (e.g. "student motivation").
- **Level and context specificity** (K-12 vs. higher education; specific
  subject-area teaching vs. general pedagogy) functions close to a hard
  filter — a higher-education-focused journal is typically a poor fit for a
  K-12 classroom study regardless of topical or theoretical overlap.
- **Method norms span the full range** seen in social sciences (quantitative
  measurement/psychometrics, qualitative classroom research, mixed methods,
  design-based research) — verify against the specific journal's recent
  corpus rather than assuming a discipline-wide default.
- **Educational technology** sits at an interdisciplinary boundary with
  HCI/CS and with mainstream education venues — route by primary
  contribution (a novel learning-technology system vs. an empirical
  pedagogy finding using technology as context); see
  [interdisciplinary.md](#interdisciplinary).
- **Policy relevance** is a distinct audience dimension from
  classroom/pedagogical relevance — an education-policy contribution needs a
  policy-audience venue, not just a general education journal.

### Genre notes

Distinguish Original Research, Practitioner/Practice Paper,
Systematic/Literature Review, Instrument/Measurement Development paper, and
Program Evaluation as distinct tracks with different evidentiary
expectations.

<a id="arts-design"></a>

## Arts and Design

Covers: music, performance studies, fine arts, design research, architecture,
film studies, theatre, creative practice research.

### Fit emphasis

Apply the humanities emphasis ([humanities.md](#humanities): tradition,
genre, and argument type over quantitative method matching) with these
additions:

- **Practice-based and practice-led research** is a legitimate, distinct
  contribution type in this cluster (the creative/design work itself as part
  of the contribution, alongside written reflection) — check whether the
  target venue's article types actually accommodate practice-based
  submissions, since many otherwise-relevant journals do not.
- **Medium/format fit** matters concretely — a journal built around written
  scholarship may not have a submission track for performance documentation,
  design artifacts, or audiovisual components even when topically aligned.
- **Design research** in particular often bridges toward
  engineering/HCI-adjacent venues as well as arts venues — route by primary
  contribution (a design methodology/theory contribution vs. an HCI systems
  contribution), consistent with
  [fit-model.md](references/fit-model.md) §Interdisciplinary
  manuscripts.

<a id="interdisciplinary"></a>

## Interdisciplinary

Covers: STS, sustainability, urban studies, AI governance, digital
humanities, bioethics, environmental humanities, health humanities,
computational social science, development studies — and any manuscript that
genuinely spans two or more of the discipline families in this Skill.

### The core problem

Interdisciplinary manuscripts often fail at submission not because they lack
a fit, but because they are *somewhat relevant to several fields and central
to none*. The task is to identify which venue logic the manuscript's
**primary contribution** actually serves — not to list every field the
topic touches.

### Method

1. Identify **home discipline** (where the manuscript's methodological and
   theoretical training most clearly sits) and **secondary discipline**
   (what it draws on or speaks to).
2. Identify the **primary contribution type** (see
   [manuscript-profile.md](references/manuscript-profile.md)
   §Contribution classification) — this, not the topic keywords, determines
   which conversation the manuscript actually belongs to.
3. Build an interdisciplinary fit matrix: for a given topic area, list the
   plausible distinct venue logics and select based on which one the primary
   contribution actually serves.

### Example matrix: AI + medicine

Could target: medical informatics, a clinical specialty journal, an AI/ML
methods venue, or a digital-health journal. Selection depends on whether the
primary contribution is a clinical finding (→ clinical specialty), a novel
algorithm/method (→ AI/ML methods venue), a system/implementation for
clinical use (→ medical informatics/digital health), or a governance/ethics
argument (→ bioethics or AI-governance venue) — not on the fact that the
manuscript mentions both "AI" and "medicine."

### Other recurring interdisciplinary boundaries

- **STS / sustainability / urban studies** often bridge social science and
  policy audiences with natural-science or engineering subject matter — check
  whether the target venue's actual readership can evaluate the technical
  content, not just whether the topic fits its scope statement.
- **AI governance** frequently spans normative/philosophical argument,
  empirical policy analysis, and technical AI-methods contributions (see
  [fit-model.md](references/fit-model.md) §Research-design fit for the
  canonical example of this mismatch trap).
- **Digital humanities / computational social science** bridge humanities or
  social-science subject matter with computational method — verify whether
  the target venue's audience and review process can evaluate both the
  humanistic/social argument and the computational method, or whether it
  privileges one over the other.
- **Bioethics / health humanities / environmental humanities** typically
  route by argument tradition (closer to [humanities.md](#humanities)) even
  when the subject matter is scientific or clinical.
- **Development studies** spans economics, sociology, policy, and area
  studies — check whether the target venue is empirical-economics-oriented,
  policy-oriented, or area-studies-oriented, since these have different
  method and audience expectations even within one journal's stated scope.

### General rule

Do not resolve interdisciplinary ambiguity by keyword coverage. Resolve it by
asking which readership is positioned to evaluate and use the manuscript's
primary contribution, and route there — while noting secondary-fit venues
honestly as alternatives with different tradeoffs (see
[submission-strategy.md](references/submission-strategy.md)
§Recommendation diversity and tradeoffs).
