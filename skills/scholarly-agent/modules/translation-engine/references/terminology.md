# Terminology

A long translation stays trustworthy only if each technical term is
rendered the same way every time. Settle the terms before translating, keep
them in a glossary, and let the check enforce it.

## Building the glossary

1. Run `python -m tre terms SOURCE` (or `tre.glossary.term_candidates(text,
   lang)`). It lists acronyms, terms the text defines or glosses ("public
   value (PV)", 「以下簡稱」, "hereafter"), and recurring multi-word or
   multi-character terms. It is a starting list, not a glossary.
2. For each term that matters, choose the rendering in this order:
   1. the author's own choice (ask for a term list when the text is dense
      with specialist vocabulary and none was given; reuse any glossary from
      an earlier translation of the author's work);
   2. the established translation in the field and target region (the
      standard term in the field's main journals, textbooks, official
      terminology databases, or the target journal's recent articles);
   3. a consistent choice of your own, recorded as a `term` note so the
      author can change it.
3. Mark terms that must not be translated as `keep`: acronyms the target
   field also uses, software, gene, protein, and dataset names, legal
   citations, survey item codes, and anything the author wants in the
   original.
4. Save the glossary with the translation (JSON or TSV) so the next chapter
   or the revision uses the same terms.

Glossary format (TSV, one entry per line; `=` or an empty second column
means keep as written):

```
數位治理能力	digital governance capacity
公共價值	public value
DGC	=
OECD	=
```

or JSON: `[{"source": "公共價值", "target": "public value"}, {"source": "DGC", "keep": true}]`.

## Field conventions

- **Established term over literal term.** 「行政院」 is the Executive Yuan,
  not "Administrative Court"; "public administration" is 公共行政, not
  公眾管理; "path dependence" is 路徑依賴, not 道路依賴. When a field has a
  standard term, use it even if a literal rendering seems more transparent.
- **Contested terms.** Where a field has competing translations (e.g.
  governance: 治理 vs 管治 in Hong Kong usage), follow the author's and the
  target venue's usage, and gloss the original on first use.
- **Institution and program names** use their official name in the target
  language when one exists; otherwise keep the original and add a
  translation in parentheses on first use.
- **Theory names and eponyms** follow the field's usage (Weberian
  bureaucracy / 韋伯式科層制).
- **Statistical and methods terms** follow the target field's textbooks:
  regression 迴歸 (Taiwan) / 回归 (Mainland), significance 顯著性 /
  显著性, robustness check 穩健性檢驗 / 稳健性检验.

<a id="chinese-varieties"></a>

## Chinese varieties

Traditional and Simplified Chinese differ in vocabulary as well as in
characters, and Taiwan and Hong Kong differ from each other. Name the
target (`zh-TW`, `zh-HK`, `zh-Hant`, `zh-CN`, `zh-Hans`) and use that
region's terms. `tre.languages.variety_mismatches` catches characters of
the wrong script; it cannot catch a right-script word from the wrong region,
so check vocabulary by hand. Common academic differences:

| English | Taiwan (zh-TW) | Mainland (zh-CN) |
|---|---|---|
| information | 資訊 | 信息 |
| software | 軟體 | 软件 |
| quality | 品質 | 质量 |
| data | 資料 / 數據 | 数据 |
| network | 網路 | 网络 |
| program (computer) | 程式 | 程序 |
| project | 計畫 | 项目 |
| policy instrument | 政策工具 | 政策工具 |
| questionnaire | 問卷 | 问卷 |
| sample | 樣本 | 样本 |
| regression | 迴歸 | 回归 |
| robustness | 穩健性 | 稳健性 |
| interview | 訪談 | 访谈 |
| video | 影片 | 视频 |
| digital | 數位 | 数字 |
| local government | 地方政府 | 地方政府 |
| county / municipality | 縣市 / 直轄市 | 县 / 市 |
| research institute | 研究所 | 研究所 / 研究院 |
| postdoctoral researcher | 博士後研究員 | 博士后 |
| peer review | 同儕審查 | 同行评议 |

Converting between Traditional and Simplified is a translation task here:
convert characters, then replace region-specific vocabulary, then run the
check with `--variety` to catch stray characters. Keep quotations from
sources in the script they were published in.

## Other regional standards

- **Portuguese:** pt-BR and pt-PT differ in spelling (pt-PT "facto", "actual"
  in some older texts) and vocabulary (pt-BR "pesquisa", pt-PT also
  "investigação" for research).
- **English:** follow the venue: en-US (-ize, "program", "behavior") or en-GB
  (-ise or Oxford -ize, "programme", "behaviour"). Do not mix.
- **Spanish:** es-ES vs Latin American usage (ordenador / computadora); prefer
  neutral academic Spanish unless the venue is regional.
- **French:** fr-FR vs fr-CA vocabulary and typography (fr-FR spaces before
  `; : ! ?`, fr-CA only before `:`).

## Enforcing it

`tre.glossary.check_glossary` (run by `tre.report`) reports each entry as
`kept`, `missing` (FAIL: the source uses the term and the required rendering
never appears), `count-differs` (REVIEW: fewer target occurrences than
source occurrences), or `not-in-source`. A term changed on purpose is
changed in the glossary, not in the text alone.
