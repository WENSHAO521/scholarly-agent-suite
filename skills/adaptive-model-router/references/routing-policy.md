# Routing policy

Load for nontrivial selection, context management, repair, or escalation. The [kernel](../SKILL.md) owns execution boundaries; [records](records.md) defines optional records. Optimize expected total cost to validated success, including initial execution and expected repair, validation, delegation, and escalation. Use qualitative judgments when measurements are unavailable.

## Capability discovery and filtering

Inspect selectable IDs and per-model effort, tool, file/image, context, and dispatch support from the active tool contract or current provider documentation. Reuse inventory until a relevant change/failure. Exclude unavailable models, host/provider-deprecated models, and candidates lacking required capabilities before ranking. Unknown deprecation status is not verified current status. Explicit deprecated-model requests require disclosure and compliance with host restrictions; never select such models automatically.

Explicit available model choice overrides mode defaults. If unavailable, report it; continue only independent work on the active model and clarify when the choice is necessary. Never claim a substitute fulfilled the request. Do not send unsupported effort values. Choose a suitable supported level and disclose a material difference. No dispatch means active-model execution. On other providers, map capabilities to roles only with evidence; these rules do not imply Claude or Gemini can call OpenAI models.

| Policy role | Illustrative label | Intended work |
|---|---|---|
| Economical generalist | Luna | Metadata, filtering, simple extraction, tiny rewriting |
| Balanced generalist | Terra | Comparisons, repository discovery, literature extraction |
| Strong professional reasoner | Sol | Methods, difficult coding, architecture, demanding synthesis |
| Expert adjudicator | Astra | Material residual expert reasoning or explicit expert selection |

These are approximate preferences for GPT-5.6 Luna/Terra/Sol and GPT-6 Astra, not guaranteed rankings, prices, availability, or dispatch IDs. Resolve real IDs from inventory. Current capabilities, observed performance, and measured current prices override the illustrative ordering. Do not maintain a legacy fallback inventory. If GPT-5.6 is absent, use an available capable non-deprecated GPT-5-family candidate and record that fact. If no GPT-5-family dispatch is possible, the default GPT-6 gate cannot be fabricated: continue feasible active-model work or report the limitation.

## Cheap task vector

All dimensions use `low`, `medium`, or `high`; include all eight in formal records, but infer only what matters during routine execution. Context volume is relative to the host, not a universal token category.

| Dimension | Decision it changes |
|---|---|
| reasoning_complexity | Inference depth and initial tier/effort |
| error_impact | Severity and required checks |
| context_volume | Retrieval, reduction, input fit |
| tool_intensity | Tool capability and duplicate-tool cost |
| ambiguity | Resolve necessary assumptions |
| verification_difficulty | Executable/source checks or expert adjudication |
| parallelism | Whether independent bounded outputs exist |
| latency_sensitivity | Whether setup, effort, or parallelism pays off |

Do not add these into a complexity score or call a classifier for obvious work. High impact increases validation; high volume triggers context management. Neither alone licenses GPT-6.

## Policy modes

| Mode | Initial selection and reasoning | Expert policy |
|---|---|---|
| Economy | Prefer Luna/Terra; Sol if materially necessary for correctness. Avoid overhead. | GPT-6 disabled absent overriding explicit model instruction |
| Balanced (default) | Adapt model and effort to expected validated success. | Full gate required |
| Deep | Usually Sol for demanding work; high/xhigh/max where useful and supported. Stronger validation. | Full gate still required |
| Expert (explicit) | Direct Astra allowed when appropriate and dispatch exists. | No automatic repeated calls |

These names are unrelated to host UI speed settings. Explicit model choice overrides mode defaults; the latest explicit prohibition or spending constraint still applies. Clarify genuinely conflicting explicit instructions. Deep does not force Sol on trivial formatting. Expert permits a direct expert call, not mandatory use for unrelated cheap extraction.

## Context cost and utility gates

Before assembling large input, classify material as `required`, `supporting`, `redundant`, `historical`, or `irrelevant`. Send required and decision-relevant supporting evidence. Historical material becomes required if it establishes a live constraint or contradiction. Remove repetition/resolved details, not evidence that could reverse the conclusion.

Use runtime input counts or a labeled estimate; never present estimates as billable counts. Account for tool results, instructions, output headroom, and model limits. Unknown counts call for selective retrieval, not invented measurements.

| Approximate input warning | Default action |
|---|---|
| At least 200K tokens | Inspect whether all material is necessary |
| At least 220K tokens | Prefer retrieval, deduplication, selective reads, source-specific extraction |
| At least 250K tokens | Strongly attempt compaction before expensive synthesis |
| Near/above actual long-context pricing threshold | Avoid complete context unless correctness requires it |
| Approaching actual context limit, even below 200K | Reduce or partition before dispatch; never knowingly overflow |

These cumulative warnings are not universal context limits or price boundaries. Actual host/model documentation takes precedence. Full context is justified only when it fits and selective evidence loses necessary dependencies; state the tradeoff briefly. A paid long-context tier does not bypass a hard limit.

Use changed-section analysis, exact source locations, deduplicated excerpts, structured intermediate notes, evidence matrices, stable prompt prefixes, and caching where supported. Preserve exact constraints, IDs, citations, unresolved contradictions, and latest relevant state. Keep original pointers for checking summaries. Cache reuse is not guaranteed savings. Subagent distillation requires the delegation ROI gate. The skill cannot remove already injected context; reduce subsequent reads and dispatch packets.

## Model and effort selection

