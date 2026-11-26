# Workflow recipe: corpus-profile-build

**Not a Skill.** For a standalone request to build/refresh a
discipline/journal/historical-scholar profile with no writing or publication
task attached (used as a building block by several other recipes, and
directly when the user asks for just the profile).

## When to select this recipe

Trigger example: "Build a style profile of [discipline/journal/scholar] for
me to reference later."

## Stages

```
scholarly-corpus-builder only:
  source acquisition -> metadata -> OA resolution -> deduplication
  -> corpus construction -> style analytics -> profile compilation
  -> provenance record
```

No other specialist is invoked by default -- this recipe's entire deliverable
is a `SCHOLARLY_PROFILE_V1` (plus its `PROVENANCE_RECORD_V1`).

## Reuse rule

Before building, scholarly-agent should check whether a compatible profile
already exists for this exact target and is not `stale` (rule 47, rule 49).
If one exists and satisfies the request, return it instead of rebuilding.
