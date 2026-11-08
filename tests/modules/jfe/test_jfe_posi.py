"""POSI (Panorama Open Scholarly Index) evidence source for the journal-fit
module. Uses a small fixture cut from the real POSI snapshot 2026-11-08
(manifest unchanged; collections reduced to a handful of real records plus
two synthetic duplicate-title records). No network access."""
import gzip
import hashlib
import io
import json
import shutil
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from jfe import cli
from jfe.http_client import HttpClient, HttpResponse
from jfe.indexing import CANNOT_VERIFY, OFFICIALLY_VERIFIED, assess_indexing
from jfe.journal_evidence import JournalEvidence
from jfe.posi import (
    COI_DISCLOSURE,
    POSI_BASE_URL,
    PosiError,
    PosiSnapshot,
    apply_to_evidence,
    fetch_snapshot,
    normalize_issn,
    normalize_title,
)
from jfe.target_journal_profile import build_target_journal_profile

FIXTURE = Path(__file__).parent / "fixtures" / "posi" / "snapshot"


@pytest.fixture(scope="module")
def snapshot():
    return PosiSnapshot.from_directory(FIXTURE)


# --- normalization -----------------------------------------------------------

@pytest.mark.parametrize("raw,expected", [
    ("1557-7317", "1557-7317"), ("15577317", "1557-7317"), ("3052-539x", "3052-539X"),
    ("", None), (None, None), ("not-an-issn", None), ("1234-567", None),
])
def test_normalize_issn(raw, expected):
    assert normalize_issn(raw) == expected


def test_normalize_title_is_case_and_punctuation_insensitive():
    assert normalize_title("The Journal of X: Studies") == normalize_title("journal of x studies")


# --- loading -----------------------------------------------------------------

def test_snapshot_provenance_names_exact_data(snapshot):
    prov = snapshot.provenance()
    assert prov["snapshot"] == "2026-11-08"
    assert prov["is_official_release"] is False
    assert prov["latest_release"] == "POSI-R-2026.1"
    assert len(prov["data_commit"]) == 40
    assert prov["ranking_snapshot_date"] == "2026-09-28"


def test_checksum_mismatch_is_refused(tmp_path):
    bad = tmp_path / "snapshot"
    shutil.copytree(FIXTURE, bad)
    core = bad / "collections" / "core-collection.json"
    core.write_text(core.read_text(encoding="utf-8").replace("Bimonthly", "Monthly"), encoding="utf-8")
    with pytest.raises(PosiError, match="SHA-256 mismatch"):
        PosiSnapshot.from_directory(bad)


def test_missing_manifest_is_an_error(tmp_path):
    with pytest.raises(PosiError):
        PosiSnapshot.from_directory(tmp_path)


# --- lookup ------------------------------------------------------------------

def test_official_ranking_lookup_by_issn(snapshot):
    rec = snapshot.lookup(issns=["1557-7317"])
    assert rec.title == "Communications of the ACM"
    assert rec.ranking_is_official
    assert rec.citation_quartile == "Q1"
    label = rec.quartile_label()
    assert label.startswith("POSI Citation Quartile C-Q1 in Computer and Information Sciences")
    assert "metric year 2026" in label and "CITATION-RANK-1.0" in label
    assert "JCR" not in label


def test_provisional_ranking_is_never_reported_as_official(snapshot):
    rec = snapshot.lookup(issns=["1895-6572"])
    assert rec.citation_ranking_status == "provisional"
    assert not rec.ranking_is_official
    assert any("provisional" in d for d in rec.disclosures())
    if rec.quartile_label():
        assert "provisional" in rec.quartile_label()


def test_not_ranked_journal_has_no_quartile(snapshot):
    rec = snapshot.lookup(issns=["0000-1112"])
    assert rec.citation_quartile is None
    assert rec.quartile_label() is None
    assert rec.ranking_status_reason == "no_eligible_items"


def test_title_lookup_is_exact_and_refuses_ambiguity(snapshot):
    assert snapshot.lookup(title="communications of the acm").title == "Communications of the ACM"
    assert snapshot.lookup(title="Communications of ACM journal") is None
    assert snapshot.lookup(title="Journal of Duplicate Titles") is None


