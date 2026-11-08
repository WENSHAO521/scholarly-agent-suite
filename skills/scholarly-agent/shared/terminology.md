# Shared terminology

A common vocabulary across all five Skills, to prevent cross-Skill drift. If a
Skill needs a term not defined here, define it locally rather than inventing a
near-synonym for a term that already exists here.

| Term | Meaning |
|---|---|
| **Corpus** | A sampled, deduplicated set of scholarly source records (metadata + available text) assembled by scholarly-corpus-builder for a specific profiling purpose. Not a permanent archive. |
| **Profile** | A structured, evidence-backed summary derived from a corpus (`SCHOLARLY_PROFILE_V1`): discipline, journal, historical-scholar, author-voice, or book. |
| **Observed style** | Style/structure regularities *measured* from a corpus (e.g. mean paragraph length, hedging frequency). Descriptive, not prescriptive. |
| **Official requirement** | A rule stated by a journal's own author guidelines (word limit, structure, citation style). Prescriptive. Kept separate from "observed style" per `JOURNAL_STYLE_CONTEXT_V1` (rule 34). |
| **Claim type** | The evidentiary status of a statement in a manuscript: `established`, `contested`, `novel`, `speculative`. Drives claim calibration in scholarly-voice-engine. |
| **OA** | Open access. A source's OA status is a *retrieval fact* (can this be lawfully read/reused), not a quality signal. |
| **Reuse license** | The specific license (e.g. CC-BY, CC-BY-NC) governing whether/how retrieved text may be quoted or reused -- distinct from OA status itself. |
| **Journal fit** | A qualitative match assessment (`STRONG_FIT` / `MODERATE_FIT` / `WEAK_FIT`) between a manuscript profile and a journal profile. Never a numeric probability (rule 75). |
| **Submission readiness** | Whether a manuscript currently satisfies a target journal's official requirements and hard constraints -- independent of fit quality. |
| **Author voice** | The composite stylistic/argumentative signature of one specific, authorized author (usually the user), derived from their own writing. Distinct from "author imitation" of an unrelated third party (rule 117). |
| **Continuity state** | The `CONTINUITY_STATE_V1` ledger (voice contract, concepts, claims, evidence, chapters, terminology, open questions) carried across a book/monograph project. |
| **Hard constraint** | A user requirement that cannot be silently violated (e.g. "SSCI only", "no APC"). See `execution-policy.schema.json` / rule 111. |
| **Soft preference** | A user preference that can be relaxed if it conflicts with a hard constraint or produces no viable candidate (rule 112). |
| **Freshness** | `current` / `aging` / `stale` -- how recently a fact was verified, distinct from whether it was ever verified at all. |
