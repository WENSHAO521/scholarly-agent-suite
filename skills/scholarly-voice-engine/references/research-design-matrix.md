# Research Design Matrix

Research design constrains claim strength and argument shape independently of
discipline — a randomized trial and a cross-sectional survey in the same field
license different prose even when the topic is identical. Resolve design
before drafting; see `claim-calibration.md` for how design maps to claim type
and `argument-architectures.md` for section-level shape.

## Design → prose calibration

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
    `disciplines/engineering-computing.md`)

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

## Resolving design from a request

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

## Interaction with claim calibration

This file sets the *ceiling*; `claim-calibration.md` sets the *language*.
Never let confident prose narrow the gap between what a design supports and
what a sentence claims — no rhetorical device (hedge removal, passive-to-
active conversion, added emphasis) changes what the data can bear.
