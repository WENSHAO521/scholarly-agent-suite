# Translation passes

How to translate a scholarly text so it reads as written in the target
language and still commits to exactly what the source commits to. Work
paragraph by paragraph; for a long text, settle the glossary first
([terminology.md](terminology.md)).

## 1. Meaning

Read the whole paragraph before writing anything. Identify, for each
sentence: the claim, its strength (asserted, hedged, speculative, reported
from someone else), its scope (all, most, some, this sample), its evidence
(citation, number, figure), and its role in the paragraph (claim, support,
concession, contrast, transition). These five things are what must survive.

- Ambiguity in the source: choose the reading the context supports, and
  record the choice as a `notes` entry of kind `ambiguity`. If the context
  does not decide it, keep the ambiguity in the target where the language
  allows, or ask the author.
- Errors in the source (a number that contradicts a table, a citation year
  that differs from the reference list): translate what is written, and
  record an `escalations` entry and a `source-error` note.

## 2. Register

Write the paragraph the way a scholar in this field writes in the target
language.

- **Sentence shape.** Chinese and Japanese academic prose tolerates long
  topic chains; English prefers one claim per sentence with the subject
  early. German nests; Spanish and French subordinate. In `academic` mode,
  re-cut sentences to the target's habits; in `faithful` mode, re-cut only
  where the target grammar requires it.
- **Connectives.** Do not carry over the source's connectives one for one.
  「此外」「另外」「同時」 at the start of every sentence becomes no connective
  at all in English most of the time; "Furthermore" and "Moreover" do not
  become 「此外」 every time either. Use a connective only where the logical
  relation would otherwise be unclear.
- **Hedging register.** Languages hedge differently: Japanese stacks
  softeners (と考えられる、可能性が示唆される), English hedges once with a
  modal or verb (may, suggests), Chinese uses 可能 / 似乎 / 或許. Translate
  the strength, not the word count: three stacked Japanese softeners can be
  one English "may"; a single English "may" must not vanish in Chinese.
- **Nominal vs verbal style.** Chinese and English academic prose often
  turn verbs into nouns (進行分析, "conduct an analysis of"). Prefer the
  verb in the target unless the field's convention is nominal.
- **Voice and person.** Follow the target field's convention for "we" /
  「本研究」/「筆者」/ 「本稿では」, passive vs active. A single-author paper in
  English uses "I" or the passive, not "we", unless the journal says
  otherwise.
- **Translationese checks.** Read the target paragraph without the source.
  If a sentence only makes sense once you know the source language, rewrite
  it.

## 3. Terminology and form

- **Glossary terms** appear exactly as the glossary says, every time.
- **Defined terms and abbreviations.** Translate the term once where it is
  defined, keep the abbreviation if the field uses it in the target language
  (e.g. GDP, RCT, ESG), otherwise define a target-language abbreviation and
  record it in the glossary. On first use in a Chinese or Japanese target,
  the English term may be glossed in parentheses: 數位治理能力（digital
  governance capacity）.
- **Citations.** Pass through unchanged: author names, years, page numbers,
  "et al." may become 等 / 等人 / ら / 외 where the target style expects it.
  Numbered citations ([3], [4-6]) stay exactly. Convert punctuation only
  (half-width vs full-width parentheses and commas) to the target's norm.
- **Author and person names.** Keep the original script. If the venue
  expects a transliteration, add it beside the original: 韋伯（Weber,
  1922）, not 韋伯（1922）. Chinese, Japanese, and Korean names going into
  English use the person's own published romanization, in the order they
  publish under; never guess a romanization when the reference list gives
  it.
- **Numbers.** Digits stay digits and keep their value: 12.5 % in French
  is 12,5 %, but never 13 %. Do not convert units, currencies, or dates
  unless asked; if you add a conversion, put it in brackets after the
  original. Large-number words (萬, 億, 만, 억, million, billion) need care:
  1.5 萬 = 15,000; the check marks these for review because the digits
  differ.
- **Formulas, variables, code, statistics notation** (β, p, t, F, CI, SD)
  stay exactly as written.
- **Quotations.** A direct quotation from a source either keeps its
  original wording (with a translation in brackets or a note) or is
  translated and marked "translation mine" / 「筆者譯」 / 「拙訳」. Never
  translate a quotation silently, and never retranslate a quotation that
  already has a published translation the author cites: use that one.
- **Titles in the reference list** stay in the original language. Some
  styles (APA) add an English translation of a non-English title in square
  brackets; add it only if the target style asks.
- **Headings, figure and table captions, footnotes** are translated with the
  body; table contents (numbers, variable names) stay as they are.

## Modes

| Mode | Change allowed |
|---|---|
| `faithful` | word order and sentence structure where the target grammar requires; nothing else moves |
| `academic` | sentence splitting, merging, and reordering within a paragraph; connectives and hedging register adapted to the target; paragraph order and content fixed |
| `bilingual` | as `faithful`, delivered paragraph by paragraph next to the source |

A request to "make it sound native" is `academic`. A request to "translate
and also improve the argument" is two tasks: translate (this module), then
revise (voice), in that order, and say so.

## 4. Verify

Run the check on the full text, not paragraph fragments:

```
python -m tre check source.txt target.txt --to en --from zh-Hant --glossary glossary.tsv
```

| Finding | Status | What to do |
|---|---|---|
| number, citation year, numbered citation, DOI, URL, formula, or code missing or added | FAIL | restore it exactly |
| cited author name missing | FAIL | put the original-script name back (a transliteration may stay beside it) |
| glossary term missing | FAIL | use the glossary rendering, or change the glossary with the author's agreement and re-run |
| target is not in the requested language | FAIL | translate it |
| number mismatch with 萬 / 億-style units present | REVIEW | confirm each converted value |
| quotation count differs | REVIEW | keep the original or add the "translation mine" note |
| paragraph count differs, or one paragraph much shorter or longer than the rest | REVIEW | check for an omission or addition; restore paragraph alignment unless merging was asked for |
| hedge or negation present in a source paragraph and absent in the target paragraph | REVIEW | restore the hedge or negation, or note why the target expresses it another way |
| characters of the other Chinese script | REVIEW | convert them; check the word, not only the character (see terminology.md) |
| text left in the source script | REVIEW | translate it, or gloss it in parentheses if it is a term kept on purpose |
| glossary term used fewer times than in the source | REVIEW | fine if a pronoun does the work; otherwise use the term |

One repair pass, then re-run the check. Anything still open goes into
`limitations` with a sentence of explanation. The check cannot see a
meaning error in a sentence that keeps all its numbers and citations: read
the translation once more against the source for claim strength and scope
before handing it back.
