# Review report (`REVIEW_REPORT_V1`)

Schema: `protocols/review-report.schema.json` (dispatcher level). Runtime
check: `prv.reports.validate_report`.

## Fields

| Field | Meaning |
|---|---|
| `reviewer_id` | `R1`, `R2`, ... Stable across rounds |
| `lens` | One lens id from [reviewer-lenses.md](reviewer-lenses.md) |
| `summary` | The paper in the reviewer's own words, 3–6 sentences |
| `strengths` | Specific, real strengths |
| `concerns` | List of concerns (below) |
| `questions_for_authors` | Clarifications that are not yet concerns |
| `recommendation` | `accept`, `minor-revision`, `major-revision`, `reject-resubmit`, `reject` |
| `confidence` | `low`, `moderate`, `high`: in this assessment, given the reviewer's expertise |
| `confidential_to_editor` | Optional note the authors would not see (as in real review) |
| `independence` | `mode` (`isolated-subagent` or `sequential-single-model`) and `saw_other_reports` (must be `false`) |
| `limitations` | What the reviewer could not check (no data access, outside expertise, supplement missing) |

### A concern

| Field | Meaning |
|---|---|
| `id` | `R2-C3`: reviewer id plus a running number |
| `severity` | `fatal`, `major`, or `minor` (scale below) |
| `category` | `validity`, `methods`, `theory`, `contribution`, `literature`, `presentation`, `ethics`, `reproducibility`, `scope` |
| `location` | Section, page, table, figure, or equation |
| `issue` | What is wrong, specifically |
| `evidence` | Why the reviewer believes it: a quote, a number, a logical step |
| `request` | What the authors should do |
| `fixable` | `true` if a revision could resolve it; `false` if resolving it means a different paper |

## Voice

The JSON is for the editor role. When the report is shown to the author,
render it as a real reviewer's report: "Reviewer 2" heading, a first-person
summary ("The authors argue..."), strengths, numbered major and minor
comments with locations, and questions. Direct and collegial; no mention of
AI or simulation; never signed with a person's name.

## Severity scale

- **fatal**: if true, the central claim does not stand (invalid
  identification, a proof error the result depends on, data that cannot
  support the conclusion, a contribution that already exists).
- **major**: the claim may stand, but the paper cannot be published until
  this is resolved (missing robustness check, unaddressed alternative
  explanation, key literature misread, overstated contribution).
- **minor**: improves the paper; publication does not depend on it
  (clarity, a missing citation, a figure label, a typo pattern).

Severity is about consequences for the claim, not how much work the fix is.
A two-week reanalysis can be `major`; a one-line fix to a wrong headline
number can be `fatal` if the conclusion depended on it.

## Example (abridged)

```json
{
  "protocol": "REVIEW_REPORT_V1",
  "reviewer_id": "R1",
  "lens": "methods",
  "summary": "The paper argues that municipal capacity conditions policy diffusion, using a panel of 412 cities (2005-2020) and a staggered difference-in-differences design.",
  "strengths": ["Original panel data assembled from council minutes", "Clear pre-registration of the main hypothesis"],
  "concerns": [
    {
      "id": "R1-C1", "severity": "major", "category": "methods",
      "location": "Section 4.2, Table 3",
      "issue": "Two-way fixed effects with staggered adoption can be biased when effects vary over time.",
      "evidence": "Adoption spans 2007-2018 and Figure 2 shows effects growing with exposure.",
      "request": "Re-estimate with a heterogeneity-robust estimator and report event-study estimates.",
      "fixable": true
    }
  ],
  "questions_for_authors": ["How were cities that merged during the panel handled?"],
  "recommendation": "major-revision",
  "confidence": "high",
  "independence": {"mode": "isolated-subagent", "saw_other_reports": false},
  "limitations": ["Replication data were not provided, so results could not be re-run."]
}
```
