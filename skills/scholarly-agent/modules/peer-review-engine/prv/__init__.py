"""prv -- Peer Review Engine runtime package.

Deterministic bookkeeping for simulated peer review: reviewer panel
selection and subagent briefings (prv.panel), REVIEW_REPORT_V1 validation
(prv.reports), and the editor's desk screen, decision, response matrix, and
second-round check (prv.decision). The judgment itself -- what counts as a
fatal flaw, whether a rebuttal holds -- belongs to the reviewer and editor
roles described in MODULE.md; this package only applies the rules to their
output. Python 3.10+ standard library only.
"""

DECISIONS = ["desk-reject", "reject", "reject-resubmit", "major-revision", "minor-revision", "accept"]
RECOMMENDATIONS = ["reject", "reject-resubmit", "major-revision", "minor-revision", "accept"]
SEVERITIES = ["fatal", "major", "minor"]
LENSES = ["methods", "statistics", "theory", "literature", "field", "ethics-integrity", "devils-advocate", "generalist"]
CATEGORIES = ["validity", "methods", "theory", "contribution", "literature", "presentation", "ethics", "reproducibility", "scope"]

SIMULATION_DISCLAIMER = (
    "Simulated editorial decision -- not a prediction of any journal's actual decision."
)
