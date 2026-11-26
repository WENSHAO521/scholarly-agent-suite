"""What translation must carry across unchanged, and the check that it did.

A translation re-expresses every sentence in another language. Some things
must come out the other side exactly as they went in, whatever the language
pair: DOIs, URLs, formulas, inline code, numbered citation markers, the
years and author names of every citation, and every number written in
digits. Others are compared by count and flagged for a human look: direct
quotations, paragraphs, hedges, negations, and text left in the source
script (references/translation-passes.md, "Verify").

``FAIL`` means something that must survive was lost, added, or altered, or
the target is not in the requested language. ``REVIEW`` means something
moved that is sometimes legitimate (a merged paragraph, a number written
with 萬 / 億, a translated quotation) and needs a sentence of explanation.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter
from typing import Dict, Iterable, List, Optional, Tuple

from tre.languages import (
    base_language, detect_language, hedge_regex, negation_regex, paragraphs, same_script,
    script_of, script_regex, units, variety_mismatches,
)

_FULLWIDTH = str.maketrans("０１２３４５６７８９％．", "0123456789%.")
_YEAR = r"(?:1[5-9]\d{2}|20\d{2})[a-z]?"
CITATION_RES = [
    re.compile(r"\([^()\n]{0,200}?\b" + _YEAR + r"\b[^()\n]{0,200}?\)"),
    re.compile(r"（[^（）\n]{0,200}?" + _YEAR + r"[^（）\n]{0,200}?）"),
]
NUMBERED_CITATION_RE = re.compile(r"\[\d+(?:\s*[-–,]\s*\d+)*\]")
DOI_RE = re.compile(r"\b10\.\d{4,9}/[^\s\"<>，。、；）)\]]+")
URL_RE = re.compile(r"https?://[^\s<>，。、；）)\]]+")
MATH_RES = [re.compile(r"\$[^$\n]{1,300}\$"), re.compile(r"\\\([^\n]{1,300}?\\\)"),
            re.compile(r"\\\[[^\n]{1,600}?\\\]")]
CODE_RE = re.compile(r"`[^`\n]{1,200}`")
QUOTATION_RES = [re.compile(r) for r in (
    r"“[^”\n]{1,600}”", r"「[^」\n]{1,600}」", r"『[^』\n]{1,600}』", r"\"[^\"\n]{1,600}\"",
    r"«[^»\n]{1,600}»", r"„[^“”\n]{1,600}[“”]", r"‹[^›\n]{1,600}›")]
NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_])\d+(?:[.,]\d+|[\u00a0\u202f ]\d{3}(?!\d))*")
CJK_NUMBER_UNITS = re.compile(r"\d\s*(?:萬|万|億|亿|兆|千|百|만|억|천)")
_NAME_RE = re.compile(r"\b([A-Z][A-Za-zÀ-ɏ'’\-]{1,40})")
_NAME_STOP = {"In", "See", "Cf", "Eds", "Ed", "Vol", "No", "And", "Et", "Al", "Pp", "P", "Ibid", "Table",
              "Figure", "Fig", "Chapter", "Appendix", "Note", "Also", "For", "The", "On", "Of", "Forthcoming",
              "Press", "In press", "Unpublished", "Supplementary"}

LENGTH_OUTLIER = (0.5, 2.0)   # a paragraph's target/source ratio relative to the median
MIN_PARAGRAPH_CHARS = 40       # shorter paragraphs are too noisy to compare


def _norm(text: str) -> str:
    return text.translate(_FULLWIDTH).replace("−", "-")


def _strip(item: str) -> str:
    return item.rstrip(".,;:")


def _spans(text: str, regexes) -> List[Tuple[int, int]]:
    return sorted(m.span() for rx in regexes for m in rx.finditer(text))


def _blank(text: str, spans: List[Tuple[int, int]]) -> str:
    chars = list(text)
    for a, b in spans:
        for i in range(a, b):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def citations(text: str) -> List[str]:
    return [m.group(0) for rx in CITATION_RES for m in rx.finditer(_norm(text))]


def citation_names(text: str) -> List[str]:
    """Latin-script author names cited in ``text``: capitalized words inside
    a parenthetical citation, and the word right before a ``(year)``."""
    text = _norm(text)
    names = []
    for c in citations(text):
        names += [n for n in _NAME_RE.findall(c) if n not in _NAME_STOP]
    for m in re.finditer(r"([A-Z][A-Za-zÀ-ɏ'’\-]{1,40})(?:\s+(?:et al\.?|等人?|ら|외))?\s*[(（]" + _YEAR, text):
        if m.group(1) not in _NAME_STOP:
            names.append(m.group(1))
    return sorted(set(names))


def extract(text: str) -> Dict[str, List[str]]:
    """Every item a translation must carry across, by kind."""
    text = _norm(text)
    fixed = _spans(text, [DOI_RE, URL_RE, CODE_RE, *MATH_RES])
    rest = _blank(text, fixed)
    years = []
    for c in citations(text):
        years += re.findall(r"(?<!\d)" + _YEAR + r"(?!\d)", c)
    return {
        "dois": sorted(_strip(m.group(0)) for m in DOI_RE.finditer(text)),
        "urls": sorted(_strip(m.group(0)) for m in URL_RE.finditer(text)),
        "math": sorted(m.group(0) for rx in MATH_RES for m in rx.finditer(text)),
        "code": sorted(m.group(0) for m in CODE_RE.finditer(text)),
        "numbered_citations": sorted(re.sub(r"\s+", "", m.group(0)) for m in NUMBERED_CITATION_RE.finditer(text)),
        "citation_years": sorted(years),
        "numbers": sorted(re.sub(r"\D", "", m.group(0)).lstrip("0") or "0" for m in NUMBER_RE.finditer(rest)),
    }


def quotation_count(text: str) -> int:
    return len(_spans(text, QUOTATION_RES))


def _diff(a: List[str], b: List[str]) -> Tuple[List[str], List[str]]:
    ca, cb = Counter(a), Counter(b)
    return sorted((ca - cb).elements()), sorted((cb - ca).elements())


def untranslated_runs(source_lang: str, target_lang: str, target: str, keep: Iterable[str] = ()) -> List[str]:
    """Stretches of the target still written in the source language's
    script, outside parentheses (where an original term is often glossed),
    quotations, citations, and terms deliberately kept. Empty when both
    languages share a script: that case is left to the reviewer."""
    if same_script(source_lang, target_lang):
        return []
    text = _norm(target)
    skip = _spans(text, [DOI_RE, URL_RE, CODE_RE, *MATH_RES, *QUOTATION_RES, *CITATION_RES,
                         re.compile(r"\([^()\n]{0,120}\)"), re.compile(r"（[^（）\n]{0,120}）")])
    text = _blank(text, skip)
    for term in keep:
        if term:
            text = text.replace(term, " " * len(term))
    script = script_of(source_lang)
    rx = script_regex(source_lang)
    if script == "latin":
        # Names, acronyms, and single terms are normal in any target; flag
        # only four or more consecutive Latin-script words.
        runs = re.findall(r"(?:[A-Za-zÀ-ɏ][\w'’\-]*[ ,;:]+){3,}[A-Za-zÀ-ɏ][\w'’\-]*", text)
    else:
        cls = rx.pattern
        runs = re.findall(cls + r"{2,}(?:[\s\-]?" + cls + r"+)*", text)
    return [r.strip() for r in runs if r.strip()]


def check_translation(source: str, target: str, source_lang: str, target_lang: str,
                      variety: Optional[str] = None, keep_terms: Iterable[str] = ()) -> Dict[str, object]:
    """Compare a translation with its source.

    Returns ``{"status", "checks", "failures", "warnings", "untranslated",
    "paragraphs"}``. Language codes are ISO 639-1, optionally with a
    region or script (``zh-Hant``, ``pt-BR``); ``variety`` is checked for
    Chinese (Traditional vs Simplified characters).
    """
    keep_terms = [t for t in keep_terms if t]
    a, b = extract(source), extract(target)
    checks: Dict[str, Dict[str, object]] = {}
    failures: List[str] = []
    warnings: List[str] = []

    cjk_units = bool(CJK_NUMBER_UNITS.search(_norm(source)) or CJK_NUMBER_UNITS.search(_norm(target)))
    for kind in ("dois", "urls", "math", "code", "numbered_citations", "citation_years", "numbers"):
        missing, added = _diff(a[kind], b[kind])
        checks[kind] = {"source": len(a[kind]), "target": len(b[kind]), "missing": missing, "added": added}
        if not (missing or added):
            continue
        msg = "%s %s in translation: missing %s, added %s" % (
            kind.replace("_", " "), "changed", missing[:6], added[:6])
        if kind == "numbers" and cjk_units:
            warnings.append(msg + " (萬/億-style units present: confirm each value converted correctly)")
        else:
            failures.append(msg)

    names = citation_names(source)
    lost = [n for n in names if n not in _norm(target)]
    checks["citation_names"] = {"source": len(names), "missing": lost}
    if lost:
        failures.append("cited author names missing from the translation (keep them in their original "
                        "script; a transliteration may be added beside them): %s" % lost[:8])

    q0, q1 = quotation_count(source), quotation_count(target)
    checks["quotations"] = {"source": q0, "target": q1}
    if q0 != q1:
        warnings.append("direct quotations: %d in the source, %d in the translation; each quotation needs "
                        "its original kept or a 'translation mine' note" % (q0, q1))

    guess = detect_language(target)
    tl = base_language(target_lang)
    if not same_script(guess, tl):
        failures.append("the translation reads as %r, not the requested %r" % (guess, target_lang))
    elif script_of(tl) == "latin" and guess != tl and len(target) > 200:
        warnings.append("the translation's function words look like %r rather than %r; confirm the language" % (guess, tl))

    wrong = variety_mismatches(target, variety)
    checks["variety"] = {"variety": variety, "mismatched_characters": wrong[:20]}
    if wrong:
        warnings.append("%s requested, but the translation contains characters of the other Chinese script: %s"
                        % (variety, "".join(wrong[:20])))

    runs = untranslated_runs(source_lang, target_lang, target, keep_terms)
    if runs:
        warnings.append("%d stretch(es) still in the source script outside parentheses and quotations: %s"
                        % (len(runs), runs[:5]))

    ps, pt = paragraphs(source), paragraphs(target)
    para = {"source": len(ps), "target": len(pt), "flagged": []}
    if len(ps) != len(pt):
        warnings.append("paragraphs: %d in the source, %d in the translation; check for an omitted, added, "
                        "or merged paragraph" % (len(ps), len(pt)))
    else:
        ratios = []
        for s, t in zip(ps, pt):
            ratios.append(len(t) / len(s) if len(s) >= MIN_PARAGRAPH_CHARS else None)
        known = [r for r in ratios if r]
        if len(known) >= 3:
            med = statistics.median(known)
            for i, r in enumerate(ratios, 1):
                if r and not (LENGTH_OUTLIER[0] * med <= r <= LENGTH_OUTLIER[1] * med):
                    para["flagged"].append(i)
            if para["flagged"]:
                warnings.append("paragraph(s) %s are much %s than the rest relative to their source; check for "
                                "omission or addition" % (para["flagged"], "shorter or longer"))
        for label, src_rx, tgt_rx in (("hedge", hedge_regex(source_lang), hedge_regex(target_lang)),
                                      ("negation", negation_regex(source_lang), negation_regex(target_lang))):
            if not (src_rx and tgt_rx):
                continue
            lost_in = [i for i, (s, t) in enumerate(zip(ps, pt), 1)
                       if re.search(src_rx, s, re.I) and not re.search(tgt_rx, t, re.I)]
            if lost_in:
                warnings.append("paragraph(s) %s have a %s in the source and none in the translation; confirm "
                                "no claim got stronger%s" % (lost_in, label, "" if label == "hedge" else " or reversed"))
    para["source_units"] = units(source, source_lang)
    para["target_units"] = units(target, target_lang)

    status = "FAIL" if failures else ("REVIEW" if warnings else "PASS")
    return {"status": status, "checks": checks, "failures": failures, "warnings": warnings,
            "untranslated": runs, "paragraphs": para}
