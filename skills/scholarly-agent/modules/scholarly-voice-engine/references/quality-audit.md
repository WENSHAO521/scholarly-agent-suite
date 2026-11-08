# Quality Audit

The final pass before returning scholarly text, and the vocabulary for
talking about what's still wrong when it isn't ready. This file adds
integrity-focused tests, quality states, repair ordering, and a stop rule on
top of `human-scholarly-prose.md`'s own prose-level quality audit (sentence/
paragraph rhythm, transitions, terminology stability) — read that file's
§Quality audit first; this one does not repeat it.

## Redundancy audit

Distinct from useful long-form recurrence (see `continuity-ledger.md`
§Repetition control). Flag:

```text
the same claim restated as if new | the same citation cluster reused for an
unrelated point | the same contribution restated in multiple places | the
same definition repeated verbatim rather than referenced back | the same
transition device reused mechanically across sections
```

## Reviewer-aware self-test

Before finalizing, silently ask (do not stage a theatrical fake review in the
output — see `article-writing.md` §Reviewer-aware tightening):

```text
What would a skeptical specialist in this field challenge first?
Which assumption is doing unstated work?
Which claim is broader than the cited evidence actually supports?
Where is a construct or term used unstably?
What alternative explanation survives the evidence presented?
Is a limitation being minimized or hidden rather than stated?
```

## Substantive integrity tests

Run whichever of these apply to the piece's claims:

```yaml
mechanism_test: >
  A claimed mechanism needs an actor/process, a link, an intermediate step,
  and an observable implication. A sequence of correlated variables is not
  automatically a mechanism — if the text asserts "mechanism" but supplies
  only correlation, either supply the missing step or downgrade the claim
  (associational, not mechanistic — see claim-calibration.md).
theory_test: >
  A list of variables is not a theory. Theory requires explanatory logic
  connecting constructs, not just their co-occurrence.
causal_test: >
  Verify the research design actually licenses causal language before
  allowing it (research-design-matrix.md). If unclear, downgrade rather than
  invent a justification.
humanities_interpretation_test: >
  Interpretive claims need source/text evidence, context, and stated
  reasoning — legitimate interpretive confidence is not the same as
  empirical certainty, and should not be dressed in empirical-certainty
  language.
normative_argument_test: >
  Separate the empirical premise, the normative premise, the value judgment,
  and the institutional consequence — especially in political theory,
  ethics, law, and policy writing. An empirical premise smuggled in as
  self-evident is a defect, not a rhetorical economy.
scientific_mechanism_test: >
  Do not let "mechanism" appear merely because two variables are related in
  a natural-science context either — apply the same field-appropriate
  evidence threshold as the mechanism_test above.
statistical_integrity: >
  Never alter p-values, effect sizes, confidence intervals, sample sizes, or
  model specification during a stylistic pass. Never let prose imply
  practical significance from statistical significance alone.
formal_integrity: >
  Never modify definitions, notation, hypotheses, or proof dependencies to
  improve prose flow in mathematical/formal work.
legal_integrity: >
  Never fabricate case law, statute text, or judgments; keep descriptive
  ("what the law is") and normative ("what it should be") claims visibly
  separate.
historical_integrity: >
  Never invent archives, dates, quotations, events, or actors; historical
  narrative polish stays subordinate to source integrity.
```

## Generic-AI audit

Cross-reference `human-scholarly-prose.md`'s checklist. In addition, watch
specifically for:

```text
empty significance claims       — "this is important" with no named stake
                                   (see §Significance guard below)
inflated novelty                — "first-ever," "unprecedented," "completely
                                   new" without evidence-grounded support
excessive topic sentences        — every paragraph telegraphed before it's
                                   made, removing any reason to read the rest
repeated mini-conclusions         — every paragraph re-closing with a summary
                                   sentence
```

## Novelty inflation guard

Replace unsupported superlatives with evidence-grounded contribution
statements:

```text
weak:   "This groundbreaking, unprecedented study reveals a novel mechanism
        never before observed."
better: name the specific prior state of knowledge and what specifically
        this work adds to or revises in it
```

## Significance guard

Replace generic significance claims with a specific answer to: what changes,
for which theory or practice, under what condition, for whom.

```text
weak:   "This is of great theoretical and practical significance."
better: "If the mechanism holds outside the studied sector, it implies X for
        Y theory and Z for practitioners managing W."
```

## Quality states

```text
PASS                              — ready to return
PASS_WITH_LIMITATIONS             — ready to return; state the limitations
                                     explicitly rather than silently
REPAIR_REQUIRED                   — a fixable defect found; repair before
                                     returning
BLOCKED_BY_MISSING_EVIDENCE       — cannot complete without evidence the
                                     user/host must supply
BLOCKED_BY_CITATION_UNCERTAINTY   — a citation cannot be verified and the
                                     claim depends on it
BLOCKED_BY_ARGUMENT_INCONSISTENCY — the source material contains a genuine
                                     contradiction that must be resolved by
                                     the user, not silently by this Skill
```

## Repair order

When a defect is found, fix in this order — do not polish prose sitting on
top of a broken argument or an unverified claim:

```text
1. factual/citation repair       (citation-integrity.md)
2. argument repair                (the integrity tests above)
3. discipline/genre repair        (disciplines/*.md, argument-architectures.md)
4. voice repair                   (voice-engine.md, human-scholarly-prose.md)
5. surface repair                 (grammar, local wording)
```

## Stop rule

Stop revising when all of the following hold — do not keep polishing past
this point:

```text
the requested deliverable is complete
AND factual/citation integrity is acceptable
AND the argument architecture is coherent
AND disciplinary conventions are satisfied
AND no critical issue remains unresolved
```

If a genuine unresolved issue remains (missing evidence, an unverifiable
citation, a contradiction only the user can resolve), report it as the
relevant `BLOCKED_BY_*` state rather than shipping prose that papers over it.
