"""ppe -- Prose Polish Engine runtime package.

Deterministic support for the polishing pass described in MODULE.md:
a catalog of templated phrasing patterns for nine languages
(ppe.patterns), language facts for any language (ppe.languages), a
diagnosis that locates templated phrasing in a text and measures how dense
it is (ppe.diagnose), a check that a polished text kept every
citation, number, quotation, and formula of the original (ppe.invariants),
and the POLISH_REPORT_V1 builder and validator (ppe.report).

Since v2.5.0 the catalogs and the diagnosis also find defensive writing:
hedges that answer to no evidence, paragraphs where every sentence is
hedged, pre-emptive caveats, disclaimers, apologetic framing, and
over-justification (references/defensive-writing.md).

The rewriting itself is done by the model following MODULE.md and its
references. Nothing here estimates whether a text was written by a person
or a machine, and nothing here scores text against any detector.
Python 3.10+ standard library only.
"""

LEVELS = ["light", "standard", "deep"]
# Phrase catalogs exist for these; every other language (any ISO 639-1
# code) is polished with structural and protected-item checks only.
CATALOG_LANGUAGES = ["en", "zh", "ja", "ko", "es", "fr", "de", "pt", "ru"]
STATUSES = ["PASS", "REVIEW", "FAIL"]
SEVERITIES = ["remove", "revise", "watch"]
CATEGORIES = [
    "chat-residue",
    "stock-connective",
    "empty-emphasis",
    "inflated-vocabulary",
    "formulaic-frame",
    "stock-summary",
    "hedge-stack",
    "contrast-template",
    "nominalization",
    "repeated-opener",
    "uniform-rhythm",
    "triplet-habit",
    "dash-habit",
    # defensive writing (references/defensive-writing.md)
    "defensive-hedge",
    "hedge-blanket",
    "preemptive-caveat",
    "disclaimer",
    "apologetic-framing",
    "over-justification",
]

# The categories that make up defensive writing. hedge-stack belongs here
# too: two hedges on one claim are a defence, not more caution.
DEFENSIVE_CATEGORIES = [
    "hedge-stack",
    "defensive-hedge",
    "hedge-blanket",
    "preemptive-caveat",
    "disclaimer",
    "apologetic-framing",
    "over-justification",
]

# What the polisher decided about each qualifier it examined in the
# defensive pass (POLISH_REPORT_V1 ``calibration``).
CALIBRATION_DECISIONS = ["kept", "scoped", "removed", "consolidated"]

# One line the polish report carries, so nobody reads it as a verdict on
# authorship or a promise about any detector.
POLISH_NOTICE = (
    "Pattern counts describe templated phrasing in this text; they are not an "
    "estimate of who or what wrote it, and no detector result is implied."
)
