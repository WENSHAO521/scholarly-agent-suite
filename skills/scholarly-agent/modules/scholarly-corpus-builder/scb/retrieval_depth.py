"""Retrieval depth levels (PART VIII). The acquisition planner should
retrieve the minimum level necessary for the feature actually needed —
see SKILL.md's retrieval-minimization decision sequence.
"""

from __future__ import annotations

from scb.oa_resolver import (
    ABSTRACT_AVAILABLE,
    OA_FULLTEXT_AVAILABLE,
    OA_LANDING_PAGE,
    OA_PDF_AVAILABLE,
    STRUCTURED_FULLTEXT_AVAILABLE,
    AccessResolution,
)

LEVEL_0_METADATA = "LEVEL_0_METADATA"
LEVEL_1_ABSTRACT = "LEVEL_1_ABSTRACT"
LEVEL_2_STRUCTURE = "LEVEL_2_STRUCTURE"
LEVEL_3_FULLTEXT = "LEVEL_3_FULLTEXT"

_ORDER = [LEVEL_0_METADATA, LEVEL_1_ABSTRACT, LEVEL_2_STRUCTURE, LEVEL_3_FULLTEXT]

_STATES_WITH_ABSTRACT_OR_BETTER = {
    ABSTRACT_AVAILABLE,
    OA_LANDING_PAGE,
    OA_FULLTEXT_AVAILABLE,
    OA_PDF_AVAILABLE,
    STRUCTURED_FULLTEXT_AVAILABLE,
}
_STATES_WITH_STRUCTURE_OR_BETTER = {OA_FULLTEXT_AVAILABLE, OA_PDF_AVAILABLE, STRUCTURED_FULLTEXT_AVAILABLE}
_STATES_WITH_FULLTEXT = {OA_FULLTEXT_AVAILABLE, OA_PDF_AVAILABLE, STRUCTURED_FULLTEXT_AVAILABLE}


def depth_reached(resolution: AccessResolution, has_abstract: bool) -> str:
    """What retrieval depth is actually available given an OA
    resolution and whether the record carries an abstract."""
    if resolution.state in _STATES_WITH_FULLTEXT and resolution.readable:
        # Structured full text (e.g. JATS/XML) is a superset of plain
        # full text — both readable and section-structured.
        return LEVEL_3_FULLTEXT
    if resolution.state in _STATES_WITH_STRUCTURE_OR_BETTER:
        return LEVEL_2_STRUCTURE
    if has_abstract or resolution.state in _STATES_WITH_ABSTRACT_OR_BETTER:
        return LEVEL_1_ABSTRACT
    return LEVEL_0_METADATA


def meets_requested_depth(resolution: AccessResolution, has_abstract: bool, requested: str) -> bool:
    reached = depth_reached(resolution, has_abstract)
    return _ORDER.index(reached) >= _ORDER.index(requested)