def test_unknown_journal_returns_none(snapshot):
    assert snapshot.lookup(issns=["1234-5679"], title="Nonexistent Journal") is None


def test_core_collection_record_carries_rating_and_apc_source(snapshot):
    rec = snapshot.lookup(issns=["3078-4441"])
    assert rec.in_core_collection
    assert rec.pqf_grade
    if rec.apc:
        assert rec.apc.get("source_url") and rec.apc.get("checked_at")


def test_operator_published_journal_carries_conflict_disclosure(snapshot):
    rec = snapshot.lookup(issns=["3052-539X"])
    assert rec.publisher == "Panorama Scholarly Group"
    assert rec.operated_by_posi_operator
    assert COI_DISCLOSURE in rec.disclosures()
    assert COI_DISCLOSURE in rec.as_dict()["disclosures"]


def test_third_party_journal_has_no_conflict_disclosure(snapshot):
    rec = snapshot.lookup(issns=["1557-7317"])
    assert not rec.operated_by_posi_operator
    assert COI_DISCLOSURE not in rec.disclosures()


def test_every_result_carries_attribution_and_snapshot(snapshot):
    d = snapshot.lookup(issns=["1557-7317"]).as_dict()
    assert "CC BY 4.0" in d["attribution"]
    assert d["provenance"]["snapshot"] == "2026-11-08"
    assert any("post-release data snapshot" in x for x in d["disclosures"])


# --- integration with evidence, indexing and TARGET_JOURNAL_PROFILE_V1 -------

def test_apply_to_evidence_fills_gaps_but_never_overwrites(snapshot):
    rec = snapshot.lookup(issns=["3052-539X"])
    evidence = JournalEvidence(display_name=rec.title, issn=["3052-539X"], source="openalex", is_oa=None)
    result = apply_to_evidence(evidence, rec)
    assert "is_oa" in result["filled"] and evidence.is_oa is True
    assert evidence.apc_usd == 450
    assert evidence.is_in_doaj is False
    assert evidence.source == "openalex+posi"
    assert "POSI snapshot 2026-11-08" in evidence.provenance_note
    assert "APC-Policy-Schedule" in evidence.provenance_note

    conflicting = JournalEvidence(display_name=rec.title, issn=["3052-539X"], source="openalex", apc_usd=999)
    result = apply_to_evidence(conflicting, rec)
    assert conflicting.apc_usd == 999
    assert any("APC" in c for c in result["conflicts"])


def test_indexing_entry_for_official_ranking(snapshot):
    rec = snapshot.lookup(issns=["1557-7317"])
    evidence = JournalEvidence(display_name=rec.title, issn=rec.issns, source="openalex")
    entry = assess_indexing(evidence, posi=rec).as_dict()["POSI"]
    assert entry["state"] == OFFICIALLY_VERIFIED
    assert entry["value"]["citation_quartile"].startswith("POSI Citation Quartile C-Q1")
    assert "not JCR" in entry["note"]
    assert entry["source"] == "posi:2026-11-08"
    # The paid-index placeholders stay cannot_verify: POSI does not stand in for them.
    assert assess_indexing(evidence, posi=rec).as_dict()["Web of Science"]["state"] == CANNOT_VERIFY


def test_indexing_entry_for_unranked_non_core_journal_is_not_verified(snapshot):
    rec = snapshot.lookup(issns=["0000-1112"])
    evidence = JournalEvidence(display_name=rec.title, issn=rec.issns, source="openalex")
    assert assess_indexing(evidence, posi=rec).as_dict()["POSI"]["state"] == CANNOT_VERIFY


def test_indexing_without_posi_is_unchanged():
    evidence = JournalEvidence(display_name="X", source="openalex")
    assert "POSI" not in assess_indexing(evidence).as_dict()


