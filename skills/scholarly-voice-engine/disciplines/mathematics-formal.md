# Mathematics and Formal Sciences

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

## Prose guidance

Short, declarative sentences; notation carries the argument. Define every symbol
before use; do not redefine a symbol with a different meaning later in the same
document. State hypotheses explicitly rather than leaving them implicit in the
proof. Distinguish clearly:

```text
motivation | formal statement | proof | intuition/remark | corollary
```

Counterarguments in this family take the form of counterexamples and boundary
cases, not prose objections — handle them as such.
