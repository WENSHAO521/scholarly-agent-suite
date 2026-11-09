"""Reference-manager import/export (scb.bibliography): BibTeX, RIS, CSL-JSON."""
import contextlib
import io
import json
import sys

import pytest

from scb import cli
from scb.bibliography import (
    BibliographyFormatError,
    detect_format,
    export_bibliography,
    load_bibliography,
    parse_bibtex,
    parse_csl_json,
    parse_ris,
    to_bibtex,
    to_csl_json,
    to_ris,
)

BIBTEX = r"""
@string{nat = "Nature"}
@comment{exported by Zotero}
@article{smith2020trust,
  author = {Smith, Jane A. and M{\"u}ller, Hans and {World Health Organization}},
  title = {Trust in {Public} Institutions \& Reform},
  journal = nat,
  year = 2020, month = mar,
  volume = {12}, number = "3", pages = {101--120},
  doi = {https://doi.org/10.1000/XYZ123},
  issn = {0028-0836},
  keywords = {trust, governance},
  abstract = {We study trust.}
}
@incollection{lee2019,
  author = "Kim Lee and Others",
  title = "A Chapter",
  booktitle = {Handbook of Things},
  publisher = {Press},
  year = {c. 2019}
}
@misc{bad, title={Bad Entry}, doi={not-a-doi}, year={n.d.}}
"""

RIS = """TY  - JOUR
ID  - wang2022
AU  - Wang, Li
AU  - Garcia, Maria
TI  - Open Data and
  Accountability
T2  - Public Administration Review
PY  - 2022/05/01/
VL  - 82
IS  - 3
SP  - 400
EP  - 415
DO  - 10.1111/puar.13456
SN  - 0033-3352
KW  - open data
KW  - accountability
AB  - An abstract.
ER  - 

TY  - BOOK
AU  - Ostrom, Elinor
TI  - Governing the Commons
PB  - Cambridge University Press
PY  - 1990
ER  - 
"""

CSL = json.dumps([
    {
        "id": "http://zotero.org/users/1/items/ABCD",
        "type": "article-journal",
        "title": "Machine Learning in Medicine",
        "author": [{"family": "Rajkomar", "given": "Alvin"}, {"literal": "The ML Consortium"}],
        "issued": {"date-parts": [[2019, 4, 4]]},
        "container-title": "New England Journal of Medicine",
        "volume": 380, "issue": "14", "page": "1347-1358",
        "DOI": "10.1056/NEJMra1814259", "PMID": "30943338",
        "ISSN": ["0028-4793", "1533-4406"],
        "keyword": "machine learning; medicine",
    }
])


def test_bibtex_parses_fields_macros_and_latex():
    smith, lee, bad = parse_bibtex(BIBTEX)
    assert smith.title == "Trust in Public Institutions & Reform"
    assert smith.venue == "Nature"  # @string macro
    assert [a["name"] for a in smith.authors] == ["Jane A. Smith", "Hans Müller", "World Health Organization"]
    assert smith.authors[0]["family"] == "Smith" and smith.authors[0]["given"] == "Jane A."
    assert "family" not in smith.authors[2]  # braced institutional author stays whole
    assert smith.publication_year == 2020 and smith.publication_date == "2020-03"
    assert smith.pages == "101-120"
    assert smith.identifiers.doi == "10.1000/xyz123"
    assert smith.identifiers.issn == ["0028-0836"]
    assert smith.keywords == ["trust", "governance"]
    assert smith.work_type == "journal-article"
    assert smith.record_id == "bibtex:doi:10.1000/xyz123"
    assert lee.work_type == "book-chapter" and lee.venue == "Handbook of Things"
    assert [a["name"] for a in lee.authors] == ["Kim Lee"]  # "and Others" dropped
    assert lee.publication_year == 2019


def test_bad_fields_become_conflicts_not_guesses():
    bad = parse_bibtex(BIBTEX)[2]
    assert bad.identifiers.doi is None and bad.publication_year is None
    assert {c["field"] for c in bad.conflicts} == {"doi", "year"}


