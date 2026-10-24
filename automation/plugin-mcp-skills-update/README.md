# Daily Plugin, MCP & Skills Maintenance

Daily automated maintenance service for `development-space`. Keeps installed skills, Superpowers plugin, and local MCP Xerj synchronized and healthy.

| Field | Value |
| --- | --- |
| Label | `com.tai.development-space.update` |
| Source owner | Tool-owned (`/Users/tai/development-space/automation/plugin-mcp-skills-update`) |
| Report root | Space-contained (`/Users/tai/development-space/automation/plugin-mcp-skills-update/logs`) |
| Installed plist | `~/Library/LaunchAgents/com.tai.development-space.update.plist` |

## Schedule and time

Scheduled daily at 03:00 (Asia/Ho_Chi_Minh). The installed plist is the only authority for the trigger; this file describes it.

Wall-clock times use the Mac's local timezone at fire time. `StartCalendarInterval` fires late after sleep; a time that passes while the Mac is asleep runs when the Mac wakes.

## Runtime

The job calls Python 3 directly:
```bash
/opt/miniconda3/envs/core/bin/python3 \
  /Users/tai/development-space/automation/plugin-mcp-skills-update/backend/main.py \
  --report-root /Users/tai/development-space/automation/plugin-mcp-skills-update/logs
```

`PATH` and `HOME` come from the plist `EnvironmentVariables`. The job loads no `.env`, no shell profile, and no version-manager init.

## Reports and retention

Reports are contained locally in the workspace at `automation/plugin-mcp-skills-update/logs`:

| File | Purpose |
| --- | --- |
| `stdout.log` | Process output and one-line run events |
| `stderr.log` | Diagnostics and tracebacks |
| `latest-result.json` | Last terminal outcome, written atomically |

A run record holds `run_id`, label, start and end time, outcome, exit code, duration, and component details. Git ignores `*.log`, `latest-result.json`, and `runs/` via local `.gitignore` to keep git status clean.

## Outcomes

| Outcome | Meaning |
| --- | --- |
| `success` | All 3 phases (Skills, Superpowers, MCP Xerj) completed successfully with exit code 0. |
| `cached` | Dry run or no changes needed. |
| `skipped_locked` | Another run held the lock. |
| `failed` | One or more components failed or reported drift. Exit code nonzero. |

## Quick commands

- **Run manually (live)**:
  ```bash
  ./update.sh
  ```
- **Run dry-run**:
  ```bash
  ./update.sh --dry-run
  ```
- **Install daemon**:
  ```bash
  ./install-launchd.sh
  ```
- **Check status**:
  ```bash
  ./status.sh
  ```
- **Run verification**:
  ```bash
  python3 ~/.agents/skills/launchd-automation/scripts/verify_automation.py . --static --report-root logs
  ```
