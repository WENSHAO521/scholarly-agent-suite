# Delegation policy

Read only for independently useful outputs. Complexity alone is insufficient. The [routing policy](routing-policy.md) governs model/effort selection and task-wide budgets.

## Positive expected value gate

Delegate only when all conditions hold:

- Authorized collaboration, free slots, and a bounded separable task exist; root has useful concurrent work. Independent validation must also fit host delegation rules.
- Saved work/latency, context reduction, or material independent validation outweigh setup, duplicated input tokens, tools/retrieval, and integration cost.
- Duplicate searches or paid-tool calls are acceptable and minimized with shared source pointers/results.
- Work does not depend on unresolved root decisions.
- Write conflicts are controlled and the user has not prohibited delegation.

Use a short qualitative judgment, not a classifier call or invented ROI percentage. Uncertain/negligible benefit means local work. Economy needs especially clear benefit. A paragraph rewrite, an indivisible proof, or two agents searching the same citations generally fails this gate.

## Caps and isolation

Default 0–2 subagents; exceptionally 3 for distinct demonstrably valuable roles. Never exceed currently free child slots (exclude root if the host reports total slots). Count all spawned agents for the task, including failed/cancelled ones. One wave: select roles once; later repairs are local or integrate existing findings. No replacement waves to bypass caps.

Delegated agents are leaves: no recursive delegation or new routing orchestration. They can apply assigned validation locally. Send minimal packets, not full history. Unavailable collaboration means single-agent work, not simulated delegation.

Read-only by default. One writer per file at a time. Parallel implementation requires confirmed separate worktrees, isolated branch checkouts, or equivalent filesystem isolation; two branch names sharing one working directory are not isolation. Assign bounded ownership, keep shared files with root, and integrate sequentially. Without isolation, workers propose edits and root writes. Root owns final integration and acceptance checks.

## Role assignment

| Independent role | Illustrative tier |
|---|---|
| Metadata filtering, simple extraction | Luna |
| Large-document scan, literature extraction | Terra |
| Repository exploration, test triage | Terra |
| Critical methods review, architecture review | Sol |
| Root synthesis/integration | Strongest appropriate capable tier |

Resolve supported IDs/effort from runtime inventory. Do not spend Sol/Astra on cheap extraction by default. Worker repairs and expert calls count against the same user-task budgets; reserve expert dispatch authorization for root.

## Minimal task packet

```text
OBJECTIVE: one bounded question or deliverable
RELEVANT INPUT: selected evidence and current state
CONSTRAINTS: acceptance criteria, read-only/isolated ownership, no delegation
SOURCE POINTERS: exact paths, URLs, IDs, reusable retrieval results
EXPECTED OUTPUT: concise findings, evidence locations, checks performed, unresolved issues
```

Preserve exact identifiers, constraints, and conclusion-changing evidence. Summaries point to originals. Distinct search/ownership boundaries prevent duplicate retrieval or editing.

## Integration

Workers return provenance, actual checks, authorized changed paths, and limitations. Root verifies material findings, resolves disagreements against originals/executable checks, applies changes, and validates the combined output. Do not majority-vote factual truth. Report failed/unavailable worker results accurately and continue feasible local work. Stop when acceptance criteria pass; a wave does not require another review call.
