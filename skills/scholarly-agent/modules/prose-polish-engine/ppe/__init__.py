"""ppe -- Prose Polish Engine runtime package.

Deterministic support for the polishing pass described in MODULE.md:
a catalog of templated phrasing patterns for nine languages
(ppe.patterns), language facts for any language (ppe.languages), a
diagnosis that locates templated phrasing in a text and measures how dense
it is (ppe.diagnose), a check that a polished text kept every
citation, number, quotation, and formula of the original (ppe.invariants),
and the POLISH_REPORT_V1 builder and validator (ppe.report).

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
]

# One line the polish report carries, so nobody reads it as a verdict on
# authorship or a promise about any detector.
POLISH_NOTICE = (
    "Pattern counts describe templated phrasing in this text; they are not an "
    "estimate of who or what wrote it, and no detector result is implied."
)
