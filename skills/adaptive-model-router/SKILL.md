---
name: adaptive-model-router
description: Apply cost-aware model routing for model selection, multi-stage research, large-context analysis, complex coding, evidence-intensive academic work, and difficult validation or repair. Use bounded delegation and controlled expert escalation when the host supports dispatch; ordinary tiny writing tasks do not need this workflow.
---

# Adaptive Model Router

Minimize expected total cost to a successfully validated task, including execution, repair, validation, delegation, and escalation. A stronger first attempt can be cheaper than repeated failed cheap attempts. This is a policy heuristic, not a numerical optimizer or savings guarantee.

## Execution boundary

Inspect the actual dispatch surface for available, non-deprecated model IDs, supported reasoning levels, tools, file/image capabilities, context limits, collaboration slots, and write isolation. Reuse known inventory until it changes. Unknown support or pricing is not confirmed capability or cost. A UI model label does not prove subagent dispatchability.

Honor explicit user model choice where available and permitted. Report unavailable choices rather than silently substituting. Never automatically select deprecated models. Host rules, permissions, and explicit no-delegation requests take precedence. Never create a user-visible task merely to switch models.

Without dispatch, perform feasible work on the active model; mention the limitation only when material. Never simulate another model's attempt. This skill cannot switch the current turn, erase injected context, enforce billing limits, or guarantee host invocation. Automatic discovery remains enabled for the described scope; tiny tasks already in progress need only a direct answer and an instruction check.

## Routing kernel

Use only steps that can change the decision. For detailed selection or a residual failure, read [routing-policy.md](references/routing-policy.md).

1. **Choose policy:** `Balanced` by default; `Economy` avoids expert use, `Deep` permits stronger initial reasoning, and explicitly selected `Expert` permits direct expert use. Explicit model choice overrides mode defaults within host constraints. Detail alone is not Expert mode.
2. **Gate context:** retain required and useful supporting evidence; omit redundant, historical, or irrelevant material unless it affects the answer. Preserve exact constraints, identifiers, citations, contradictions, and latest state. Around 200K/220K/250K input tokens, respectively inspect necessity, prefer selective retrieval, and strongly attempt compaction. These are warning heuristics; actual context limits and pricing thresholds take precedence. Never discard conclusion-changing evidence.
3. **Classify cheaply:** infer `reasoning_complexity`, `error_impact`, `context_volume`, `tool_intensity`, `ambiguity`, `verification_difficulty`, `parallelism`, and `latency_sensitivity` as low/medium/high. No classifier call for obvious work.
4. **Select model, then effort:** choose the least costly capable candidate for validated success; select a supported reasoning level separately. Luna/Terra/Sol/Astra are policy-role examples, not an inventory or verified price list. Jump to suitable effort without walking every tier.
5. **Gate delegation:** default to zero agents. Read [delegation-policy.md](references/delegation-policy.md) only for separable work with a concrete expected benefit over coordination and duplicate retrieval/context cost. Use 0–2 leaf agents, exceptionally 3, within available slots and one wave. Read-only by default; one writer per file and confirmed isolation for parallel implementation. Root integrates and validates.
6. **Execute and validate:** select checks tied to the deliverable and risk. Record evidence, not an invented probability. A critical failure blocks a clean `PASS`.
7. **Repair the residual:** classify its cause before buying more reasoning. Normally at most two targeted GPT-5-family repair cycles, each followed by relevant validation. For reasoning failure, consider higher supported effort on the same capable model before moving up a tier. Skip unhelpful intermediate levels. Missing sources, tool/permission failures, and context overflow need source/workflow/context repair.
8. **Expert gate:** except explicit GPT-6 or Expert selection, require a real GPT-5-family attempt, meaningful validation, a concrete material reasoning failure, targeted repair, and a reason further GPT-5.6 effort is inefficient. Eligibility is not a mandatory call. Default maximum: one successful Astra dispatch per task; one additional attempt only for invalid expert output, tool execution failure, materially new evidence, or explicit instruction. Count attempts separately and stop repeated infrastructure failures. No GPT-6 self-review loop.
9. **Deliver:** stop when required checks pass. State material unresolved limitations; do not conceal blocked evidence or claim unperformed validation.

## Validation states

- `PASS`: required checks passed with recorded evidence.
- `PASS_WITH_LIMITATIONS`: useful output meets its stated scope with noncritical limitations disclosed.
- `REPAIR_REQUIRED`: a concrete defect remains; fix it before claiming completion.
- `BLOCKED_BY_MISSING_EVIDENCE`: a required source, input, or observation is absent.
- `BLOCKED_BY_TOOL_FAILURE`: tools or permissions prevent a required check/action; preserve the precise cause.
- `ESCALATION_CANDIDATE`: a material reasoning failure meets the expert gate; budget and dispatch still apply.

## Load only relevant detail

- [Paper workflow](references/paper-workflow.md): evidence-intensive manuscripts, methods, empirical studies, or reviews. Preserve the ordinary, empirical, systematic-review, and bounded sentence-polishing branches; never fabricate sources or results.
- [Records](references/records.md): compact decisions, failure taxonomy, source provenance, and telemetry when requested or operationally useful. Do not generate logs for tiny tasks or write persistent user memory without explicit authorization.

Describe observable decisions and validation evidence; do not expose private deliberation.
