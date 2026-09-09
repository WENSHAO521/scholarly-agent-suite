#!/usr/bin/env python3
"""Reproducible component sync for scholarly-agent-suite.

Reads scripts/component-sources.json (public, portable: repo_url + a pinned
commit sha + optional tag + runtime allowlist per component) and an optional,
gitignored scripts/component-sources.local.json override (a "repo_path" per
component pointing at a contributor's own local working copy, to skip the
network clone during iterative local development). For each component:
verify the pinned commit is reachable -- from the local override repo if one
is configured, otherwise from a maintained local bare clone of repo_url under
.cache/components/ -- export exactly that commit via `git archive`, copy only
the allowlisted runtime paths into skills/<name>/, validate the resulting
SKILL.md, and rewrite COMPONENTS.json with the exact synced version, source
repository, and source commit.

This script never reads a component's working-tree HEAD or a floating
branch -- it always exports the exact pinned commit, so an official release
cannot accidentally pick up uncommitted or since-changed content. A local
override is only an alternate source of those same bytes: it must still
contain the pinned commit, not a different revision.

Usage:
    python scripts/sync_components.py [--check] [--offline]

--check performs the export/validation but does not write skills/ or
COMPONENTS.json; it exits non-zero if any component would fail to sync.
--offline skips `git clone`/`git fetch` against repo_url and requires the
pinned commit to already be present in the local cache or override repo
(useful for CI or a fully reproducible build without network access).
"""
from __future__ import annotations

import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "scripts" / "component-sources.json"
LOCAL_OVERRIDE_FILE = ROOT / "scripts" / "component-sources.local.json"
SKILLS_DIR = ROOT / "skills"
COMPONENTS_FILE = ROOT / "COMPONENTS.json"
CACHE_DIR = ROOT / ".cache" / "components"

REQUIRED_RUNTIME_FILE = "SKILL.md"


class SyncError(RuntimeError):
    pass


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, check=False)


def verify_commit_reachable(repo_path: str, ref: str) -> None:
    proc = run(["git", "-C", repo_path, "cat-file", "-e", ref])
    if proc.returncode != 0:
        raise SyncError(f"commit {ref} not found in {repo_path}")


def ensure_local_cache(name: str, repo_url: str, ref: str, offline: bool) -> str:
    """Return a local repo path containing `ref`, cloning/fetching as needed."""
    cache_repo = CACHE_DIR / name
    exists = (cache_repo / "HEAD").is_file()
    if not exists:
        if offline:
            raise SyncError(f"{name}: no local cache at {cache_repo} and --offline was given")
        cache_repo.parent.mkdir(parents=True, exist_ok=True)
        proc = run(["git", "clone", "--quiet", "--bare", repo_url, str(cache_repo)])
        if proc.returncode != 0:
            raise SyncError(f"{name}: clone failed: {proc.stderr.decode(errors='replace')}")
    elif run(["git", "-C", str(cache_repo), "cat-file", "-e", ref]).returncode != 0:
        if offline:
            raise SyncError(f"{name}: commit {ref} not in local cache and --offline was given")
        proc = run(["git", "-C", str(cache_repo), "fetch", "--quiet", "origin"])
        if proc.returncode != 0:
            raise SyncError(f"{name}: fetch failed: {proc.stderr.decode(errors='replace')}")
    verify_commit_reachable(str(cache_repo), ref)
    return str(cache_repo)


