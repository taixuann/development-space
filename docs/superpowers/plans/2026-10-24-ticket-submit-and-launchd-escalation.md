# Ticket Submit Skill and Launchd Escalation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a reusable `ticket-submit` skill with a standalone CLI/module to report and deduplicate incidents in the Notion **Agent Tickets** database via `ntn`, update `launchd-automation` to reference `ticket-submit` for failure escalation and 30-day retention, and integrate both into `development-space` daily maintenance.

**Architecture:** 
A centralized, reusable skill `ticket-submit` lives in `~/.agents/skills/ticket-submit/` with documentation and an executable helper `scripts/ticket_submit.py`. It encapsulates the Notion Agent Tickets schema, deduplication querying, and comment appending via `ntn`. The `launchd-automation` skill references `ticket-submit` as its standard incident escalation layer. Finally, `development-space`'s daily maintenance automation invokes this helper on error and enforces 30-day log retention.

**Tech Stack:** Python 3, Notion CLI (`ntn`), Launchd, JSON REST API (`v1/data_sources/.../query`, `v1/pages`, `v1/comments`).

**Spec:** Notion Database `Agents Ticket` (`3ff0a859-ed1f-8072-8ae0-fdb996889173`, Data Source `3ff0a859-ed1f-80c4-b3b1-000b9c10da55`).

## Global Constraints

- Never hardcode Notion property schemas inside domain automations; resolve them through `ticket-submit`.
- Database target: `3ff0a859-ed1f-8072-8ae0-fdb996889173` (Data Source: `3ff0a859-ed1f-80c4-b3b1-000b9c10da55`).
- Request Type for automated failure escalation is always `Fix`.
- System Component for launchd jobs is always `Automations & Runtime`.
- Target Space is dynamically resolved: `Development` for `~/development-space`, `Admin` or `Cross-space` for `~/.agents`.
- Deduplication rule: never create duplicate tickets for the same unresolved issue; append a comment with timestamp and log snippet if an open ticket exists.
- 30-day retention: automatically purge run records and log snapshots older than 30 days; `latest-result.json` is preserved.

## Review Focus

1. `ntn` CLI unavailable or failing network: reporter must fail softly, logging an error to stderr without crashing the automation.
2. Deduplication query accuracy: queries must filter by title signature and exclude tickets with status `Done` or `Canceled`.
3. Space path resolution: correctly maps workspace root paths to the appropriate Notion `Target Space` multi-select options.
4. Skills discovery: distinguishes npx-managed skills from custom bespoke skills in `skills/`.
5. Retention window calculation: correctly computes `mtime` older than 30 days and removes only rotation files, never `latest-result.json`.

---

### Task 1: Create the `ticket-submit` Reusable Skill and CLI Helper

**Files:**
- Create: `/Users/tai/.agents/skills/ticket-submit/SKILL.md`
- Create: `/Users/tai/.agents/skills/ticket-submit/scripts/ticket_submit.py`
- Create: `/Users/tai/.agents/skills/ticket-submit/tests/test_ticket_submit.py`

- [x] **Step 1: Write failing unit test for `ticket_submit.py`**
  - Create `test_ticket_submit.py` testing query, comment append, create, dedup, and soft failure.
  - Confirmed RED.

- [x] **Step 2: Implement `scripts/ticket_submit.py`**
  - Implemented query, comment, create, and submit_or_update_ticket.
  - Set executable permissions.

- [x] **Step 3: Run unit tests and ensure 100% pass**
  - Ran `test_ticket_submit.py`: 7/7 tests passed (GREEN).

- [x] **Step 4: Author `SKILL.md` for `ticket-submit`**
  - Documented properties, dedup contract, CLI usage, and python import.
  - Created symlinks to `~/.gemini/config/skills/ticket-submit` and `~/.claude/skills/ticket-submit`.

---

### Task 2: Update `launchd-automation` Skill Specification

**Files:**
- Modify: `/Users/tai/.agents/skills/launchd-automation/SKILL.md`

- [x] **Step 1: Update `SKILL.md` with Incident Escalation and Retention Standards**
  - Added Section on **Incident Escalation**: Referenced `ticket-submit` for failure escalation and dynamic space mapping.
  - Standardized 30-day retention for `runs/` snapshots and rotated logs.

---

### Task 3: Integrate `ticket-submit` & Retention into `development-space` Automation

**Files:**
- Modify: `/Users/tai/development-space/automation/plugin-mcp-skills-update/backend/main.py`
- Modify: `/Users/tai/development-space/automation/plugin-mcp-skills-update/backend/skills_updater.py`
- Modify: `/Users/tai/development-space/automation/plugin-mcp-skills-update/tests/test_backend.py`

- [x] **Step 1: Write unit tests in `test_backend.py` for retention and failure reporting**
  - Added `test_cleanup_old_runs` and `test_run_maintenance_failure_escalation`.
  - Confirmed RED.

- [x] **Step 2: Implement 30-day retention and ticket escalation in `backend/main.py`**
  - Implemented `cleanup_old_runs`.
  - Added escalation via `submit_or_update_ticket` on failure.

- [x] **Step 3: Enhance `backend/skills_updater.py`**
  - Added `ensure_skills_lock` and error signature parsing.

- [x] **Step 4: Run full test suite & static verification**
  - Ran `test_backend.py`: 7/7 tests passed.
  - Ran `verify_automation.py --static`: 17/17 checks passed (0 failures).
  - Executed `update.sh` live: OK (duration 2.22s, exit 0).
