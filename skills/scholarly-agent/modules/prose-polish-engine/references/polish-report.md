# POLISH_REPORT_V1 and the hand-back

Schema: `protocols/polish-report.schema.json`. Built by
`ppe.report.build_polish_report()`, checked by
`ppe.report.validate_polish_report()`.

## Fields

| Field | Meaning |
|---|---|
| `protocol` | `POLISH_REPORT_V1` |
| `language` | ISO 639 code of the text (`en`, `zh`, `ja`, `ar`, ...) |
| `catalog` | `true` when `ppe.patterns` has a phrase catalog for that language; otherwise `limitations` says so |
| `level` | `light`, `standard`, or `deep` |
| `before`, `after` | `pattern_load` (low / moderate / high), `density` (weighted findings per 1,000 words, or characters for Chinese, Japanese, Thai), `by_category`, `must_remove` (chat residue count), `units` |
| `changes` | the polisher's log: `{category, before, after, note?}` per edit worth showing |
| `remaining` | `revise` and `remove` findings still in the polished text; each one the polisher keeps on purpose gets `kept_because` |
| `invariants` | `status` PASS / REVIEW / FAIL, `failures`, `warnings`, `length_ratio` |
| `status` | the report's overall status: `FAIL` if invariants failed or residue remains, otherwise the invariant status |
| `notice` | `ppe.POLISH_NOTICE`, unchanged |
| `escalations` | argument- or structure-level problems noticed and deliberately left for a revision pass (voice module) |
| `limitations` | anything left unresolved after the one repair pass |

The dispatcher treats `status: FAIL` as a blocked stage and `REVIEW` as
`COMPLETE_WITH_LIMITATIONS` unless every warning is explained in the
hand-back.

## Worked example

```json
{
  "protocol": "POLISH_REPORT_V1",
  "language": "zh",
  "catalog": true,
  "level": "standard",
  "before": {"pattern_load": "high", "density": 130.43, "by_category": {"formulaic-frame": 4, "stock-connective": 3, "empty-emphasis": 2, "hedge-stack": 1, "nominalization": 1, "stock-summary": 1}, "must_remove": 0, "units": 115},
  "after":  {"pattern_load": "low", "density": 0.0, "by_category": {}, "must_remove": 0, "units": 59},
  "changes": [
    {"category": "formulaic-frame", "before": "隨著人工智慧技術的快速發展，生成式模型在教育領域起著至關重要的作用", "after": "生成式模型正在改變課堂上的寫作作業"},
    {"category": "hedge-stack", "before": "教師也可能或許會受到影響", "after": "教師也可能受到影響"}
  ],
  "remaining": [],
  "invariants": {"status": "REVIEW", "failures": [], "warnings": ["hedges changed from 2 to 1; confirm no claim got stronger or weaker"], "length_ratio": 0.576},
  "status": "REVIEW",
  "notice": "Pattern counts describe templated phrasing in this text; they are not an estimate of who or what wrote it, and no detector result is implied."
}
```

Here the hedge warning is expected (a stacked 「可能或許」 became 「可能」) and
is explained in the hand-back.

## Presenting the polish to the author

Write the hand-back in the author's language. Order:

1. **The polished text**, complete, ready to paste.
2. **What changed**, in three to six lines grouped by kind ("removed eight
   stock connectives", 「刪去三處『具有重要意義』類的空洞強調，改為具體陳述」),
   with two or three before/after pairs that show the pattern.
3. **Kept on purpose**, if any, with the reason.
4. **Check**: one line, e.g. "All 14 citations, 9 numbers, and 2 quotations
   are unchanged; one stacked hedge was reduced to one." Mention any
   REVIEW warning and how it was resolved.
5. **Needs a revision pass**, only if there are escalations.

Do not present `pattern_load` or `density` as a score of how "human" or
"AI-like" the text is, and do not report a before/after figure as a
predicted detector result. If the author asks for one, say the numbers
count templated phrases in this text and nothing more.
