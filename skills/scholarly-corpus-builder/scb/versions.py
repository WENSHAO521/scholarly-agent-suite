"""Version resolution (PART VI).

Clusters preprint / accepted-manuscript / version-of-record / repository
copy / updated-correction entries for one work, and keeps two
independent concepts distinct: which entry anchors the citation
(`bibliographic_authority`) versus which entry is the best lawfully
accessible machine-readable text (`best_lawful_access`). One must never
silently overwrite the other.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

VERSION_OF_RECORD = "version_of_record"
ACCEPTED_MANUSCRIPT = "accepted_manuscript"
PREPRINT = "preprint"
REPOSITORY_COPY = "repository_copy"
UPDATED_CORRECTED = "updated_corrected"

# Preference order for bibliographic identity (title/venue/year/DOI).
_AUTHORITY_PREFERENCE = [VERSION_OF_RECORD, UPDATED_CORRECTED, ACCEPTED_MANUSCRIPT, PREPRINT, REPOSITORY_COPY]

# Preference order for lawful full-text access — open versions first.
_ACCESS_PREFERENCE = [REPOSITORY_COPY, ACCEPTED_MANUSCRIPT, PREPRINT, VERSION_OF_RECORD, UPDATED_CORRECTED]


@dataclass
class VersionEntry:
    kind: str  # one of the module-level constants above
    is_open: bool
    url: Optional[str] = None
    source_adapter: Optional[str] = None
    identifier: Optional[str] = None


@dataclass
class VersionResolution:
    bibliographic_authority: Optional[VersionEntry]
    best_lawful_access: Optional[VersionEntry]
    all_versions: List[VersionEntry] = field(default_factory=list)


def resolve_versions(entries: List[VersionEntry]) -> VersionResolution:
    if not entries:
        return VersionResolution(None, None, [])

    def rank(entry: VersionEntry, preference: List[str]) -> int:
        try:
            return preference.index(entry.kind)
        except ValueError:
            return len(preference)

    authority = min(entries, key=lambda e: rank(e, _AUTHORITY_PREFERENCE))

    open_entries = [e for e in entries if e.is_open]
    if open_entries:
        access = min(open_entries, key=lambda e: rank(e, _ACCESS_PREFERENCE))
    else:
        access = None

    return VersionResolution(bibliographic_authority=authority, best_lawful_access=access, all_versions=list(entries))


def to_dict(resolution: VersionResolution) -> Dict:
    def entry_dict(e: Optional[VersionEntry]) -> Optional[Dict]:
        if e is None:
            return None
        return {"kind": e.kind, "is_open": e.is_open, "url": e.url, "source_adapter": e.source_adapter, "identifier": e.identifier}

    return {
        "bibliographic_authority": entry_dict(resolution.bibliographic_authority),
        "best_lawful_access": entry_dict(resolution.best_lawful_access),
        "all_versions": [entry_dict(e) for e in resolution.all_versions],
    }
