# Citation Integrity

Non-negotiable rules for how citations, quotations, and evidence attribution
are handled during drafting and rewriting. This outranks every voice
consideration (see `SKILL.md` §Operating hierarchy).

## Never fabricate

Never invent, guess, or "plausibly reconstruct":

```text
authors | titles | journal or venue names | publication years | DOIs |
ISBNs/ISSNs | page numbers | volume/issue numbers | quotations |
study findings or effect sizes | sample sizes | statistics
```

If a citation is needed but not supplied and cannot be retrieved through an
available tool, mark it `[VERIFY]` (or `[INSERT CITATION]` for a placeholder
the user will fill) rather than inventing a plausible-looking one. Where a
host provides retrieval tools, use them to find a real source rather than
guessing — but do not silently invent one either way.

## Reuse, don't reinvent, verification states

When a citation's source material comes from `scholarly-corpus-builder` (or
another provenance-aware tool), carry its verification state through rather
than treating every quoted or cited fact as equally certain:

```text
VERIFIED            persistent identifier checked
PARTIALLY_VERIFIED  title/venue/year found but identifier unverified
NEEDS_CHECK         plausible but not yet confirmed
REJECTED            could not be confirmed, or evidence contradicts it
```

(See that skill's `references/provenance-schema.md` for the authoritative
definitions — do not redefine these states differently here.) Do not present
a `NEEDS_CHECK` or `PARTIALLY_VERIFIED` source with the same confidence as a
`VERIFIED` one; say so if the distinction matters to the claim being made.

## The citation-preservation invariant

During any rewrite of existing scholarship:

- Preserve which specific claim each citation supports — never silently move
  a citation to support a different claim than the source text used it for.
- Never combine several citations into one so that a claim appears supported
  by a reference that does not actually address it.
- Never alter quoted material, even to "smooth" it stylistically — a
  quotation's wording is not subject to voice calibration.
- Never invent a quotation attributed to a historical or living scholar (see
  `historical-voice-profiles.md` §Using this library).

## Citation density

Density should track discipline, genre, section, and claim type (see the
relevant `disciplines/*.md` file and `genre-matrix.md`) — not a fixed rate.
Mathematics and formal proof carry very few, precise citations; empirical
social science is dense at literature-positioning and sparser in results;
humanities argument is often citation-dense throughout but each citation
attaches to a specific reading, not a general area. Not every sentence needs
one; not every paragraph can go without one.

## Integration over dumping

Use citations to do specific argumentative work:

```text
establish consensus | mark contradiction | attribute origin/priority |
support a specific empirical claim | mark the boundary of what's established
```

Avoid citation dumping — a string of references at a paragraph's end doing no
individually identifiable work:

```text
weak:   "This is well established (Smith 2019; Jones 2020; Lee 2021; Park
        2018; Chen 2022)."
better: name what each cluster of sources actually establishes, or prune to
        the sources that are doing real work for the specific claim
```

## Quotation discipline

Quote only when the wording itself matters (a legal holding's exact language,
a literary passage under analysis, a definition whose precise phrasing is the
point) — not to decorate prose with borrowed authority. Never use a quotation
(real or invented) merely to make a passage sound more scholarly. Do not use
a famous line "because it sounds right" without verifying it is both real and
actually attributable to the claimed source.

## When rewriting under voice calibration

Voice strength (`editing-modes.md`) governs how much a sentence's wording may
change — it never governs whether a citation, quotation, statistic, dataset
description, or study finding may change. If a "high" voice-strength rewrite
would require altering any of these to make the prose flow better, restructure
the sentence around them instead of altering the substance.
