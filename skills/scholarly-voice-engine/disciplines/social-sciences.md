# Social Sciences

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
  argument (see chapter roles in `references/book-writing.md`) rather than
  repeating the same literature review or restating the contribution in every
  chapter.
article_writing_norms: >
  Name the mechanism explicitly, state its scope conditions, and match claim
  strength (descriptive/associational/causal/mechanistic) to the actual research
  design. Prefer a substantive gap type (mechanism, measurement, boundary
  condition, institutional, theoretical contradiction) over generic gap language.
```

## Prose guidance

State scope conditions plainly ("under conditions of low state capacity...")
rather than leaving generalization implicit. Keep evidence close to the specific
claim it supports rather than batching citations. Treat qualitative and
quantitative evidence with genre-appropriate standards — do not narrate
qualitative material as if it carried statistical generalizability, or vice
versa.

## Economics

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
  welfare/policy implication (see argument-architectures.md §Economics)
typical_evidence:
  - observational/administrative data with an identification strategy (DiD,
    RDD, IV, natural experiment — see research-design-matrix.md)
  - structural or reduced-form models
  - lab/field experiments (behavioral and experimental economics)
citation_behavior: dense_at_identification_and_literature_positioning
methods_visibility: very_high  # the identification strategy must be fully inspectable
acceptable_first_person: yes
common_failure_modes:
  - causal language exceeding what the identification strategy actually
    establishes (see research-design-matrix.md rows for did/rdd/iv/
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
