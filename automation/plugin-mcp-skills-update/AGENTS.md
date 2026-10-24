# Agent contract: Daily Plugin, MCP & Skills Maintenance

Read `README.md` first. It owns the schedule, outcomes, and recovery.

## Ownership

- Source repository: `/Users/tai/development-space`. Layout: tool.
- Source folder: `/Users/tai/development-space/automation/plugin-mcp-skills-update`. It owns `launchd.plist`, `backend/`, and the runbook.
- Report root: `/Users/tai/.agents/automation/development-space-update-runtime/logs`. Runtime output only; keep it out of the source folder and out of Git.

## Boundaries

- Edit the source plist here. `~/Library/LaunchAgents/com.tai.development-space.update.plist` is an installed build output.
- Activate, restart, enable, disable, or remove the job only with explicit authorization for this label.
- Commit, push, merge, or publish only with explicit authorization.
- Change the schedule, environment, or command in the source plist and the README together.

## Checks before reporting work complete

1. `plutil -lint launchd.plist` returns OK.
2. `verify_automation.py "/Users/tai/development-space/automation/plugin-mcp-skills-update" --static --report-root "/Users/tai/.agents/automation/development-space-update-runtime/logs"` exits 0.
3. Unit tests in `tests/test_backend.py` exit 0.
4. A live check shows a fresh terminal outcome in `/Users/tai/.agents/automation/development-space-update-runtime/logs/latest-result.json`.
