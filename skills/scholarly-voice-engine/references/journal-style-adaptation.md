# Journal Style Adaptation

How this Skill consumes an adaptation target from `journal-fit-engine` when
that Skill is present. Journal Fit Engine decides *where* a manuscript might
belong and hands this Skill a compact target profile; it does not perform the
rewrite itself — that is this Skill's job. See `references/integration.md`
for the ecosystem-level relationship.

## What journal-fit-engine sends

As of journal-fit-engine v0.3.0, the primary handoff is a
`JOURNAL_STYLE_CONTEXT_V1` envelope (`jfe.style_context`,
`scholarly-agent-suite/protocols/journal-style-context.schema.json`),
consumed here via `scripts/voice/journal_context.py`:

```yaml
protocol: JOURNAL_STYLE_CONTEXT_V1
journal_name: Journal of Example Studies
official_requirements: { word_limit: 8000, citation_style: APA7 }
observed_patterns: { tone: formal, contribution_placement_observed: early }
freshness: current | aging | stale
```

`official_requirements` becomes a `hard_requirements` block: apply it as
stated, never confidence-gated, never silently dropped or overridden by
anything else in this reference. `observed_patterns` is fed into the
existing author→discipline→journal→historical precedence resolution
(`corpus-profile-integration.md`) as the "journal" layer, with its
confidence set from `freshness` — a `stale` or absent freshness gates it
down to low confidence exactly as an already-low-confidence journal
profile would be gated (`corpus-profile-integration.md` §Conflict
resolution), so it yields to a lower-precedence layer rather than silently
winning on stale evidence.

Older callers (or a caller that has already derived writing-level
adjustments itself, e.g. from its own reasoning over a
`JOURNAL_STYLE_CONTEXT_V1`) may instead hand over the compact form:

```yaml
target_voice_adjustment:
  contribution_position: earlier
  mechanism_visibility: higher
  policy_implication: medium
  sentence_density: moderate
```

or the fuller form:

```yaml
journal_target:
  genre: empirical_social_science
  contribution_position: early
  theory_density: medium_high
  policy_implications: high
  methods_transparency: high
  introduction_length: moderate
```

Treat these field names as authoritative — do not rename them or invent
additional fields on this Skill's side. If a host or user supplies a journal
name without going through `journal-fit-engine`, either request the profile
from that Skill (if present) or ask the user for the journal's actual
instructions rather than guessing its house style from the name alone.

## Adaptation boundary — framing and structure only

Journal adaptation may change:

```text
contribution placement | section order | abstract architecture | technical
density | policy/clinical-implication emphasis | discussion structure |
word count | reference style
```

It must never change:

```text
results | data | findings | study design | sample | statistical values |
historical facts | legal authority | theorem statements | definitions
```

This matches `journal-fit-engine`'s own adaptation policy verbatim ("never
recommend changing the scientific findings, data, results, sample, or
legal/historical evidence to fit a journal") — this Skill enforces the same
line at the point where the actual rewrite happens.

## Observed style is not destiny

A `journal_target` reflects an **observed** pattern in that journal's own
recent articles (see `corpus-profile-integration.md` §OBSERVED, RECOMMENDED,
MANDATORY). Compress toward it when doing so doesn't damage the argument —
but do not gut a theoretical section the manuscript genuinely needs merely to
match a shorter median article length. If following the target would require
cutting something the argument depends on, say so rather than silently
complying.

## Precedence against author and discipline

A journal-observed target sits below the user's own established voice and
current disciplinary convention in the overall precedence order (see
`corpus-profile-integration.md` §Voice precedence). Use the journal target to
adjust structure and emphasis; do not let it flatten the author's genuine
voice or override a discipline's non-negotiable evidentiary norms (e.g., a
journal's typically shorter methods section never licenses omitting
information a clinical design requires for critical appraisal).

## What this Skill returns

After adapting, report back (conceptually, for a caller like
`journal-fit-engine` or the user) which target fields were actually applied,
which were not applied and why (usually: would have required changing
substance), and any residual mismatch the user should know about before
submitting.

## Standalone fallback

If `journal-fit-engine` is not present, adapt only from explicit information
the user supplies (e.g., a pasted "Instructions for Authors" page) and mark
anything else as unknown rather than inferring a journal's house style from
its name or reputation.