def git_archive_to(repo_path: str, ref: str, dest: Path) -> None:
    """Export `ref` from the repo at repo_path into dest (a clean directory)."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    proc = run(["git", "-C", repo_path, "archive", ref])
    if proc.returncode != 0:
        raise SyncError(
            f"git archive failed for {repo_path}@{ref}: "
            f"{proc.stderr.decode(errors='replace')}"
        )
    with tarfile.open(fileobj=io.BytesIO(proc.stdout)) as tf:
        tf.extractall(dest)  # noqa: S202 -- exact pinned commit of a known component repo


def copy_allowlisted(export_dir: Path, include: list[str], target_dir: Path) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True)
    for rel in include:
        src = export_dir / rel
        if not src.exists():
            # Optional entries (e.g. LICENSE, assets/) may not exist in every
            # component; SKILL.md is checked separately as mandatory.
            continue
        dst = target_dir / rel
        if src.is_dir():
            shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)


def validate_skill_md(target_dir: Path, expected_name: str) -> str:
    skill_md = target_dir / REQUIRED_RUNTIME_FILE
    if not skill_md.exists():
        raise SyncError(f"{expected_name}: missing {REQUIRED_RUNTIME_FILE} after sync")
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SyncError(f"{expected_name}: {REQUIRED_RUNTIME_FILE} has no frontmatter")
    end = text.find("\n---", 3)
    if end == -1:
        raise SyncError(f"{expected_name}: {REQUIRED_RUNTIME_FILE} frontmatter not closed")
    frontmatter = text[3:end]
    name_line = next((l for l in frontmatter.splitlines() if l.startswith("name:")), None)
    if name_line is None:
        raise SyncError(f"{expected_name}: {REQUIRED_RUNTIME_FILE} missing name: field")
    actual_name = name_line.split(":", 1)[1].strip()
    if actual_name != expected_name:
        raise SyncError(
            f"{expected_name}: SKILL.md name mismatch (found '{actual_name}')"
        )
    return actual_name


def load_local_overrides() -> dict[str, str]:
    """Map component name -> local repo_path, from the gitignored override file."""
    if not LOCAL_OVERRIDE_FILE.exists():
        return {}
    data = json.loads(LOCAL_OVERRIDE_FILE.read_text(encoding="utf-8"))
    overrides = {}
    for entry in data.get("components", []):
        if entry.get("name") and entry.get("repo_path"):
            overrides[entry["name"]] = entry["repo_path"]
    return overrides


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="dry run, no writes")
    parser.add_argument("--offline", action="store_true",
                         help="do not clone/fetch from repo_url; require the pinned commit locally")
    args = parser.parse_args()

    manifest = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    overrides = load_local_overrides()
    components_out: dict[str, dict] = {}
    work_root = ROOT / ".sync_work"
    if work_root.exists():
        shutil.rmtree(work_root)
    work_root.mkdir()

    errors: list[str] = []
    for entry in manifest["components"]:
        name = entry["name"]
        try:
            local_path = overrides.get(name)
            if local_path:
                verify_commit_reachable(local_path, entry["ref"])
                repo_path, source_note = local_path, f"local override ({local_path})"
            else:
                repo_path = ensure_local_cache(name, entry["repo_url"], entry["ref"], args.offline)
                source_note = f"cached clone of {entry['repo_url']}"
            export_dir = work_root / f"{name}-export"
            git_archive_to(repo_path, entry["ref"], export_dir)
            target_dir = SKILLS_DIR / name
            if not args.check:
                copy_allowlisted(export_dir, entry["include"], target_dir)
                validate_skill_md(target_dir, name)
            else:
                staging = work_root / f"{name}-staged"
                copy_allowlisted(export_dir, entry["include"], staging)
                validate_skill_md(staging, name)
            components_out[name] = {
                "version": entry["version"],
                "role": entry["role"],
                "source_repository": entry["repo_url"],
                "source_commit": entry["ref"],
            }
            print(f"OK  {name} @ {entry['ref'][:12]} (v{entry['version']}) via {source_note}")
        except SyncError as exc:
            errors.append(str(exc))
            print(f"FAIL {name}: {exc}", file=sys.stderr)

    shutil.rmtree(work_root, ignore_errors=True)

    if errors:
        print(f"\n{len(errors)} component(s) failed to sync.", file=sys.stderr)
        return 1

    if not args.check:
        suite_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
        components_out["scholarly-agent"] = {
            "version": suite_version,
            "role": "orchestration",
            "source_repository": "in-tree (scholarly-agent-suite)",
            "source_commit": "n/a",
        }
        existing = json.loads(COMPONENTS_FILE.read_text(encoding="utf-8")) if COMPONENTS_FILE.exists() else {}
        existing["suite"] = "scholarly-agent-suite"
        existing["suite_version"] = suite_version
        existing["components"] = {
            k: components_out[k]
            for k in ["scholarly-agent", "adaptive-model-router", "scholarly-corpus-builder",
                      "scholarly-voice-engine", "journal-fit-engine"]
        }
        COMPONENTS_FILE.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
        print(f"\nWrote {COMPONENTS_FILE}")

    print("\nAll components synced." if not args.check else "\nAll components would sync cleanly.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
