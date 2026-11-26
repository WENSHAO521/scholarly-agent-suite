"""Small stdlib-only helper modules operationalizing this Skill's reference
docs: profile_schema (shape validators), profile_merge (precedence
resolution), continuity (long-form ledger), audit (prose heuristics).

These are deliberately lightweight — they exist to make the rules in
references/*.md testable and reusable, not to reimplement them as a parallel
system of record. See references/quality-and-editing.md#quality-audit and
references/integration.md#corpus-profile-integration for the authoritative rules.
"""
