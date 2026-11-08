"""scb — Scholarly Corpus Builder runtime package.

Standard-library-first Python implementation of the acquisition,
resolution, analytics, stability, profiling, and compilation pipeline
described in SKILL.md and references/. This package is what SKILL.md's
workflow steps call into when a host provides a Python execution
environment; the Skill's instructions remain usable without it (see
README.md "Runtime requirements").
"""

import os as _os


def _read_version():
    version_path = _os.path.join(_os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))), "VERSION")
    try:
        with open(version_path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return "0.0.0"


__version__ = _read_version()
