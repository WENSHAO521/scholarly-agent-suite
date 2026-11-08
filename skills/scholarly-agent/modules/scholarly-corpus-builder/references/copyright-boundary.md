# Copyright Boundary

This file states the hard rules. They are not defaults to be optimized away
under time pressure or user insistence — they are the floor.

1. **Derive features, don't reproduce text.** The product of this skill is a
   structured profile (sentence rhythm, argument architecture, section
   layout), not a copy of the source. Quotations, when used at all, must be
   short and clearly justified by the analytical point being made.
2. **Use only lawful access paths.** Tier 1 (user-authorized), Tier 2–3
   (open metadata/abstracts), Tier 4 (genuinely open-access full text), and
   Tier 5 (verified or reasonably believed public domain).
3. **Never bypass paywalls, login walls, or bot/anti-scraping protections.**
   If a source sits behind one and no lawful open version exists, stop at
   metadata or abstract level and record `access_status: access_restricted`.
4. **Do not use leaked databases, unauthorized mirrors, or shadow libraries**
   to acquire books or articles, even when they are "commonly available."
5. **Do not store unnecessary full text.** If full text was used transiently
   to extract features, persistent storage should retain the provenance
   record and derived features — not the full text — unless the user has
   separately authorized retaining their own material (Tier 1).
6. **Do not build characteristic-phrase imitation libraries.** Never compile
   a bank of an author's or journal's distinctive sentences/phrases intended
   for direct reuse. Feature extraction stays at the level of patterns
   ("claim-first paragraphs," "mechanism-centered examples"), not verbatim
   text.
7. **Do not create living-author imitation systems.** A profile of a living,
   contemporary scholar's public work may describe high-level argument and
   structural tendencies, but must not become a signature-sentence generator
   or a template for passing off writing as theirs.
8. **Retain provenance for everything used.** Every source that contributed to
   a profile must have a provenance record (`provenance-schema.md`), even if
   only metadata was used.
9. **Do not fabricate licensing.** If a license is unknown, record
   `license: null`. Free access does not imply a permissive license (e.g. do
   not infer `CC BY` from mere availability).
10. **Public domain is not global.** Status varies by jurisdiction and can
    depend on author death date, publication date, and renewal history. Use
    `public_domain_status: verified / likely / unknown` rather than a blanket
    assertion, and prefer conservative wording when unverified.

## What to do when access is unavailable

```text
record metadata
mark full_text_status = unavailable
continue with lawful evidence (abstract, headings, prior profile)
```

Do not treat an access failure as a task failure — the profile can usually
still be built, just with a lower confidence rating and a recorded limitation.

## Refusal pattern

If a user explicitly asks to bypass a paywall, scrape protected content, pull
from a leaked/shadow database, or build a phrase-imitation library for a living
author, decline that specific action, explain the lawful alternative (Tier 1–4
sources, feature-level profiling), and proceed with what is actually
obtainable.
