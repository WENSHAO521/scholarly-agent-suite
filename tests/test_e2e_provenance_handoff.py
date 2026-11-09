"""PROVENANCE_RECORD_V1 handoff, end to end (v2.1.0).

Until v2.1.0 the record was only ever hand-written in tests: nothing built
it from the records a profile actually came from. scb.compiler.
build_provenance_record_v1() is now the producer. This drives:

  user library (BibTeX) + adapter-verified record
    -> CanonicalRecords -> PROVENANCE_RECORD_V1 (shared schema)
    -> SCHOLARLY_PROFILE_V1 (shared schema) -> voice module request

Real module code throughout -- no mocks at the protocol boundary.
"""
import pytest
from conftest import load_module_at
from schema_lite import validate_file

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "scholarly-agent"
MODULES = SKILL_DIR / "modules"
PROTOCOLS = SKILL_DIR / "protocols"

from scb.bibliography import parse_bibtex  # noqa: E402
from scb.compiler import build_provenance_record_v1, compile_scholarly_profile_protocol_v1  # noqa: E402
from scb.profile_schema import build_style_profile  # noqa: E402
from scb.records import Access, CanonicalRecord, Identifiers, ProvenanceEntry  # noqa: E402
from scb.text_normalize import Document, Section  # noqa: E402

voice_schema = load_module_at(
    "voice_profile_schema_provenance_handoff",
    MODULES / "scholarly-voice-engine" / "scripts" / "voice" / "profile_schema.py",
)

LIBRARY = r"""
@article{good, author={Smith, Jane}, title={Diffusion}, journal={J Pol}, year={2021},
         doi={10.1000/good.1}}
@article{typo, author={Lee, Kim}, title={Capacity}, journal={J Pol}, year={2022},
         doi={doi-missing-prefix}}
"""


def _verified(doi: str, oa: bool) -> CanonicalRecord:
    rec = CanonicalRecord(
        record_id="crossref:%s" % doi,
        title="Verified work",
        identifiers=Identifiers(doi=doi),
        access=Access(is_oa=oa, readable=True if oa else None),
        retrieved_at="2026-11-05T10:00:00Z",
    )
    rec.add_provenance(ProvenanceEntry(adapter="crossref", operation="lookup", source_identifier=doi,
                                       verification="VERIFIED", retrieved_at="2026-11-05T10:00:00Z"))
    return rec


def _style_profile() -> dict:
    doc = Document(
        title="Paper",
        abstract="We examine policy diffusion.",
        sections=[Section("Introduction", "introduction", [
            "We argue that diffusion depends on capacity (Smith, 2020). However, prior work rarely tests it.",
        ])],
    )
    return build_style_profile("journal", "J Pol", [doc] * 6).to_dict()


def test_all_adapter_verified_sources_give_verified_record():
    record = build_provenance_record_v1([_verified("10.1000/a.1", True), _verified("10.1000/b.2", False)])
    validate_file(record, PROTOCOLS / "provenance.schema.json")
    assert record["verification_status"] == "verified"
    assert record["retrieval_date"] == "2026-11-05"
    assert [s["access_status"] for s in record["sources"]] == ["open-access", "metadata-only"]


def test_library_import_is_unverified_until_looked_up():
    good, _typo = parse_bibtex(LIBRARY)
    record = build_provenance_record_v1([good], retrieval_date="2026-11-09")
    validate_file(record, PROTOCOLS / "provenance.schema.json")
    assert record["verification_status"] == "unverified"
    assert record["sources"][0] == {
        "identity": "10.1000/good.1", "access_status": "user-supplied",
        "verification": "NEEDS_CHECK", "via": ["user_bibliography"],
    }


def test_mixed_sources_are_partially_verified():
    good, _ = parse_bibtex(LIBRARY)
    record = build_provenance_record_v1([good, _verified("10.1000/a.1", True)])
    assert record["verification_status"] == "partially-verified"


def test_field_conflicts_surface_as_conflict_notes():
    good, typo = parse_bibtex(LIBRARY)
    record = build_provenance_record_v1([good, typo], retrieval_date="2026-11-09")
    validate_file(record, PROTOCOLS / "provenance.schema.json")
    assert record["verification_status"] == "conflicting"
    assert any("malformed DOI" in n for n in record["conflict_notes"])
    # no DOI survived, so identity falls back to an explicit user-supplied marker
    assert record["sources"][1]["identity"] == "user-supplied:bibtex:typo"


def test_unidentified_source_is_flagged_not_guessed():
    bare = CanonicalRecord(record_id="openalex:W1", title="Only a title")
    bare.add_provenance(ProvenanceEntry(adapter="openalex", operation="search"))
    record = build_provenance_record_v1([bare], retrieval_date="2026-11-09")
    assert record["sources"][0]["identity"] == "record:openalex:W1"
    assert record["verification_status"] == "conflicting"


def test_refuses_to_invent_inputs():
    with pytest.raises(ValueError):
        build_provenance_record_v1([])
    good, _ = parse_bibtex(LIBRARY)
    with pytest.raises(ValueError):
        build_provenance_record_v1([good])  # no retrieval date anywhere


def test_record_flows_through_scholarly_profile_into_voice():
    good, _ = parse_bibtex(LIBRARY)
    provenance = build_provenance_record_v1([good, _verified("10.1000/a.1", True)])
    profile = compile_scholarly_profile_protocol_v1(_style_profile(), provenance, freshness="current")
    validate_file(profile, PROTOCOLS / "scholarly-profile.schema.json")
    request = voice_schema.VoiceRequest(task="journal_adapt", scholarly_profile=profile)
    assert request.validate() == []
    assert request.scholarly_profile["provenance"]["verification_status"] == "partially-verified"
