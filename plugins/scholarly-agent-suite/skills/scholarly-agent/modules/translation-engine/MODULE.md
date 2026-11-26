<!-- Module of the scholarly-agent Skill (native module, added in v2.4.0).
     Loaded on demand by ../../SKILL.md; paths below are relative to this module's directory. -->

> **Module `translation-engine`** -- part of the single `scholarly-agent` Skill. Load this file only when the
> dispatcher in `SKILL.md` selects this module. Sibling modules are at `modules/<name>/`.
> Paths such as `references/...` are relative to `modules/translation-engine/`.
>
> Scope: Scholarly translation (翻譯) of academic text between any two languages -- abstracts, articles, chapters, theses, reviewer responses -- and conversion between Traditional and Simplified Chinese with regional terminology: the claims, claim strength, citations, numbers, DOIs, formulas, and defined terms come through unchanged, terminology stays consistent through a glossary, and the result reads as written in the target language's academic register rather than as translationese.

# Translation Engine

A scholarly translation can fail in two opposite ways. It can be accurate
and unreadable, keeping the source language's word order, connectives, and
sentence length until every line sounds translated. Or it can read
beautifully and quietly change the science: a hedge dropped, "is associated
with" turned into "causes", a number rounded, a citation lost, a defined
term rendered three different ways. This module does neither. It writes the
target text a scholar in that field would write, and then proves, item by
item, that nothing the source committed to was lost.

## Languages

Every language pair is in scope, in both directions. The checks that matter
most (citations, numbers, DOIs, URLs, formulas, inline code, paragraph
alignment, glossary terms) do not depend on the language at all. Script
detection covers Latin, Han, kana, Hangul, Cyrillic, Arabic, Hebrew, Greek,
Thai, and Devanagari, and catches text left in the source script. Hedge and
negation lists for English, Chinese, Japanese, Korean, Spanish, French,
German, Portuguese, and Russian let the check flag a paragraph whose hedge or
negation disappeared.

Chinese needs its variety named. Ask (or infer from the user's own writing)
whether the target is Traditional (`zh-Hant`; Taiwan `zh-TW`, Hong Kong
`zh-HK`) or Simplified (`zh-Hans` / `zh-CN`), and use that region's academic
terms, not just its characters: 資訊 / 信息, 軟體 / 软件, 品質 / 质量 as
appropriate (`references/terminology.md#chinese-varieties`). Converting
between Traditional and Simplified is handled here too, with the same term
check, because character-by-character conversion gets the vocabulary wrong.
The same applies to pt-BR / pt-PT, en-US / en-GB, and other regional
standards when the venue cares.

```
Prepare    source and target language and variety, mode, audience, venue; glossary (python -m tre terms)
Translate  paragraph by paragraph, in the target language's academic register
Verify     tre.report: citations, numbers, DOIs, formulas, glossary, script, paragraphs, hedges
Repair     fix every FAIL; explain or fix every REVIEW; one repair pass, then report what is open
Report     translation + translator's notes + TRANSLATION_REPORT_V1
```

## Ecosystem position

```
Translation Engine (this)  same text, another language: meaning, claims, and citations unchanged
Scholarly Voice Engine     drafts and revises in any language: argument, structure, claims, voice
Prose Polish Engine        the finished text's wording in one language: templated phrasing out
Journal Fit Engine         the target journal's language and style requirements, if one is named
Peer Review Engine         critiques and decides; never translates or rewrites
```

Stay in lane. Translation re-expresses; it does not improve the argument,
correct the data, or update the literature. Problems found in the source (a
number that contradicts a table, a citation that does not match the
reference list, an ambiguous sentence) go into `escalations` and the
translator's notes, never silently "fixed" in the translation. Rewriting
for a new audience or a different genre is the voice module's job. A
polishing pass after translation is optional and only on request: the
academic mode already writes natural target-language prose.

## When to use

- 「翻譯這篇摘要成英文」「把論文翻成中文」「中譯英」「英譯中」「幫我翻成日文」「簡轉繁」「繁體轉簡體」
- "Translate my abstract into English for submission." / "Translate this chapter from German."
- 「この論文を英語に翻訳して」「이 논문 초록을 영어로 번역해 줘」« Traduis cet article en anglais »
- Translating reviewer comments or a response letter; a bilingual (parallel)
  version for a co-author or supervisor to check.
- As a stage of a writing workflow when the user drafts in one language and
  submits in another (the dispatcher adds it after the draft is final).

Not for: translating a single title or sentence (answer directly); writing
a new paper directly in another language from notes (voice); polishing text
that stays in its language (polish); translating someone else's copyrighted
work for publication without permission (see Integrity).

## Modes

Ask nothing if the request makes the mode clear; otherwise use `academic`
for a manuscript meant for submission and `faithful` for everything else,
and say which.

| Mode | Use for | Sentence freedom | Paragraphs |
|---|---|---|---|
| `faithful` (default) | contracts with the source: theses for an examiner, legal and archival text, anything someone will compare line by line | keep each sentence's content and order; restructure only where the target grammar demands | one target paragraph per source paragraph |
| `academic` | a manuscript for a journal in the target language | split, merge, and reorder within a paragraph to follow the target's academic conventions (topic sentences, hedging register, connectives, nominal vs verbal style) | one per source paragraph |
| `bilingual` | checking by a co-author, supervisor, or editor | as `faithful` | source and translation paragraph by paragraph (`tre.report.bilingual`) |

No mode changes data, findings, citations, quotations, defined terms, or how
strongly a claim is made.

## Workflow

1. **Prepare.** Fix the source and target language and variety, the mode,
   the field, and the venue if any (a named journal's language rules come
   from journal-fit-engine's `JOURNAL_STYLE_CONTEXT_V1` if one is already in
   hand; never build one just to translate). Run `python -m tre terms
   SOURCE` (or `tre.glossary.term_candidates`) and settle the glossary
   before translating anything long: the user's own term choices first,
   then the field's established translations, then a consistent choice of
   your own, recorded. See `references/terminology.md`.
2. **Translate.** Paragraph by paragraph, following
   `references/translation-passes.md`: meaning first, then the target's
   academic register, then terminology and form. Citations, numbers in
   digits, DOIs, URLs, formulas, code, and variable names pass through
   unchanged; author names stay in their original script (a transliteration
   may be added beside them where the venue expects it). Direct quotations
   keep the original wording or are translated with a "translation mine" /
   「筆者譯」 note, never silently reworded. Reference-list entries are not
   translated (an English gloss of a title in square brackets is added only
   if the target style requires it).
3. **Verify.** Run `tre.report.build_translation_report(source, target,
   target_language, source_language, mode, variety, glossary, notes)` (or
   `python -m tre check SOURCE TARGET --to LANG [--from LANG] [--variety
   zh-Hant] [--glossary FILE]`). `FAIL` means a citation, number, DOI, URL,
   formula, glossary term, or the target language itself is wrong: fix it,
   do not explain it away. `REVIEW` means paragraphs, quotations, hedges,
   negations, variety characters, or untranslated text need a look: fix it
   or record why it is right (`notes`). One repair pass at most; anything
   still open goes into `limitations`.
4. **Hand back.** The translation first; then the translator's notes (terms
   chosen, quotations, names, numbers, ambiguities resolved, source problems
   escalated); then the report summary. For long texts, offer the
   bilingual view (`python -m tre bilingual SOURCE TARGET`). Format:
   `references/translation-report.md`.

