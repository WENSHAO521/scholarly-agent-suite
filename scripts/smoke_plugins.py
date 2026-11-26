#!/usr/bin/env python3
"""Install the built suite with both native clients and verify their loaded Skill."""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from queue import Queue
from threading import Thread

from package_suite import ROOT, SKILL_DIR, normalized_bytes
from sync_manifests import CLAUDE_ROOT, CODEX_MARKETPLACE, MARKETPLACE

PLUGIN = "scholarly-agent-suite"
PLUGIN_ID = f"{PLUGIN}@{PLUGIN}"


def verify_skill(skill_dir, *, manual=False):
    """Check all release resources at the path reported by the host."""
    if not skill_dir.is_dir():
        raise RuntimeError(f"Skill missing at {skill_dir}")
    for path in SKILL_DIR.rglob("*"):
        rel = path.relative_to(SKILL_DIR)
        if not path.is_file() or "__pycache__" in rel.parts:
            continue
        if manual and rel.parts[0] == "agents":
            continue
        actual = skill_dir / rel
        if not actual.is_file() or normalized_bytes(actual) != normalized_bytes(path):
            raise RuntimeError(f"Missing or modified installed resource: {actual}")

    # Import the shipped engines and resolve workflows outside the checkout.
    script = """
import sys
from pathlib import Path
skill = Path(sys.argv[1])
for name in ("scholarly-corpus-builder", "journal-fit-engine", "scholarly-voice-engine",
             "peer-review-engine", "prose-polish-engine", "translation-engine"):
    sys.path.insert(0, str(skill / "modules" / name))
sys.path.insert(0, str(skill / "scripts"))
import scb, jfe, prv, ppe, tre, scripts.voice, workflow_resolver
assert all(workflow_resolver.resolve_workflow(skill, name).ok
           for name in workflow_resolver.KNOWN_WORKFLOWS)
for package in (scb, jfe, prv, ppe, tre, scripts.voice, workflow_resolver):
    assert Path(package.__file__).is_relative_to(skill)
"""
    subprocess.run([sys.executable, "-I", "-B", "-c", script, str(skill_dir)],
                   cwd=skill_dir.parent, check=True, timeout=30)


def smoke_claude(executable, suite, sandbox, version):
    env = {**os.environ, "CLAUDE_CONFIG_DIR": str(sandbox / "claude")}
    env.pop("ANTHROPIC_API_KEY", None)
    env.pop("CLAUDE_CODE_OAUTH_TOKEN", None)

    def run(*args):
        result = subprocess.run(
            [executable, "plugin", *args], cwd=sandbox, env=env,
            encoding="utf-8", capture_output=True, timeout=60,
        )
        if result.returncode:
            raise RuntimeError(f"Claude {args} failed:\n{result.stdout}\n{result.stderr}")
        return result.stdout

    run("validate", "--strict", str(suite / MARKETPLACE))
    run("validate", "--strict", str(suite / CLAUDE_ROOT / ".claude-plugin/plugin.json"))
    run("marketplace", "add", str(suite))
    run("install", PLUGIN_ID)
    installed = next(p for p in json.loads(run("list", "--json")) if p["id"] == PLUGIN_ID)
    if not installed["enabled"] or installed["version"] != version:
        raise RuntimeError(f"Unexpected Claude plugin state: {installed}")
    inventory = run("details", PLUGIN)
    if not re.search(r"Skills \(1\)\s+scholarly-agent\b", inventory):
        raise RuntimeError(f"Claude did not load the Skill:\n{inventory}")
    plugin_root = Path(installed.get("readFromFolder") or installed["installPath"])
    verify_skill(plugin_root / "skills" / SKILL_DIR.name, manual=True)
    run("uninstall", PLUGIN_ID)
    if any(p["id"] == PLUGIN_ID for p in json.loads(run("list", "--json"))):
        raise RuntimeError("Claude plugin is still installed")
    run("marketplace", "remove", PLUGIN)


