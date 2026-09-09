# Workflow recipe: target-journal-adaptation

**Not a Skill.** For when a target journal is already chosen (or picked in
this same session via `journal-selection.md`) and the manuscript needs to be
adapted to it.

## When to select this recipe

Trigger example: "Improve this paper for Journal X." Distinguish from
`journal-selection.md` (no chosen journal yet, deliverable is a shortlist)
and `revise-manuscript.md` (general revision, no specific venue).

## Stages

```
journal-fit-engine: confirm/refresh target journal profile
  |
  v
scholarly-corpus-builder      (only if the journal's style/requirement
                                evidence is stale -- rule 49)
  |
  v
journal-fit-engine: produce JOURNAL_STYLE_CONTEXT_V1
  (official_requirements kept separate from observed_patterns -- rule 34)
  |
  v
scholarly-voice-engine: targeted adaptation
  (structure, section policies, citation style, length -- driven by the
   style context, not a full rewrite from scratch)
```

## Freshness handling

If the journal profile is `STALE` and the user's request implies current
constraints matter (e.g. asking about APC or word limits), refresh via
scholarly-corpus-builder before adapting. If the profile is merely
non-current historical style evidence with no current-fact dependency,
skip the refresh (rule 49).

## Implementation (as of journal-fit-engine v0.3.0 / scholarly-voice-engine v1.1.0)

`journal-fit-engine`'s `jfe.style_context.build_journal_style_context()` /
`from_journal_evidence()` produce the envelope; `scholarly-voice-engine`'s
`scripts/voice/journal_context.from_journal_style_context_v1()` /
`apply_journal_style_context()` consume it. `official_requirements`
propagates as a `hard_requirements` block applied verbatim -- never
confidence-gated, never merged into the author/discipline/journal/
historical precedence resolution. `observed_patterns` is fed into that
precedence resolution as the "journal" layer, with `freshness` set its
confidence (`current`→high, `aging`→moderate, `stale` or absent→low) so a
stale or unstated freshness yields to a lower-precedence layer rather than
winning on weak evidence. Every evidence gap on either side (`no
official_requirements supplied`, `no observed_patterns supplied`, `stale`)
surfaces as a `limitations` entry that survives the full handoff -- this
is the concrete contract asserted by `scholarly-agent-suite`'s
`tests/test_e2e_protocol_handoff.py`.
