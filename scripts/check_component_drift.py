#!/usr/bin/env python3
"""Report drift between what scholarly-agent-suite has pinned
(scripts/component-sources.json) and each component repository's actual
current state.

This script only detects and reports. It never edits component-sources.json
or COMPONENTS.json, never re-pins, and never triggers a release -- a
version bump is always a deliberate maintainer action (see
RELEASE_CHECKLIST.md). It requires each component's git history to already
be available locally: either via scripts/component-sources.local.json (a
contributor's own working-copy clone) or via the same .cache/components/
bare-clone cache scripts/sync_components.py uses. Pass --fetch to update
that cache from repo_url first; without it, the script only reads what is
already present locally (same offline-by-default posture as
sync_components.py --offline).

Per-component status is one of:

  CURRENT                    -- pin matches the latest tagged release, and
                                 the pinned ref is exactly the tip of the
                                 default branch (nothing ahead, nothing
                                 newer).
  UNRELEASED_COMMITS_AHEAD   -- the component's default branch has commits
                                 past the pinned ref that are not yet a
                                 tagged release (informational).
  NEW_RELEASE_AVAILABLE      -- a newer version-tag exists than the one
                                 pinned (informational: a newer component
                                 HEAD does not by itself mean the Suite is
                                 outdated -- see README's Component
                                 synchronization section).
  PIN_NOT_TAGGED              -- the pinned ref has no tag pointing at it at
                                 all (warning: pins should normally land on
                                 a real release tag).
  PIN_UNREACHABLE             -- the pinned ref cannot be found in the local
                                 repository (hard failure: the pin itself is
                                 broken).
  VERSION_TAG_MISMATCH        -- component-sources.json declares a "tag" for
                                 this pin, but that tag does not point at the
                                 pinned ref (hard failure: inconsistent pin
                                 metadata).
  SOURCE_VERSION_MISMATCH     -- component-sources.json's declared "version"
                                 does not match the component's own VERSION
                                 file content *at the pinned ref* (hard
                                 failure: COMPONENTS.json would ship a wrong
                                 version number).
  NO_LOCAL_SOURCE             -- neither a local override nor a local cache
                                 clone was available to check this component
                                 against (informational -- not a failure by
                                 itself, since this script never fetches
                                 unless asked).

Exit code: 0 unless a hard-failure status (PIN_UNREACHABLE,
VERSION_TAG_MISMATCH, SOURCE_VERSION_MISMATCH) is found, or --fail-on-drift
is passed and any informational drift status is found.

Usage:
    python scripts/check_component_drift.py [--fetch] [--fail-on-drift] [--json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES_FILE = ROOT / "scripts" / "component-sources.json"
LOCAL_OVERRIDE_FILE = ROOT / "scripts" / "component-sources.local.json"
CACHE_DIR = ROOT / ".cache" / "components"

CURRENT = "CURRENT"
UNRELEASED_COMMITS_AHEAD = "UNRELEASED_COMMITS_AHEAD"
NEW_RELEASE_AVAILABLE = "NEW_RELEASE_AVAILABLE"
PIN_NOT_TAGGED = "PIN_NOT_TAGGED"
PIN_UNREACHABLE = "PIN_UNREACHABLE"
VERSION_TAG_MISMATCH = "VERSION_TAG_MISMATCH"
SOURCE_VERSION_MISMATCH = "SOURCE_VERSION_MISMATCH"
NO_LOCAL_SOURCE = "NO_LOCAL_SOURCE"

HARD_FAILURE_STATUSES = {PIN_UNREACHABLE, VERSION_TAG_MISMATCH, SOURCE_VERSION_MISMATCH}
INFORMATIONAL_STATUSES = {UNRELEASED_COMMITS_AHEAD, NEW_RELEASE_AVAILABLE, PIN_NOT_TAGGED, NO_LOCAL_SOURCE}


def run(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(args, capture_output=True, text=True, check=False)


def load_local_overrides() -> dict[str, str]:
    if not LOCAL_OVERRIDE_FILE.exists():
        return {}
    data = json.loads(LOCAL_OVERRIDE_FILE.read_text(encoding="utf-8"))
    return {e["name"]: e["repo_path"] for e in data.get("components", []) if e.get("name") and e.get("repo_path")}


def local_repo_path(name: str, overrides: dict[str, str]) -> str | None:
    if name in overrides:
        return overrides[name]
    cache_repo = CACHE_DIR / name
    if (cache_repo / "HEAD").is_file():
        return str(cache_repo)
    return None


def maybe_fetch(name: str, repo_url: str, overrides: dict[str, str]) -> None:
    if name in overrides:
        run(["git", "-C", overrides[name], "fetch", "--quiet", "--tags", "origin"])
        return
    cache_repo = CACHE_DIR / name
    if (cache_repo / "HEAD").is_file():
        run(["git", "-C", str(cache_repo), "fetch", "--quiet", "origin"])
    else:
        cache_repo.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--quiet", "--bare", repo_url, str(cache_repo)])


def ref_exists(repo_path: str, ref: str) -> bool:
    return run(["git", "-C", repo_path, "cat-file", "-e", ref]).returncode == 0


def resolve_head(repo_path: str) -> str | None:
    proc = run(["git", "-C", repo_path, "rev-parse", "HEAD"])
    return proc.stdout.strip() if proc.returncode == 0 else None


def tags_pointing_at(repo_path: str, ref: str) -> list[str]:
    proc = run(["git", "-C", repo_path, "tag", "--points-at", ref])
    return [t for t in proc.stdout.splitlines() if t.strip()]


def latest_version_tag(repo_path: str) -> str | None:
    proc = run(["git", "-C", repo_path, "tag", "--list", "v*", "--sort=-v:refname"])
    tags = [t for t in proc.stdout.splitlines() if t.strip()]
    return tags[0] if tags else None


def commits_ahead(repo_path: str, base_ref: str, head_ref: str) -> int | None:
    proc = run(["git", "-C", repo_path, "rev-list", "--count", f"{base_ref}..{head_ref}"])
    if proc.returncode != 0:
        return None
    return int(proc.stdout.strip())


def version_file_at_ref(repo_path: str, ref: str) -> str | None:
    proc = run(["git", "-C", repo_path, "show", f"{ref}:VERSION"])
    return proc.stdout.strip() if proc.returncode == 0 else None


def check_component(entry: dict, overrides: dict[str, str], fetch: bool) -> dict:
    name = entry["name"]
    pinned_ref = entry["ref"]
    pinned_tag = entry.get("tag")
    pinned_version = entry["version"]

    if fetch:
        maybe_fetch(name, entry["repo_url"], overrides)

    repo_path = local_repo_path(name, overrides)
    result = {
        "name": name, "pinned_ref": pinned_ref, "pinned_tag": pinned_tag,
        "pinned_version": pinned_version, "status": None, "detail": "",
    }
    if repo_path is None:
        result["status"] = NO_LOCAL_SOURCE
        result["detail"] = (
            "no local override and no .cache/components/ clone for this component -- "
            "pass --fetch, or add a scripts/component-sources.local.json override, to check it"
        )
        return result

    if not ref_exists(repo_path, pinned_ref):
        result["status"] = PIN_UNREACHABLE
        result["detail"] = f"pinned ref {pinned_ref!r} not found in {repo_path}"
        return result

    if pinned_tag:
        tags_at_pin = tags_pointing_at(repo_path, pinned_ref)
        if pinned_tag not in tags_at_pin:
            result["status"] = VERSION_TAG_MISMATCH
            result["detail"] = (
                f"component-sources.json declares tag {pinned_tag!r} for ref {pinned_ref[:12]}, "
                f"but that ref's actual tags are {tags_at_pin or '(none)'}"
            )
            return result

    actual_version = version_file_at_ref(repo_path, pinned_ref)
    if actual_version is not None and actual_version != pinned_version:
        result["status"] = SOURCE_VERSION_MISMATCH
        result["detail"] = (
            f"component-sources.json declares version {pinned_version!r}, but VERSION at the "
            f"pinned ref reads {actual_version!r}"
        )
        return result

    if not tags_pointing_at(repo_path, pinned_ref):
        result["status"] = PIN_NOT_TAGGED
        result["detail"] = f"pinned ref {pinned_ref[:12]} has no tag pointing at it"
        return result

    latest_tag = latest_version_tag(repo_path)
    if latest_tag and latest_tag != pinned_tag:
        result["status"] = NEW_RELEASE_AVAILABLE
        result["detail"] = f"latest tag in the repository is {latest_tag!r}, pin is {pinned_tag!r}"
        return result

    head = resolve_head(repo_path)
    if head and head != pinned_ref:
        ahead = commits_ahead(repo_path, pinned_ref, head)
        if ahead:
            result["status"] = UNRELEASED_COMMITS_AHEAD
            result["detail"] = f"default branch is {ahead} commit(s) ahead of the pinned ref, not yet tagged"
            return result

    result["status"] = CURRENT
    result["detail"] = "pin matches the latest tagged release and the default branch tip"
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fetch", action="store_true", help="fetch/clone each component's repo before checking")
    parser.add_argument("--fail-on-drift", action="store_true",
                         help="also exit non-zero on an informational drift status, not just a hard failure")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON instead of text")
    args = parser.parse_args()

    manifest = json.loads(SOURCES_FILE.read_text(encoding="utf-8"))
    overrides = load_local_overrides()
    results = [check_component(entry, overrides, args.fetch) for entry in manifest["components"]]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        for r in results:
            print(f"{r['status']:<28} {r['name']:<26} {r['detail']}")

    hard_failures = [r for r in results if r["status"] in HARD_FAILURE_STATUSES]
    informational = [r for r in results if r["status"] in INFORMATIONAL_STATUSES]

    if not args.json:
        print()
        print(f"{len(results) - len(hard_failures) - len(informational)} current, "
              f"{len(informational)} informational, {len(hard_failures)} hard failure(s).")

    if hard_failures:
        return 1
    if informational and args.fail_on_drift:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
