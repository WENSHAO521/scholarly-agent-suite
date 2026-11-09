"""What polishing must not change, and the check that it did not.

Polishing rewrites wording. It must leave the scholarly content alone:
every citation, DOI, URL, number, direct quotation, and formula in the
original must come out the other side unchanged, and any term the author
marks as protected must keep its exact form. Hedges and negations are
counted too: a change there is not always wrong (a stacked hedge collapses
to one), but it can move a claim's strength, so it is flagged for review
(references/polishing-passes.md, "Verify").
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Dict, Iterable, List, Tuple

from ppe.languages import hedge_regex, negation_regex

_YEAR = r"(?:1[5-9]\d{2}|20\d{2})[a-z]?"

PROTECTED = {
    # (Smith, 2020), (Smith et al. 2020; Lee 2019a, p. 4), Smith (2020)
    "citations": [
        r"\([^()\n]{0,200}?\b" + _YEAR + r"\b[^()\n]{0,200}?\)",
        r"（[^（）\n]{0,200}?" + _YEAR + r"[^（）\n]{0,200}?）",
        r"\[\d+(?:\s*[-–,]\s*\d+)*\]",
    ],
    "dois": [r"\b10\.\d{4,9}/[^\s\"<>，。、；）)\]]+"],
    "urls": [r"https?://[^\s<>，。、；）)\]]+"],
    "quotations": [r"“[^”\n]{1,600}”", r"「[^」\n]{1,600}」", r"『[^』\n]{1,600}』", r"\"[^\"\n]{1,600}\"",
                   r"«[^»\n]{1,600}»", r"„[^“”\n]{1,600}[“”]", r"‹[^›\n]{1,600}›"],
    "math": [r"\$[^$\n]{1,300}\$", r"\\\([^\n]{1,300}?\\\)", r"\\\[[^\n]{1,600}?\\\]"],
    "numbers": [r"(?<![A-Za-z0-9_.])[-−]?\d+(?:[.,]\d+)*(?:\s?%)?"],
}
STRICT = ["citations", "dois", "urls", "quotations", "math", "numbers"]

LENGTH_RANGE = (0.55, 1.30)


def _clean(item: str) -> str:
    item = item.replace("−", "-").strip()
    return item.rstrip(".,;:") if item[:1].isdigit() or item.startswith("10.") or item.startswith("http") else item


def extract(text: str) -> Dict[str, List[str]]:
    """Every protected item in ``text``, by kind, in order of appearance."""
    out: Dict[str, List[str]] = {}
    for kind, regexes in PROTECTED.items():
        found: List[Tuple[int, str]] = []
        for rx in regexes:
            found += [(m.start(), _clean(m.group(0))) for m in re.finditer(rx, text)]
        out[kind] = [s for _, s in sorted(found)]
    return out


def protected_spans(text: str) -> List[Tuple[int, int]]:
    """Character spans of citations, DOIs, URLs, quotations, and math --
    the parts of a text the diagnosis never flags and a rewrite never
    touches."""
    spans: List[Tuple[int, int]] = []
    for kind in ("citations", "dois", "urls", "quotations", "math"):
        for rx in PROTECTED[kind]:
            spans += [m.span() for m in re.finditer(rx, text)]
    return sorted(spans)


def _diff(a: List[str], b: List[str]) -> Tuple[List[str], List[str]]:
    ca, cb = Counter(a), Counter(b)
    return sorted((ca - cb).elements()), sorted((cb - ca).elements())


def _count(rx: str, text: str, lang: str) -> int:
    return len(re.findall(rx, text, 0 if lang in ("zh", "ja", "ko") else re.IGNORECASE))


def check_invariants(original: str, polished: str, lang: str = "en",
                     protected_terms: Iterable[str] = ()) -> Dict[str, object]:
    """Compare a polished text with its original.

    Returns ``{"status", "checks", "failures", "warnings", "length_ratio"}``.
    ``lang`` is any ISO 639-1 code; hedges and negations are counted only
    for languages with a list in ppe.languages.
    ``FAIL``: a protected item or protected term was dropped, added, or
    altered. ``REVIEW``: hedges or negations changed in number, or the length
    moved outside 55-130 % of the original. ``PASS`` otherwise.
    """
    a, b = extract(original), extract(polished)
    checks: Dict[str, Dict[str, object]] = {}
    failures: List[str] = []
    warnings: List[str] = []
    for kind in STRICT:
        missing, added = _diff(a[kind], b[kind])
        checks[kind] = {"original": len(a[kind]), "polished": len(b[kind]), "missing": missing, "added": added}
        if missing:
            failures.append("%s missing after polishing: %s" % (kind, missing[:5]))
        if added:
            failures.append("%s added by polishing: %s" % (kind, added[:5]))
    for term in protected_terms:
        n0, n1 = original.count(term), polished.count(term)
        if n0 != n1:
            failures.append("protected term %r appears %d time(s) in the original and %d after" % (term, n0, n1))
    for label, rx in (("hedges", hedge_regex(lang)), ("negations", negation_regex(lang))):
        if rx is None:
            continue  # no list for this language; ppe.languages.supported_note() records it
        n0, n1 = _count(rx, original, lang), _count(rx, polished, lang)
        checks[label] = {"original": n0, "polished": n1}
        if n0 != n1:
            warnings.append("%s changed from %d to %d; confirm no claim got stronger or weaker" % (label, n0, n1))
    ratio = round(len(polished.strip()) / max(1, len(original.strip())), 3)
    if not (LENGTH_RANGE[0] <= ratio <= LENGTH_RANGE[1]):
        warnings.append("length is %.0f%% of the original; confirm nothing substantive was cut or added" % (ratio * 100))
    status = "FAIL" if failures else ("REVIEW" if warnings else "PASS")
    return {"status": status, "checks": checks, "failures": failures, "warnings": warnings, "length_ratio": ratio}
