# Natural Sciences

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

## Prose guidance

Scientific prose should be clear rather than artificially ornate. Prefer plain,
cumulative sentences that stack evidence before inference (see the Darwin entry
in `historical-voice-profiles.md`). Keep causal language proportionate: reserve
causal verbs ("causes," "drives," "produces") for designs that support them;
otherwise use associational language ("is associated with," "correlates with,"
"predicts").

## Uncertainty language

```text
is consistent with / supports the possibility that / suggests a role for /
does not exclude / cannot rule out / within the limits of this design
```

## Common terminology to disambiguate in interdisciplinary work

`resilience`, `robustness`, `stability` — see
`references/interdisciplinary-writing.md`.
