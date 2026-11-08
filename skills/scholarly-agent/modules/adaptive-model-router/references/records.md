# Routing and evaluation records

Record observable decisions and evidence, not private deliberation. Logging is optional; avoid telemetry for tiny work. Unknown values are null, not fabricated zeros. Do not write persistent user memory without explicit authorization.

## Routing record

```json
{
  "task_type": "methods_revision",
  "mode": "Balanced",
  "task_vector": {
    "reasoning_complexity": "high",
    "error_impact": "high",
    "context_volume": "medium",
    "tool_intensity": "medium",
    "ambiguity": "high",
    "verification_difficulty": "high",
    "parallelism": "low",
    "latency_sensitivity": "low"
  },
  "available_models": [],
  "dispatch_available": null,
  "selected_model": null,
  "actual_model": null,
  "reasoning_effort": null,
  "context_tokens": null,
  "context_tokens_estimated": null,
  "context_strategy": null,
  "delegation": {
    "eligible": false,
    "expected_benefit": null,
    "attempted": false,
    "count": 0,
    "roles": [],
    "integration_status": "skipped"
  },
  "validation_state": null,
  "validation_evidence": [],
  "failure_type": null,
  "failure_detail": null,
  "repair_cycles": 0,
  "gpt6_eligible": false,
  "gpt6_reason": null,
  "gpt6_attempts": 0,
  "gpt6_successful_dispatches": 0,
  "unresolved_limitations": []
}
```

This is a pre-execution example, not evidence a model ran. All vector values use low/medium/high. Available models are runtime-confirmed IDs; empty means no confirmed candidates recorded, not proof no models exist. Selected is a proposal; actual requires execution evidence. Effort records only supported settings, not an imaginary mid-turn switch.

Context strategy describes selective reads, compaction, partitioning, or a justified complete input. Preserve original pointers and label token estimates. Delegation count includes all spawned agents in the one wave; distinguish eligibility, attempts, and completed integration. Integration status: skipped, delegated, completed, failed. Root and worker repairs/calls share task-wide budgets.

## Validation and failure

States and transitions are defined in the [kernel](../SKILL.md) and [routing policy](routing-policy.md): PASS, PASS_WITH_LIMITATIONS, REPAIR_REQUIRED, BLOCKED_BY_MISSING_EVIDENCE, BLOCKED_BY_TOOL_FAILURE, ESCALATION_CANDIDATE. Null means not evaluated. Record the check, observed outcome, exact source/artifact location, and remaining unmet requirement. A blocked check is not a passed check.

Failure types: none, reasoning, retrieval, tool, permission, context_overflow, instruction_mismatch, evidence_gap, implementation, validation, unknown. Use failure_detail for invalid assumptions and secondary causes; see routing policy for repair mapping. Missing permission uses BLOCKED_BY_TOOL_FAILURE plus permission as the cause. A critical error blocks both clean PASS and an attempt to relabel incomplete core work as PASS_WITH_LIMITATIONS.

