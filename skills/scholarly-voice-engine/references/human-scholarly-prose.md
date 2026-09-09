# Human Scholarly Prose

This module's purpose is **not** to defeat AI-detection tools. It exists to remove
generic, machine-like academic prose and replace it with the intellectual
variation that characterizes writing by a practicing scholar.

## Transitions to avoid overusing

Not banned outright — flag when they substitute for actual argumentative
connection rather than expressing one:

```text
Furthermore. Moreover. Additionally. It is important to note that.
It is worth noting that. In today's rapidly changing world.
This study aims to. The results highlight the importance of.
From this perspective. In conclusion.
```

## Prefer transitions with argumentative function

Use only where the relationship they name is actually true of the surrounding
text — do not decorate with these either:

```text
The difficulty lies elsewhere.
This explanation, however, leaves one question unresolved.
The distinction matters for two reasons.
The evidence supports a narrower claim.
At first sight, these findings appear inconsistent.
The institutional explanation changes once time is introduced.
A competing interpretation is possible.
The stronger claim does not follow from these results.
```

## Controlled asymmetry

Genuine scholarly prose is not geometrically uniform. Permit:

- short, decisive paragraphs beside long conceptual ones where each is earned;
- occasional very short sentences for emphasis;
- uneven evidence density (some claims need one citation, others need five);
- recurring concepts revisited rather than redefined from scratch each time;
- different rhythms across sections of the same piece.

Do **not** mechanically force uniform paragraph length, uniform sentence length,
a fixed citation count per paragraph, or a restated mini-conclusion at the end of
every paragraph — that regularity is itself a generic-AI signature. Do not,
however, introduce actual mistakes to fake this variation (see Integrity, below).

## Anti-generic-AI checklist

Before finalizing, scan the draft for these patterns and revise any that fired
mechanically rather than substantively:

```text
transition repetition           — same connective word reused across paragraphs
over-signposting                — "In this section, we will..." / "As shown above..."
                                   used more than the structure actually requires
parallel paragraph symmetry     — every paragraph same length/shape
excessive recap                 — restating prior points instead of advancing
generic importance claims       — "this is an important area of study" with no
                                   specific stake named
inflated contribution language  — "novel," "unprecedented," "groundbreaking"
                                   applied to incremental contributions
uniform sentence length         — no rhythmic variation across a paragraph
mechanical three-part lists     — reflexive rule-of-three where two or four items
                                   are the true count
citation dumping                — strings of citations not tied to a specific claim
abstract noun overload          — nominalizations ("utilization," "implementation
                                   of methodologies") replacing direct verbs
```

## Claim strength and uncertainty language

Match hedging to what the evidence supports, using field-appropriate phrasing
(see also each `disciplines/*.md` file):

```text
Experimental science:  is consistent with / supports the possibility that /
                        suggests a role for / does not exclude
Social science:         the evidence is compatible with / under these
                        institutional conditions / within the observed sample
Humanities:             may be read as / this interpretation emphasizes /
                        a competing reading would
Law:                    the stronger interpretation would imply / the doctrine
                        does not clearly resolve
```

Avoid both overclaiming and excessive hedging — a sentence qualified past the
point of making a claim at all is a failure mode, not caution.

## First-person calibration

Do not universally ban or universally require "I"/"we." Determine appropriateness
from discipline, genre, and specific journal convention (see
`disciplines/*.md` → `acceptable_first_person`). "We show...", "we estimate...",
"I argue...", "we interpret..." are legitimate scholarly prose in the right
context (most empirical sciences, much social science, philosophy) and jarring in
others (some legal doctrinal writing, some formal mathematics).

## Section-level voice calibration

Within one document, vary register by function rather than applying one template
throughout:

```text
Introduction — more conceptual, more argumentative
Methods      — precise, low rhetorical intensity
Results      — evidence-first, minimal interpretation
Discussion   — interpretive, qualified, conceptual
```

## Integrity constraints on "humanizing"

Naturalness comes from genuine intellectual variation — never from deliberately
degrading quality. Never introduce, for the sake of sounding human:

```text
grammar errors, typos, logical gaps, incorrect citations,
random punctuation, awkward wording
```

## Quality audit (run before returning text)

```text
Does this sound like a scholar in this field?
Does the argument move rather than merely summarize?
Are claims calibrated to the evidence actually presented?
Are transitions intellectual rather than mechanical?
Does evidence sit near the claim it supports?
Does the prose vary naturally in rhythm across paragraphs/sections?
Does terminology remain stable across the document?
Does the writing preserve the author's actual position (not silently drifted)?
```

If any answer is no, revise that specific part rather than regenerating the whole
document.
