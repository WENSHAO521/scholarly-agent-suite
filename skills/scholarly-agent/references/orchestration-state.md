# Orchestration state, freshness, and the final quality gate

## States

Use exactly these workflow states -- do not invent synonyms:

`PLANNED`, `IN_PROGRESS`, `COMPLETE`, `COMPLETE_WITH_LIMITATIONS`,
`BLOCKED_BY_EVIDENCE`, `BLOCKED_BY_TOOL`.

Never report `COMPLETE` when a required specialist failed, returned
`PARTIAL`, or left an unresolved integrity flag -- use
`COMPLETE_WITH_LIMITATIONS` instead (rule 45, rule 73).

## Task-local workflow state shape

```json
{
  "goal": "",
  "active_workflow_recipe": "",
  "completed_stages": [],
  "active_stage": "",
  "artifacts": {
    "corpus_profile_id": null,
    "manuscript_profile_id": null,
    "journal_profile_id": null,
    "continuity_state_id": null
  },
  "hard_constraints": [],
  "soft_preferences": [],
  "open_issues": [],
  "limitations": []
}
```

This is scratch state for the current task, not a persistent user memory
system (rule 46, rule 130). Do not add task boards, dashboards, or
scheduling beyond this shape (rule 130).

## Freshness handling

Respect a component's own `freshness` label (`current` / `aging` / `stale`)
on any profile it returns:

- A `stable`/`current` historical or discipline profile does not need a
  refresh just because time has passed.
- A `stale` journal profile *does* need a refresh if the current request
  depends on a fact that changes over time (APC policy, indexing status,
  submission requirements) -- rule 49.
- Do not call scholarly-corpus-builder "just in case" for a request that
  does not need current external evidence (rule 50) -- e.g. a plain
  paragraph rewrite never triggers a corpus refresh.

## Final quality gate (check before COMPLETE)

1. The requested final deliverable actually exists.
2. Required evidence was verified, or its absence is declared as a
   limitation -- never silently assumed complete (rule 74).
3. Argument integrity passed (no unresolved `ARGUMENT_INCONSISTENCY`).
4. No fabricated or unverified-but-unlabeled citations
   (`shared/integrity-policy.md`).
5. Journal claims are current where the request depended on currency, or
   labeled `JOURNAL_STATUS_UNVERIFIED` otherwise.
6. All component outputs consumed used a protocol version this Suite
   supports (`COMPONENTS.json` -> `protocol_versions`); any
   `PROTOCOL_MISMATCH` blocks `COMPLETE`.

If any check fails, use `COMPLETE_WITH_LIMITATIONS` (checks 2-5 recoverable
via a stated limitation) or a `BLOCKED_BY_*` state (check 1 or 6 unmet).

## Bounded repair

At most one main adaptation cycle plus one targeted repair pass per
workflow run. If a second repair pass would be needed, stop and report the
remaining issue to the user rather than continuing to cycle specialists
against each other (rule 107).

## Human decision points

Pause for user input before proceeding on genuinely divergent, hard-to-reverse
choices -- e.g. two materially different journal-strategy options, a book's
overall architecture, or whether to apply a high-strength author-voice
calibration. Do not pause for routine, easily-inferred defaults; over-asking
defeats the point of orchestration (rule 108-109).