`gpt6_reason` uses only the [escalation reason codes](routing-policy.md#escalation-reason-codes) (REASONING_FAILURE, EVIDENCE_GAP, TOOL_FAILURE, CONTEXT_LIMIT, VALIDATION_FAILURE, USER_EXPERT_REQUEST); it is a coarser, escalation-specific label, not a second copy of the failure types above.

No quality-score thresholds, confidence probabilities, allocation quotas, or necessity scores govern escalation.

## Optional measured telemetry

When runtime measurements exist, collect tasks by model, attempts/successes, repair rate/success, escalation and delegation rate, GPT-6 rescue rate, cached/input/output tokens, and approximate cost using current actual pricing. Document sample size and denominators. Count a rescue only when a previously failing result passes the same meaningful check after escalation; this does not prove the expert model was uniquely necessary.

Cost per successfully validated task is total measured execution, repair, validation, delegation, and escalation cost for the cohort (including failed tasks) divided by tasks reaching PASS under the declared acceptance criteria. Report PASS_WITH_LIMITATIONS separately unless a different success definition was declared before evaluation. Missing costs or zero validated successes make that metric unavailable. Include cache and context pricing rules when known. Never infer exact usage from prose length or claim savings without a comparable baseline.

## Task state (reuse before recompute)

Compact rolling state one task may carry across its own steps/turns so already-done work is reused instead of recomputed. This is task-scoped bookkeeping, not long-term user memory; discard it when the task ends unless the host has its own persistence with explicit authorization.

```json
{
  "objective": "",
  "completed_stages": [],
  "files_read": [],
  "sources_verified": [],
  "reusable_results": [],
  "failed_attempts": [],
  "unresolved_issues": []
}
```

Populate only fields that matter for the current task; omit rather than fabricate. `sources_verified` holds `source_key` values from [paper evidence records](#paper-evidence-records) rather than duplicating them. `failed_attempts` records cause (a failure type above) and what was tried, for repair-cycle accounting, not blame. `reusable_results` are prior task-scoped outputs (a retrieval, a computed diff, a passed check) safe to reuse verbatim while their inputs are unchanged; drop or recompute an entry the moment its input changes. Prefer pointers to originals over inlined content, and remove resolved entries rather than accumulate history.

## Paper evidence records

```json
{
  "source_key": "",
  "title": "",
  "authors": [],
  "year": null,
  "venue": null,
  "identifiers": {"doi": null, "arxiv": null, "openalex": null},
  "version_status": "unknown",
  "source_url": null,
  "checked_at": null,
  "claims_supported": [],
  "evidence_locations": [],
  "access_status": "unknown",
  "license": null,
  "verification": "needs-check",
  "notes": ""
}
```

Retain exact checked title/authors/year/venue/IDs, version and provenance. A verified source needs a checked record and a source-backed evidence location. A needs-check source must not support a final material claim. Keep bibliographic verification separate from checking whether full text supports a claim.

Claim matrix fields: claim, section, source_key_or_result, evidence_location, strength, caveat, repair_action. Distinguish reproduced results, source-reported results, and proposed experiments. Paper phase can be discovery, outline, drafting, revision, submission; branch can be ordinary, empirical, systematic_review, sentence_polishing. See [paper workflow](paper-workflow.md).

## Evaluation fixture contract

Each JSONL line is one independent policy scenario with unique id, task, context, expect, and rationale. Context states relevant inventory/dispatch assumptions, evidence, budget, and task state. Unless overridden in context, fixtures assume Balanced mode, all four illustrative roles available and non-deprecated with the stated supported effort, valid tool capability, no previous calls, no explicit model choice, and no delegation benefit. These are fictional test conditions, not claims about a real host.

- Routing: expect contains gpt6 (boolean), delegation (boolean), tier_ceiling (Luna/Terra/Sol/Astra/active), context_strategy (direct/inspect/selective/compact/partition), and action.
- Delegation: expect contains delegation (boolean), max_agents (0–3), and write_policy (none/read_only/isolated).
- Escalation: expect contains gpt6 (boolean), action, and validation_state (one of the six states).
- Actions: execute, stay_active, report_unavailable, repair, raise_effort, escalate_tier, retrieve, fix_tool, request_permission, reduce_context, expert_dispatch, report_limitations.

For routing, gpt6 means permission for a next GPT-6 dispatch in the scenario, not a requirement or a successful call. Tier ceilings assume capable candidates; active means no dispatch. For escalation, validation_state describes the current observed deliverable, not a prediction of a future call's success. Explicit expert choice can allow dispatch without labeling an unvalidated deliverable ESCALATION_CANDIDATE.

The validator checks file/schema/link integrity and obvious expectation consistency. It does not execute a router or grade a live model. To evaluate behavior, give a host the task and context plus this skill, hide expect/rationale, record its actual decision and evidence, and compare against the fixture. Report policy agreement separately from objective output quality, latency, and measured cost. Use isolated artifacts and authorized dispatch; no benchmark has been run merely by parsing these fixtures.
