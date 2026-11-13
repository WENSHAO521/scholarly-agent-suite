"""Locate templated phrasing in a text and measure how dense it is.

``diagnose(text)`` returns every catalog match (ppe.patterns) plus the
structural habits the catalog cannot express as a phrase: paragraphs or
consecutive sentences that open the same way, paragraphs whose sentences
all run the same length, reflexive three-item lists, dash habits, and two
signs of defensive writing -- a sentence carrying three or more hedges,
and a paragraph in which nearly every sentence is hedged
(references/defensive-writing.md).
Citations, quotations, URLs, DOIs, and formulas are masked first, so a
phrase quoted from a source is never flagged. Any language works: phrase
findings need a catalog (ppe.patterns), structural findings do not.

``pattern_load`` (low / moderate / high) summarizes weighted findings per
1,000 words, or per 1,000 characters for languages written without spaces
(Chinese, Japanese, Thai). It describes this
text's phrasing and nothing else (ppe.POLISH_NOTICE). ``defensive`` counts
the findings in ppe.DEFENSIVE_CATEGORIES, and ``hedge_rate`` is the share
of sentences that carry at least one hedge (None for a language without a
hedge list): a high rate is a prompt to ask what evidence each hedge
answers to, not a target to drive to zero.
"""

from __future__ import annotations

import re
import statistics
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

from ppe import DEFENSIVE_CATEGORIES
from ppe.invariants import protected_spans
from ppe.languages import (CONNECTIVE_OPENERS, detect_language, hedge_regex, sentence_splitter,
                           triplet_regex, uses_char_units)
from ppe.patterns import patterns_for

WEIGHTS = {"remove": 3, "revise": 2, "watch": 1}
LOAD_THRESHOLDS = (4.0, 10.0)  # density below 4 = low, below 10 = moderate, else high

_DASH = re.compile(r"—|(?<=\w) -- (?=\w)|(?<=\w)--(?=\w)")
_CHAR = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff\u0e00-\u0e7f]")
_WORD = re.compile(r"[^\W_]+(?:['’-][^\W_]+)*")
_NO_DASH_CHECK = {"zh", "ja", "ko"}
# Defensive-writing thresholds: hedges in one sentence before it reads as a
# pile-up, and the share of hedged sentences (in a paragraph of at least
# BLANKET_MIN_SENTENCES) before the hedging stops marking real uncertainty.
PILEUP_HEDGES = 3
BLANKET_SHARE = 0.75
BLANKET_MIN_SENTENCES = 3


def _mask(text: str) -> str:
    chars = list(text)
    for start, end in protected_spans(text):
        for i in range(start, end):
            if chars[i] != "\n":
                chars[i] = " "
    return "".join(chars)


def _paragraphs(text: str) -> List[Tuple[int, str]]:
    """(offset, paragraph) pairs. Blank lines separate paragraphs; without
    any blank line, each non-empty line is a paragraph."""
    sep = r"\n\s*\n" if re.search(r"\n\s*\n", text) else r"\n"
    out, pos = [], 0
    for m in re.finditer(sep, text):
        out.append((pos, text[pos:m.start()]))
        pos = m.end()
    out.append((pos, text[pos:]))
    return [(o, p) for o, p in out if p.strip()]


def _sentences(paragraph: str, lang: str) -> List[Tuple[int, str]]:
    splitter = sentence_splitter(lang)
    out, pos = [], 0
    for m in splitter.finditer(paragraph):
        if m.end() > pos:
            out.append((pos, paragraph[pos:m.end()]))
            pos = m.end()
    out.append((pos, paragraph[pos:]))
    return [(o, s) for o, s in out if s.strip()]


def _units(text: str, lang: str) -> int:
    return len(_CHAR.findall(text)) if uses_char_units(lang) else len(_WORD.findall(text))


def _opener(sentence: str, lang: str) -> str:
    s = sentence.strip().lstrip("\"“‘«„(（「¿¡")
    if uses_char_units(lang):
        head = re.split(r"[，,、：:]", s, maxsplit=1)[0]
        return head if len(head) <= 4 else s[:2]
    words = _WORD.findall(s.lower())
    if len(words) >= 2 and " ".join(words[:2]) in CONNECTIVE_OPENERS.get(lang, ()):
        return " ".join(words[:2])
    return words[0] if words else ""


def _finding(kind_id, category, severity, para, sent, start, end, text, hint):
    return {
        "id": kind_id, "category": category, "severity": severity,
        "paragraph": para, "sentence": sent, "start": start, "end": end,
        "excerpt": text[start:end].strip()[:160], "hint": hint, "recurring": False,
    }


