import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


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
