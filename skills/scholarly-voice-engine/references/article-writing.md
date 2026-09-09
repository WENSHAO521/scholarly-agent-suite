# Article Writing

Loaded when the task is article-scale (see `SKILL.md` §Book vs. article routing).
Distinguishes major article architectures rather than forcing one universal
template. See `argument-architectures.md` for the underlying family shapes and
`genre-matrix.md` for genre-specific length/feature expectations — this file adds
drafting and section-calibration guidance on top of those.

## Architecture selection

Pick the architecture from `argument-architectures.md` matching the discipline
family and genre, not by default reflex toward IMRaD. A theory article in public
administration and an experimental article in molecular biology should not share
a section skeleton just because both are "research articles."

## Section-level voice calibration

Within a single article, vary register by function (see also
`human-scholarly-prose.md` and `voice-engine.md`):

```text
Introduction — conceptual, argumentative; earns the reader's attention on the
               stakes and the specific gap, not a generic "importance" claim
Literature   — positions the contribution against specific prior claims, not an
               undifferentiated list
Methods      — precise, low rhetorical intensity, reproducible level of detail
Results      — evidence-first, interpretation minimal and clearly bracketed off
Discussion   — interpretive, qualified, conceptual; where mechanism/implication
               is argued
Limitations  — substantive (design, scope, measurement), not ritual disclaimer
Conclusion   — narrowed, earned claim; not a restatement of the abstract
```

## Contribution framing

State the specific contribution type (see `argument-architectures.md`
§Contribution types) early and concretely. Avoid generic gap-spotting language
("few studies have examined X") in favor of the substantive gap actually being
addressed (mechanism, measurement, boundary condition, etc.).

## Reviewer-aware tightening

Before finalizing, silently interrogate the draft:

```text
What would a skeptical specialist challenge?
What assumption is unstated?
Which claim is broader than the evidence supports?
Which term is used unstably across sections?
Which evidence does the argument actually establish, versus merely gesture at?
```

Use the answers to tighten specific sentences — do not perform a theatrical fake
"Reviewer 2" dialogue in the output.

## Claim and citation discipline

- Match claim strength to what the design/evidence supports (see
  `argument-architectures.md` §Claim calibration and the relevant
  `disciplines/*.md` file).
- Never fabricate citations, quotations, DOIs, or results. Mark missing evidence
  `[VERIFY]` rather than inventing it.
- Keep evidence physically close to the claim it supports (`evidence_proximity`
  in `voice-engine.md`) rather than batching citations at paragraph end
  disconnected from specific assertions.

## When rewriting an existing article draft

Do not silently alter data, results, causal claims, sample description, or
method — voice edits are subordinate to epistemic accuracy (see `SKILL.md`
§Terminology and integrity). Flag, rather than silently fix, anything that looks
like a substantive (not stylistic) problem — e.g., a claim the results section
doesn't actually support.
