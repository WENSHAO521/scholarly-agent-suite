# Workflow recipe: paper-from-idea

**Not a Skill.** A recipe scholarly-agent may follow when the deliverable is
an end-to-end journal article starting from a research idea, not a finished
manuscript.

## When to select this recipe

Trigger example: "Help me turn this idea into an SSCI paper."
Not for: a one-step edit, a single paragraph rewrite, or a request that
already supplies a full manuscript (use `revise-manuscript.md` instead).

## Stages

```
interpret research idea
  |
  v
scholarly-corpus-builder            (only if evidence is actually needed --
  retrieve/verify evidence           see rule 50; skip for a purely
                                      theoretical/opinion piece)
  |
  v
scholarly-voice-engine
  research question + argument architecture
  |
  v
draft manuscript  (VOICE_OUTPUT_V1)
  |
  v
journal-fit-engine                  (optional -- only if the user asked
                                      "where should this go" too)
  |
  v
target adaptation (scholarly-voice-engine, journal_style_context attached)
```

adaptive-model-router, where active, may manage execution/delegation/
validation throughout (it is never a required stage by itself).

## Components skipped by default

- journal-fit-engine, unless the user asked for a venue recommendation as
  part of the same request.
- Continuity state (`CONTINUITY_STATE_V1`) -- book-only, not used here.

## Artifacts produced

`research_brief` -> `corpus_profile` (optional) -> `voice_context` ->
`draft_manuscript` -> `journal_shortlist` (optional) -> `target_adaptation`
(optional).

## Completion states

`COMPLETE` only if every requested artifact exists and passed the final
quality gate (rule 106). If evidence retrieval failed but the draft is
otherwise sound, report `COMPLETE_WITH_LIMITATIONS`, not `COMPLETE`.
