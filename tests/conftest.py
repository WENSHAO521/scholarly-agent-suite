import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

# Module engines, importable as `scb`, `jfe`, `prv`, `ppe`, and `scripts.voice` for the
# merged module tests under tests/modules/ (and the cross-module e2e tests).
MODULES_DIR = ROOT / "skills" / "scholarly-agent" / "modules"
for _module in ("scholarly-corpus-builder", "journal-fit-engine", "scholarly-voice-engine", "peer-review-engine",
                "prose-polish-engine"):
    _path = str(MODULES_DIR / _module)
    if _path not in sys.path:
        sys.path.insert(0, _path)


def load_module(name: str, filename: str):
    path = SCRIPTS_DIR / filename
    return load_module_at(name, path)


def load_module_at(name: str, path: Path):
    """Load a module from an arbitrary absolute path under a unique name,
    bypassing sys.path/package resolution entirely. Used for component
    runtime code that lives under a directory literally named "scripts"
    (e.g. skills/scholarly-agent/scripts/, skills/scholarly-voice-engine/
    scripts/) -- a plain `sys.path.insert` + `import scripts...` would
    collide the moment two such component directories are both on sys.path
    in the same process, since Python caches "scripts" as one global name
    regardless of which directory it first resolved from.

    Registers the module in sys.modules under `name` before executing it --
    required for a module using `from __future__ import annotations` with
    dataclasses, since dataclasses resolves deferred annotations via
    `sys.modules[cls.__module__]` and raises AttributeError on a module
    that exec'd successfully but was never registered."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module
