# Source Hierarchy

Prefer sources in this order. Only move down a tier when the tier above cannot
answer the analytical question at hand.

## Tier 1 — User-provided or explicitly authorized material

- Uploaded papers or books
- Author manuscript files
- Personal publication archive
- Institutionally authorized corpus

This is the preferred, and normally required, source for personal author
profiling (see `author-profile.md` § Authorization boundary). Do not substitute
publicly retrieved papers for this tier merely because a name matches.

## Tier 2 — Open metadata

- Crossref, OpenAlex, PubMed metadata, other bibliographic indexes
- Repository and publisher metadata

Metadata alone is usually sufficient for: title analysis, year distributions,
journal sampling, author disambiguation, DOI verification, venue
identification. **Do not retrieve full text when metadata solves the task.**

## Tier 3 — Open abstracts

Use when lawfully accessible. Abstracts support: argument framing, contribution
language, claim calibration, abstract architecture, field terminology.

## Tier 4 — Open-access full text

Prioritize, in order of preference:

1. Public repositories and institutional repositories
2. PMC or similar lawful archives
3. Preprint servers
4. Author manuscripts
5. Clearly open-licensed publisher versions

Verify access status when practical before use. Never bypass a paywall or bot
protection to reach a version that would otherwise sit behind Tier 4's lawful
boundary.

## Tier 5 — Public-domain historical works

Valuable for historical voice profiles. For each work record: edition, source,
publication date, and public-domain status when known (see
`historical-profile.md` and `copyright-boundary.md` for jurisdiction caveats —
public-domain status is not global and must not be assumed).

## Retrieval minimization decision sequence

```text
What feature is needed?
  -> Can metadata answer it?          -> use Tier 2, stop
  -> Can the abstract answer it?      -> use Tier 3, stop
  -> Can section headings answer it?  -> use structural metadata, stop
  -> Is open full text materially necessary? -> use Tier 4, minimally
```

Only escalate a tier when doing so would change the analytical result — not
because more text is available.

## Escalation is never permission to bypass access

Escalating from Tier 3 to Tier 4 means "look for a lawful open-access copy," not
"retrieve the paywalled version by any means." If no lawful Tier 4 copy exists,
stop at Tier 3, record `access_status: access_restricted`, and continue the
profile with abstract-level evidence.
