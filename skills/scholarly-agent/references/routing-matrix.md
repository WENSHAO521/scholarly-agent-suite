# Routing matrix (heuristic, not rigid)

Which specialists a given user intent typically needs. "optional" means
invoke only if the request or context specifically calls for it; "maybe"
means invoke only if current/verifiable evidence is genuinely required;
"no" means do not invoke even if installed (rule 156: use the smallest
sufficient specialist set for the requested outcome).

| User intent | Router | Corpus Builder | Voice Engine | Journal Fit | Peer Review | Polish |
|---|---|---|---|---|---|---|
| Light edit of a paragraph (wording, clarity) | optional | no | yes | no | no | no |
| Draft an article | optional | maybe | yes | no | no | no |
| Literature review | optional | yes | yes | no | no | no |
| Find a journal | optional | maybe | no | yes | no | no |
| Adapt manuscript for a target journal | optional | maybe | yes | yes | no | no |
| Build an author voice profile | no | yes | yes | no | no | no |
| Book project | optional | yes | yes | no | no | no |
| End-to-end paper (idea to submission-ready) | yes, if available | yes | yes | optional | optional | optional (final pass) |
| Pre-submission peer review / editorial decision | optional (subagent dispatch) | no | no | maybe | yes | no |
| Peer review, then revise and write the response letter | optional (subagent dispatch) | maybe | yes | maybe | yes | optional (final pass) |
| Import or export a Zotero / BibTeX / RIS library | no | yes | no | no | no | no |
| Polish (潤色) finished text so it no longer reads templated or machine-made, any language | no | no | no | no | no | yes |
| Polish, and the diagnosis shows the argument itself needs work | optional | no | yes (escalations) | no | no | yes |

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

## Workflow-resolution error taxonomy

Separate from the specialist error taxonomy above: failures to locate a
*workflow recipe file itself* (`references/workflows/*.md`) use their own
three-way classification, never a generic "missing" message. This exists
because of a real incident where a workflow recipe present in the
repository and in the release tag was reported as missing from an install
that had never actually been inspected:

- `WORKFLOW_SOURCE_MISSING` -- the requested name is not a workflow recipe
  this orchestrator has ever declared. A genuine "does not exist" case;
  safe to report immediately, no runtime inspection required.
- `WORKFLOW_RUNTIME_MISSING` -- the recipe is real and declared, this
  Skill's own `references/workflows/` directory was successfully located
  and read, and the specific file is confirmed absent from it. This is the
  *only* condition that may be reported as "the installed package is
  missing `<file>`" -- because it is the only one that actually inspected
  the runtime before saying so.
- `WORKFLOW_UNRESOLVABLE` -- `references/workflows/` could not be located
  or read at all under the given install root (wrong root, absent
  directory, permission error). Report this as a runtime-resolution /
  installation-visibility problem. Repository or tag metadata confirming
  the workflow exists is never overridden by a lookup that never
  successfully inspected the runtime -- an unresolvable lookup is not
  evidence of absence.

See `skills/scholarly-agent/scripts/workflow_resolver.py` for the concrete
implementation and SKILL.md's "Resolving a workflow recipe file" section
for when to use it.