Choose a suitable capable tier first, then supported effort. A stronger first attempt can prevent repeated weaker failures. Before switching tiers for residual reasoning failure, ask whether more effort on the current capable model is efficient. Do not exhaust all effort levels; jump to a justified level or change tier when a concrete capability limitation makes more effort unhelpful.

Conceptual routes: Luna low → medium/high for still-simple work; Terra medium → high/xhigh for tractable analysis; Sol medium/high → xhigh/max for difficult residual reasoning. Levels such as none, low, medium, high, xhigh, max are examples only. Changing effort requires an actual supported subsequent dispatch, not a claim that the running turn changed settings.

## Objective validation and bounded repair

Choose the smallest meaningful checks; stop on sufficient success rather than purchase redundant review.

| Deliverable | Observable checks |
|---|---|
| Code | Relevant tests, lint/type/schema checks, build, runtime behavior, diff review |
| Academic work | Source existence, identifier match, claim support, methods consistency, provenance, journal requirements, statistical assumptions |
| Document | Completeness, exact user constraints, factual consistency, formatting/rendering when layout matters |
| Data | Schema, counts, missingness, calculations, reproducibility, leakage |

Use the kernel's six states. A critical failure cannot become PASS_WITH_LIMITATIONS merely to stop repairs. That state describes a useful bounded deliverable with noncritical limitations, not an unfulfilled core requirement. If checks cannot run, preserve the actual blocker rather than substitute confidence.

Failure types: `none`, `reasoning`, `retrieval`, `tool`, `permission`, `context_overflow`, `instruction_mismatch`, `evidence_gap`, `implementation`, `validation`, `unknown`.

| Cause | Next action |
|---|---|
| reasoning | Repair exact logic gap; consider same-model higher effort, then stronger GPT-5-family tier |
| retrieval / evidence_gap | Retrieve/verify missing source; if absent, BLOCKED_BY_MISSING_EVIDENCE |
| tool / permission | Repair workflow or obtain required authorization; if blocked, BLOCKED_BY_TOOL_FAILURE with precise cause |
| context_overflow | Selectively retrieve, compact, or partition; recheck fit |
| instruction_mismatch | Reapply exact constraint to affected output |
| implementation | Fix defect and rerun failing check |
| validation | Investigate failing/inadequate check before blaming reasoning |
| unknown | Diagnose; do not escalate unidentified causes |
| none | Deliver when required checks pass |

An invalid assumption is instruction_mismatch if it contradicts user constraints, evidence_gap if unsupported, or reasoning if inference contradicts evidence. Reclassify implementation/validation failure as reasoning only with evidence.

Normally at most two targeted GPT-5-family repair cycles across agents, models, and effort changes; switching tiers does not reset the counter. Each targets a residual defect and reruns relevant checks. Do not redo the whole task. This limits repeated model repair, not the initial multi-step workflow or independent necessary tool operations. At exhaustion use the expert gate only for qualifying reasoning failure; otherwise report the unmet requirement and cause. Two failed retrieval attempts do not turn missing evidence into reasoning failure.

## GPT-6 gate and call budget

Except explicit available GPT-6 selection or explicit Expert mode, require all:

1. Confirmed GPT-5-family execution, preferably GPT-5.6 when available.
2. Meaningful validation against a material requirement.
3. Concrete unresolved reasoning failure.
4. Targeted repair and revalidation.
5. Evidence or a capability-based reason further GPT-5.6 effort/tier changes are inefficient, plus a specific expected expert benefit.

Examples: unresolved critical contradiction, repeated logical failure, competing plausible expert solutions, reasoning-caused executable failure, or severe architectural uncertainty tested against concrete constraints. Mark ESCALATION_CANDIDATE, then check authorization, mode, inventory, context fit, and remaining budget. Length, file/citation count, requested detail, missing evidence, tool errors, and self-assigned scores are insufficient.

Default maximum: one successful Astra dispatch across root/leaves per user task; returned but invalid output still consumed a successful dispatch. One additional attempt is eligible only for invalid expert output, tool execution failure, materially new evidence, or explicit instruction. Absent an explicit larger budget, cap total expert attempts at two including failed dispatches; the exception is not renewable. Failed transport counts as an attempt, not successful output. Tool failure alone never authorizes a first GPT-6 call. Stop repeated unavailable infrastructure; no GPT-6 self-review loop. Explicit choice bypasses the reasoning gate, not permissions/capability checks.

Send only a residual-question packet: objective, latest state, exact constraints/IDs/source pointers, previous GPT-5 result, validation evidence, failed repairs, unresolved issue, required output. Preserve uncertainty and conclusion-changing evidence. Root checks the result against the same acceptance criteria.

## Examples (conditional preferences)

| Task | Route and check |
|---|---|
| Short email rewrite/translation | Luna low/medium if dispatch is appropriate; otherwise active model, zero subagents, instruction check; no router overhead if not active |
| Standard research comparison | Terra medium, retrieve relevant evidence, verify claims; Sol only for synthesis limitations |
| Ordinary academic wording edit | Luna low/medium, preserve meaning/citations; no research orchestration |
| Advanced methodology/manuscript methods | Sol medium/high, paper workflow, identification checks; xhigh for residual issues |
| Difficult debugging | Sol high, run failing tests, targeted higher-effort repair; Astra only for surviving reasoning failure |
| Large repository analysis | Context gate, selective reads, optional ROI-positive Terra exploration, appropriate Sol integration, tests/build |
| Unresolved architecture | Sol high, constraint checks fail, xhigh/max targeted repair inconclusive; expert adjudication may qualify |

These are policy expectations, not measured model quality or dispatch promises.
