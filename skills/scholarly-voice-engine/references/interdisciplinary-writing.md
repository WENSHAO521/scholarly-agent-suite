# Interdisciplinary Writing

Prevents disciplinary collision when a task genuinely spans more than one field
(e.g., bioethics, STS, digital humanities, computational social science,
environmental humanities, health humanities, urban studies, development studies,
sustainability studies, complexity science, AI governance).

## Setup

Before drafting, establish:

```text
home discipline        — whose evidentiary standard governs the piece overall
secondary discipline    — the contributing field(s) supplying concepts/methods
borrowed concepts        — which concepts cross from secondary into home
borrowed methods         — which methods cross, and whether they're used natively
                           or adapted
terminology conflicts    — terms that mean different things in each field
evidentiary standards    — reconcile: e.g., a philosophy-of-science argument
                           embedded in an empirical health-policy paper must be
                           explicit about which claims are conceptual and which
                           are empirical
```

Load the home discipline's module as primary and the secondary discipline's
module for its specific contributions — do not blend them into an undifferentiated
voice.

## Terminology ownership

When a term carries different meanings across the fields in play, name the
intended meaning explicitly on first use rather than letting it float:

```text
institution    — (economics: rules of the game) vs. (sociology: durable social
                  pattern) vs. (political science: formal organization)
resilience     — (ecology: return to equilibrium) vs. (engineering: capacity to
                  absorb shock) vs. (psychology: individual adaptive capacity)
complexity     — (complexity science: emergent system behavior) vs. (colloquial:
                  "complicated")
agency         — (sociology/philosophy: capacity for independent action) vs.
                  (principal-agent economics: a specific contractual relationship)
representation — (political theory: standing for constituents) vs. (statistics:
                  sample reflecting a population) vs. (humanities: depiction)
validity        — (measurement: construct/internal/external validity) vs. (logic:
                  soundness of an argument) vs. (law: legal effect)
robustness      — (statistics: insensitivity to specification) vs. (engineering:
                  tolerance to failure) vs. (evolutionary biology: phenotypic
                  stability)
```

State the chosen meaning once, then use it consistently for the rest of the
document — do not let it silently drift back to a different field's sense.

## Avoiding incompatible mixing

Do not combine concepts from different fields as if they were interchangeable
without explanation. If a claim requires borrowing an evidentiary standard from
one field into a text otherwise governed by another (e.g., invoking statistical
significance inside a doctrinal legal argument), flag the borrowing explicitly
rather than letting the standards blur.

## Genre and continuity

Interdisciplinary work still follows `article-writing.md` or `book-writing.md`
for its scale; this file only governs how the disciplinary content within that
architecture is kept coherent. For book-length interdisciplinary work, record
terminology choices in the monograph continuity state's `terminology:` field so
later chapters don't redefine a cross-disciplinary term inconsistently.
