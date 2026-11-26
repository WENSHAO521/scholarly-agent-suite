#!/usr/bin/env python3
"""Generate committed distribution metadata from VERSION and the Codex manifest."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEX = ".codex-plugin/plugin.json"
CLAUDE = ".claude-plugin/plugin.json"
MARKETPLACE = ".claude-plugin/marketplace.json"
CODEX_MARKETPLACE = ".agents/plugins/marketplace.json"


def read_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def expected_manifests():
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", version):
        raise ValueError("VERSION must be a stable semantic version (MAJOR.MINOR.PATCH)")
    codex = read_json(CODEX)
    codex["version"] = version
    fields = ("name", "version", "description", "author", "homepage", "repository", "license", "keywords")
    claude = {field: codex[field] for field in fields}
    label = codex["interface"]["displayName"]
    claude["displayName"] = label
    # Claude discovers the conventional skills/ directory automatically.
    marketplace = {
        "name": claude["name"],
        "owner": claude["author"],
        "metadata": {"description": claude["description"]},
        "plugins": [{**claude, "source": "."}],
    }
    codex_marketplace = {
        "name": codex["name"],
        "interface": {"displayName": label},
        "plugins": [{
            "name": codex["name"],
            "source": {"source": "local", "path": "./"},
            "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
            "category": codex["interface"]["category"],
        }],
    }
    components = read_json("COMPONENTS.json")
    components["suite_version"] = version
    return {
        CODEX: codex,
        CLAUDE: claude,
        MARKETPLACE: marketplace,
        CODEX_MARKETPLACE: codex_marketplace,
        "COMPONENTS.json": components,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without editing files")
    args = parser.parse_args()
    drift = []
    for relative, manifest in expected_manifests().items():
        path = ROOT / relative
        rendered = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
        if path.exists() and path.read_text(encoding="utf-8") == rendered:
            continue
        if args.check:
            drift.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(rendered.encode("utf-8"))
    if drift:
        parser.exit(1, "Manifest drift: " + ", ".join(drift) + ". Run python scripts/sync_manifests.py\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
