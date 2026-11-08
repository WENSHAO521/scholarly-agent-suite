"""POSI (Panorama Open Scholarly Index) as a journal-evidence source.

POSI publishes open, versioned, immutable journal data snapshots
(https://data.posi.panorama-sg.com, generated from
https://github.com/WENSHAO521/posi-data). This module reads one snapshot
and answers "what does POSI say about this journal?" for the fit workflow:

- Citation Ranking (`collections/citation-ranking.json.gz`): PNCI, category
  rank, percentile, Citation Quartile (displayed C-Q1..C-Q4), POSI Zone, and
  each record's ranking status.
- Core Collection (`collections/core-collection.json`): PQF grade, AJR
  Rating, APC (with its source URL and check date), open-access licence.

Evidence discipline (references/indexing-metrics.md, references/evidence-policy.md):

- A POSI quartile is POSI's own Citation Quartile in a named POSI category
  for a named metric year. It is never reported as, or mixed up with, a JCR,
  SJR, or CiteScore quartile; `quartile_label()` always names the system,
  category, and year.
- Only records whose `citation_ranking_status` is `official` count as
  verified ranking evidence. `provisional`, `observation`, and the
  not-ranked statuses are reported as such, never upgraded.
- Every result carries the snapshot id, release state, data commit, and
  ranking snapshot date, so a claim can be traced to exactly the data seen.
- POSI is operated by Panorama Scholarly Group, which also publishes
  journals that POSI rates. For those journals every result carries a
  conflict-of-interest disclosure, and POSI's rating must not be the sole
  basis for recommending them.
- Lookup is exact: by ISSN, or by exact normalized title. No fuzzy matching,
  because a wrong match is worse than no match.

POSI data licence: CC BY 4.0 for POSI-produced metrics; attribution is
returned with every result (`ATTRIBUTION`).

Offline first: `PosiSnapshot.from_directory()` reads a local snapshot (as
downloaded by `fetch_snapshot()`, or a test fixture). Network access goes
through the injectable `HttpClient` transport, so tests never touch the
network.
"""
from __future__ import annotations

import gzip
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from jfe.http_client import HttpClient, HttpError

POSI_BASE_URL = "https://data.posi.panorama-sg.com"
# Every snapshot's collections are also published as a GitHub release
# asset; used when the Pages host is unreachable.
POSI_RELEASE_URL = "https://github.com/WENSHAO521/posi-data-delivery/releases/download/snapshot-{snapshot}/{file}"
POSI_CURRENT_FALLBACK_URL = "https://raw.githubusercontent.com/WENSHAO521/posi-data-delivery/main/current.json"
SOURCE_NAME = "POSI (Panorama Open Scholarly Index)"
ATTRIBUTION = (
    "POSI data, Panorama Open Scholarly Index "
    "(https://github.com/WENSHAO521/posi-data), CC BY 4.0."
)
COLLECTION_FILES = ("core-collection.json", "citation-ranking.json.gz")

OPERATOR = "Panorama Scholarly Group"
COI_DISCLOSURE = (
    "POSI is operated by Panorama Scholarly Group, which also publishes this "
    "journal. Treat POSI's rating of it as the operator's own assessment: "
    "disclose this to the user and weigh independent evidence before "
    "recommending the journal."
)

OFFICIAL = "official"
_ISSN_RE = re.compile(r"^\d{4}-?\d{3}[\dXx]$")


class PosiError(Exception):
    """Raised for a missing/invalid snapshot or a checksum mismatch."""


def normalize_issn(issn: Optional[str]) -> Optional[str]:
    if not issn:
        return None
    s = issn.strip().upper()
    if not _ISSN_RE.match(s):
        return None
    s = s.replace("-", "")
    return f"{s[:4]}-{s[4:]}"


def normalize_title(title: Optional[str]) -> Optional[str]:
    if not title:
        return None
    t = re.sub(r"[^\w\s]", " ", title.lower())
    t = re.sub(r"\s+", " ", t).strip()
    if t.startswith("the "):
        t = t[4:]
    return t or None


