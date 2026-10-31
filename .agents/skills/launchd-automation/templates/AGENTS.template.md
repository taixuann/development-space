# Agent contract: {{SERVICE_TITLE}}

Read `README.md` first. It owns the schedule, outcomes, and recovery.

## Ownership

- Source repository: `{{REPO_ROOT}}`. Layout: {{LAYOUT_DESCRIPTION}}.
- Branch convention: `{{BRANCH}}`.
- Source folder: `{{WORKING_DIR}}`. It owns `launchd.plist`, the runbook, and any runner.
- Report root: `{{REPORT_ROOT}}`. Runtime output only; keep it out of the source folder and out of Git.

## Boundaries

- Edit the source plist here. `~/Library/LaunchAgents/{{LABEL}}.plist` is a build output.
- Activate, restart, enable, disable, or remove the job only with explicit authorization for this label.
- Commit, push, merge, or publish only with explicit authorization.
- Change the schedule, environment, or command in the source plist and the README together.

## Checks before reporting work complete

1. `plutil -lint launchd.plist` returns OK.
2. `verify_automation.py "{{WORKING_DIR}}" --static --report-root "{{REPORT_ROOT}}"` exits 0.
3. A live check, only when authorized, shows a fresh terminal outcome in `{{REPORT_ROOT}}/latest-result.json`.

State which checks ran, which were skipped, and why.