## Integrity (non-negotiable)

`shared/integrity-policy.md` applies in full. In addition:

- **Meaning is fixed.** No change to data, results, citations, quotations,
  or claim strength. "May", 「可能」, 「と考えられる」 survive as hedges;
  "is associated with" never becomes "causes". The claim-calibration rules
  in `modules/scholarly-voice-engine/references/argument-and-claims.md#claim-calibration`
  apply across languages.
- **No silent correction.** A translation is not a revision. Errors in the
  source are reported, not fixed in the target text.
- **Unverified stays unverified.** `[VERIFY]` markers and unresolved
  citations are carried over as they are.
- **Disclosure stays with the author.** Many journals and universities
  require authors to disclose AI-assisted translation or language editing.
  The report's notice says so; when the user is translating for submission,
  remind them once to follow the venue's policy. Never advise hiding it.
- **Other people's work.** Translating a published text for the user's own
  reading or research is fine. Translating someone else's copyrighted work
  for publication or distribution needs the rights holder's permission;
  say so, and translate only short passages as quotation for analysis.
- **Confidential material.** A manuscript under review, a grant under
  assessment, or anything the user received in confidence is not translated
  with an AI tool unless the user confirms the owner's policy allows it.

## Runtime code

`tre/` is a small standard-library package (Python 3.10+), importable by
putting this module's directory on `sys.path`:

- `tre.languages` -- `detect_language`, script facts for any language,
  hedge and negation lists, `variety_mismatches` (Traditional vs Simplified
  characters), paragraph splitting, length units.
- `tre.glossary` -- `term_candidates(text, lang)`, `load_glossary(path)`
  (JSON or two-column TSV), `check_glossary(source, target, glossary)`.
- `tre.invariants` -- `extract(text)`, `check_translation(source, target,
  source_lang, target_lang, variety, keep_terms)`.
- `tre.report` -- `build_translation_report(...)` producing
  `TRANSLATION_REPORT_V1`, `validate_translation_report(report)`, and
  `bilingual(source, target)`.
- `python -m tre terms | check | bilingual` -- the same, from a shell.

The code checks and counts; the translating and every judgment about
wording belong to the translator following this file.

## References

- `references/translation-passes.md` -- the passes, per-mode rules, citations, names, numbers, quotations, formulas, verification
- `references/terminology.md` -- building and enforcing a glossary, field terms, Chinese varieties (Taiwan, Hong Kong, Mainland), other regional standards
- `references/translation-report.md` -- `TRANSLATION_REPORT_V1` fields and how to present a translation to the author
