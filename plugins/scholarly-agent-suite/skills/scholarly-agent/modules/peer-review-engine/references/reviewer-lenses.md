# Reviewer lenses

Each reviewer reads the whole manuscript but is accountable for one lens.
Distinct lenses are what make a panel more useful than one long critique:
they catch different problems and disagree in informative ways.

## Lenses

| Lens id | Reviewer role | Checks first |
|---|---|---|
| `methods` | Methods and evidence | Design fits the question; identification or inference is valid; sampling, measures, analysis, robustness; results support the claims; reproducibility (data, code, materials) |
| `statistics` | Statistical reviewer | Model specification, assumptions, multiple comparisons, effect sizes and uncertainty, power, missing data. Use instead of `methods` when the paper is primarily quantitative and high-stakes (clinical, policy evaluation) |
| `theory` | Theory and contribution | The question matters; the argument is coherent; concepts are defined and used consistently; the contribution is real, stated, and not overstated relative to prior work |
| `literature` | Field and literature | Positioning in the current conversation; missing or misread key work; whether the "gap" is real; fit to the journal's readership |
| `field` | Domain specialist | Substantive accuracy in the subfield, context (country, period, archive, clinical setting), whether practitioners or specialists would accept the framing |
| `ethics-integrity` | Ethics and integrity | Consent and approvals, data protection, conflicts of interest, citation integrity, image or data irregularities, reporting-guideline compliance (CONSORT, PRISMA, STROBE, etc.) |
| `devils-advocate` | Skeptical reviewer | The strongest case against the paper's central claim: alternative explanations, the most damaging counterexample, the reading under which the contribution disappears |
| `generalist` | Non-specialist reader | Clarity, structure, whether the abstract and introduction promise what the paper delivers. Useful for broad-audience journals and commentaries |

`ethics-integrity` concerns can be raised by any reviewer; give it its own
seat only for clinical, human-subjects, or data-heavy work, or when the user
asks.

## Default panels

`prv.panel.build_panel` uses these defaults; the editor may override with a
reason (for example, swap `field` for `statistics` on a meta-analysis).

| Article type (`MANUSCRIPT_PROFILE_V1`) | 2 reviewers | 3rd reviewer |
|---|---|---|
| `empirical` | `methods`, `theory` | `literature` |
| `theory` | `theory`, `literature` | `devils-advocate` |
| `review` | `literature`, `methods` (search and synthesis method) | `theory` |
| `case-study` | `methods`, `field` | `theory` |
| `commentary` | `field`, `generalist` | `devils-advocate` |
| `book-chapter` | `theory`, `field` | `generalist` |
| `other` | `theory`, `methods` | `literature` |

Discipline adjustments, from the shared taxonomy (`shared/disciplines.md`):

- `medicine-health`: replace `theory` with `statistics` for trials and
  observational studies, and add `ethics-integrity` as the third seat.
- `humanities`, `arts-design`, `law`: `methods` reads as "sources and
  method" (archive, corpus, doctrine, interpretive method), not statistics.
- `mathematics-formal`: `methods` reads as "correctness of proofs";
  `literature` checks priority and novelty.

## What every reviewer does regardless of lens

- Summarizes the paper in their own words first. A summary the authors
  would not recognize is itself a finding (the paper is unclear).
- Lists real strengths. A report with no strengths is not more rigorous; it
  is less useful.
- Grades each concern `fatal`, `major`, or `minor`
  ([review-report.md](review-report.md)) and says what would resolve it.
- States confidence and the limits of their expertise for this paper.
- Recommends a decision, knowing the editor decides.