@dataclass
class PosiRecord:
    """What one POSI snapshot says about one journal."""

    posi_id: Optional[str]
    title: Optional[str]
    issns: list
    publisher: Optional[str]
    open_access: Optional[bool]
    # Citation Ranking
    citation_ranking_status: Optional[str] = None
    ranking_status_reason: Optional[str] = None
    pnci: Optional[float] = None
    citation_quartile: Optional[str] = None
    citation_percentile: Optional[float] = None
    citation_rank: Optional[int] = None
    citation_rank_total: Optional[int] = None
    ranking_category_id: Optional[str] = None
    ranking_category_name: Optional[str] = None
    posi_zone: Optional[int] = None
    zone_status: Optional[str] = None
    metric_year: Optional[int] = None
    ranking_methodology_version: Optional[str] = None
    ranking_snapshot_date: Optional[str] = None
    # Core Collection
    in_core_collection: bool = False
    pqf_grade: Optional[str] = None
    ajr_rating: Optional[str] = None
    ajr_rating_status: Optional[str] = None
    ajr_rating_version: Optional[str] = None
    apc: Optional[dict] = None
    license: Optional[str] = None
    doaj_status: Optional[str] = None
    operated_by_posi_operator: bool = False
    # Provenance
    provenance: dict = field(default_factory=dict)

    @property
    def ranking_is_official(self) -> bool:
        return self.citation_ranking_status == OFFICIAL and self.citation_quartile is not None

    def quartile_label(self) -> Optional[str]:
        """A quartile is only meaningful with its system, category, and year."""
        if not self.citation_quartile:
            return None
        category = self.ranking_category_name or self.ranking_category_id or "unnamed category"
        status = "" if self.ranking_is_official else f", {self.citation_ranking_status}"
        return (f"POSI Citation Quartile C-{self.citation_quartile} in {category} "
                f"(metric year {self.metric_year}, {self.ranking_methodology_version}{status})")

    def disclosures(self) -> list:
        notes = []
        if self.operated_by_posi_operator:
            notes.append(COI_DISCLOSURE)
        if self.citation_ranking_status and not self.ranking_is_official:
            reason = f" ({self.ranking_status_reason})" if self.ranking_status_reason else ""
            notes.append(
                f"POSI citation ranking status is '{self.citation_ranking_status}'{reason}: "
                "not an official POSI ranking result."
            )
        if self.provenance.get("is_official_release") is False:
            notes.append(
                f"Snapshot {self.provenance.get('snapshot')} is a post-release data snapshot, "
                f"not the reviewed release {self.provenance.get('latest_release')}; cite the snapshot id."
            )
        return notes

    def as_dict(self) -> dict:
        d = {k: v for k, v in self.__dict__.items()}
        d["quartile_label"] = self.quartile_label()
        d["disclosures"] = self.disclosures()
        d["attribution"] = ATTRIBUTION
        return d


def _is_operator_journal(core: Optional[dict], ranking: Optional[dict]) -> bool:
    for rec in (core, ranking):
        if not rec:
            continue
        if rec.get("source_group") == "psg":
            return True
        if (rec.get("publisher") or "").strip().lower() == OPERATOR.lower():
            return True
    return False


