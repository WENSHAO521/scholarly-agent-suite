<!-- Module of the scholarly-agent Skill (native module, added in v2.2.0).
     Loaded on demand by ../../SKILL.md; paths below are relative to this module's directory. -->

> **Module `prose-polish-engine`** -- part of the single `scholarly-agent` Skill. Load this file only when the
> dispatcher in `SKILL.md` selects this module. Sibling modules are at `modules/<name>/`.
> Paths such as `references/...` are relative to `modules/prose-polish-engine/`.
>
> Scope: Polishing (潤色) of finished academic prose in any language: find and rewrite the templated phrasing that makes a text read as machine-made or boilerplate -- stock connectives, empty emphasis, inflated vocabulary, formulaic openings and closings, stacked hedges, repeated sentence shapes, uniform rhythm (the "language watermark", 語言水印, of templated writing) -- and defensive writing (防禦性寫作: hedges that answer to no evidence, pre-emptive caveats, disclaimers, apologies for the work, over-justification) -- so it reads like a careful scholar wrote it, while every claim, citation, number, quotation, and term, and every uncertainty the evidence warrants, stays exactly as it was.

# Prose Polish Engine

A text can be correct and still read as if it came off a template: every
paragraph opens with "Furthermore", 「此外」, or « De plus », every finding
"plays a crucial role", 「具有重要意義」, or 「重要な役割を果たす」, every list has three items, every sentence
is the same length. Readers, editors, and reviewers notice these marks, and
they cost the author credibility before the argument is even weighed. This
module removes them, in whatever language the text is written.

The same is true of defensive writing (防禦性寫作): a text that hedges every
sentence, apologizes for itself 「拋磚引玉」, concedes limitations nobody
raised, and justifies routine choices reads as unsure of its own results,
and it hides the uncertainties that are real. Since v2.5.0 this module
removes the defence and keeps the real uncertainty, once, specifically, on
the claim it qualifies ([references/defensive-writing.md](references/defensive-writing.md)).

## Languages

Every language is in scope. Nine have a phrase catalog in `ppe/patterns.py`:
English, Chinese (Traditional and Simplified), Japanese, Korean, Spanish,
French, German, Portuguese, and Russian. For any other language the
structural checks and the protection of citations, numbers, quotations,
and formulas run the same way, and the phrase-level pass follows
[references/other-languages.md](references/other-languages.md). The
polished text stays in the author's language, script, and regional variety;
polishing never translates or converts.

```
Protect   mark citations, numbers, quotations, formulas, and the author's key terms
Diagnose  find templated phrasing, defensive writing, and structural habits (ppe.diagnose)
Defend    warrant test on every qualifier: keep the real uncertainty, remove the defence
Polish    rewrite, pass by pass, at the level the user asked for
Verify    check nothing protected moved (ppe.invariants), re-diagnose, one repair pass at most
Report    polished text + what changed + what was kept and why (POLISH_REPORT_V1)
```

## What "language watermark" means here

In this module, 語言水印 / "language watermark" means the visible stylistic
marks of templated writing: phrases and sentence habits a reader can point
to. It works on the text a reader sees. It does not inspect or try to alter
token-level statistical watermarks that some text generators embed, and it
does not measure or optimize against any AI-text detector (see Integrity).

## Defensive writing (防禦性寫作)

Six forms, each a category in `ppe.patterns` and `ppe.diagnose`:

| Category | Looks like |
|---|---|
| `defensive-hedge` | "it could be argued that", "seems to suggest a possible", 「從某種意義上說」「或可認為」 |
| `hedge-blanket` | three or more hedges in one sentence; nearly every sentence of a paragraph hedged (structural, any language with a hedge list) |
| `preemptive-caveat` | "while this study has some limitations", "should be interpreted with caution", "further research is needed", 「本研究也存在一些不足」「有待進一步研究」 |
| `disclaimer` | "by no means exhaustive", "does not claim to be comprehensive", 「限於篇幅」「本文無意窮盡」 |
| `apologetic-framing` | "we humbly suggest", "this modest attempt", 「拋磚引玉」「不當之處，敬請指正」 |
| `over-justification` | "it is reasonable to assume", "for the sake of rigour", 「為了保證研究的嚴謹性」「學界普遍認為」 |

The line between defence and caution is the **warrant test**: every
qualifier must answer to a source of uncertainty the polisher can name
(design ceiling, statistical uncertainty, scope, measurement, contested
interpretation, extrapolation). If it does, one qualifier stays, made
specific and placed on the claim it qualifies; if not, it goes. Removing a
defensive hedge never makes a claim stronger than its design allows. Each
decision is logged in the report's `calibration` ledger, and the report
validator rejects a polish whose hedge count fell with no logged reason.
Full procedure: [references/defensive-writing.md](references/defensive-writing.md).

