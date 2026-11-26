"""tre -- Translation Engine runtime package.

Deterministic support for the scholarly translation pass described in
MODULE.md: language and script facts for any language, including the
Traditional / Simplified Chinese check (tre.languages); term extraction and
glossary enforcement (tre.glossary); the check that a translation kept every
citation, number, DOI, URL, formula, and paragraph of the source and left
nothing untranslated (tre.invariants); and the TRANSLATION_REPORT_V1
builder, validator, and bilingual side-by-side view (tre.report).

The translating itself is done by the model following MODULE.md and its
references. Python 3.10+ standard library only.
"""

MODES = ["faithful", "academic", "bilingual"]
STATUSES = ["PASS", "REVIEW", "FAIL"]
# Written varieties a target can name. "zh-Hant" / "zh-Hans" are checked
# character by character (tre.languages.variety_mismatches); the rest are
# recorded and followed by the translator.
VARIETIES = ["zh-Hant", "zh-Hans", "zh-TW", "zh-HK", "zh-CN", "pt-BR", "pt-PT", "en-US", "en-GB",
             "es-ES", "es-419", "fr-FR", "fr-CA"]
GLOSSARY_STATUSES = ["kept", "missing", "count-differs", "not-in-source"]

# One line every translation report carries.
TRANSLATION_NOTICE = (
    "Machine-assisted translation prepared by Scholarly Agent. Have a reader fluent in both "
    "languages and the field check terminology and claims before submission, and follow the "
    "venue's policy on disclosing AI-assisted translation."
)
