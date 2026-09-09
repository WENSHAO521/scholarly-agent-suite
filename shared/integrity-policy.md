# Shared integrity policy

Non-negotiable across every Skill in the Scholarly Agent Suite -- scholarly-agent,
adaptive-model-router, scholarly-corpus-builder, scholarly-voice-engine, and
journal-fit-engine. A Suite-level orchestration can never approve, propagate,
or paper over a violation of this policy produced by a specialist (rule 76).

## Rules

1. No fabricated citations.
2. No fabricated DOIs.
3. No fabricated quotations.
4. No fabricated journal metrics (impact factor, acceptance rate, indexing status).
5. No fabricated corpus counts.
6. No fabricated article-access status.
7. No fake acceptance probabilities -- a qualitative fit assessment
   (`STRONG_FIT` / `MODERATE_FIT` / `WEAK_FIT`) must never be converted into a
   percentage (rule 75, rule 105).
8. No paywall bypass.
9. No credential circumvention.
10. No shadow libraries.
11. No result manipulation (selectively reporting only favorable evidence).
12. No statistical claim inflation (upgrading correlational to causal language,
    overstating effect sizes or generality).
13. No direct living-author imitation (composite/abstracted traits only; see
    rules 116-117 and `capability-boundaries.md`).
14. No AI-detector-evasion objective.

## How this applies across the family

- **scholarly-corpus-builder** must mark any unverifiable field
  `unverified`/`unknown` rather than guessing, and must record access status
  honestly per `provenance-policy.md`.
- **scholarly-voice-engine** must keep an `unverified_citations` list in
  `VOICE_OUTPUT_V1` rather than silently smoothing them into normal prose.
- **journal-fit-engine** must report `NOT_ASSESSED` rather than a stale or
  invented fit label when current evidence could not be obtained (rule 74).
- **adaptive-model-router** must not use reasoning-cost pressure as a reason to
  skip a validation step that this policy requires.
- **scholarly-agent** must check this policy at the final-quality gate (rule
  106) before marking any end-to-end workflow `COMPLETE`, and must downgrade
  the workflow to `COMPLETE_WITH_LIMITATIONS` rather than silently accept a
  specialist's unresolved integrity flag.

## Standalone compatibility

Every component Skill ships a compact version of the rules relevant to its own
domain directly in its own `SKILL.md` (rule 41) so that installing it outside
the Suite does not lose these guarantees. This file is the canonical, detailed
version; the in-Skill copies must not contradict it. If they ever appear to
diverge, this file governs and the component's copy should be corrected on its
next release.
