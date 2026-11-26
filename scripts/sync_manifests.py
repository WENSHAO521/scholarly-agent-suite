#!/usr/bin/env python3
"""Generate committed distribution metadata from VERSION and the Codex manifest."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CODEX = ".codex-plugin/plugin.json"
CLAUDE_SOURCE = "./plugins/scholarly-agent-suite"
CLAUDE_ROOT = "plugins/scholarly-agent-suite"
CLAUDE = f"{CLAUDE_ROOT}/.claude-plugin/plugin.json"
MARKETPLACE = ".claude-plugin/marketplace.json"
CODEX_MARKETPLACE = ".agents/plugins/marketplace.json"
SKILL_PATH = "skills/scholarly-agent"
CLAUDE_SKILL_ALLOWLIST = {
    "LICENSE", "SKILL.md", "modules", "protocols", "references", "scripts", "shared",
}
RUNTIME_EXCLUDES = {"__pycache__", ".git", "tests", "evals", "dist", ".github"}
CLAUDE_FILE_LIMIT = 200


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
        "plugins": [{**claude, "source": CLAUDE_SOURCE}],
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


def claude_skill_files():
    skill = ROOT / SKILL_PATH
    files = []
    for path in skill.rglob("*"):
        relative = path.relative_to(skill)
        if relative.parts[0] not in CLAUDE_SKILL_ALLOWLIST:
            continue
        if RUNTIME_EXCLUDES.intersection(relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"Symlink in Claude Skill source: {relative}")
        if path.is_file():
            if relative.name != "LICENSE" and path.suffix not in {".md", ".json", ".py"}:
                raise ValueError(f"Unsupported Claude runtime file type: {relative}")
            files.append(path)
    return sorted(files, key=lambda path: path.relative_to(skill).as_posix())


def generated_files():
    files = {
        relative: (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
        for relative, manifest in expected_manifests().items()
    }
    for path in [ROOT / "LICENSE", *claude_skill_files()]:
        relative = path.relative_to(ROOT).as_posix()
        files[f"{CLAUDE_ROOT}/{relative}"] = path.read_text(encoding="utf-8").encode("utf-8")
    if sum(path.startswith(f"{CLAUDE_ROOT}/") for path in files) > CLAUDE_FILE_LIMIT:
        raise ValueError(f"Claude Plugin exceeds the {CLAUDE_FILE_LIMIT}-file distribution target")
    return files


def sync(*, check):
    expected = generated_files()
    drift = []
    plugin = ROOT / CLAUDE_ROOT
    if plugin.resolve() != plugin.absolute():
        raise ValueError(f"Claude plugin directory is redirected: {plugin}")
    for path in plugin.rglob("*"):
        if path.is_symlink() or (path.is_dir() and path.resolve() != path.absolute()):
            raise ValueError(f"Redirected path in generated Claude plugin: {path}")
        if path.is_file() and path.relative_to(ROOT).as_posix() not in expected:
            drift.append(path.relative_to(ROOT).as_posix())
            if not check:
                path.unlink()
    for relative, content in expected.items():
        path = ROOT / relative
        if path.exists() and path.read_text(encoding="utf-8").encode("utf-8") == content:
            continue
        drift.append(relative)
        if not check:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
    return drift


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without editing files")
    args = parser.parse_args()
    drift = sync(check=args.check)
    if args.check and drift:
        parser.exit(1, "Generated distribution drift: " + ", ".join(drift) + ". Run python scripts/sync_manifests.py\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
