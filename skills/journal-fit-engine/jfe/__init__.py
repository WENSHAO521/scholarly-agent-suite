"""jfe -- reference implementation for journal-fit-engine's manuscript
profile, journal evidence lookup, hard filters, APC/OA classification, and
categorical fit model. Standard library only.

SKILL.md is the authoritative workflow a host/LLM follows; this package is
an optional, real, testable operationalization of the evidence-lookup and
mechanical-filter portions of that workflow (mirrors the relationship
between scholarly-corpus-builder's SKILL.md and its scb/ package). Nothing
here replaces the LLM's own judgment on soft fit, submission strategy, or
ethical boundaries.
"""
