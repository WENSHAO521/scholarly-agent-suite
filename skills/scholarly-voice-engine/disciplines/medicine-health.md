# Medicine and Health Sciences

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

## Prose guidance

Keep method (population, design, measurement, follow-up) visible and close to
the results it produced. State the evidence level explicitly when making a
clinical-implication claim. Do not let a p-value or effect size stand in for a
clinical-significance judgment — name both separately.

## Uncertainty language

```text
is associated with / was observed in this population / does not establish
efficacy / consistent with, but not proof of, a causal effect / diagnostic
performance in this sample does not by itself establish clinical utility
```
