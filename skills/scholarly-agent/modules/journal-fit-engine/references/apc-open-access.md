# APC & Open Access

## APC verification

Current APC should be verified from official sources whenever it matters to
the recommendation (i.e. whenever the user has a budget constraint or an OA
mandate). Record: mandatory APC, optional-OA APC, waiver information,
currency, tax status if known, and verification date. Do not reuse a cached
APC figure without flagging its `verified_at` date — APCs change frequently
and sometimes substantially.

## Fee-model distinctions

Do not confuse:

- **hybrid OA charge** — an *optional* fee on an otherwise subscription
  journal, paid only if the author wants the article to be openly accessible
- **mandatory publication fee** — required regardless of OA choice (typical
  of full-OA journals)
- **diamond OA** — no fee to authors or readers (often society- or
  institution-subsidized)

These have very different implications for a no-APC constraint and must be
reported distinctly, not collapsed into a single "has a fee / doesn't have a
fee" flag.

## No-APC mode

When the user specifies a no-mandatory-APC constraint, this is a hard
constraint on candidate selection (see [fit-model.md](fit-model.md) §Hard
filters and [submission-strategy.md](submission-strategy.md) §Constraint
handling). Distinguish clearly between:

- a subscription journal with an *optional* OA fee (satisfies "no mandatory
  APC" — author can decline the OA option)
- a diamond-OA journal (satisfies "no mandatory APC" and is fully open)
- a full-OA journal with a mandatory APC (does **not** satisfy a no-APC
  constraint, regardless of prestige or fit)

If a top-fit candidate fails a no-APC constraint, say so explicitly and offer
it as a relaxation option rather than silently omitting it or silently
including it.