class PosiSnapshot:
    """One immutable POSI snapshot, indexed for exact lookup."""

    def __init__(self, manifest: dict, core_collection: list, citation_ranking: dict):
        if not manifest.get("snapshot"):
            raise PosiError("POSI manifest has no snapshot id")
        self.manifest = manifest
        self.citation_meta = {k: v for k, v in citation_ranking.items() if k != "records"}
        self._core_by_issn: dict = {}
        self._core_by_title: dict = {}
        for rec in core_collection:
            for issn in (rec.get("issn_print"), rec.get("issn_online")):
                n = normalize_issn(issn)
                if n:
                    self._core_by_issn[n] = rec
            t = normalize_title(rec.get("title"))
            if t:
                self._core_by_title.setdefault(t, []).append(rec)
        self._rank_by_issn: dict = {}
        self._rank_by_title: dict = {}
        for rec in citation_ranking.get("records", []):
            for issn in rec.get("issn") or []:
                n = normalize_issn(issn)
                if n:
                    self._rank_by_issn[n] = rec
            t = normalize_title(rec.get("title"))
            if t:
                self._rank_by_title.setdefault(t, []).append(rec)

    # --- loading -------------------------------------------------------

    @classmethod
    def from_directory(cls, path, verify_checksums: bool = True) -> "PosiSnapshot":
        """Load a snapshot directory laid out like data.posi.panorama-sg.com:
        manifest.json, optional SHA256SUMS, collections/<file>."""
        root = Path(path)
        manifest_path = root / "manifest.json"
        if not manifest_path.is_file():
            raise PosiError(f"no POSI manifest.json in {root}")
        if verify_checksums and (root / "SHA256SUMS").is_file():
            _verify_checksums(root, ["manifest.json"] + [f"collections/{f}" for f in COLLECTION_FILES])
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        core = _read_json(root / "collections" / "core-collection.json")
        ranking = _read_json(root / "collections" / "citation-ranking.json.gz")
        return cls(manifest, core or [], ranking or {"records": []})

    # --- lookup --------------------------------------------------------

    def provenance(self) -> dict:
        m = self.manifest
        return {
            "source": SOURCE_NAME,
            "snapshot": m.get("snapshot"),
            "type": m.get("type"),
            "is_official_release": m.get("is_official_release"),
            "release": m.get("release"),
            "latest_release": m.get("latest_release"),
            "data_commit": m.get("data_commit"),
            "engine_commit": m.get("engine_commit"),
            "data_cutoff": m.get("data_cutoff"),
            "ranking_snapshot_date": m.get("ranking_snapshot_date") or self.citation_meta.get("snapshot_date"),
            "url": f"{POSI_BASE_URL}/snapshots/{m.get('snapshot')}/manifest.json",
        }

    def lookup(self, issns: Iterable[str] = (), title: Optional[str] = None) -> Optional[PosiRecord]:
        """Exact lookup by any of `issns`, else by exact normalized `title`.
        A title shared by more than one POSI record is ambiguous and returns
        None rather than guessing."""
        core = rank = None
        for issn in issns or ():
            n = normalize_issn(issn)
            if not n:
                continue
            core = core or self._core_by_issn.get(n)
            rank = rank or self._rank_by_issn.get(n)
        if core is None and rank is None and title:
            t = normalize_title(title)
            core_hits = self._core_by_title.get(t, [])
            rank_hits = self._rank_by_title.get(t, [])
            core = core_hits[0] if len(core_hits) == 1 else None
            rank = rank_hits[0] if len(rank_hits) == 1 else None
        if core is None and rank is None:
            return None
        return self._build(core, rank)

    def _build(self, core: Optional[dict], rank: Optional[dict]) -> PosiRecord:
        issns = set()
        if core:
            issns.update(i for i in (normalize_issn(core.get("issn_print")), normalize_issn(core.get("issn_online"))) if i)
        if rank:
            issns.update(i for i in (normalize_issn(x) for x in rank.get("issn") or []) if i)
        rating = (core or {}).get("early_stage_rating") or (core or {}).get("mature_rating") or {}
        open_access = (core or {}).get("open_access")
        if open_access is None and rank:
            open_access = rank.get("open_access")
        return PosiRecord(
            posi_id=(core or {}).get("posi_id"),
            title=(core or rank or {}).get("title"),
            issns=sorted(issns),
            publisher=(core or rank or {}).get("publisher"),
            open_access=open_access,
            citation_ranking_status=(rank or {}).get("citation_ranking_status"),
            ranking_status_reason=(rank or {}).get("ranking_status_reason"),
            pnci=(rank or {}).get("pnci"),
            citation_quartile=(rank or {}).get("citation_quartile"),
            citation_percentile=(rank or {}).get("citation_percentile"),
            citation_rank=(rank or {}).get("citation_rank"),
            citation_rank_total=(rank or {}).get("citation_rank_total"),
            ranking_category_id=(rank or {}).get("ranking_category_id"),
            ranking_category_name=(rank or {}).get("ranking_category_name"),
            posi_zone=(rank or {}).get("posi_zone"),
            zone_status=(rank or {}).get("zone_status"),
            metric_year=(rank or {}).get("metric_year") or self.citation_meta.get("metric_year"),
            ranking_methodology_version=(rank or {}).get("ranking_methodology_version"),
            ranking_snapshot_date=(rank or {}).get("ranking_snapshot_date"),
            in_core_collection=core is not None,
            pqf_grade=((core or {}).get("pqf") or {}).get("grade"),
            ajr_rating=rating.get("rating"),
            ajr_rating_status=rating.get("rating_status"),
            ajr_rating_version=rating.get("rating_version"),
            apc=(core or {}).get("apc"),
            license=(core or {}).get("license"),
            doaj_status=(core or {}).get("doaj_status"),
            operated_by_posi_operator=_is_operator_journal(core, rank),
            provenance=self.provenance(),
        )


def _read_json(path: Path):
    if not path.is_file():
        return None
    raw = path.read_bytes()
    if path.suffix == ".gz":
        raw = gzip.decompress(raw)
    return json.loads(raw.decode("utf-8"))


