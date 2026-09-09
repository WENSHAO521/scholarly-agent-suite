# Humanities

Philosophy, history, literature, linguistics, religious studies, classics, art
history, cultural studies, intellectual history, ethics, political thought.

```yaml
discipline_family: humanities
default_claim_style: interpretive  # readings argued for, not "proven" in the scientific sense
typical_argument_structures:
  - interpretive problem → existing reading → text/source evidence → conceptual
    intervention → close analysis → implication (literature/cultural studies)
  - question → sources → chronological reconstruction → interpretation →
    historiographical positioning → implication (history)
  - thesis → key distinction → argument → strongest objection →
    response/qualification → refined thesis (philosophy)
typical_evidence:
  - primary text/source close reading
  - archival material
  - historiographical/critical tradition
  - conceptual argument (philosophy)
citation_behavior: moderate_to_dense  # attributed readings, engaged rather than listed
methods_visibility: moderate  # source/interpretive method made explicit, not a "methods section" in the scientific sense
acceptable_first_person: yes  # "I argue", "this reading suggests" is standard and often necessary to mark interpretive stance
common_failure_modes:
  - treating one's own reading as the only possible one without engaging
    competing readings
  - anachronism (importing a later concept into an earlier text/period without
    marking the move)
  - source evidence disconnected from the interpretive claim it is meant to
    support
  - forcing scientific-style claim calibration onto genuinely interpretive work
recommended_voice_profiles:
  - interpretive-humanistic
  - historical-structural
  - normative-systematic
book_writing_norms: >
  Do not force scientific article structure onto book chapters. Narrative and
  interpretive presence may be stronger here than in empirical disciplines; keep
  terminology (especially contested concepts) stable across chapters via the
  monograph continuity state, or explicitly flag and justify a chapter's
  refinement of an earlier definition.
article_writing_norms: >
  Support close reading, archival argument, historical contextualization,
  conceptual interpretation, historiographical intervention, and philosophical
  argument as first-class architectures — do not impose IMRaD. Allow stronger
  authorial presence where the genre permits it.
```

## Prose guidance

Mark interpretive stance explicitly ("may be read as," "this interpretation
emphasizes," "a competing reading would") rather than asserting a reading as
the only possible one. Keep source evidence physically close to the claim it is
adduced for. Distinguish observation (what the text/source says), interpretation
(what it plausibly means), and speculation (what it might mean, more tentatively)
as three distinct registers.

## Philosophy

Grouped with humanities for routing, but distinctive enough for dedicated
treatment: analytic philosophy, continental philosophy, ethics, political
philosophy, philosophy of science, epistemology, metaphysics.

```yaml
subfield: philosophy
default_claim_style: argued_thesis  # a position defended against its strongest objection, not "proven" empirically
typical_argument_structure: >
  problem → conceptual distinction → argument → strongest objection →
  counterexample → refinement → bounded conclusion
typical_evidence:
  - argument from consequence, counterexample, and thought experiment
  - close engagement with the primary and secondary philosophical literature
  - conceptual analysis
citation_behavior: dense_and_engaged  # attributed, argued with, not merely listed
acceptable_first_person: yes  # "I argue," "I will show" is standard
common_failure_modes:
  - engaging a weaker version of an objection than its strongest form
  - fake profundity — rhetorical amplitude standing in for an actual argument
  - treating a continental-tradition text with analytic-style claim
    calibration or vice versa without acknowledging the difference in method
  - a key term used inconsistently across the piece's central argument
recommended_voice_profiles:
  - normative-systematic
prose_guidance: >
  Take the strongest form of an opposing view seriously before responding to
  it (see the Popper entry in historical-voice-profiles.md). High definition
  and counterargument density are appropriate here in a way they would be
  excessive elsewhere — but every distinction earns its place by doing
  argumentative work, not by performing rigor.
```

## History

Grouped with humanities for routing, but distinctive enough for dedicated
treatment: political history, social history, economic history, intellectual
history, cultural history, global history, microhistory, history of science.

```yaml
subfield: history
default_claim_style: interpretive_reconstruction  # argued from available sources, not proven the way a formal claim is
typical_argument_structure: >
  historical problem → historiography → source base → context → episode →
  interpretation → comparison → historical significance
typical_evidence:
  - primary sources (archival, documentary, material)
  - secondary historiographical literature, positioned rather than merely
    cited
  - comparative historical cases
citation_behavior: dense_and_source_grounded
acceptable_first_person: variable  # common in historiographical positioning, less so in pure narrative reconstruction
common_failure_modes:
  - treating a single source as settling a contested chronology
  - anachronism — importing a later concept into an earlier period without
    marking the move
  - narrating a historical episode as inevitable in hindsight rather than as
    it was contingently experienced
  - historiographical positioning skipped, so the piece reads as if no one
    has written on the topic before
recommended_voice_profiles:
  - historical-structural
prose_guidance: >
  Make source reliability explicit rather than treating all sources as
  equally probative. Position the account against the existing
  historiography by name — not "historians have studied this topic" but
  which interpretive tradition this account extends, revises, or breaks
  from. Do not force hypothesis-testing language onto a genuinely
  interpretive reconstruction.
```