## Ecosystem position

```
Scholarly Voice Engine     drafts and revises: argument, structure, claims, voice
Prose Polish Engine (this) the finished text's wording: templated phrasing out, meaning unchanged
Peer Review Engine         critiques and decides; never rewrites
Journal Fit Engine         target journal's style context, if the user names a journal
Scholarly Corpus Builder   an author-voice or journal style profile, if one exists
```

Stay in lane. Polishing changes wording, never content. If the diagnosis
shows the real problem is the argument (a claim the evidence does not carry,
paragraphs in the wrong order, a missing step), do not fix it here: record it
under `escalations` and tell the user it needs a revision pass (voice
module). If a `JOURNAL_STYLE_CONTEXT_V1` or an author voice profile is
already in hand, polish toward it; never build one just for a polish.

## When to use

- 「潤色」「幫我潤色這段」「去 AI 味」「讀起來太像 AI 寫的」「去掉語言水印」「改得自然一點」
- 「去掉防禦性寫作」「限定語太多」「別一直說『可能』」「不要那麼多免責聲明」「太謙虛、太像在道歉」
- "Cut the hedging." / "This reads too defensive." / "Stop apologizing for the study."
- "Polish this so it doesn't read machine-written." / "Remove the AI-sounding phrasing."
- "This reads like a template; make it sound like me."
- 「AIっぽさを消して」「AI 티 안 나게 다듬어 줘」«Quítale el tono de IA» « Rends ce texte moins artificiel »
- After drafting, as the last language pass before submission (the dispatcher
  may add it as a final stage of a writing workflow).

Not for: drafting from notes, restructuring, or strengthening an argument
(voice); a single obvious grammar fix (answer directly); judging whether a
text was written by AI (decline; see Integrity); translation as such
(translation-engine).

## Levels

Ask nothing if the request makes the level clear; otherwise default to
`standard` and say so.

| Level | Touches | Leaves alone |
|---|---|---|
| `light` | chat residue, stock connectives, empty emphasis, inflated words, stacked hedges; apologetic framing, disclaimers, defensive hedges | sentence and paragraph shape |
| `standard` (default) | everything in light, plus formulaic openings and closings, nominalizations, repeated openers, three-item habits, sentence rhythm inside a paragraph; pre-emptive caveats, over-justification, hedge blankets | paragraph order, what each paragraph claims |
| `deep` | everything in standard, plus sentence order within a paragraph, merging and splitting sentences, cutting recap sentences that restate the paragraph; consolidating caveats about one limitation into one specific statement, deleting a caveat that repeats a limitation stated in full elsewhere | the argument, section structure, evidence, claim strength |

No level changes data, findings, citations, quotations, defined terms, or
how strongly a claim is made, and no level removes an uncertainty the
evidence warrants.

## Workflow

1. **Intake.** Detect the language (`ppe.languages.detect_language`, or
   take it from the user) and its script and regional variety
   (Traditional or Simplified Chinese, pt-BR or pt-PT, ...); keep them exactly
   as the author wrote them. A text mixing languages is polished language by
   language, each against its own conventions. Note the discipline and
   genre if known, and any target journal or author voice already in hand.
   Ask the user for terms that must not change only if the text is full of
   specialist vocabulary and none were given.
2. **Protect.** Treat citations, DOIs, URLs, numbers and statistics, direct
   quotations, formulas, and the author's key terms as fixed
   (`ppe.invariants.extract`). Never rewrite inside a quotation: a quoted
   source keeps its own wording, templated or not.
3. **Diagnose.** Run `ppe.diagnose.diagnose(text)` (or `python -m ppe
   diagnose FILE`) and read the findings by paragraph. The catalog is a
   starting point, not a verdict: a flagged "however" that does real
   contrastive work stays. See
   [references/pattern-catalog.md](references/pattern-catalog.md) (English and
   the shared categories),
   [references/chinese-academic-prose.md](references/chinese-academic-prose.md),
   and [references/other-languages.md](references/other-languages.md).
4. **Defend.** For every qualifier in a paragraph with defensive findings,
   run the warrant test in
   [references/defensive-writing.md](references/defensive-writing.md):
   `kept`, `scoped`, `removed`, or `consolidated`, each with its warrant,
   recorded for the report's `calibration` ledger. Real limitations are
   stated once, specifically: what, which result, which direction, what
   still holds. If the hedging is everywhere because the claim is bigger
   than the evidence, do not shrink the claim here: escalate it.
