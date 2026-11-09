# Polishing in any language

The module polishes academic prose in every language. How much the runtime
helps depends on the language:

| Coverage | Languages | What runs |
|---|---|---|
| Phrase catalog | English (`pattern-catalog.md`), Chinese (`chinese-academic-prose.md`), Japanese, Korean, Spanish, French, German, Portuguese, Russian (below) | phrase findings, structural findings, protected-item check, hedge and negation counts |
| Any other language | Italian, Dutch, Arabic, Hebrew, Greek, Turkish, Thai, Hindi, Indonesian, Vietnamese, Polish, Ukrainian, … (any ISO 639 code) | structural findings, protected-item check; phrase-level work done by the polisher with this page's procedure |

`ppe.languages.detect_language()` guesses the language from its script and
common function words. Pass `lang` explicitly when the guess matters
(Serbian Cyrillic, Persian vs. Arabic, Malay vs. Indonesian, mixed-language
text). A report for a language without a catalog records that in
`limitations`, so no one mistakes "no findings" for "clean".

## The categories are universal

Templated academic prose looks alike across languages, because it comes
from the same habits. Every category in `pattern-catalog.md` has an
equivalent in every language:

| Category | Ask of each sentence |
|---|---|
| chat-residue | Is any of this addressed to a chat user rather than a reader? |
| stock-connective | Does "furthermore / además / さらに / кроме того" name a real relation? |
| empty-emphasis | Does "it is important to note / cabe destacar / 注目すべきは / важно отметить" frame a point instead of making it? |
| inflated-vocabulary | Is a grand or marketing word standing in for a specific one? |
| formulaic-frame | Does the opening ("in today's world / dans le monde actuel / 近年…の発展に伴い") delay the actual problem? |
| stock-summary | Does the closing only restate the paragraph? |
| hedge-stack | Is the claim hedged twice? |
| contrast-template | Is "not only … but also / non seulement … mais aussi / не только … но и" a habit? |
| nominalization | Is a verb buried in "carry out an analysis / realizar un análisis / 分析を行う / провести анализ"? |
| structural habits | Same openers, same sentence length, reflexive three-item lists, dashes |

## Procedure for a language without a catalog

1. Identify the language and, where it matters, the variety and script
   (European vs. Brazilian Portuguese, Serbian Latin vs. Cyrillic, Modern
   Standard Arabic). Keep the author's variety; never convert it.
2. Run `ppe.diagnose.diagnose(text, lang)` for the structural findings.
3. Read the text once per category in the table above, using your knowledge
   of that language's academic register. List the phrases you would flag
   before rewriting, so the change log can name them.
4. Follow `polishing-passes.md` exactly as for any other language,
   including protection and verification.
5. Note in the hand-back that the phrase-level pass relied on judgment, not
   a catalog.

Language-specific conventions still apply: academic Arabic, Japanese, and
Korean are more formal than English and tolerate longer sentences; German
academic prose expects precise compound terms and does not need them
broken up; Romance languages use longer sentences than English academic
prose without that being a defect. Polish toward the conventions of the
language and discipline, not toward English.

## Catalog summaries

Full patterns are in `ppe/patterns.py`. These are the commonest ones.

### Japanese (ja)

- Residue: 「もちろんです」「以下は修正した…」「お役に立てれば幸いです」
- Connectives: 段落や文頭の「さらに、」「加えて、」の連続
- Empty emphasis: 「重要な役割を果たしている」「注目すべきは」「言うまでもなく」
- Frames: 「近年、…の急速な発展に伴い」「新たな視点を提供する」「本研究の目的は」
- Summary: 「以上のことから」「総じて」「まとめると」
- Nominalization: 「分析を行う」→「分析する」
- だ・である調とです・ます調を混ぜない。原文の文体を保つ。

### Korean (ko)

- Residue: 「물론입니다」「다음은 수정된…」「도움이 되었으면 좋겠습니다」
- Connectives: 「또한,」「더불어,」의 반복
- Empty emphasis: 「중요한 역할을 한다」「주목할 만한 점은」
- Frames: 「최근 …의 급속한 발전에 따라」「새로운 시사점을 제공한다」
- Summary: 「결론적으로」「요약하면」「종합하면」
- Nominalization: 「분석을 진행하였다」→「분석하였다」
- 학술 문체(-다)를 유지하고 경어체와 섞지 않는다.

### Spanish (es)

- Residue: «¡Claro!», «Aquí tienes la versión revisada», «Espero que te sea útil»
- Connectives: «Además,», «Asimismo,», «Por otro lado,»
- Empty emphasis: «cabe destacar que», «es importante señalar que», «desempeña un papel crucial»
- Frames: «en el mundo actual», «arrojar luz sobre», «sentar las bases», «el presente estudio pretende»
- Summary: «En conclusión,», «En definitiva,»
- Nominalization: «realizar un análisis» → «analizar»

### French (fr)

- Residue: « Bien sûr ! », « Voici la version révisée », « J'espère que cela vous aide »
- Connectives: « De plus, », « En outre, », « Par ailleurs, »
- Empty emphasis: « il convient de noter que », « joue un rôle crucial »
- Frames: « dans le monde actuel », « mettre en lumière », « ouvrir de nouvelles perspectives », « cette étude vise à »
- Summary: « En conclusion, », « En somme, »
- Nominalization: « procéder à une analyse » → « analyser »
- Respect French typography (espaces insécables before ; : ! ?, guillemets « »).

### German (de)

- Residue: „Natürlich!", „Hier ist die überarbeitete Fassung", „Ich hoffe, das hilft"
- Connectives: „Darüber hinaus", „Außerdem", „Zudem", „Des Weiteren"
- Empty emphasis: „es ist wichtig zu betonen, dass", „spielt eine entscheidende Rolle"
- Frames: „in der heutigen Welt", „wirft ein neues Licht auf", „ebnet den Weg", „Ziel dieser Arbeit ist es"
- Summary: „Zusammenfassend lässt sich sagen"
- Nominalization: „eine Analyse wurde durchgeführt" → „analysiert"

### Portuguese (pt)

- Residue: «Claro!», «Aqui está a versão revisada», «Espero que isso ajude»
- Connectives: «Além disso,», «Ademais,», «Outrossim,»
- Empty emphasis: «vale ressaltar que», «é importante destacar que», «desempenha um papel crucial»
- Frames: «no mundo atual», «lançar luz sobre», «abrir caminho», «o presente estudo visa»
- Summary: «Em suma,», «Em conclusão,»
- Keep the author's variety (pt-BR or pt-PT) in spelling and vocabulary.

### Russian (ru)

- Residue: «Конечно!», «Вот исправленный вариант», «Надеюсь, это поможет»
- Connectives: «Кроме того,», «Более того,», «Помимо этого,»
- Empty emphasis: «важно отметить, что», «следует подчеркнуть, что», «играет ключевую роль»
- Frames: «в современном мире», «проливает свет на», «открывает новые перспективы», «целью данного исследования является»
- Summary: «В заключение,», «Подводя итог,»
- Nominalization: «провести анализ» → «проанализировать»
