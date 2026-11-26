# Platform acceptance

Record the client version, test date, result, and release version separately
for every platform. An account-backed result is unverified until the
corresponding interface has been exercised. The automated local tests do not
inspect Claude's hosted validation service.

## Claude Desktop Marketplace

1. Open Plugins, choose Add, then add a marketplace from a repository.
   Enter `https://github.com/WENSHAO521/scholarly-agent-suite` and sync.
2. Confirm that synchronization succeeds, the Scholarly Agent Suite
   listing is visible, and the advertised version matches the release.
3. Install and enable the plugin, start a new session, and confirm
   `scholarly-agent` is listed among the plugin's Skills. Ask it to resolve
   the `theory-paper.md` workflow and identify all seven modules.
4. Enable automatic sync where the client offers it. After a subsequent
   version-bump pull request is merged, confirm synchronization and the
   new plugin version. Run a manual re-sync if needed, and start a new
   session before rechecking the Skill.
5. Verify uninstall and reinstall if testing a disposable installation.

If sync fails, retain the exact UI message, Desktop version, time, repository
URL, and expected commit. The Windows Desktop logs can be inspected under
`%APPDATA%\Claude\logs`. On macOS, inspect `~/Library/Logs/Claude/`.
Search around the failure time for `MARKETPLACE_ERROR`,
`validation_errors`, and `error_code`. If the client exposes a developer
network response, inspect the failing synchronization response for its
validation details. Share only the failing filename, error code, and message
after removing cookies, authorization headers, personal information, and
unrelated log records. The UI may display only an aggregate failure.

For v2.6.0 the observed dialog reported one failed plugin validation. No
specific error code or per-plugin reason was available from the dialog or
the locally inspected logs. The generated subdirectory in v2.6.1 is a
compatibility change whose hosted Desktop outcome must be measured.

## Cowork

Install the synced plugin using the same Claude account and start a new
Cowork session. Confirm the plugin and its Skill are enabled, then request a
workflow that uses a reference file. Verify the response identifies the
workflow and relevant modules. Record the client and account scope, outcome,
and any error. An organization-managed GitHub marketplace has separate
visibility, app installation, permissions, and sync requirements.

## Claude.ai Skill ZIP

In Plugins or Skills, upload `scholarly-agent-skill-v<VERSION>.zip`.
Confirm upload, enablement, and a new chat that can use the Skill. To test an
update, replace the uploaded Skill with a later ZIP and verify the resulting
version or changed content in a new session. Record the result independently
from plugin installation.

## Claude Code

Run `python scripts/package_suite.py` and
`python scripts/smoke_plugins.py --platform claude` with Claude Code
installed. The smoke test runs the official strict validator, installs from
the generated marketplace, checks the Skill and runtime, and uninstalls it.
The test uses isolated settings and the built Claude plugin ZIP.

## Codex

Run `python scripts/smoke_plugins.py --platform codex` with Codex installed.
It installs the Codex ZIP through the local marketplace, checks Skill
discovery and runtime loading, and uninstalls it in an isolated profile.

## References

- [Claude marketplace reference](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude plugin manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference)
- [Agent Skills overview](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Manage plugins for an organization](https://support.claude.com/en/articles/13837433-manage-plugins-for-your-organization)