def test_posi_flows_into_target_journal_profile(snapshot):
    rec = snapshot.lookup(issns=["1557-7317"])
    evidence = JournalEvidence(display_name=rec.title, issn=rec.issns, issn_l=rec.issns[0],
                               source="openalex", checked_at="2026-11-08T00:00:00+00:00")
    profile = build_target_journal_profile(evidence, indexing_assessment=assess_indexing(evidence, posi=rec))
    assert "POSI" in profile["indexing"]


# --- network fetch (injected transport, no real network) ---------------------

def _fake_transport(files: dict, fail_primary: bool = False):
    calls = []

    def transport(url, headers):
        calls.append(url)
        if fail_primary and url.startswith(POSI_BASE_URL):
            return HttpResponse(403, b"")
        if url.endswith("/current.json"):
            return HttpResponse(200, json.dumps({"snapshot": "2026-11-08"}).encode())
        name = url.rsplit("/", 1)[-1]
        for rel, body in files.items():
            if rel.endswith(name):
                return HttpResponse(200, body)
        return HttpResponse(404, b"")

    return transport, calls


def _fixture_files():
    return {rel: (FIXTURE / rel).read_bytes() for rel in [
        "manifest.json", "SHA256SUMS", "collections/core-collection.json",
        "collections/citation-ranking.json.gz"]}


def test_fetch_snapshot_downloads_verifies_and_caches(tmp_path):
    transport, calls = _fake_transport(_fixture_files())
    client = HttpClient(user_agent="test", transport=transport)
    snap = fetch_snapshot(client, tmp_path)
    assert snap.provenance()["snapshot"] == "2026-11-08"
    assert (tmp_path / "2026-11-08" / "collections" / "citation-ranking.json.gz").is_file()
    n = len(calls)
    fetch_snapshot(client, tmp_path, snapshot="2026-11-08")  # cached: no new downloads
    assert len(calls) == n


def test_fetch_snapshot_falls_back_to_release_assets(tmp_path):
    transport, calls = _fake_transport(_fixture_files(), fail_primary=True)
    snap = fetch_snapshot(HttpClient(user_agent="test", transport=transport, max_retries=0), tmp_path)
    assert snap.lookup(issns=["1557-7317"]) is not None
    assert any("raw.githubusercontent.com" in c and c.endswith("current.json") for c in calls)
    assert any("releases/download/snapshot-2026-11-08" in c for c in calls)


def test_fetch_snapshot_rejects_tampered_download(tmp_path):
    files = _fixture_files()
    files["collections/core-collection.json"] = files["collections/core-collection.json"].replace(b"Bimonthly", b"Monthly")
    transport, _ = _fake_transport(files)
    with pytest.raises(PosiError):
        fetch_snapshot(HttpClient(user_agent="test", transport=transport), tmp_path, snapshot="2026-11-08")
    assert not (tmp_path / "2026-11-08").exists()


# --- CLI ---------------------------------------------------------------------

def _run_cli(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = cli.main(argv)
    return code, json.loads(buf.getvalue())


def test_cli_posi_lookup_found():
    code, out = _run_cli(["posi-lookup", "--snapshot-dir", str(FIXTURE), "--issn", "1557-7317"])
    assert code == 0 and out["found"] is True
    assert out["record"]["quartile_label"].startswith("POSI Citation Quartile C-Q1")


def test_cli_posi_lookup_not_found_says_absence_is_not_evidence():
    code, out = _run_cli(["posi-lookup", "--snapshot-dir", str(FIXTURE), "--issn", "1234-5679"])
    assert code == 0 and out["found"] is False
    assert "not evidence" in out["note"]


def test_cli_posi_lookup_requires_a_query():
    code, out = _run_cli(["posi-lookup", "--snapshot-dir", str(FIXTURE)])
    assert code == 1 and "error" in out


def test_fixture_checksums_are_current():
    sums = dict(reversed(l.split("  ", 1)) for l in (FIXTURE / "SHA256SUMS").read_text().splitlines() if l)
    for rel, digest in sums.items():
        assert hashlib.sha256((FIXTURE / rel).read_bytes()).hexdigest() == digest
    json.loads(gzip.decompress((FIXTURE / "collections" / "citation-ranking.json.gz").read_bytes()))
