# Engineering and Computing

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

## Prose guidance

State the design goal and constraint before the design choice, so the choice
reads as a decision rather than an arbitrary description. Report benchmark
numbers with the conditions that produced them adjacent to the numbers, not in a
separate appendix the prose never references. Interpret ablations mechanistically
("removing X causes Y because...") rather than only numerically ("X: 0.81, no X:
0.76").
