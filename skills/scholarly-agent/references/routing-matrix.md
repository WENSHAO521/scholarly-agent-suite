# Routing matrix (heuristic, not rigid)

Which specialists a given user intent typically needs. "optional" means
invoke only if the request or context specifically calls for it; "maybe"
means invoke only if current/verifiable evidence is genuinely required;
"no" means do not invoke even if installed (rule 156: use the smallest
sufficient specialist set for the requested outcome).

| User intent | Router | Corpus Builder | Voice Engine | Journal Fit |
|---|---|---|---|---|
| Polish a paragraph | optional | no | yes | no |
| Draft an article | optional | maybe | yes | no |
| Literature review | optional | yes | yes | no |
| Find a journal | optional | maybe | no | yes |
| Adapt manuscript for a target journal | optional | maybe | yes | yes |
| Build an author voice profile | no | yes | yes | no |
| Book project | optional | yes | yes | no |
| End-to-end paper (idea to submission-ready) | yes, if available | yes | yes | optional |

## Negative examples (do not orchestrate)

These should resolve without invoking `scholarly-agent` at all -- either a
direct answer or a single specialist:

- "Fix this grammar." -- direct edit or scholarly-voice-engine alone.
- "What's a DOI?" -- direct answer, no Skill.
- "Format this citation in APA." -- direct answer or scholarly-voice-engine.
- "Translate this title into English." -- direct answer.
- "What does this term mean?" -- direct answer.

## Why Router is always "optional" here

adaptive-model-router governs *how* a stage executes (model selection,
delegation, validation depth) -- it is never itself the reason a workflow
needs multiple specialists, and it has no scholarly-domain judgment of its
own. Treat its presence as an execution-quality layer under whichever
specialists are already selected, not as a fifth workflow stage to schedule
(shared/capability-boundaries.md).

## Shared error taxonomy

Specialists and this orchestrator use these error/blocked labels
consistently so failures compose instead of needing per-pair translation:

`EVIDENCE_GAP`, `RETRIEVAL_FAILURE`, `TOOL_FAILURE`, `PROTOCOL_MISMATCH`,
`STALE_PROFILE`, `CITATION_UNVERIFIED`, `ARGUMENT_INCONSISTENCY`,
`JOURNAL_STATUS_UNVERIFIED`.

A `PROTOCOL_MISMATCH` (a producer emits a protocol version this orchestrator
or a consuming specialist does not recognize) is never guessed around --
report it plainly (rule 79, `shared/protocol-versioning.md`).
