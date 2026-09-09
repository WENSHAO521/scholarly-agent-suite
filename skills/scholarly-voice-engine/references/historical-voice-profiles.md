# Historical Voice Profiles

Historical scholars are modeled here as sources of **transferable writing
mechanisms** — sentence architecture, argument architecture, how they define
terms, how evidence enters the text, how they handle counterargument — never as
sources of characteristic phrases or quotations to copy. Do not fabricate or
reproduce any quotation attributed to a figure below. The abstract profiles in
`voice-engine.md` (Analytical-Mechanistic, Institutional-Comparative, etc.) are
the operational unit; the entries below explain where each abstraction draws its
mechanisms from and, importantly, what *not* to imitate mechanically (period-bound
vocabulary, dated terminology, or now-outdated conventions).

## Profile entry schema

```text
Scholar
Discipline
Period
Primary writing genres
Sentence architecture
Argument architecture
Definition style
Evidence style
Citation style
Use of examples
Use of counterargument
Level of abstraction
Typical intellectual rhythm
Strengths worth transferring
Traits not to imitate mechanically
Best-fit modern genres
```

## Illustrative entries

### Max Weber — sociology, comparative-historical (feeds Institutional-Comparative)
```text
Sentence architecture:   long, subordinate-clause-heavy, qualification embedded
                          mid-sentence rather than appended
Argument architecture:   ideal type → comparative variation → causal adequacy
Definition style:        explicit, stipulative, revisited across a text
Evidence style:          comparative-historical illustration, not statistical
Counterargument:         addressed by narrowing scope conditions, not refutation
Strengths to transfer:   scope-conditioned generalization; ideal types as
                          analytical tools rather than descriptions of reality
Not to imitate:          the sheer sentence length itself — modern journals
                          require shorter units carrying the same precision
Best-fit modern genres:  theory articles, comparative institutional analysis
```

### Charles Darwin — natural history (feeds Experimental-Mechanistic / Economical-Scientific)
```text
Sentence architecture:   plain, cumulative, evidence stacked before inference
Argument architecture:   observation → anomaly → mechanism → generalization
Definition style:        minimal; concepts built through examples rather than
                          stipulated definitions
Evidence style:          dense concrete particulars, patient accumulation
Counterargument:         anticipated objections addressed one at a time, in the
                          author's own voice, before conclusions are drawn
Strengths to transfer:   restraint in inference; letting accumulated observation
                          carry the argument's weight
Not to imitate:          Victorian-era diction; anecdotal sample sizes acceptable
                          then are not acceptable evidentiary practice now
Best-fit modern genres:  natural-history and field-biology synthesis, review
                          articles building toward a mechanism
```

### David Hilbert — mathematics (feeds Formal-Deductive)
```text
Sentence architecture:   short, declarative, notation doing most of the work
Argument architecture:   problem → axioms/definitions → theorem → proof
Definition style:        maximally precise, minimal redundancy
Evidence style:          proof as the only evidence; no rhetorical support
Counterargument:         handled as boundary cases and counterexamples, not prose
                          objection
Strengths to transfer:   notation discipline; refusal to let prose substitute
                          for proof
Not to imitate:          period-specific notation conventions superseded by
                          modern standard notation
Best-fit modern genres:  mathematical papers, formal sections of any discipline
```

### Claude Bernard — experimental physiology (feeds Clinical-Evidentiary)
```text
Sentence architecture:   medium length, method and result kept in close
                          proximity within the same paragraph
Argument architecture:   hypothesis → controlled intervention → observed effect
                          → mechanistic interpretation → explicit limits
Definition style:        operational — defined by how a variable was measured
Evidence style:          the experiment itself narrated as evidence
Counterargument:         alternative explanations tested experimentally rather
                          than argued away in prose
Strengths to transfer:   explicit separation of what was observed from what is
                          inferred; distrust of unearned generalization
Not to imitate:          single-investigator, uncontrolled-comparison norms of
                          the period, superseded by modern controlled-trial design
Best-fit modern genres:  experimental biology/medicine articles, clinical
                          research papers
```

### Marc Bloch — history (feeds Historical-Structural)
```text
Sentence architecture:   moderate length, source and interpretation interleaved
Argument architecture:   question → source critique → chronological
                          reconstruction → interpretation → historiographical
                          positioning
Definition style:        concepts defined through their historical variation,
                          not fixed once and reused unchanged
Evidence style:          primary-source grounded, source reliability made
                          explicit
Counterargument:         engaged as alternative readings of the same sources
Strengths to transfer:   source skepticism; treating a concept's historical
                          instability as itself informative
Not to imitate:          absence of the citation apparatus expected in current
                          historical scholarship
Best-fit modern genres:  historical studies, intellectual-history chapters
```

### Karl Popper — philosophy of science (feeds Normative-Systematic / Analytical)
```text
Sentence architecture:   short to medium, high logical connective density
Argument architecture:   thesis → distinction → argument → objection →
                          qualification → sharpened thesis
Definition style:        adversarial — defined partly by contrast with rejected
                          alternatives
Evidence style:          argument from consequence and counterexample rather
                          than empirical citation
Counterargument:         central to the method, not an afterthought section
Strengths to transfer:   taking the strongest form of an opposing view seriously
                          before responding to it
Not to imitate:          polemical tone where a gentler register better serves
                          the target venue
Best-fit modern genres:  philosophical essays, theoretical/normative articles
```

### John von Neumann — mathematics/game theory (feeds Formal-Deductive / Strategic-Interaction)
```text
Sentence architecture:   dense, terse, assumes reader fluency with formalism
Argument architecture:   formalize the situation → derive consequence → interpret
Definition style:        axiomatic, minimal appeal to intuition once formalized
Evidence style:          formal derivation; intuition offered only as a gloss
Strengths to transfer:   translating an informal problem into a formal structure
                          before arguing about it
Not to imitate:          terseness that assumes away necessary exposition for a
                          non-specialist target audience
Best-fit modern genres:  formal theory articles, economics/game-theory papers
```

## Using this library

1. Identify the mechanism the task actually needs (e.g., "scope-conditioned
   generalization," "evidence-close mechanistic interpretation") rather than
   picking a name first.
2. Route to the corresponding abstract profile in `voice-engine.md`.
3. Combine primary/secondary/depth layers as needed; do not import an entire
   named figure's voice wholesale.
4. Never quote, paraphrase into a "signature phrase," or otherwise reproduce a
   named figure's actual wording.

## Living and contemporary scholars

Do not build named profiles for living scholars. If a request references one,
extract only high-level, discipline-general traits (e.g., "mechanism-centered
prose," "economical causal argument," "comparative institutional analysis,"
"narrative theoretical exposition," "highly formal methodological writing") and
synthesize a composite, original voice from those traits — never a stylistic copy.
See `SKILL.md` §Voice profiles for the operational rule and
`disciplines/interdisciplinary.md` / eval file `anti-generic-ai-cases.jsonl` for
the corresponding safeguard tests.
