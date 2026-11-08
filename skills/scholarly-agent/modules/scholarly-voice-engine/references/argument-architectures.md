# Argument Architectures

Section-level shapes by discipline family and by rhetorical pattern. Never impose
IMRaD (Introduction, Methods, Results, Discussion) universally — it is one
architecture among several, native to experimental/empirical sciences, and often
wrong for mathematics, law, or humanities.

## Family architectures

### Empirical social science
```text
problem → literature → theoretical mechanism → hypotheses/questions →
data → methods → results → interpretation → limitations → contribution
```

### Experimental science
```text
problem → known mechanism → specific uncertainty → experimental strategy →
results → mechanistic interpretation → boundary conditions
```

### Mathematics
```text
problem → notation → definitions → main theorem → supporting results →
proof → discussion / corollaries
```

### Humanities (interpretive)
```text
interpretive problem → existing reading → text/source evidence →
conceptual intervention → close analysis → implication
```

### Law (doctrinal)
```text
legal problem → doctrine/authority → conflict or ambiguity → interpretation →
comparative or normative analysis → consequence
```

### Sociology / institutional social science
```text
concept → mechanism → social structure → empirical pattern → scope condition
```

### Engineering / systems
```text
motivation → design goals/constraints → design choice → implementation →
evaluation/benchmark → ablation → interpretation → limitations
```

### Clinical / health sciences
```text
clinical problem → prior evidence → design → population/sample →
outcome measures → results → clinical interpretation → limitations →
implications for practice (kept separate from causal claims)
```

### Historical study
```text
question → sources → chronological reconstruction → interpretation →
historiographical positioning → implication
```

### Philosophical essay
```text
thesis → key distinction → argument for thesis → strongest objection →
response/qualification → refined thesis
```

### Economics
```text
economic question → model/identification strategy → institutional
assumptions → estimand → data → results → robustness → mechanism →
welfare/policy implication
```
See the Economics subsection of `disciplines/social-sciences.md` and
`research-design-matrix.md` for the identification-strategy rows (DiD, RDD,
IV, natural experiment) this architecture draws on.

## Additional reusable patterns

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

## Paragraph- and section-level rhythm patterns

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
mechanically throughout a document (see `human-scholarly-prose.md` §Controlled
Asymmetry).

## Claim calibration by architecture

Match the architecture's evidentiary apparatus to the claim type it is entitled to
produce — see `claim-calibration.md` for the full taxonomy and invariant, and
`research-design-matrix.md` for how the specific research design (not just the
discipline family) sets the claim ceiling. An experimental-science architecture
with only correlational data supports `associational`, not `causal`, claims —
no amount of confident prose narrows that gap (see `disciplines/*.md` for
field-specific guardrails, e.g. clinical association/causal/utility
separation).

## Contribution types

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
