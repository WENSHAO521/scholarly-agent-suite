"""Terminology: find the terms a translation must render consistently, and
check that it did.

A glossary is a list of entries ``{"source": ..., "target": ...}`` (render
this term this way, every time) or ``{"source": ..., "keep": true}`` (leave
it exactly as written: acronyms, gene and software names, legal citations,
a term the author wants kept in the original). Load one from JSON (a list of
entries, or an object mapping source to target) or from a two-column TSV;
a TSV row whose second column is ``=`` or empty means keep.
See references/terminology.md.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Union

from tre.languages import base_language, uses_char_units

Entry = Dict[str, object]

_ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]{1,7}s?\b")
_DEFINED = [
    # "public value (PV)", 「公共價值（public value）」, hereafter, 以下簡稱, 下称
    re.compile(r"([A-Za-z][A-Za-z\- ]{2,60}?)\s*\(([A-Z][A-Za-z0-9]{1,9})\)"),
    re.compile(r"[「“\"]([^」”\"\n]{1,30})[」”\"]\s*[(（]([A-Za-z][^)）\n]{1,60})[)）]"),
    re.compile(r"(?:以下簡稱|以下简称|下稱|下称|簡稱|简称)\s*[「“\"]?([^」”\"，。,)）\s]{1,20})"),
    re.compile(r"\b(?:hereafter|henceforth|referred to as)\s+[“\"']?([A-Za-z][A-Za-z\- ]{1,40}?)[”\"']?[,.;)]"),
]
_STOP_EN = set("the a an of and or to in on for with by from as at is are was were be this that these those "
               "we our it its their which who whom whose not no can may might will would should".split())


def load_glossary(source: Union[str, Path, List[Entry], Dict[str, str]]) -> List[Entry]:
    """Read a glossary from a path (``.json`` or ``.tsv``) or from data."""
    if isinstance(source, (str, Path)) and Path(source).exists():
        path = Path(source)
        text = path.read_text(encoding="utf-8")
        if path.suffix.lower() == ".json":
            return normalize(json.loads(text))
        rows = []
        for line in text.splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            cols = line.split("\t")
            src, tgt = cols[0].strip(), (cols[1].strip() if len(cols) > 1 else "")
            rows.append({"source": src, "keep": True} if tgt in ("", "=") else {"source": src, "target": tgt})
        return normalize(rows)
    return normalize(source)  # type: ignore[arg-type]


def normalize(data) -> List[Entry]:
    if isinstance(data, dict):
        data = [{"source": k, "target": v} if v not in (None, "", "=") else {"source": k, "keep": True}
                for k, v in data.items()]
    out = []
    for e in data or []:
        if not isinstance(e, dict) or not str(e.get("source", "")).strip():
            raise ValueError("glossary entry needs a non-empty 'source': %r" % (e,))
        entry: Entry = {"source": str(e["source"]).strip()}
        if e.get("keep") or not str(e.get("target", "")).strip():
            entry["keep"] = True
        else:
            entry["target"] = str(e["target"]).strip()
        if e.get("note"):
            entry["note"] = str(e["note"])
        out.append(entry)
    return out


def _count(term: str, text: str) -> int:
    if re.search(r"[A-Za-z]", term) and not re.search(r"[^\x00-\x7f]", term):
        return len(re.findall(r"(?<![A-Za-z])" + re.escape(term) + r"(?![a-z])", text, re.I if term.islower() else 0))
    return text.count(term)


def term_candidates(text: str, lang: str = "en", limit: int = 40) -> List[Dict[str, object]]:
    """Terms worth fixing in a glossary before translating: acronyms,
    terms the text defines or glosses, and recurring multi-word terms.
    A starting list for the translator and the author, not a glossary."""
    found: Counter = Counter()
    kinds: Dict[str, str] = {}
    for m in _ACRONYM.finditer(text):
        a = m.group(0).rstrip("s") if m.group(0).endswith("s") and m.group(0)[:-1].isupper() else m.group(0)
        found[a] += 1
        kinds.setdefault(a, "acronym")
    for rx in _DEFINED:
        for m in rx.finditer(text):
            for g in m.groups():
                g = (g or "").strip()
                if len(g) >= 2:
                    found[g] += 1
                    kinds[g] = "defined"
    if uses_char_units(lang):
        # Recurring 2-6 character Han strings; the longest recurring form wins.
        runs = re.findall(r"[一-鿿]{2,}", text)
        grams: Counter = Counter()
        for run in runs:
            for n in range(2, 7):
                for i in range(len(run) - n + 1):
                    grams[run[i:i + n]] += 1
        chosen: List[str] = [k for k, v in kinds.items() if v == "defined"]
        for g in sorted((g for g, n in grams.items() if n >= 3), key=lambda g: (-len(g), -grams[g], g)):
            if any(g in c for c in chosen):
                continue
            chosen.append(g)
            found[g] += grams[g]
            kinds.setdefault(g, "recurring")
    elif base_language(lang) == "en":
        words = re.findall(r"[A-Za-z][a-z\-]+", text)
        bigrams: Counter = Counter()
        for i in range(len(words) - 1):
            w1, w2 = words[i].lower(), words[i + 1].lower()
            if w1 not in _STOP_EN and w2 not in _STOP_EN and len(w1) > 3 and len(w2) > 3:
                bigrams[w1 + " " + w2] += 1
        for g, n in bigrams.items():
            if n >= 3:
                found[g] += n
                kinds.setdefault(g, "recurring")
    ranked = sorted(found.items(), key=lambda kv: ({"defined": 0, "acronym": 1}.get(kinds[kv[0]], 2), -kv[1], kv[0]))
    return [{"term": t, "kind": kinds[t], "count": n} for t, n in ranked[:limit]]


def check_glossary(source: str, target: str, glossary: Iterable[Entry]) -> List[Dict[str, object]]:
    """One result per entry: ``kept`` (rendered or kept as the glossary
    says), ``missing`` (the source uses the term but the required rendering
    never appears), ``count-differs`` (it appears fewer times than the
    source term; fine when a pronoun or ellipsis does the work, otherwise a
    drifting translation), or ``not-in-source``."""
    results = []
    for e in normalize(list(glossary)):
        n_src = _count(str(e["source"]), source)
        want = str(e["source"] if e.get("keep") else e["target"])
        n_tgt = _count(want, target)
        if n_src == 0:
            status = "not-in-source"
        elif n_tgt == 0:
            status = "missing"
        elif n_tgt < n_src:
            status = "count-differs"
        else:
            status = "kept"
        r = {"source": e["source"], "expected": want, "source_count": n_src, "target_count": n_tgt,
             "status": status}
        if e.get("keep"):
            r["keep"] = True
        results.append(r)
    return results