def test_every_imported_record_is_needs_check():
    for records in (parse_bibtex(BIBTEX), parse_ris(RIS), parse_csl_json(CSL)):
        for r in records:
            assert r.provenance and all(p.verification == "NEEDS_CHECK" for p in r.provenance)
            assert r.sources == ["user_bibliography"]


def test_ris_parses_multi_valued_and_continuation_lines():
    wang, ostrom = parse_ris(RIS)
    assert wang.title == "Open Data and Accountability"
    assert [a["family"] for a in wang.authors] == ["Wang", "Garcia"]
    assert wang.publication_date == "2022-05-01" and wang.publication_year == 2022
    assert wang.pages == "400-415" and wang.identifiers.doi == "10.1111/puar.13456"
    assert wang.keywords == ["open data", "accountability"]
    assert ostrom.work_type == "book" and ostrom.publisher == "Cambridge University Press"


def test_csl_json_parses_zotero_export():
    (r,) = parse_csl_json(CSL)
    assert r.title == "Machine Learning in Medicine"
    assert r.authors[1]["name"] == "The ML Consortium"
    assert r.publication_date == "2019-04-04"
    assert r.volume == "380" and r.identifiers.pmid == "30943338"
    assert r.identifiers.issn == ["0028-4793", "1533-4406"]
    assert r.keywords == ["machine learning", "medicine"]


@pytest.mark.parametrize("exporter,parser", [(to_bibtex, parse_bibtex), (to_ris, parse_ris), (to_csl_json, parse_csl_json)])
def test_round_trip_keeps_core_fields(exporter, parser):
    original = parse_bibtex(BIBTEX)[:2] + parse_ris(RIS) + parse_csl_json(CSL)
    again = parser(exporter(original))
    assert len(again) == len(original)
    for a, b in zip(original, again):
        assert b.title == a.title
        assert b.identifiers.doi == a.identifiers.doi
        assert b.publication_year == a.publication_year
        assert b.venue == a.venue
        assert [x["name"] for x in b.authors] == [x["name"] for x in a.authors]
        assert b.work_type == a.work_type


def test_bibtex_export_escapes_and_dedupes_keys():
    rec = parse_csl_json(CSL)[0]
    rec.versions = []  # force a generated key
    out = to_bibtex([rec, rec])
    assert "@article{rajkomar2019machine," in out
    assert "@article{rajkomar2019machinea," in out
    assert "{The ML Consortium}" in out


def test_format_detection_and_errors(tmp_path):
    assert detect_format("x.bib") == "bibtex"
    assert detect_format("x.txt", "TY  - JOUR\n") == "ris"
    with pytest.raises(BibliographyFormatError):
        detect_format("x.txt", "plain words")
    with pytest.raises(BibliographyFormatError):
        parse_csl_json("{not json")
    with pytest.raises(BibliographyFormatError):
        parse_ris("no records here")
    with pytest.raises(BibliographyFormatError):
        parse_bibtex("@article{open, title={never closed}")
    with pytest.raises(BibliographyFormatError):
        export_bibliography([], "endnote-xml")
    path = tmp_path / "lib.ris"
    path.write_text("﻿" + RIS, encoding="utf-8")
    assert len(load_bibliography(str(path))) == 2


def test_cli_import_then_export(tmp_path, monkeypatch):
    path = tmp_path / "lib.bib"
    path.write_text(BIBTEX, encoding="utf-8")
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert cli.main(["import-bib", str(path)]) == 0
    payload = json.loads(buf.getvalue())
    assert payload["count"] == 3 and payload["verification"] == "NEEDS_CHECK"
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        assert cli.main(["export-bib", "--format", "ris"]) == 0
    assert out.getvalue().count("ER  - ") == 3


def test_builder_version_is_the_suite_version():
    """Regression: since the v2.0.0 merge scb looked for a per-module VERSION
    file that no longer exists, so every corpus manifest said 0.0.0."""
    from pathlib import Path

    import scb

    root = Path(__file__).resolve().parents[3]
    assert scb.__version__ == (root / "VERSION").read_text(encoding="utf-8").strip()
