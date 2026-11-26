# Journal Profile

## Schema

```yaml
journal:
publisher:
issn:
eissn:
discipline:
subdisciplines: []
scope:                       # verbatim or close paraphrase of official aims & scope
audience:
article_types: []            # journal's own taxonomy, not generic labels
methods_commonly_published: []   # OBSERVED
recent_topics: []                # OBSERVED
interdisciplinary_orientation:
word_limits:
abstract_requirements:
reference_style:
open_access_model:           # subscription | hybrid | full-OA | diamond
apc:
indexing: []
submission_url:
official_guidelines:         # URL
profile_date:                # when this profile was assembled
verified_at:                 # when key facts were last checked against source
status:                      # active | ceased | discontinued | renamed | merged | inactive
```

## Official vs. observed evidence — strict separation

Two categories, never blended:

**OFFICIAL JOURNAL DATA** — aims and scope, accepted article types, word
limits, submission rules, APC, open-access policy, formatting requirements.
Sourced from the publisher/journal's own current pages.

**OBSERVED ARTICLE PROFILE** — dominant methods, recurring topics, typical
theoretical density, writing architecture, geographical tendencies, article
structure. Inferred by examining a sample of recent published articles.

When presenting a journal profile, label which category each fact belongs to.
Never state an observed tendency ("this journal tends to publish qualitative
work") as if it were a formal rule ("this journal only accepts qualitative
work") — say "recent issues predominantly feature X" instead of "this journal
requires X."

## Journal identity resolution

Resolve journals by, in order of reliability: ISSN/eISSN > canonical
publisher URL > publisher + title > title alone. Title-only matching is
unreliable because of:

- similar/near-duplicate journal names across publishers or regions
- journal title changes over time
- discontinued journals whose name is reused or squatted
- journal splits (one journal becomes two) and mergers (two become one)
- successor titles after a relaunch

When identity is ambiguous, say so explicitly and ask for or seek the ISSN
rather than guessing which journal is meant.

## Currency requirement

Journal facts drift: scope statements get revised, APCs increase, indexing
status changes, publishers change, journals get discontinued or renamed.
Whenever scope, APC, indexing, submission rules, article types, publisher, or
journal title/status matter to the recommendation, prefer freshly verified
information over a cached description, and record `verified_at`. See
[evidence-policy.md](evidence-policy.md) for the tiered source hierarchy and
[journal-integrity.md](journal-integrity.md) for discontinuation detection.

## Profile caching and refresh

Status: `CURRENT`, `AGING`, `STALE`, `INCOMPLETE`.

Default refresh window: 6–12 months for stable journals; shorter for
fast-moving fields (AI, medical AI, computational biology) where article-type
mix and topic focus shift faster than the nominal scope statement.

Refresh triggers: scope changed, publisher changed, APC changed, article
types changed, indexing status newly matters to the user's constraints,
profile is stale, or the user explicitly requests current status.

## Special issues

A special issue is not representative of the journal as a whole. If
recommending submission to a currently open special issue, verify: topic,
deadline, guest editors, accepted article types, submission conditions, and
current open/closed status. Do not recommend an expired call.

## Journal families and transfer pathways

Some publishers offer cascading manuscript-transfer pathways between sibling
journals. This may be reported as practical information (e.g. "if desk
rejected here, this publisher offers transfer to X") when current, but never
treat a transfer offer as evidence of acceptance likelihood.