def smoke_codex(executable, suite, sandbox, version):
    home = sandbox / "codex"
    home.mkdir()
    env = {**os.environ, "CODEX_HOME": str(home), "RUST_LOG": "error"}
    env.pop("OPENAI_API_KEY", None)
    server = subprocess.Popen(
        [executable, "app-server"], cwd=sandbox, env=env,
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, encoding="utf-8",
    )
    lines = Queue()

    def read_stdout():
        for line in server.stdout:
            lines.put(line)
        lines.put(None)

    reader = Thread(target=read_stdout, daemon=True)
    reader.start()
    request_id = 0

    def call(method, params, *, notification=False):
        nonlocal request_id
        request = {"jsonrpc": "2.0", "method": method, "params": params}
        if not notification:
            request_id += 1
            request["id"] = request_id
        server.stdin.write(json.dumps(request) + "\n")
        server.stdin.flush()
        if notification:
            return None
        while True:
            line = lines.get(timeout=60)
            if line is None:
                raise RuntimeError(f"Codex exited during {method}")
            response = json.loads(line)
            if response.get("id") == request_id:
                if "error" in response:
                    raise RuntimeError(f"Codex {method}: {response['error']}")
                return response["result"]

    try:
        call("initialize", {
            "clientInfo": {"name": "scholarly-agent-smoke", "version": version},
            "capabilities": {"experimentalApi": True},
        })
        call("initialized", {}, notification=True)
        call("plugin/install", {
            "marketplacePath": str(suite / CODEX_MARKETPLACE),
            "pluginName": PLUGIN,
        })
        params = {"cwds": [str(sandbox)], "forceReload": True}
        skills = call("skills/list", params)["data"][0]["skills"]
        matches = [s for s in skills if s.get("pluginId") == PLUGIN_ID]
        skill_names = {SKILL_DIR.name, f"{PLUGIN}:{SKILL_DIR.name}"}
        if len(matches) != 1 or matches[0]["name"] not in skill_names or not matches[0]["enabled"]:
            raise RuntimeError(f"Codex did not load one enabled Scholarly Agent Skill: {matches}")
        skill = Path(matches[0]["path"])
        if not skill.is_relative_to(home / "plugins" / "cache") or skill.parents[2].name != version:
            raise RuntimeError(f"Unexpected Codex installed Skill path: {skill}")
        verify_skill(skill.parent)
        call("plugin/uninstall", {"pluginId": PLUGIN_ID})
        skills = call("skills/list", params)["data"][0]["skills"]
        if any(s.get("pluginId") == PLUGIN_ID for s in skills):
            raise RuntimeError("Codex plugin is still installed")
    finally:
        server.stdin.close()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait()
        reader.join(timeout=5)
        server.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude", default="claude", help="Claude Code executable")
    parser.add_argument("--codex", default="codex", help="Codex executable")
    parser.add_argument("--platform", choices=("all", "claude", "skill", "codex"), default="all")
    args = parser.parse_args()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    with tempfile.TemporaryDirectory(prefix="scholarly-agent smoke ") as tmp:
        sandbox = Path(tmp).resolve()

        def extract(package, target):
            archive = ROOT / "dist" / f"scholarly-agent-{package}-v{version}.zip"
            with zipfile.ZipFile(archive) as zf:
                zf.extractall(target)

        if args.platform in ("all", "skill"):
            extract("skill", sandbox)
            verify_skill(sandbox / SKILL_DIR.name, manual=True)
            print("Claude.ai Skill ZIP: resources verified", flush=True)
        if args.platform in ("all", "claude"):
            extract("claude-plugin", sandbox / "claude-archive")
            market = sandbox / "marketplace"
            plugin = market / CLAUDE_ROOT
            plugin.parent.mkdir(parents=True)
            shutil.move(sandbox / "claude-archive" / PLUGIN, plugin)
            (market / MARKETPLACE).parent.mkdir()
            shutil.copyfile(ROOT / MARKETPLACE, market / MARKETPLACE)
            smoke_claude(args.claude, market, sandbox, version)
            print("Claude Code: strict schema validation, installation, Skill load and removal passed", flush=True)
        if args.platform in ("all", "codex"):
            extract("suite", sandbox)
            smoke_codex(args.codex, sandbox / PLUGIN, sandbox, version)
            print("Codex: installation, Skill load and removal passed")


if __name__ == "__main__":
    main()
