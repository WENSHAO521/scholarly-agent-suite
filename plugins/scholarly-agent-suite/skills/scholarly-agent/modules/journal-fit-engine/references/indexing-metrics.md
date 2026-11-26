# Indexing & Metrics

## Indexing verification

If the user cares about SSCI, SCIE, AHCI, ESCI, Scopus, MEDLINE, PubMed, or
DOAJ status, verify current status against the index's own authoritative
listing where possible — do not infer indexing from a publisher's own claim
alone when authoritative evidence is checkable. Record `indexing_verified_at`.
If verification isn't possible, say `CURRENT_STATUS_NOT_VERIFIED` rather than
repeating an unverified publisher claim as fact.

## Quartile verification

Q1/Q2/Q3/Q4 is meaningless without specifying *which ranking system and
category*: JCR category quartile, SJR quartile, or another system — and a
journal's quartile can differ by category (a journal cross-listed in two JCR
categories may be Q1 in one and Q3 in the other). Never state a bare "Q1"
without naming the system and category.

## POSI (Panorama Open Scholarly Index)

POSI publishes open, versioned journal data (CC BY 4.0) that this module can
read through `jfe/posi.py`: a Citation Ranking (PNCI, category rank,
percentile, Citation Quartile, POSI Zone) for about 158,000 journals, and a
small Core Collection with PQF grades, AJR Ratings, and APCs that cite their
source page and check date. Rules for using it:

- Report a POSI quartile as **POSI Citation Quartile C-Q*n* in <POSI
  category> (metric year, methodology version)**. It is not a JCR, SJR, or
  CiteScore quartile and never substitutes for one; those stay
  `cannot_verify`.
- Only `citation_ranking_status: official` is a POSI ranking result.
  `provisional`, `observation`, and the not-ranked statuses are reported
  as such.
- Cite the snapshot id (and the release it follows) with every POSI claim.
  Snapshots are immutable, so the claim stays checkable.
- **Conflict of interest.** POSI is operated by Panorama Scholarly Group,
  which also publishes journals in POSI's Core Collection. For those
  journals, state this to the user, treat POSI's rating as the operator's
  own assessment, and never let it be the sole basis for recommending the
  journal.
- Absence from POSI is not evidence about a journal's quality or its
  indexing elsewhere.
- Like any metric, POSI values are secondary strategy variables, never the
  primary basis for a recommendation.

## Impact metrics

Impact Factor, CiteScore, SJR, h-index, and similar metrics may be included
if current and verified — but treat them as secondary strategy variables
(Stage 2 in [submission-strategy.md](submission-strategy.md)), never as the
primary basis for a recommendation, and never rank a candidate pool solely by
metric value.

## Acceptance rates

Only state a journal's acceptance rate when it is officially published,
reasonably current, and clearly defined (e.g. what counts as "submitted" —
before or after desk rejection). Otherwise state `not reliably available`.
Do not rely on crowdsourced or informal estimates as if they were fact.

## Review speed

Only report from official sources, and label precisely which metric is being
reported — `time to first editorial decision` (often includes desk rejects,
so can look misleadingly fast) is not the same as `time to first full
peer-review decision`, which is not the same as `time to publication`
(includes production). Do not conflate these.
