# Multilingual Writing

English-language academic writing is the primary, most-developed target of
this Skill. This file governs architecture-level support for other languages
and translation between them — it does not assume English rhetorical
structure transfers mechanically to another language, and it does not build
out full language-specific prose rulebooks to the same depth as English.

## Language-independent voice vs. language-specific realization

Keep two layers separate:

```yaml
language_independent:   # carries across languages unchanged
  - discipline/genre argument architecture
  - claim type and claim strength (claim-calibration.md)
  - mechanism focus, definition discipline, scope conditions
  - citation integrity and evidence proximity

language_specific:      # realized differently per language
  - sentence order and clause structure
  - pronoun/subject-drop conventions
  - transition frequency and connective vocabulary
  - punctuation and citation-integration conventions
  - register markers (formality levels, honorifics where applicable)
```

A translation or non-English draft should preserve the language-independent
layer exactly and re-realize the language-specific layer natively — not
transliterate English sentence structure into another language's grammar.

## Supported languages (architecture-level)

```text
Chinese | German | French | Spanish | Japanese | Korean
```

For each, apply the discipline/genre architecture from
`argument-architectures.md` and `disciplines/*.md` as usual, but let sentence
rhythm, connective choice, and formality register follow that language's own
scholarly convention rather than a word-for-word rendering of the English
version.

## Chinese academic writing

Avoid mechanical translationese — connective words such as 因此, 此外,
与此同时, 值得注意的是 used reflexively in nearly every paragraph read the
same way "Furthermore/Moreover" overuse reads in English (see
`human-scholarly-prose.md`). Chinese scholarly prose still needs genuine
argumentative transitions; the fix is the same principle as the English
anti-generic-AI rules, realized in Chinese connective choices rather than
suppressing transitions altogether.

## English academic writing — avoid pseudo-formality

Prefer precise verbs, clear subjects, and bounded claims over unnecessary
nominalization ("the utilization of," "the implementation of methodologies")
— see `human-scholarly-prose.md` §Anti-generic-AI checklist §abstract noun
overload. Formality is not measured by syllable count.

## Translation mode

When translating existing scholarly prose, preserve:

```text
claim strength | concept hierarchy | which citation supports which claim |
authorial stance | argument progression | uncertainty expression
```

Do not mirror the source language's sentence structure mechanically — a
faithful translation re-expresses the same claims and argument moves in the
target language's native scholarly register, not a clause-by-clause mirror.
Where a source-language rhetorical device has no natural target-language
equivalent, replace it with the target language's own device for
accomplishing the same argumentative work rather than a literal rendering
that reads as foreign.

## Cross-language author profile

If a user writes in more than one language, maintain:

```text
author_intellectual_profile      # language-independent: mechanism focus,
                                   claim style, definitional habits
language_specific_profiles:      # one per language, its own realization
  en: {...}
  zh: {...}
  ...
```

Do not infer a user's English sentence-level style from their Chinese (or
other language) writing, or vice versa — sentence-level habits are
language-specific; only the intellectual profile (what kind of claims they
make, how they handle counterargument, their definitional discipline)
transfers across languages. See `author-voice-calibration.md` for how the
intellectual profile itself is derived.

## Standalone note

This file documents architecture-level guidance, not a full rhetorical-
structure module per language. For deep, idiomatic non-English scholarly
prose beyond what this file specifies, rely on the model's own fluency in
that language's scholarly register, applying the language-independent
constraints above as the invariant.
