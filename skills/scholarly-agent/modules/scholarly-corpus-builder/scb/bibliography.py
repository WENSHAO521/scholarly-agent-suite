"""Reference-manager import and export: BibTeX, RIS, and CSL-JSON.

These three formats cover the export options of Zotero, Mendeley, EndNote,
JabRef, and most citation managers, so a user's existing library can become
a corpus seed list or a citation source without retyping it. See
references/reference-managers.md for when and how to use it.

Integrity rules (shared/integrity-policy.md, shared/provenance-policy.md):

- Imported metadata is *user-supplied*, not verified. Every record gets a
  ``ProvenanceEntry`` with ``verification="NEEDS_CHECK"``; nothing here
  ever marks a record VERIFIED. Verify through an adapter lookup (Crossref,
  OpenAlex, PubMed) before a record supports a material claim.
- Fields that do not parse (a malformed DOI, a non-numeric year) are left
  empty and reported in ``record.conflicts``, never guessed.
- Local only: this module makes no network call.

Standard library only.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, Iterable, List, Optional, Tuple

from scb.identifiers import normalize_doi, normalize_issn, normalize_pmcid, normalize_pmid
from scb.records import CanonicalRecord, Identifiers, ProvenanceEntry

ADAPTER_NAME = "user_bibliography"

FORMAT_BY_EXTENSION = {
    ".bib": "bibtex",
    ".bibtex": "bibtex",
    ".ris": "ris",
    ".json": "csl-json",
    ".csljson": "csl-json",
}

# BibTeX entry type -> internal work_type (Crossref/CSL-style names, the same
# vocabulary the Crossref and OpenAlex adapters already emit).
_BIBTEX_TO_WORK_TYPE = {
    "article": "journal-article",
    "book": "book",
    "inbook": "book-chapter",
    "incollection": "book-chapter",
    "inproceedings": "proceedings-article",
    "conference": "proceedings-article",
    "phdthesis": "dissertation",
    "mastersthesis": "dissertation",
    "thesis": "dissertation",
    "techreport": "report",
    "report": "report",
    "unpublished": "manuscript",
    "online": "webpage",
    "misc": "other",
}
_WORK_TYPE_TO_BIBTEX = {
    "journal-article": "article",
    "book": "book",
    "book-chapter": "incollection",
    "proceedings-article": "inproceedings",
    "dissertation": "phdthesis",
    "report": "techreport",
    "manuscript": "unpublished",
    "webpage": "online",
    "preprint": "misc",
}

_RIS_TO_WORK_TYPE = {
    "JOUR": "journal-article",
    "JFULL": "journal-article",
    "EJOUR": "journal-article",
    "BOOK": "book",
    "EBOOK": "book",
    "CHAP": "book-chapter",
    "ECHAP": "book-chapter",
    "CONF": "proceedings-article",
    "CPAPER": "proceedings-article",
    "THES": "dissertation",
    "RPRT": "report",
    "UNPB": "manuscript",
    "ELEC": "webpage",
    "GEN": "other",
}
_WORK_TYPE_TO_RIS = {
    "journal-article": "JOUR",
    "book": "BOOK",
    "book-chapter": "CHAP",
    "proceedings-article": "CPAPER",
    "dissertation": "THES",
    "report": "RPRT",
    "manuscript": "UNPB",
    "webpage": "ELEC",
    "preprint": "UNPB",
}

_CSL_TO_WORK_TYPE = {
    "article-journal": "journal-article",
    "book": "book",
    "chapter": "book-chapter",
    "paper-conference": "proceedings-article",
    "thesis": "dissertation",
    "report": "report",
    "manuscript": "manuscript",
    "webpage": "webpage",
    "post-weblog": "webpage",
}
_WORK_TYPE_TO_CSL = {
    "journal-article": "article-journal",
    "book": "book",
    "book-chapter": "chapter",
    "proceedings-article": "paper-conference",
    "dissertation": "thesis",
    "report": "report",
    "manuscript": "manuscript",
    "webpage": "webpage",
    "preprint": "article",
}

_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}


class BibliographyFormatError(ValueError):
    """The input is not in the declared format at all (as opposed to one
    entry with a bad field, which is recorded as a conflict)."""


# --------------------------------------------------------------------------
# Shared helpers
# --------------------------------------------------------------------------

def _person(given: str, family: str, literal: str = "") -> Dict[str, Any]:
    given, family, literal = given.strip(), family.strip(), literal.strip()
    name = literal or " ".join(p for p in (given, family) if p)
    person: Dict[str, Any] = {"name": name, "orcid": None}
    if family:
        person["family"] = family
    if given:
        person["given"] = given
    return person


def _split_name(raw: str) -> Dict[str, Any]:
    """'Family, Given' or 'Given Family' -> author dict. A name wrapped in
    braces in BibTeX (an institution) arrives here already unbraced and
    without a comma; keep multi-word institutional names whole when flagged
    by the caller via a literal."""
    raw = " ".join(raw.split())
    if "," in raw:
        family, given = raw.split(",", 1)
        return _person(given, family)
    parts = raw.split(" ")
    if len(parts) == 1:
        return _person("", parts[0])
    return _person(" ".join(parts[:-1]), parts[-1])


def _year(raw: Optional[str], record_conflicts: List[Dict[str, Any]], field: str) -> Optional[int]:
    if raw is None or str(raw).strip() == "":
        return None
    m = re.search(r"\b(\d{4})\b", str(raw))
    if not m:
        record_conflicts.append({"field": field, "value": str(raw), "issue": "unparseable year; left empty"})
        return None
    return int(m.group(1))


def _doi(raw: Optional[str], conflicts: List[Dict[str, Any]]) -> Optional[str]:
    if not raw:
        return None
    doi = normalize_doi(raw)
    if doi is None:
        conflicts.append({"field": "doi", "value": raw, "issue": "malformed DOI; left empty"})
    return doi


def _issns(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    out = []
    for part in re.split(r"[,;\s]+", raw):
        issn = normalize_issn(part)
        if issn and issn not in out:
            out.append(issn)
    return out


def _keywords(raw: Optional[str]) -> List[str]:
    if not raw:
        return []
    return [k.strip() for k in re.split(r"[;,]", raw) if k.strip()]


def _record_id(prefix: str, key: Optional[str], doi: Optional[str], index: int) -> str:
    if doi:
        return "%s:doi:%s" % (prefix, doi)
    if key:
        return "%s:%s" % (prefix, key)
    return "%s:%d" % (prefix, index)


def _provenance(operation: str, key: Optional[str]) -> ProvenanceEntry:
    return ProvenanceEntry(
        adapter=ADAPTER_NAME,
        operation=operation,
        source_identifier=key,
        verification="NEEDS_CHECK",
    )


# --------------------------------------------------------------------------
# BibTeX
# --------------------------------------------------------------------------

_LATEX_ACCENTS = {
    '"': {"a": "ä", "o": "ö", "u": "ü", "A": "Ä", "O": "Ö", "U": "Ü", "e": "ë", "i": "ï"},
    "'": {"a": "á", "e": "é", "i": "í", "o": "ó", "u": "ú", "E": "É", "A": "Á", "c": "ć", "n": "ń", "s": "ś", "z": "ź"},
    "`": {"a": "à", "e": "è", "i": "ì", "o": "ò", "u": "ù", "A": "À", "E": "È"},
    "^": {"a": "â", "e": "ê", "i": "î", "o": "ô", "u": "û"},
    "~": {"n": "ñ", "a": "ã", "o": "õ", "N": "Ñ"},
    "c": {"c": "ç", "C": "Ç", "s": "ş"},
    "v": {"c": "č", "s": "š", "z": "ž", "C": "Č", "S": "Š", "Z": "Ž", "r": "ř", "e": "ě"},
}
_LATEX_SYMBOLS = {r"\&": "&", r"\%": "%", r"\$": "$", r"\_": "_", r"\#": "#", r"\ss": "ß",
                  r"\o": "ø", r"\O": "Ø", r"\ae": "æ", r"\AE": "Æ", r"\aa": "å", r"\AA": "Å", r"\l": "ł", r"\L": "Ł"}


def _delatex(value: str) -> str:
    def accent(m: "re.Match[str]") -> str:
        table = _LATEX_ACCENTS.get(m.group(1), {})
        return table.get(m.group(2), m.group(2))

    value = re.sub(r"\\([\"'`^~cv])\s*\{?\\?([A-Za-z])\}?", accent, value)
    for latex, char in sorted(_LATEX_SYMBOLS.items(), key=lambda kv: -len(kv[0])):
        value = re.sub(re.escape(latex) + r"(?![A-Za-z])", lambda _m, c=char: c, value)
    value = value.replace("{", "").replace("}", "")
    value = value.replace("~", " ")
    return " ".join(value.split())


def _bibtex_entries(text: str) -> Iterable[Tuple[str, str, Dict[str, str]]]:
    """Yield (entry_type, key, raw_fields) for each regular entry, with
    @string macros expanded. @comment and @preamble are skipped."""
    macros: Dict[str, str] = {m: m.capitalize() for m in _MONTHS}
    pos = 0
    n = len(text)
    while True:
        at = text.find("@", pos)
        if at < 0:
            return
        m = re.match(r"@\s*([A-Za-z]+)\s*([({])", text[at:])
        if not m:
            pos = at + 1
            continue
        entry_type = m.group(1).lower()
        open_ch = m.group(2)
        start = at + m.end()
        depth = 1
        i = start
        while i < n and depth:
            ch = text[i]
            if ch == "{" or (open_ch == "(" and ch == "("):
                depth += 1
            elif ch == "}" or (open_ch == "(" and ch == ")"):
                depth -= 1
            i += 1
        if depth:
            raise BibliographyFormatError("unterminated @%s entry starting at offset %d" % (entry_type, at))
        body = text[start:i - 1]
        pos = i
        if entry_type in ("comment", "preamble"):
            continue
        if entry_type == "string":
            fields = _bibtex_fields(body, macros)
            macros.update({k: v for k, v in fields.items()})
            continue
        key, _, rest = body.partition(",")
        yield entry_type, key.strip(), _bibtex_fields(rest, macros)


def _bibtex_fields(body: str, macros: Dict[str, str]) -> Dict[str, str]:
    fields: Dict[str, str] = {}
    i, n = 0, len(body)
    while i < n:
        m = re.compile(r"\s*,?\s*([A-Za-z][\w:-]*)\s*=\s*").match(body, i)
        if not m:
            break
        name = m.group(1).lower()
        i = m.end()
        parts: List[str] = []
        while i < n:
            ch = body[i]
            if ch == "{":
                depth, j = 1, i + 1
                while j < n and depth:
                    if body[j] == "{":
                        depth += 1
                    elif body[j] == "}":
                        depth -= 1
                    j += 1
                parts.append(body[i + 1:j - 1])
                i = j
            elif ch == '"':
                j = i + 1
                depth = 0
                while j < n and not (body[j] == '"' and depth == 0 and body[j - 1] != "\\"):
                    if body[j] == "{":
                        depth += 1
                    elif body[j] == "}":
                        depth -= 1
                    j += 1
                parts.append(body[i + 1:j])
                i = j + 1
            else:
                tok = re.compile(r"[\w:.-]+").match(body, i)
                if not tok:
                    break
                word = tok.group(0)
                parts.append(macros.get(word.lower(), word))
                i = tok.end()
            ws = re.compile(r"\s*#\s*").match(body, i)
            if ws:
                i = ws.end()
                continue
            break
        fields[name] = "".join(parts)
        comma = re.compile(r"\s*,").match(body, i)
        if comma:
            i = comma.end()
    return fields


def _bibtex_authors(raw: Optional[str]) -> List[Dict[str, Any]]:
    if not raw:
        return []
    authors = []
    for chunk in re.split(r"\s+and\s+", raw.strip()):
        chunk = chunk.strip()
        if not chunk or chunk.lower() == "others":
            continue
        if chunk.startswith("{") and chunk.endswith("}"):
            authors.append(_person("", "", _delatex(chunk)))  # institutional author
        else:
            authors.append(_split_name(_delatex(chunk)))
    return authors


def parse_bibtex(text: str) -> List[CanonicalRecord]:
    records = []
    for index, (entry_type, key, raw) in enumerate(_bibtex_entries(text)):
        conflicts: List[Dict[str, Any]] = []
        f = {k: (v if k in ("author", "editor") else _delatex(v)) for k, v in raw.items()}
        doi = _doi(f.get("doi"), conflicts)
        venue = f.get("journal") or f.get("journaltitle") or f.get("booktitle")
        if entry_type in ("phdthesis", "mastersthesis", "thesis"):
            venue = venue or f.get("school") or f.get("institution")
        month = f.get("month", "").strip().lower()[:3]
        year = _year(f.get("year") or f.get("date"), conflicts, "year")
        date = None
        if year and month in _MONTHS:
            date = "%04d-%02d" % (year, _MONTHS[month])
        elif f.get("date") and re.match(r"^\d{4}-\d{2}(-\d{2})?$", f["date"]):
            date = f["date"]
        pages = f.get("pages")
        if pages:
            pages = re.sub(r"\s*-+\s*", "-", pages)
        rec = CanonicalRecord(
            record_id=_record_id("bibtex", key, doi, index),
            title=f.get("title"),
            subtitle=f.get("subtitle"),
            authors=_bibtex_authors(raw.get("author")),
            publication_year=year,
            publication_date=date,
            venue=venue,
            publisher=f.get("publisher"),
            volume=f.get("volume"),
            issue=f.get("number") or f.get("issue"),
            pages=pages,
            work_type=_BIBTEX_TO_WORK_TYPE.get(entry_type, "other"),
            language=f.get("language") or f.get("langid"),
            identifiers=Identifiers(
                doi=doi,
                pmid=normalize_pmid(f.get("pmid")),
                pmcid=normalize_pmcid(f.get("pmcid")),
                arxiv_id=(f.get("eprint") if (f.get("archiveprefix") or f.get("eprinttype", "")).lower() == "arxiv" else None),
                issn=_issns(f.get("issn")),
                other=[{"scheme": "isbn", "value": f["isbn"]}] if f.get("isbn") else [],
            ),
            abstract=f.get("abstract"),
            keywords=_keywords(f.get("keywords")),
            conflicts=conflicts,
        )
        if f.get("url"):
            rec.access.best_url = f["url"]
        rec.versions.append({"citation_key": key, "source_format": "bibtex", "entry_type": entry_type})
        rec.add_provenance(_provenance("parse_bibtex", key))
        records.append(rec)
    return records


# --------------------------------------------------------------------------
# RIS
# --------------------------------------------------------------------------

_RIS_LINE = re.compile(r"^([A-Z][A-Z0-9])  -(?: (.*))?$")


def parse_ris(text: str) -> List[CanonicalRecord]:
    entries: List[Dict[str, List[str]]] = []
    current: Optional[Dict[str, List[str]]] = None
    last_tag: Optional[str] = None
    for line in text.lstrip("\ufeff").splitlines():
        m = _RIS_LINE.match(line.rstrip())
        if not m:
            if current is not None and last_tag and line.strip():
                current[last_tag][-1] += " " + line.strip()  # continuation line
            continue
        tag, value = m.group(1), (m.group(2) or "").strip()
        if tag == "TY":
            current = {"TY": [value]}
            entries.append(current)
        elif tag == "ER":
            current, last_tag = None, None
            continue
        elif current is not None:
            current.setdefault(tag, []).append(value)
        last_tag = tag
    if text.strip() and not entries:
        raise BibliographyFormatError("no RIS records found (each record starts with a 'TY  - ' line)")

    records = []
    for index, e in enumerate(entries):
        conflicts: List[Dict[str, Any]] = []
        first = lambda *tags: next((e[t][0] for t in tags if e.get(t)), None)  # noqa: E731
        doi = _doi(first("DO"), conflicts)
        key = first("ID")
        sp, ep = first("SP"), first("EP")
        pages = "%s-%s" % (sp, ep) if sp and ep else sp
        date_raw = first("PY", "Y1", "DA")
        year = _year(date_raw, conflicts, "year")
        date = None
        dm = re.match(r"^(\d{4})/(\d{2})(?:/(\d{2}))?", date_raw or "")
        if dm:
            date = "-".join(p for p in dm.groups() if p)
        authors = [_split_name(a) for a in e.get("AU", []) + e.get("A1", [])]
        ty = (first("TY") or "GEN").upper()
        rec = CanonicalRecord(
            record_id=_record_id("ris", key, doi, index),
            title=first("TI", "T1", "CT"),
            authors=authors,
            publication_year=year,
            publication_date=date,
            venue=first("T2", "JO", "JF", "JA", "BT"),
            publisher=first("PB"),
            volume=first("VL"),
            issue=first("IS"),
            pages=pages,
            work_type=_RIS_TO_WORK_TYPE.get(ty, "other"),
            language=first("LA"),
            identifiers=Identifiers(doi=doi, issn=_issns(" ".join(e.get("SN", [])))),
            abstract=first("AB", "N2"),
            keywords=[k for k in e.get("KW", []) if k],
            conflicts=conflicts,
        )
        if first("UR"):
            rec.access.best_url = first("UR")
        rec.versions.append({"citation_key": key, "source_format": "ris", "entry_type": ty})
        rec.add_provenance(_provenance("parse_ris", key))
        records.append(rec)
    return records


# --------------------------------------------------------------------------
# CSL-JSON (Zotero's "CSL JSON" export, Better BibTeX, pandoc/citeproc)
# --------------------------------------------------------------------------

def _csl_people(items: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    people = []
    for p in items or []:
        people.append(_person(p.get("given", ""), p.get("family", ""), p.get("literal", "")))
    return people


def parse_csl_json(text: str) -> List[CanonicalRecord]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise BibliographyFormatError("not valid CSL-JSON: %s" % exc) from exc
    if isinstance(data, dict):
        data = data.get("items", [data])
    if not isinstance(data, list):
        raise BibliographyFormatError("CSL-JSON must be a list of items")
    records = []
    for index, item in enumerate(data):
        if not isinstance(item, dict):
            raise BibliographyFormatError("CSL-JSON item %d is not an object" % index)
        conflicts: List[Dict[str, Any]] = []
        doi = _doi(item.get("DOI"), conflicts)
        key = item.get("id") if isinstance(item.get("id"), str) else (str(item["id"]) if "id" in item else None)
        parts = ((item.get("issued") or {}).get("date-parts") or [[None]])[0] or [None]
        year = None
        if parts[0] is not None:
            year = _year(str(parts[0]), conflicts, "issued")
        date = None
        if year and len(parts) > 1 and parts[1]:
            date = "-".join(["%04d" % year] + ["%02d" % int(p) for p in parts[1:3] if p])
        issn = item.get("ISSN")
        if isinstance(issn, list):
            issn = " ".join(issn)
        keywords = item.get("keyword")
        rec = CanonicalRecord(
            record_id=_record_id("csl", key, doi, index),
            title=item.get("title"),
            authors=_csl_people(item.get("author")),
            publication_year=year,
            publication_date=date,
            venue=item.get("container-title"),
            publisher=item.get("publisher"),
            volume=str(item["volume"]) if item.get("volume") is not None else None,
            issue=str(item["issue"]) if item.get("issue") is not None else None,
            pages=item.get("page"),
            work_type=_CSL_TO_WORK_TYPE.get(item.get("type", ""), "other"),
            language=item.get("language"),
            identifiers=Identifiers(
                doi=doi,
                pmid=normalize_pmid(item.get("PMID")),
                pmcid=normalize_pmcid(item.get("PMCID")),
                issn=_issns(issn),
                other=[{"scheme": "isbn", "value": item["ISBN"]}] if item.get("ISBN") else [],
            ),
            abstract=item.get("abstract"),
            keywords=_keywords(keywords) if isinstance(keywords, str) else list(keywords or []),
            conflicts=conflicts,
        )
        if item.get("URL"):
            rec.access.best_url = item["URL"]
        rec.versions.append({"citation_key": key, "source_format": "csl-json", "entry_type": item.get("type")})
        rec.add_provenance(_provenance("parse_csl_json", key))
        records.append(rec)
    return records


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

PARSERS = {"bibtex": parse_bibtex, "ris": parse_ris, "csl-json": parse_csl_json}


def detect_format(path: str, text: Optional[str] = None) -> str:
    ext = os.path.splitext(path)[1].lower()
    if ext in FORMAT_BY_EXTENSION:
        return FORMAT_BY_EXTENSION[ext]
    if text is not None:
        stripped = text.lstrip("\ufeff \t\r\n")
        if stripped.startswith("@"):
            return "bibtex"
        if stripped.startswith("TY  -"):
            return "ris"
        if stripped.startswith("[") or stripped.startswith("{"):
            return "csl-json"
    raise BibliographyFormatError("cannot tell the bibliography format of %s; use .bib, .ris, or .json" % path)


def load_bibliography(path: str, fmt: Optional[str] = None) -> List[CanonicalRecord]:
    with open(path, "r", encoding="utf-8-sig") as f:
        text = f.read()
    fmt = fmt or detect_format(path, text)
    if fmt not in PARSERS:
        raise BibliographyFormatError("unknown bibliography format %r; choose from %s" % (fmt, sorted(PARSERS)))
    return PARSERS[fmt](text)


# --------------------------------------------------------------------------
# Export
# --------------------------------------------------------------------------

def _family_given(author: Dict[str, Any]) -> Tuple[str, str]:
    if author.get("family") or author.get("given"):
        return author.get("family", ""), author.get("given", "")
    parts = (author.get("name") or "").split()
    if len(parts) <= 1:
        return (parts[0] if parts else ""), ""
    return parts[-1], " ".join(parts[:-1])


def _is_literal(author: Dict[str, Any]) -> bool:
    return not author.get("family") and not author.get("given") and " " in (author.get("name") or "")


def citation_key(record: CanonicalRecord, taken: Optional[set] = None) -> str:
    for v in record.versions:
        if v.get("citation_key"):
            key = v["citation_key"]
            break
    else:
        family = _family_given(record.authors[0])[0] if record.authors else "anon"
        family = re.sub(r"[^A-Za-z0-9]", "", family.lower()) or "anon"
        word = re.sub(r"[^A-Za-z0-9]", "", ((record.title or "").split() or ["untitled"])[0].lower())
        key = "%s%s%s" % (family, record.publication_year or "nd", word)
    if taken is not None:
        base, suffix = key, ord("a")
        while key in taken:
            key = "%s%s" % (base, chr(suffix))
            suffix += 1
        taken.add(key)
    return key


def _bibtex_escape(value: str) -> str:
    value = str(value)
    for ch in ("&", "%", "$", "#", "_"):
        value = value.replace(ch, "\\" + ch)
    return value


def to_bibtex(records: Iterable[CanonicalRecord]) -> str:
    out, taken = [], set()
    for r in records:
        fields: List[Tuple[str, str]] = []
        if r.authors:
            names = []
            for a in r.authors:
                if _is_literal(a):
                    names.append("{%s}" % a["name"])
                else:
                    fam, giv = _family_given(a)
                    names.append("%s, %s" % (fam, giv) if giv else fam)
            fields.append(("author", " and ".join(names)))
        etype = _WORK_TYPE_TO_BIBTEX.get(r.work_type or "", "misc")
        venue_field = {"article": "journal", "inproceedings": "booktitle", "incollection": "booktitle",
                       "phdthesis": "school"}.get(etype, "howpublished" if etype == "misc" else "journal")
        for name, value in (
            ("title", r.title), ("subtitle", r.subtitle), (venue_field, r.venue),
            ("year", r.publication_year), ("volume", r.volume), ("number", r.issue),
            ("pages", r.pages.replace("-", "--") if r.pages else None), ("publisher", r.publisher),
            ("doi", r.identifiers.doi), ("issn", ", ".join(r.identifiers.issn) or None),
            ("pmid", r.identifiers.pmid), ("url", r.access.best_url), ("language", r.language),
            ("keywords", ", ".join(r.keywords) or None), ("abstract", r.abstract),
        ):
            if value not in (None, ""):
                fields.append((name, str(value)))
        body = ",\n".join("  %s = {%s}" % (k, _bibtex_escape(v) if k not in ("url", "doi") else v) for k, v in fields)
        out.append("@%s{%s,\n%s\n}" % (etype, citation_key(r, taken), body))
    return "\n\n".join(out) + ("\n" if out else "")


def to_ris(records: Iterable[CanonicalRecord]) -> str:
    out = []
    for r in records:
        lines = ["TY  - %s" % _WORK_TYPE_TO_RIS.get(r.work_type or "", "GEN")]
        add = lambda tag, value: lines.append("%s  - %s" % (tag, value)) if value not in (None, "") else None  # noqa: E731
        key = citation_key(r)
        add("ID", key)
        for a in r.authors:
            fam, giv = _family_given(a)
            add("AU", a["name"] if _is_literal(a) else ("%s, %s" % (fam, giv) if giv else fam))
        add("TI", r.title)
        add("T2", r.venue)
        add("PY", r.publication_year)
        if r.publication_date:
            add("DA", r.publication_date.replace("-", "/"))
        add("VL", r.volume)
        add("IS", r.issue)
        if r.pages:
            sp, _, ep = r.pages.partition("-")
            add("SP", sp)
            add("EP", ep)
        add("PB", r.publisher)
        add("DO", r.identifiers.doi)
        for issn in r.identifiers.issn:
            add("SN", issn)
        add("LA", r.language)
        add("UR", r.access.best_url)
        for kw in r.keywords:
            add("KW", kw)
        add("AB", r.abstract)
        lines.append("ER  - ")
        out.append("\n".join(lines))
    return "\n\n".join(out) + ("\n" if out else "")


def to_csl_json(records: Iterable[CanonicalRecord]) -> str:
    items = []
    for r in records:
        item: Dict[str, Any] = {"id": citation_key(r), "type": _WORK_TYPE_TO_CSL.get(r.work_type or "", "article")}
        if r.title:
            item["title"] = r.title
        if r.authors:
            item["author"] = [
                {"literal": a["name"]} if _is_literal(a) else
                {k: v for k, v in zip(("family", "given"), _family_given(a)) if v}
                for a in r.authors
            ]
        if r.publication_year:
            parts = [r.publication_year]
            if r.publication_date:
                parts += [int(p) for p in r.publication_date.split("-")[1:3]]
            item["issued"] = {"date-parts": [parts]}
        for key, value in (
            ("container-title", r.venue), ("publisher", r.publisher), ("volume", r.volume),
            ("issue", r.issue), ("page", r.pages), ("DOI", r.identifiers.doi), ("PMID", r.identifiers.pmid),
            ("PMCID", r.identifiers.pmcid), ("URL", r.access.best_url), ("language", r.language),
            ("abstract", r.abstract),
        ):
            if value not in (None, ""):
                item[key] = value
        if r.identifiers.issn:
            item["ISSN"] = r.identifiers.issn[0] if len(r.identifiers.issn) == 1 else r.identifiers.issn
        if r.keywords:
            item["keyword"] = ", ".join(r.keywords)
        items.append(item)
    return json.dumps(items, ensure_ascii=False, indent=2) + "\n"


EXPORTERS = {"bibtex": to_bibtex, "ris": to_ris, "csl-json": to_csl_json}


def export_bibliography(records: Iterable[CanonicalRecord], fmt: str) -> str:
    if fmt not in EXPORTERS:
        raise BibliographyFormatError("unknown bibliography format %r; choose from %s" % (fmt, sorted(EXPORTERS)))
    return EXPORTERS[fmt](records)
