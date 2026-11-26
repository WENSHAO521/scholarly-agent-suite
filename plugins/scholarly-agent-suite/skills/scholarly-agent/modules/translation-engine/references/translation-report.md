# Translation report (`TRANSLATION_REPORT_V1`)

Every translation is handed back with a report the author (and the
dispatcher's final quality gate) can read. Schema:
`protocols/translation-report.schema.json` (from the Skill root). Built by
`tre.report.build_translation_report`, checked by
`tre.report.validate_translation_report`.

## Fields

| Field | Meaning |
|---|---|
| `protocol` | `TRANSLATION_REPORT_V1` |
| `source_language`, `target_language` | language codes, optionally with script or region (`zh-Hant`, `pt-BR`) |
| `variety` | the written variety asked for, if any (`zh-Hant`, `zh-Hans`, `en-GB`, ...) |
| `mode` | `faithful`, `academic`, or `bilingual` |
| `paragraphs` | source and target paragraph counts, and `flagged`: paragraphs whose length moved far from the rest |
| `glossary` | one entry per glossary term: `expected` rendering, counts, `status` (`kept`, `missing`, `count-differs`, `not-in-source`) |
| `invariants` | `status`, `failures`, `warnings` from `tre.invariants.check_translation` |
| `untranslated` | stretches still in the source script outside parentheses and quotations |
| `status` | `PASS`, `REVIEW`, or `FAIL`: FAIL if any invariant failed or a glossary term is missing; REVIEW if anything needs a look |
| `notice` | `tre.TRANSLATION_NOTICE`, unchanged |
| `notes` | the translator's decisions: `{kind, note, source?}`, kind one of `quotation`, `term`, `name`, `number`, `ambiguity`, `culture`, `source-error` |
| `escalations` | problems in the source itself, reported rather than fixed |
| `limitations` | anything still open after the one repair pass |

A report that says `PASS` while its invariant check says `FAIL`, or that
drops a missing glossary term from the status, does not validate.

## Presenting a translation

1. **The translation**, complete, in the target language and variety. For
   `bilingual`, the paragraph-by-paragraph view instead
   (`tre.report.bilingual`).
2. **Translator's notes**, short and grouped: terms chosen (with the
   original), quotations and how they were handled, names and
   transliterations, numbers converted, ambiguities and how they were read.
3. **Escalations**, if any: what in the source looks wrong and where. The
   translation keeps what the source says.
4. **The check**, in one or two sentences: status, and what was reviewed
   and why it stands. Offer the full JSON report or glossary file if the
   author wants it.
5. **The notice**, once: a fluent reader in the field should check the
   translation before submission, and the venue's AI-disclosure policy
   applies.

Example summary (Traditional Chinese user, English target):

> 已譯為英文（academic 模式），共 6 段，段落與原文一一對應。術語依您提供的詞表：
> 數位治理能力 → digital governance capacity，DGC 保留。檢查結果 REVIEW：第 3 段原文的「可能」
> 已保留為 "may"；第 5 段的引文為筆者自譯，已加註 "translation mine"。原文表 1 的樣本數
> 為 21，但內文寫 22，譯文照原文保留，請確認。投稿前請由熟悉該領域的雙語讀者再看一次，
> 並依期刊規定揭露 AI 輔助翻譯。
