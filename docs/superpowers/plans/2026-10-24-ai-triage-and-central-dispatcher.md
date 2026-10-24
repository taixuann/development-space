# AI-Assisted Triage and Central Dispatcher Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete end-to-end autonomous triage and execution loop: failed launchd automations invoke OpenCode to author a formal `/writing-plans` fix document and push a ticket in `Status: Human review` to Notion; a global Central Dispatcher polls for `Status: Approved`, dispatches OpenCode with `/executing-plans` in the target space, verifies the fix, and closes the ticket as `Done`.

**Architecture:**
1. **Local AI Triage (Caller side)**: When `development-space` maintenance fails, a triage helper (`backend/ai_triage.py`) calls `opencode run` in the workspace root with a persistent session ID (`devspace-maintenance-triage`). It writes a plan into `docs/superpowers/plans/`, then invokes `ticket_submit` to create/update a Notion ticket with `Status: Human review` and the plan path.
2. **Central Dispatcher (Receiver side)**: A global Launchd service at `~/.agents/automation/agent-tickets-dispatcher/` runs every 5 minutes. It queries `ntn` for tickets with `Status: Approved`. When found, it immediately locks the ticket (`Status: In progress`), resolves the target space workspace, executes the plan via OpenCode, runs the target verification command, posts verification evidence to Notion comments, and marks `Status: Done`.

**Tech Stack:** Python 3, OpenCode CLI, Notion CLI (`ntn`), macOS Launchd, JSON REST API.

**Spec:** Notion Database `Agents Ticket` (`3ff0a859-ed1f-8072-8ae0-fdb996889173`, Data Source `3ff0a859-ed1f-80c4-b3b1-000b9c10da55`).

---

## Global Constraints

- No unreviewed mutations on `master`: AI only authors plans during automated background runs; execution happens ONLY after human status flips to `Approved`.
- Lock-before-execute: Central Dispatcher must immediately update Notion `Status: In progress` before starting execution to prevent duplicate dispatch.
- Target Space mapping:
  - `Development` -> `/Users/tai/development-space`
  - `Admin` -> `/Users/tai/.agents`
  - `Research` -> `/Users/tai/research-projects`
- Log retention: Dispatcher and maintenance jobs preserve 30-day log retention.
- Launchd compliance: Conforms to `launchd-automation` standards (absolute paths, space-contained logs with `.gitignore`, static verification pass).

## Review Focus

1. OpenCode failure or timeout: AI triage failure must fall back gracefully to raw error logging without blocking the exit code or crashing the runner.
2. Plan path extraction: Dispatcher must robustly extract relative or absolute plan paths from ticket properties or markdown bodies.
3. Race conditions: Concurrent dispatcher runs must not pick the same `Approved` ticket simultaneously.
4. Execution verification gate: Central Dispatcher must run the target space verification script; it must NOT mark `Done` unless verification exits with code 0.
5. Soft-failure reporting: If execution fails, ticket must be updated to `Status: Blocked` with error output, alerting the human.

---

### Task 1: Implement AI Triage & Plan Generation in `development-space`

**Files:**
- Create: `/Users/tai/development-space/automation/plugin-mcp-skills-update/backend/ai_triage.py`
- Modify: `/Users/tai/development-space/automation/plugin-mcp-skills-update/backend/main.py`
- Modify: `/Users/tai/development-space/automation/plugin-mcp-skills-update/tests/test_backend.py`

- [ ] **Step 1: Write unit tests for `ai_triage.py`**
  - Test `generate_triage_plan(workspace_root, error_log)`:
    - Mock `subprocess.run(["opencode", ...])` returning a simulated plan creation.
    - Test fallback when OpenCode is unavailable (generates a fallback emergency plan).
    - Test plan path extraction.
  - Test `main.py` failure handler: verifies that on failure, `generate_triage_plan` is called, plan path is attached to ticket properties, and `ticket-submit` is called with `status="Human review"`.

- [ ] **Step 2: Implement `ai_triage.py`**
  - Implement `generate_triage_plan(workspace_root: str, error_summary: str, session_id: str = "devspace-maintenance-triage") -> Tuple[Optional[str], str]`:
    - Calls `opencode run --session {session_id} --auto ...` with prompt:
      `"An automation failure occurred in development-space. Error log:\n{error_summary}\nRead AGENTS.md, inspect the error, use the /writing-plans skill to create a plan in docs/superpowers/plans/YYYY-MM-DD-fix-maintenance.md. Print the exact plan path as PLAN_PATH: <path>."`
    - Parses output to extract plan path.
    - If OpenCode is missing or fails, writes a fallback plan document and returns its path.

