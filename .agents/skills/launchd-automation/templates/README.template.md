# {{SERVICE_TITLE}}

{{SERVICE_DESCRIPTION}}

| Field | Value |
| --- | --- |
| Label | `{{LABEL}}` |
| Source owner | {{OWNER_DESCRIPTION}} |
| Branch | `{{BRANCH}}` |
| Source folder | `{{WORKING_DIR}}` |
| Report root | `{{REPORT_ROOT}}` |
| Installed plist | `~/Library/LaunchAgents/{{LABEL}}.plist` |

## Schedule and time

{{SCHEDULE_HUMAN_READABLE}}. The installed plist is the only authority for the trigger; this file describes it.

Wall-clock times use the Mac's local timezone at fire time ({{LOCAL_TIMEZONE}} when scaffolded). A timezone change moves the next run. `StartCalendarInterval` fires late after sleep; a time that passes while the Mac is asleep runs only if launchd replays it. `StartInterval` counts from the last start and does not count sleep. Record the real start time in the run report rather than assuming the nominal one.

## Runtime

The job calls `{{PROGRAM_PATH}}` with absolute arguments. `PATH`, `HOME`, and `LANG` come from the plist `EnvironmentVariables`. The job loads no `.env`, no shell profile, and no version-manager init.
{{WRAPPER_LINE}}
## Reports and retention

Reports go to `{{REPORT_ROOT}}`:

| File | Purpose |
| --- | --- |
| `stdout.log` | Process output and one-line run events |
| `stderr.log` | Diagnostics and tracebacks |
| `latest-result.json` | Last terminal outcome, written atomically |
| `runs/` | One record per run, named by `run_id` |

A run record holds `run_id`, label, source revision and dirty state, start and end time, outcome, exit code, and duration. Keep 30 days and at most 100 completed runs. Rotation never removes `latest-result.json`.

## Outcomes

| Outcome | Meaning |
| --- | --- |
| `success` | The job reached its intended effect. |
| `cached` | No change was needed. This is a successful run. |
| `skipped_locked` | Another run held the lock. Record the skip, exit 0, leave the active run's record alone. |
| `failed` | The tool failed. Keep the previous valid state and exit nonzero. |

Delivery failure: a local report stays valid when external delivery fails. Pending deliveries stay in the tool's own queue, are reconciled before retry, and retry within a bounded limit.

## Replay and recovery

Replay a failed run by calling the same entrypoint with the old parameters and a new `run_id`. A replay is a new run; it does not rewrite history.

Recovery keeps the last valid configuration:
1. `launchctl bootout gui/$(id -u)/{{LABEL}}`
2. Copy the saved plist over `~/Library/LaunchAgents/{{LABEL}}.plist`.
3. `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/{{LABEL}}.plist`
4. Confirm a fresh terminal outcome in `latest-result.json`.

## Known limit

A runner cannot report its own absence. A run that never starts leaves no local trace. Detect missed runs with a separate observer that reads the age of `latest-result.json`; do not claim the job is healthy from schedule alone.

## Commands

```bash
# Static check. Never starts the job.
python3 ~/.agents/skills/launchd-automation/scripts/verify_automation.py "{{WORKING_DIR}}" --static --report-root "{{REPORT_ROOT}}"

# Manual run, when authorized.
{{MANUAL_RUN_COMMAND}} --report-root "{{REPORT_ROOT}}"
```
