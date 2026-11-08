# Evidence-first paper workflow

Load this reference for evidence-intensive academic drafting, revision, literature review, methods planning, and manuscript submission work. Routine sentence edits need only the bounded polishing branch when this reference is already loaded. It is a platform-neutral synthesis; adapt the order to the target journal and the user's actual evidence.

## Choose the lightest valid branch

- **Ordinary manuscript:** frame → source map → architecture → draft → audit → submission.
- **Empirical or computational paper:** add baseline reproduction, leakage checks, run configuration, variance, ablations, and a reproducibility record.
- **Systematic review:** add protocol, eligibility, database and date records, screening counts, risk-of-bias assessment, synthesis rules, and the PRISMA 2020 reporting branch.
- **Sentence-level polishing after sources and argument are settled:** use a single bounded language pass and skip expensive research orchestration.

Do not force a systematic-review protocol onto a conceptual essay, and do not present a generic paper template as a journal's author instructions.

## 1. Build a paper context

Record the working title, research question, target journal or venue, genre, audience, contribution candidate, known evidence, required format, deadlines, and open questions. Keep confirmed facts separate from assumptions. If an item is unknown, mark it as an open question instead of filling it from memory.

For a new paper, write an identity sentence in the form “We claim X changes Y under condition Z, compared with baseline B, measured by M.” State the delta from the closest prior work. A reproduction or extension is valid when it is labeled accurately.

## 2. Search and preserve source evidence

For a normal paper, identify the roughly 5–15 sources that govern the problem rather than collecting a long uncited list. Use source-specific queries and inspect original papers, publisher records, proceedings, or recognized scholarly metadata services. For each source, keep an evidence entry with:

| Field | Requirement |
|---|---|
| Citation key and full record | Use the exact title, authors, year, venue, and persistent identifier that were verified. |
| Version | Record published article, proceedings version, preprint, or other status; prefer the formal version when one exists. |
| Provenance | Save the URL or database record and the date checked. |
| Contribution | Summarize the claim, method, data or sample, baseline, result, and limitation from the source actually read. |
| Use in paper | Name the claim or section supported by the source and the evidence location, such as page, table, or figure, when verified. |
| Access and license | Record whether the full text was openly licensed, user supplied, or unavailable. Do not infer redistribution permission from a working URL. |
| Verification state | Use `verified`, `needs-check`, or `rejected`; never treat a plausible title as a confirmed citation. |

Resolve DOI, arXiv, OpenAlex, or another persistent identifier when available. When a preprint and a formal publication may be the same work, verify the match by title, authors, venue, and identifier before canonicalizing it. Reopen the original paper before quoting or making a material claim. Retrieval output is a candidate until that check passes.

## 3. Map claims to evidence

Maintain a small claim matrix with `claim`, `section`, `source or result pointer`, `strength`, `caveat`, and `repair action`. Every material claim in the abstract and introduction must map to evidence in the body. Do not generalize from one dataset, sample, or setting without saying so. Separate source-backed claims, interpretations, and proposed wording.

When a source cannot be verified, keep the gap visible and use `[VERIFY]` or an equivalent internal marker until it is resolved. Never invent references, findings, identifiers, quotations, page numbers, datasets, or publication credentials.

## 4. Architect the argument

Create a section outline with one key claim per section, a figure and table plan, and a page or word budget when the venue supplies one. Write topic sentences before full paragraphs and read them in sequence; they should form a coherent argument. A provisional introduction can set guardrails for the evaluation, then be rewritten after results so it promises exactly what the evidence supports.

During integration, check terminology drift, claim-to-result coverage, transitions between paragraphs, section-opening signposts, figure and table references, and whether the named contribution appears consistently in the introduction, method, evaluation, and related work.

## 5. Protect empirical integrity

Before claiming an improvement, run the strongest feasible baseline on the same setup. Record data source and license, exact splits, temporal or group boundaries, seeds, code commit, configuration, hardware, and evaluation metric. Audit label leakage, train/test contamination, split-after-transform errors, grouped or temporal leakage, and tuning on the test set. Report mean ± standard deviation across at least three seeds when feasible; explain a smaller design rather than hiding it.

Change one factor at a time when attributing an effect. Use ablations or controls to identify what causes a gain. Preserve negative and null results when they affect the conclusion. If a number is unexpectedly strong, investigate the pipeline before treating it as a breakthrough.

## 6. Use the systematic-review branch when applicable

Capture the review question and framework (for example PICO, PICo, or SPIDER), registration or protocol status, information sources and last-search dates, complete search strings, inclusion and exclusion criteria, screening process, duplicate handling, data extraction, risk-of-bias tool, synthesis method, and certainty limits. Distinguish **records** (database entries), **reports** (full documents), and **studies** (underlying investigations). Keep exclusion reasons specific and countable.

Use PRISMA 2020 as a reporting and checklist branch, not as a substitute for conducting a sound review. Confirm every flow-diagram count and mark missing values as unknown. Select an applicable PRISMA extension when the review design requires one. Adapt citation style and document layout to the target journal instead of assuming APA 7 is universal.

## 7. Audit before delivery

For a substantive draft, audit citation reality and claim alignment, methods and results consistency, operational definitions, assumptions, limitations, reproducibility fields, terminology, target-journal structure, references, figures and tables, and anonymization when relevant. Return exact locations, severity, evidence, and a repair recommendation. A red-team pass is useful for material risk; it is not a reason to repeat routine line edits.

Use the root agent as the sole integrator. Apply the [delegation ROI policy](delegation-policy.md) before assigning source verification, argument/methods review, or journal-compliance roles; a manuscript alone does not justify delegation. Use the [routing policy](routing-policy.md) for failure classification and bounded repair. Do not automatically write persistent lessons or memory; retain only authorized task artifacts and evidence records.

## 8. Submission record

Before submission, confirm that the abstract claims are supported, citations resolve, identifiers and versions are correct, figures and tables are referenced, required declarations are present, the venue's word and format limits are met, and limitations are stated. Report unresolved evidence or formatting decisions instead of silently filling them.

For source provenance and license boundaries, see [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md).
