---
name: launchd-automation
description: Create, change, and verify macOS launchd jobs. Supports tool-owned source at <tool-repo>/automation/<job-name>/ and Space-owned source at ~/.agents/automation/<job-name>/, both reporting to an explicit absolute report root. Use for scheduled macOS jobs, LaunchAgents, launchctl failures, or automation placement and verification.
compatibility: macOS (darwin)
---

# launchd automation

Own one job at a time: where its source lives, where it reports, and what proves a change works. Placement rules live in `automation/README.md` and `automation/AGENTS.md`; tool-owned jobs belong to Development Space (`tools/AGENTS.md`). Lifecycle detail is in [`references/launchd_best_practices.md`](references/launchd_best_practices.md).

## 1. Classify the owner

| The job… | Layout | Source folder | Branch |
| --- | --- | --- | --- |
| serves one tool | `tool` | `<tool-repo>/automation/<job-name>/` | `admin/<tool-name>_<request-id>` |
| coordinates several tools, or applies Space policy | `space` | `~/.agents/automation/<job-name>/` | `automation/<job-name>` |

> [!IMPORTANT]
> **Production Isolation Invariant**: A production LaunchAgent (`~/Library/LaunchAgents/<label>.plist`) must NEVER execute against a `development-space` source path (`/Users/tai/development-space/...`). It must point strictly to the target consumer space runner (e.g. `/Users/tai/.agents/automation/<job-name>/run.sh`) or a globally installed CLI in `/Users/tai/.local/bin/`. Development space is an active workshop with isolated worktrees and uncommitted changes; background daemons must never depend on development trees.

Decide from the primary responsibility and the job's own lifecycle. A shared incident reporter or a shared helper does not move ownership. Ask when the owner is unclear; the layout decides the repository, and the repository decides who reviews the change.

Prefer launchd for a deterministic script: a Hermes cron job starts an agent session and a model call on every run, and bare `crontab` does not replay runs missed during sleep. Before creating a new label for a small recurring chore (for example pruning merged git branches), check whether an existing Space job already has the lock, run records and incident reporting it needs; add the chore as a new phase of that job (README description updated, same schedule) instead of a second label.

## 2. Fix the report root first

Runtime reports go to an explicit absolute path.
- **Space-contained layout (default for space tools)**: Keep logs inside the owning space at `<job-dir>/logs/` (with a `.gitignore` ignoring `*.log`, `latest-result.json`, `runs/`) so each space fully owns its logs.
- **External layout**: Use `/Users/tai/.agents/automation/<stable-job-name>/logs/` when an external runtime store is required.

The scheduled entrypoint receives that path as an argument. A worktree or fixture run uses a temporary report root, temporary state, and fake configuration, and writes nothing to the live root.

## 3. Scaffold

```bash
python3 ~/.agents/skills/launchd-automation/scripts/scaffold_automation.py \
    --layout space \
    --target-dir /Users/tai/.agents/automation/nightly-report \
    --report-root /Users/tai/.agents/automation/nightly-report-runtime/logs \
    --label com.tai.nightly.report \
    --title "Nightly report" \
    --schedule "0 4 * * *" \
    --program /opt/homebrew/bin/python3 \
    --command "/Users/tai/.agents/automation/nightly-report/run.py"
```

For a tool-owned job, pass `--layout tool --request-id 008` and a target inside the tool repository. The scaffold derives the tool branch from the repository name and the request id.

The scaffold refuses a relative report root, a report root inside the source folder, an existing scaffold, a tool target outside a Git repository, and a Space target inside another repository. It reports the conflicting files instead of overwriting.

Default output is direct execution: `ProgramArguments` holds the absolute program and its absolute arguments, with no wrapper. Add `--wrapper` only when the job needs a lock or a terminal event line. It writes `scripts/run.sh` and calls that.

Schedules: `"0 4 * * *"`, `"daily:04:00"`, or `"interval:3600"`. `RunAtLoad` is off unless `--run-at-load` is passed.

## 4. Customize the job

