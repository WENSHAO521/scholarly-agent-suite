"""adaptive-model-router is platform-neutral (v2.1.0).

Its routing roles (Luna/Terra/Sol standard tier, Astra expert tier) map onto
whatever models the host exposes. Before v2.1.0 the module hard-coded
"GPT-5-family" and "GPT-6" into its gates and eval keys, so its rules read as
OpenAI-only on Claude, Gemini, or local hosts. These tests keep provider
model names out of the policy and check the eval fixture contract that
references/records.md defines."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MODULE_DIR = ROOT / "skills" / "scholarly-agent" / "modules" / "adaptive-model-router"
EVALS_DIR = ROOT / "evals" / "modules" / "adaptive-model-router"

VALIDATION_STATES = {
    "PASS", "PASS_WITH_LIMITATIONS", "REPAIR_REQUIRED",
    "BLOCKED_BY_MISSING_EVIDENCE", "BLOCKED_BY_TOOL_FAILURE", "ESCALATION_CANDIDATE",
}
ACTIONS = {
    "execute", "stay_active", "report_unavailable", "repair", "raise_effort",
    "escalate_tier", "retrieve", "fix_tool", "request_permission",
    "reduce_context", "expert_dispatch", "report_limitations",
}
EXPECT_KEYS = {
    "routing-cases.jsonl": {"expert_dispatch", "delegation", "tier_ceiling", "context_strategy", "action"},
    "delegation-cases.jsonl": {"delegation", "max_agents", "write_policy"},
    "escalation-cases.jsonl": {"expert_dispatch", "action", "validation_state"},
}


def rows(name):
    path = EVALS_DIR / name
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_policy_text_names_no_provider_model_generation():
    pattern = re.compile(r"\bGPT-\d|\bgpt\d|\bgpt_?\d", re.I)
    hits = []
    for path in list(MODULE_DIR.rglob("*.md")) + list(EVALS_DIR.glob("*.jsonl")):
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if pattern.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{i}")
    assert not hits, "provider-specific model generations in router policy:\n" + "\n".join(hits)


def test_platform_mapping_covers_common_hosts():
    text = (MODULE_DIR / "references" / "routing-policy.md").read_text(encoding="utf-8")
    assert "### Platform mapping" in text
    for host in ("OpenAI / Codex", "Anthropic Claude", "Google Gemini", "Open-weight / local", "Single-model host"):
        assert f"| {host}" in text, host
    module = (MODULE_DIR / "MODULE.md").read_text(encoding="utf-8")
    assert "references/routing-policy.md#platform-mapping" in module


def test_eval_fixtures_follow_the_records_contract():
    seen = set()
    for name, keys in EXPECT_KEYS.items():
        for row in rows(name):
            assert {"id", "task", "context", "expect", "rationale"} <= row.keys(), row.get("id")
            assert row["id"] not in seen, row["id"]
            seen.add(row["id"])
            expect = row["expect"]
            assert set(expect) == keys, f"{row['id']}: {sorted(expect)}"
            if "action" in expect:
                assert expect["action"] in ACTIONS, row["id"]
            if "validation_state" in expect:
                assert expect["validation_state"] in VALIDATION_STATES, row["id"]
            if "tier_ceiling" in expect:
                assert expect["tier_ceiling"] in {"Luna", "Terra", "Sol", "Astra", "active"}, row["id"]
            if "max_agents" in expect:
                assert 0 <= expect["max_agents"] <= 3, row["id"]


def test_expert_dispatch_never_paired_with_unrepaired_reasoning_failure():
    """Obvious-consistency check the records contract promises: a routing
    scenario that allows an expert dispatch must either be an explicit
    expert request or end in the expert_dispatch action."""
    for row in rows("routing-cases.jsonl"):
        if row["expect"]["expert_dispatch"]:
            ctx = row["context"]
            assert ctx.get("explicit_model") == "Astra" or ctx.get("mode") == "Expert" \
                or row["expect"]["action"] == "expert_dispatch", row["id"]
