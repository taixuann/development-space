# Consumer Integration Checks & Decoupled Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement consumer-specific live integration verification (`backend/integration.py`) with one-word smoke tests for Hermes and OpenCode, expose verification via CLI and status output, decouple automation in `scripts/install.sh`, and provide a Hermes cron prompt spec.

**Architecture:**
- `backend/integration.py` manages one-word smoke tests:
  - Hermes (`hermes -p <profile> chat -q "hi" --yolo`).
  - OpenCode (`opencode run "hi"` in target workspace).
  - Custom command runner (`consumer.check_cmd`).
- `backend/cli.py` adds `check` subcommand (`opencode-model-router check [--consumer <id>] [--all] [--json]`).
- `backend/model_sync.py` records integration results in state and displays them in `--status`.
- `automation/hermes-cron-prompt.md` provides prompt spec for Hermes Agent.
- `scripts/install.sh` accepts `--automation [launchd|hermes|none]`.

## Global Constraints
- Zero hardcoded user paths (`/Users/tai`).
- One-word probe timeout: strictly bounded to 15 seconds.
- Soft-failure: an integration probe failure must report clean diagnostics without crashing the router.
- No heavy benchmarks: lightweight inference only.

## Review Focus
1. Tool not installed on system: If `hermes` or `opencode` binary is not found, record `skipped_tool_missing` rather than crashing.
2. Hermes profile flag syntax: Ensure `-p <profile>` is only added when `consumer.get('profile_name')` exists; fallback to default profile if omitted.
3. Timeout handling: If an inference probe hangs, `subprocess.TimeoutExpired` must be caught cleanly and reported as `timeout`.
4. Automation selection in `install.sh`: Must allow choosing `launchd`, `hermes`, or `none`.
5. Notion ticket sync: Update Notion Ticket 1 (`4040a859-ed1f-8130-847a-c398ee06020f`) and Ticket 3 (`4040a859-ed1f-81b5-908a-d67fa9206cc1`) with progress and solution links.

## Tasks

### Task 1: Create `backend/integration.py` with Hermes and OpenCode Checks
- Files: `tools/admin/opencode-model-router/backend/integration.py`, `tests/test_integration.py`

### Task 2: Wire Integration Check Subcommand into CLI and Status
- Files: `tools/admin/opencode-model-router/backend/cli.py`, `backend/model_sync.py`, `tests/test_cli.py`

### Task 3: Decouple Automation in `install.sh` and Add Hermes Cron Prompt
- Files: `tools/admin/opencode-model-router/automation/hermes-cron-prompt.md`, `scripts/install.sh`, `README.md`

### Task 4: Release `v0.1.5` and Update Notion Tickets
- Files: `pyproject.toml`, Notion Ticket 1 & Ticket 3 via `ntn api`