- Keep the program and every file argument absolute. The plist declares no working directory.
- Declare the environment once in the plist `EnvironmentVariables`. The job loads no `.env`, shell profile, or version-manager init.
- Write one terminal outcome per run: `latest-result.json` with `run_id`, label, source revision and dirty state, start and end time, `outcome`, exit code, and duration. Outcomes are `success`, `cached`, `failed`, and `skipped_locked`.
- Treat a held lock as a recorded skip, not a failure, and leave the active run's record alone.
- Keep the previous valid state when the tool fails.
- The scheduled run executes whatever is in the stable checkout's working tree, including uncommitted edits and a checked-out task branch. A change goes live at the next fire without redeploy when the installed plist already points at the source path, so finish and verify code before leaving it in the checkout, and expect an unmerged worker branch to run if the tree sits on it.
- Any job step that deletes or force-removes (branches, files) deletes only after a proof computed in the same run, skips whatever is checked out or in use, and has a dry-run mode that the tests and the pre-merge check exercise.
- Set retention in the README and enforce it in the job: purge `runs/` snapshots and rotated logs older than 30 days. Keep `latest-result.json` outside rotation.
- Fill the runbook: schedule and timezone, sleep and wake limits, absolute tool paths, report location, outcomes, delivery failure, replay, rollback, and the statement that a runner cannot report its own absence.

## 5. Validate statically

```bash
python3 ~/.agents/skills/launchd-automation/scripts/verify_automation.py \
    "/path/to/automation/<job-name>" --static --report-root "/abs/report/root"
```

Static is the default and starts nothing. It checks file presence, the executable bit, `plutil -lint`, the Label read from plist contents, plist paths, an absolute report root outside the source, and one installed plist per label. Add `--compare-installed` to compare the source plist with `~/Library/LaunchAgents/<label>.plist` byte for byte. It calls only read-only `launchctl print`; add `--skip-launchctl` to omit even that.

Each check prints `PASS` or `FAIL` with an identifier, then a `SUMMARY` line. Exit code is nonzero on any failure. Fix every `FAIL` before proposing a deploy.

## 6. Deploy only when authorized

A scaffolded job is source, not a running service. Copying the plist, booting out, and bootstrapping change live state and need explicit authorization for that label.

```bash
launchctl bootout gui/$(id -u)/<label>          # tolerate "not loaded"
cp "<job-dir>/launchd.plist" ~/Library/LaunchAgents/<label>.plist
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/<label>.plist
```

`scaffold_automation.py --deploy` performs the same steps with an argument list and prints the exact commands. It is opt-in and off by default. Keep the previous plist and record the rollback before the copy.

## 7. Prove a live outcome

```bash
python3 ~/.agents/skills/launchd-automation/scripts/verify_automation.py \
    "/path/to/automation/<job-name>" --live --timeout 600
```

`--live` is the only mode that kickstarts, and only after the static checks pass. Dispatch is not completion: a kickstart exit code of 0 proves the request was accepted. The verifier then polls for a fresh terminal result file or a `terminal=` log line and fails when none appears, or when the outcome is `failed`.

A plist in `~/Library/LaunchAgents` that matches the source byte for byte does not prove the job is loaded. Check `launchctl print gui/$(id -u)/<label>` (it reports "Could not find service" when dormant, for example after a migration or reboot) and compare the newest `latest-result.json` or log time with the schedule. Report a dormant job and ask before `bootstrap`, since loading it starts unattended runs; read the job's side effects first (a sync job may auto-commit and push every tracked repo).

Report configuration checks, live checks, and skipped checks separately. State the authorization you relied on.

## 8. Incident escalation & ticket submission

When a launchd job fails, encounters an unhandled exception, or registers persistent drift:
- Reference and use the `/ticket-submit` skill (`~/.agents/skills/ticket-submit/scripts/ticket_submit.py`).
- **Target Space**: Inferred dynamically from the job's directory root:
  - `~/development-space` → `Development`
  - `~/.agents` → `Admin` or `Cross-space`
  - `~/research-projects` → `Research`
  - `~/study` → `Study`
  - `~/personal` → `Personal`
- **System Component**: Always `Automations & Runtime`.
- **Request Type**: Always `Fix`.
- **Status**: `Blocked` (for failures) or `Captured`.
- **Deduping**: `ticket_submit` checks for existing open tickets with the issue signature. If found, it appends a recurrence comment; if not, it creates a new ticket.
- **Resilience**: The failure escalation call must fail softly. An outage of Notion or `ntn` must log to `stderr` and never mask the underlying automation exit code.

## Reference

Read [`references/launchd_best_practices.md`](references/launchd_best_practices.md) for exit codes 78, 126, 127, bootstrap and bootout failures, sleep and wake behavior, deployment order, and rollback.