5. **Polish.** Work through the passes in
   [references/polishing-passes.md](references/polishing-passes.md) up to the
   chosen level: residue, defense, words, connectives, sentences, paragraphs. Each
   rewrite must say the same thing more specifically, or the same thing in
   fewer words. Never swap one template for another ("Furthermore" ->
   "Moreover") and never replace a phrase with a rarer synonym just because
   the common one is on the list.
6. **Verify.** Run `ppe.report.build_polish_report(original, polished, ...,
   calibration=...)`
   (or `python -m ppe check ORIGINAL POLISHED`). `FAIL` means something
   protected was lost or altered: restore it, do not explain it away.
   `REVIEW` means hedges, negations, or length moved: confirm each one is a
   wording change and not a change in the claim, and say so in the report
   (for hedges, the `calibration` ledger does this).
   One repair pass at most; anything still open goes into `limitations`.
7. **Hand back.** Return the polished text first, then a short summary of
   what changed (grouped by category, with two or three representative
   before/after pairs), anything kept on purpose (`kept_because`), and any
   escalations. Format: [references/polish-report.md](references/polish-report.md).

## Integrity (non-negotiable)

`shared/integrity-policy.md` applies in full. In addition:

- **Quality, not evasion.** The goal is prose a reader trusts. This module
  never scores text for "AI probability," never runs or loops against an
  AI-text detector, never promises a result on one, and never adds noise,
  typos, odd punctuation, invisible characters, or homoglyphs to change how
  a text is classified (`shared/integrity-policy.md` rule 14). If a user asks
  for detector evasion as such, say plainly that this module improves the
  writing and cannot promise anything about any detector, then offer the
  polish.
- **Disclosure stays with the author.** Many journals, publishers, and
  universities require authors to disclose AI assistance. Polishing does not
  change that obligation, and this module never advises hiding AI use where
  disclosure is required. When the user's request is explicitly about
  passing an AI check for a submission or an assessment, remind them once,
  briefly, to follow the venue's AI-use policy.
- **Meaning is fixed.** No change to data, results, citations, quotations,
  or claim strength (`modules/scholarly-voice-engine/references/argument-and-claims.md#claim-calibration`
  applies: never let a polish turn "is associated with" into "causes," or
  drop a hedge the evidence needs). Unverified citations stay flagged, never
  smoothed into confident prose.
- **Confidence is earned, not added.** Removing defensive writing means
  stating supported claims plainly. It never means deleting a real
  limitation, hiding a null or fragile result, dropping a reporting
  guideline's required limitations section, or writing more certainty
  than the design allows. A limitation the author must report stays, made
  specific.
- **No faked naturalness.** Variation comes from saying things precisely,
  not from deliberately degrading the text.
- **The author's voice wins.** Where the author has a distinctive habit that
  happens to be on the list, keep it if it is consistent and purposeful;
  the catalog targets templates, not personality. No imitation of a living
  author's voice.

## Runtime code

`ppe/` is a small standard-library package (Python 3.10+), importable by
putting this module's directory on `sys.path`:

- `ppe.patterns` -- the phrase catalogs (en, zh, ja, ko, es, fr, de, pt, ru),
  including the defensive-writing categories (`ppe.DEFENSIVE_CATEGORIES`).
- `ppe.languages` -- `detect_language(text)` for any language, sentence
  splitting, units, hedge and negation lists, connective openers.
- `ppe.diagnose` -- `diagnose(text, lang)` (findings, counts by category,
  density, `pattern_load`, `defensive`, `hedge_rate`, and the hedge pile-up
  and hedge blanket checks), for any language; `defensive_findings(d)`.
- `ppe.invariants` -- `extract(text)`, `check_invariants(original, polished,
  lang, protected_terms)`.
- `ppe.report` -- `build_polish_report(...)` producing `POLISH_REPORT_V1`
  (with the optional `calibration` ledger), and `validate_polish_report(report)`.
- `python -m ppe diagnose FILE [--defensive]` / `python -m ppe check ORIGINAL
  POLISHED [--term TERM]` -- the same, from a shell, as JSON.

The code finds and counts; the rewriting and the judgment about what to
keep belong to the polisher following this file.

## References

- `references/polishing-passes.md` -- levels, the six passes, verification, the repair limit
- `references/defensive-writing.md` -- defensive writing: the warrant test, the six forms, non-defensive limitations, the calibration ledger
- `references/pattern-catalog.md` -- English templated phrasing, by category, with rewrites
- `references/chinese-academic-prose.md` -- Chinese (Traditional and Simplified) templated phrasing and academic register
- `references/other-languages.md` -- Japanese, Korean, Spanish, French, German, Portuguese, Russian, and the procedure for any other language
- `references/polish-report.md` -- `POLISH_REPORT_V1` fields and how to present a polish to the author
