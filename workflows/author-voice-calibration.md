# Workflow recipe: author-voice-calibration

**Not a Skill.** For building/using a profile of the user's own authorized
writing so future output sounds like them.

## When to select this recipe

Trigger example: "Use my previous papers to make new writing sound like me."

## Stages

```
scholarly-corpus-builder: author profile
  (SCHOLARLY_PROFILE_V1, profile_type=author-voice, built only from the
   user's own authorized writing -- see rule 117)
  |
  v
scholarly-voice-engine: author voice calibration
  (VOICE_CONTEXT_V1.author_voice populated from the profile;
   composite/abstracted traits, not verbatim-text cloning)
```

adaptive-model-router and journal-fit-engine are not part of this recipe.

## Authorization boundary

This is explicitly *not* treated as third-party living-author imitation
(rule 117) -- it requires the writing to be the user's own or otherwise
authorized. If authorization is unclear (e.g. co-authored work, or writing
attributed to someone else), scholarly-agent must surface that ambiguity
rather than silently proceeding (rule 116, `shared/integrity-policy.md` rule
13).

## Privacy

The resulting author profile is user-specific and must not be committed into
this repository as a fixture; see `shared/provenance-policy.md` and rule 113.
