"""scb — Scholarly Corpus Builder runtime package.

Standard-library-first Python implementation of the acquisition,
resolution, analytics, stability, profiling, and compilation pipeline
described in MODULE.md and references/. This package is what MODULE.md's
workflow steps call into when a host provides a Python execution
environment; the instructions remain usable without it. Python 3.10+
standard library only.
"""

import os as _os


def _read_version():
    """The Suite version. Since v2.0.0 this package lives at
    skills/scholarly-agent/modules/scholarly-corpus-builder/scb/, and the only
    VERSION file is the Suite's, four directories above the module (present
    in a repository checkout and in the release ZIP). Before v2.1.0 this read
    a per-module VERSION that no longer exists and reported 0.0.0 in every
    corpus build manifest."""
    here = _os.path.dirname(_os.path.abspath(__file__))
    for _ in range(6):
        here = _os.path.dirname(here)
        version_path = _os.path.join(here, "VERSION")
        try:
            with open(version_path, "r", encoding="utf-8") as f:
                return f.read().strip()
        except OSError:
            continue
    return "0.0.0"


__version__ = _read_version()