def diagnose(text: str, lang: Optional[str] = None) -> Dict[str, object]:
    """Findings, counts by category, density, pattern load, and the
    defensive-writing figures (``defensive``, ``hedge_rate``) for ``text``."""
    lang = lang or detect_language(text)
    masked = _mask(text)
    patterns = [(p, p.compiled()) for p in patterns_for(lang)]
    hedge_rx = hedge_regex(lang)
    hedge_c = re.compile(hedge_rx, 0 if lang in ("zh", "ja", "ko") else re.IGNORECASE) if hedge_rx else None
    findings: List[Dict[str, object]] = []
    para_openers: List[Tuple[int, int, str]] = []
    n_sentences = n_hedged = 0

    for pi, (poff, para) in enumerate(_paragraphs(masked)):
        sentences = _sentences(para, lang)
        prev_open, run = None, 0
        hedged_here = 0
        for si, (soff, sent) in enumerate(sentences):
            base = poff + soff
            if hedge_c is not None:
                n_hedges = len(hedge_c.findall(sent))
                n_sentences += 1
                if n_hedges:
                    n_hedged += 1
                    hedged_here += 1
                if n_hedges >= PILEUP_HEDGES:
                    findings.append(_finding("struct-hedge-pileup", "hedge-blanket", "revise", pi, si,
                                             base, base + len(sent), text,
                                             "%d hedges in one sentence; keep the one the evidence needs, "
                                             "on the claim it qualifies" % n_hedges))
            for pat, rx in patterns:
                for m in rx.finditer(sent):
                    findings.append(_finding(pat.id, pat.category, pat.severity, pi, si,
                                             base + m.start(), base + m.end(), text, pat.hint))
            op = _opener(sent, lang)
            if si == 0:
                para_openers.append((pi, base, op))
            run = run + 1 if op and op == prev_open else 1
            if run == 3:
                findings.append(_finding("struct-sentence-opener-run", "repeated-opener", "revise", pi, si,
                                         base, base + len(sent), text,
                                         "three sentences in a row open with %r; vary the entry point" % op))
            prev_open = op
        if (hedge_c is not None and len(sentences) >= BLANKET_MIN_SENTENCES
                and hedged_here / len(sentences) >= BLANKET_SHARE):
            findings.append(_finding("struct-hedge-blanket", "hedge-blanket", "revise", pi, 0,
                                     poff, poff + len(para), text,
                                     "%d of %d sentences are hedged; state the well-supported ones plainly so "
                                     "the hedges left mark real uncertainty" % (hedged_here, len(sentences))))
        lengths = [_units(s, lang) for _, s in sentences]
        if len(lengths) >= 5 and statistics.mean(lengths) > 0:
            cv = statistics.pstdev(lengths) / statistics.mean(lengths)
            if cv < 0.25:
                findings.append(_finding("struct-uniform-rhythm", "uniform-rhythm", "watch", pi, 0,
                                         poff, poff + len(para), text,
                                         "sentence lengths barely vary (CV %.2f); let one sentence run long "
                                         "or land short where the argument turns" % cv))
        triplet = triplet_regex(lang)
        for m in (triplet.finditer(para) if triplet else ()):
            findings.append(_finding("struct-triplet", "triplet-habit", "watch", pi, 0,
                                     poff + m.start(), poff + m.end(), text,
                                     "three-item list; keep it only if there really are three"))
        if lang not in _NO_DASH_CHECK:
            for m in _DASH.finditer(para):
                findings.append(_finding("struct-dash", "dash-habit", "watch", pi, 0,
                                         poff + m.start(), poff + m.end(), text,
                                         "dash; a comma, colon, or new sentence is often plainer"))

    connectives = CONNECTIVE_OPENERS.get(lang, set())
    by_opener: Dict[str, List[Tuple[int, int]]] = defaultdict(list)
    for pi, off, op in para_openers:
        if op:
            by_opener[op].append((pi, off))
    for op, where in by_opener.items():
        limit = 1 if op in connectives else 2
        for pi, off in where[limit:]:
            findings.append(_finding("struct-paragraph-opener", "repeated-opener", "revise", pi, 0,
                                     off, off + len(op) + 1, text,
                                     "%d paragraphs open with %r" % (len(where), op)))

    # Watch-level habits count only once they recur; triplets and dashes
    # need three in the text before the first one counts.
    per_id = Counter(f["id"] for f in findings)
    free = {"struct-triplet": 2, "struct-dash": 3}
    seen: Counter = Counter()
    weighted = 0
    for f in sorted(findings, key=lambda f: f["start"]):
        seen[f["id"]] += 1
        f["recurring"] = per_id[f["id"]] > 1
        if f["severity"] != "watch":
            weighted += WEIGHTS[f["severity"]]
        elif seen[f["id"]] > free.get(f["id"], 1):
            weighted += WEIGHTS["watch"]
    findings.sort(key=lambda f: (f["start"], f["id"]))

    units = _units(text, lang)
    density = round(weighted * 1000.0 / max(units, 1), 2)
    must_remove = sum(1 for f in findings if f["severity"] == "remove")
    if must_remove or density >= LOAD_THRESHOLDS[1]:
        load = "high"
    elif density >= LOAD_THRESHOLDS[0]:
        load = "moderate"
    else:
        load = "low"
    return {
        "language": lang,
        "catalog": bool(patterns),
        "unit": "chars" if uses_char_units(lang) else "words",
        "units": units,
        "findings": findings,
        "by_category": dict(sorted(Counter(f["category"] for f in findings).items())),
        "weighted": weighted,
        "density": density,
        "pattern_load": load,
        "must_remove": must_remove,
        "defensive": sum(1 for f in findings if f["category"] in DEFENSIVE_CATEGORIES),
        "hedge_rate": round(n_hedged / n_sentences, 2) if n_sentences else None,
    }


def defensive_findings(diagnosis: Dict[str, object]) -> List[Dict[str, object]]:
    """Only the findings that belong to defensive writing."""
    return [f for f in diagnosis["findings"] if f["category"] in DEFENSIVE_CATEGORIES]


def summary(diagnosis: Dict[str, object]) -> Dict[str, object]:
    """The compact form recorded in POLISH_REPORT_V1."""
    keys = ("pattern_load", "density", "by_category", "must_remove", "units", "defensive", "hedge_rate")
    return {k: diagnosis[k] for k in keys}