- [ ] **Step 3: Integrate AI Triage into `main.py`**
  - In `run_maintenance()`, when `outcome == "failed"`:
    - Call `generate_triage_plan`.
    - Pass plan path in `current_step`: `f"Plan ready: {plan_path}"`.
    - Call `submit_or_update_ticket` with `status="Human review"`.

- [ ] **Step 4: Run unit tests and static verification**
  - Run `python3 -m unittest automation/plugin-mcp-skills-update/tests/test_backend.py`.
  - Ensure all tests pass.

---

### Task 2: Scaffold the Global Central Dispatcher Automation

**Files:**
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/launchd.plist`
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/README.md`
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/AGENTS.md`
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/logs/.gitignore`
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/logs/.gitkeep`
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/update.sh`

- [ ] **Step 1: Create directory layout and standard metadata**
  - Initialize `~/.agents/automation/agent-tickets-dispatcher/` adhering to `launchd-automation` Space layout.
  - Create `README.md` and `AGENTS.md` defining schedule (every 300 seconds), ownership, and runbook.
  - Set up `logs/` directory with `.gitignore` and `.gitkeep`.

- [ ] **Step 2: Generate `launchd.plist`**
  - Label: `com.tai.agents.tickets-dispatcher`
  - Program: `/opt/miniconda3/envs/core/bin/python3`
  - Arguments: `/Users/tai/.agents/automation/agent-tickets-dispatcher/backend/main.py --report-root /Users/tai/.agents/automation/agent-tickets-dispatcher/logs`
  - `StartInterval`: 300 (runs every 5 minutes).
  - Standard PATH with fnm, node, ntn, and opencode.

---

### Task 3: Implement Central Dispatcher Engine & Ticket Processor

**Files:**
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/backend/__init__.py`
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/backend/ticket_poller.py`
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/backend/plan_executor.py`
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/backend/main.py`
- Create: `/Users/tai/.agents/automation/agent-tickets-dispatcher/tests/test_dispatcher.py`

- [ ] **Step 1: Write unit tests in `test_dispatcher.py`**
  - Test `fetch_approved_tickets()` queries Notion for `Status == "Approved"`.
  - Test `claim_ticket(page_id)` updates status to `In progress`.
  - Test `resolve_workspace_root(target_space)` maps `Development` -> `/Users/tai/development-space`.
  - Test `execute_plan_and_verify()` runs OpenCode with `/executing-plans`, runs verification, and returns success boolean.
  - Test `complete_ticket(page_id, success, evidence)` updates Notion status to `Done` or `Blocked`.

- [ ] **Step 2: Implement `ticket_poller.py`**
  - `fetch_approved_tickets()`: calls `ntn api -X POST v1/data_sources/{DEFAULT_DATASOURCE_ID}/query` filtering on `Status: Approved`.
  - `claim_ticket(page_id)`: calls `ntn api -X PATCH v1/pages/{page_id}` setting `Status: In progress`.
  - `complete_ticket(page_id, success, log_excerpt)`: sets `Status: Done` (or `Blocked`) and appends comment with execution log.

- [ ] **Step 3: Implement `plan_executor.py`**
  - Maps space string to local path.
  - Extracts plan path from page properties or body.
  - Invokes `opencode run --session {session_id} "/executing-plans {plan_path}"`.
  - Runs target space verification command (e.g. `verify_automation.py` or unit tests).
  - Returns `(success: bool, output: str)`.

- [ ] **Step 4: Implement `main.py` entrypoint**
  - Orchestrates: 30-day retention cleanup -> poll approved tickets -> for each ticket: claim -> execute -> complete.
  - Writes atomic `latest-result.json`.

- [ ] **Step 5: Run unit tests and static verification**
  - Run `python3 -m unittest discover -s ~/.agents/automation/agent-tickets-dispatcher/tests`.
  - Run `verify_automation.py ~/.agents/automation/agent-tickets-dispatcher --static`.

---

### Task 4: Update Skill Documentation and End-to-End Simulation

**Files:**
- Modify: `/Users/tai/.agents/skills/launchd-automation/SKILL.md`
- Modify: `/Users/tai/.agents/skills/ticket-submit/SKILL.md`

- [ ] **Step 1: Document Autonomous Triage & Central Dispatcher Lifecycle in Skills**
  - In `launchd-automation/SKILL.md`: Document Section on "AI-Assisted Triage and Dispatcher Contract" (`Human review` -> `Approved` -> Central Dispatcher `In progress` -> `Done`).
  - In `ticket-submit/SKILL.md`: Document the `Approved` status transition and plan attachment conventions.

- [ ] **Step 2: Run an end-to-end simulation**
  - Simulate an automation error dispatch in test mode.
  - Verify ticket moves to `Human review` with attached plan.
  - Verify simulated dispatcher pickup on `Approved`.