def _parse_sha256sums(text: str) -> dict:
    sums = {}
    for line in text.splitlines():
        parts = line.strip().split(None, 1)
        if len(parts) == 2:
            sums[parts[1].lstrip("*")] = parts[0].lower()
    return sums


def _verify_checksums(root: Path, files: list) -> None:
    sums = _parse_sha256sums((root / "SHA256SUMS").read_text(encoding="utf-8"))
    for rel in files:
        path = root / rel
        if not path.is_file() or rel not in sums:
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != sums[rel]:
            raise PosiError(f"SHA-256 mismatch for {rel}: snapshot is corrupt or was altered")


# --- network ---------------------------------------------------------------

def _get_bytes(client: HttpClient, url: str) -> bytes:
    response = client.transport(url, {"User-Agent": client.user_agent})
    if response.status != 200:
        raise HttpError(f"HTTP {response.status} for {url}", status=response.status)
    return response.body


def fetch_snapshot(client: HttpClient, cache_dir, snapshot: Optional[str] = None) -> PosiSnapshot:
    """Download one POSI snapshot into `cache_dir/<snapshot>/` and load it.

    Resolves the current snapshot from current.json unless `snapshot` is
    given. Snapshots are immutable, so an already-cached snapshot is reused.
    Every file is checked against the snapshot's SHA256SUMS; a mismatch
    raises PosiError and nothing corrupt is kept.
    """
    if snapshot is None:
        try:
            current = client.get_json(f"{POSI_BASE_URL}/current.json")
        except HttpError:
            current = client.get_json(POSI_CURRENT_FALLBACK_URL)
        snapshot = current.get("snapshot")
        if not snapshot:
            raise PosiError("POSI current.json names no snapshot")
    target = Path(cache_dir) / snapshot
    if (target / "manifest.json").is_file() and all((target / "collections" / f).is_file() for f in COLLECTION_FILES):
        return PosiSnapshot.from_directory(target)

    def download(rel: str) -> bytes:
        primary = f"{POSI_BASE_URL}/snapshots/{snapshot}/{rel}"
        try:
            return _get_bytes(client, primary)
        except HttpError:
            return _get_bytes(client, POSI_RELEASE_URL.format(snapshot=snapshot, file=Path(rel).name))

    files = {"manifest.json": download("manifest.json"), "SHA256SUMS": download("SHA256SUMS")}
    for name in COLLECTION_FILES:
        files[f"collections/{name}"] = download(f"collections/{name}")
    sums = _parse_sha256sums(files["SHA256SUMS"].decode("utf-8"))
    for rel, body in files.items():
        if rel in sums and hashlib.sha256(body).hexdigest() != sums[rel]:
            raise PosiError(f"SHA-256 mismatch for downloaded {rel}")
    for rel, body in files.items():
        out = target / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(body)
    return PosiSnapshot.from_directory(target)


# --- integration with JournalEvidence -------------------------------------

def apply_to_evidence(evidence, record: PosiRecord) -> dict:
    """Fill fields JournalEvidence does not already have from a POSI record.

    Never overwrites an existing value: a disagreement is returned under
    `conflicts` for the user to see, not silently resolved. Returns
    {"filled": [...], "conflicts": [...]}; updates evidence.source and
    evidence.provenance_note when anything is filled.
    """
    filled, conflicts = [], []

    def consider(attr: str, value, label: str):
        if value is None:
            return
        current = getattr(evidence, attr)
        if current is None:
            setattr(evidence, attr, value)
            filled.append(attr)
        elif current != value:
            conflicts.append(f"{label}: index says {current!r}, POSI says {value!r}")

    consider("is_oa", record.open_access, "open access")
    if record.doaj_status in ("listed", "not_listed"):
        consider("is_in_doaj", record.doaj_status == "listed", "DOAJ")
    apc = record.apc or {}
    if apc.get("currency") == "USD" and isinstance(apc.get("amount"), (int, float)):
        consider("apc_usd", int(apc["amount"]), "APC (USD)")

    if filled:
        snap = record.provenance.get("snapshot")
        evidence.source = f"{evidence.source}+posi" if evidence.source and evidence.source != "unknown" else "posi"
        detail = f"POSI snapshot {snap} filled: {', '.join(filled)}"
        if "apc_usd" in filled and apc.get("source_url"):
            detail += f" (APC from {apc['source_url']}, checked {apc.get('checked_at')})"
        evidence.provenance_note = f"{evidence.provenance_note} {detail}."
    return {"filled": filled, "conflicts": conflicts}
