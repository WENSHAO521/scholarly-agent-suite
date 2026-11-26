# Manuscript Profile

The manuscript-first rule: never recommend journals before this profile exists,
even in abbreviated form. Build it from what the user provides (abstract,
draft, description) plus direct questions — never from assumption.

## Schema

```yaml
discipline:              # top-level field, e.g. "sociology"
subdiscipline:            # e.g. "urban sociology"
topic:
research_question:
central_contribution:
contribution_type:        # see Contribution classification
secondary_contribution:
theoretical_framework:
research_design:
methods:
data:
unit_of_analysis:
geographic_scope:
temporal_scope:
article_type:             # see Manuscript genre
audience:                 # see Audience fit
interdisciplinarity:      # none | secondary-field | genuinely-cross-cutting
policy_relevance:         # none | low | medium | high
clinical_relevance:       # none | low | medium | high
technical_depth:
word_count:
reference_count:
current_stage:            # draft | near-final | under-revision | preprint | already-submitted-elsewhere
```

Any field the user has not supplied and cannot be inferred with reasonable
confidence stays `unknown`. Do not fill gaps with plausible-sounding guesses —
an `unknown` field is more useful than a wrong one, because it tells the fit
logic to weight that dimension as unverified rather than confidently mismatched
or matched.

## Contribution classification

Determine what the manuscript actually contributes, not what topic it discusses.

Types: theory, mechanism, empirical finding, causal evidence, measurement,
method, dataset, algorithm, benchmark, clinical evidence, historical
reinterpretation, conceptual distinction, comparative evidence, doctrinal
reinterpretation, normative argument, policy analysis, systematic synthesis.

- Multiple contributions may coexist; identify **primary** and **secondary**.
- Do not inflate novelty — "extends X to a new setting" is comparative
  evidence, not a new theory, unless the manuscript genuinely revises the
  mechanism.
- A manuscript that only cites theory without developing, extending, or
  testing it is not making a theoretical contribution (see
  [fit-model.md](fit-model.md) §Theory fit).

## Manuscript genre (article type)

Classify from this list, matching the closest fit:

original research, empirical article, experimental article, theory article,
conceptual paper, methods paper, systematic review, meta-analysis, narrative
review, scoping review, case study, comparative study, historical study,
ethnography, legal doctrinal paper, philosophical article, mathematical paper,
engineering/system paper, clinical study, research note, short communication,
perspective, commentary, editorial, book review.

Journal matching must respect what article types the target journal actually
accepts — this is one of the primary hard filters (§ Hard filters,
[fit-model.md](fit-model.md)). Do not assume a "review" written by the author
is what the journal categorizes as a Review — check the journal's own
taxonomy (narrative vs. systematic vs. scoping are frequently non-interchangeable).

## Research-design fit (topic × method × genre)

Topical relevance is necessary but not sufficient. Explicitly compare all
three axes before treating a journal as a fit:

- **Topic fit** — does the subject matter sit inside the journal's stated
  scope and recent coverage?
- **Method fit** — does the journal's recent corpus actually publish this
  research design (e.g. RCTs, doctrinal analysis, ethnography, formal proof)?
- **Genre fit** — does the journal accept this article type at all?

Example failure mode: a journal on "AI governance" that mainly publishes
empirical policy studies is a topic match but a method/genre mismatch for a
normative-philosophy manuscript. Flag this explicitly rather than defaulting
to the topical read.

## Audience fit

Identify who should care about the manuscript's contribution, independent of
topic: disciplinary specialists, interdisciplinary scholars, methodologists,
clinicians, policy researchers, practitioners, legal scholars, technical
engineers, general scientists, humanities specialists.

A journal can be topically relevant but audience-inappropriate — e.g. a
methods-focused statistics contribution submitted to a substantive
disciplinary journal whose readers want application, not derivation.

## Manuscript fingerprint (compact form)

For candidate matching, compress the profile into:

```json
{
  "discipline": "",
  "topic_terms": [],
  "contribution": [],
  "methods": [],
  "genre": "",
  "audience": [],
  "geography": "",
  "theory": [],
  "constraints": []
}
```

Use this fingerprint for candidate discovery ([candidate-generation.md](candidate-generation.md))
and for the "no keyword-only matching" check — topic_terms alone must never be
the sole basis for a recommendation.
