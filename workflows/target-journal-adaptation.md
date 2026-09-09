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

## Implementation (as of journal-fit-engine v0.4.0 / Suite v1.2.0)

Stage 1 (`journal-fit-engine: confirm/refresh target journal profile`) now
has a real code path, not just a documented recipe step:
`jfe.target_journal_profile.build_target_journal_profile()` composes
already-computed `JournalEvidence`/`FitResult`/`APCClassification`/
`IndexingAssessment`/`IntegrityScreen` into a `TARGET_JOURNAL_PROFILE_V1`
envelope; `scholarly-agent`'s
`skills/scholarly-agent/scripts/target_journal_adapter.py` is the
consumer -- it validates the envelope, applies a **hard compatibility
gate** against the manuscript's own stated hard constraints
(`no_mandatory_apc`, `requires_indexing`), and returns one of `SELECTED` /
`REJECTED` / `NEEDS_VERIFICATION` plus the reasons, limitations, and
provenance that must survive downstream. A fact the profile could not
verify (unknown `apc_status`, a requested index absent from `indexing`) is
`NEEDS_VERIFICATION`, never a guessed pass or fail; a confirmed hard
mismatch (e.g. `apc_status: apc-required` against `no_mandatory_apc`) is
`REJECTED` and blocks the next stage entirely unless the user explicitly
overrides it. Stale profile evidence (`freshness: stale`) never silently
downgrades a `REJECTED` verdict back to selectable, but does force a
`SELECTED` verdict down to `NEEDS_VERIFICATION` whenever a hard constraint
actually depended on the stale fact.

Only a `SELECTED` (or user-overridden) profile proceeds:
`target_journal_adapter.journal_style_context_seed()` hands forward
exactly the identity, freshness, and provenance a
`JOURNAL_STYLE_CONTEXT_V1` build may safely reuse -- never
`fit_assessment`/`apc_status`/`oa_status`/`indexing`, which answer "is this
a plausible target?" and must never leak into "how should this manuscript
be written?" `official_requirements` and `observed_patterns` still come
from their own real sources (a host LLM's guideline fetch,
scholarly-corpus-builder), exactly as before.

The rest of the chain is unchanged: `jfe.style_context.build_journal_style_context()`
/ `from_journal_evidence()` produce the `JOURNAL_STYLE_CONTEXT_V1` envelope;
`scholarly-voice-engine`'s `scripts/voice/journal_context.from_journal_style_context_v1()`
/ `apply_journal_style_context()` consume it. `official_requirements`
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
`tests/test_e2e_protocol_handoff.py` (`TestE2E03`-`TestE2E06` for the
style-context leg, `TestE2E07`-`TestE2E12` for the target-profile leg and
the combined round trip).
