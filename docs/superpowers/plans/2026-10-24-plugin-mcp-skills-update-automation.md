# Plugin, MCP, and Skills Daily Update Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean repository root by relocating MCP definition to `.agents/mcp.json`, syncing it across `.codex` and `.opencode`, and building a daily automated update system with launchd in `automation/plugin-mcp-skills-update/` that updates Superpowers, syncs Xerj MCP, and updates installed Skills via `vercel-labs/skills` CLI, outputting structured logs.

**Architecture:**
- **MCP Source of Truth:** `.agents/mcp.json` defines `xerj`. Synced to `.codex/config.toml` and `.opencode/opencode.json`. Root `.mcp.json` deleted.
- **Update Automation:** A standalone POSIX shell script `automation/plugin-mcp-skills-update/update.sh` that updates Skills (`npx skills update -p -y`), checks Superpowers plugin git commit, and validates Xerj MCP.
- **Launchd Daemon:** macOS `launchd` plist `com.tai.development-space.update.plist` with install/uninstall/status management helpers, logging daily execution to `logs/`.

**Tech Stack:** macOS launchd, zsh/bash, Node.js (`npx skills` v0.8.0), OpenCode v2.1.4, Codex CLI.

**Spec:** User instructions (hướng 1: local `.agents/` source of truth; clean root `.mcp.json`; update Superpowers plugin, Xerj MCP, and vercel-labs/skills daily; pure logging; placed in `automation/plugin-mcp-skills-update/`).

## Global Constraints

- Root directory `/Users/tai/development-space/` MUST remain pristine (no loose config files like `.mcp.json`).
- Script runs non-interactively without user prompts (`-y` flags).
- All logs written to `automation/plugin-mcp-skills-update/logs/`.
- No modification of global user space without approval.

## Review Focus

1. Root cleanliness: `git status` verifies `.mcp.json` is removed from repository root.
2. Xerj availability: Both `.codex/config.toml` and `.opencode/opencode.json` correctly resolve `xerj`.
3. Skills lockfile preservation: `skills update` respects `skills-lock.json` and updates safely.
4. Log rotation / formatting: Logs contain ISO timestamps and clear exit codes.
5. Launchd idempotency: `install-launchd.sh` safely unloads prior daemon instances before loading.

---

### Task 1: Clean Root `.mcp.json` and Establish `.agents/mcp.json` Source of Truth

**Files:**
- Create: `.agents/mcp.json`
- Modify: `.opencode/opencode.json`
- Modify: `.codex/config.toml`
- Delete: `.mcp.json`
- Test: `tests/test_mcp_source_of_truth.sh`

- [ ] **Step 1: Write verification test for MCP configuration**
- [ ] **Step 2: Run test to verify it fails on missing `.agents/mcp.json` and presence of root `.mcp.json`**
- [ ] **Step 3: Create `.agents/mcp.json`, update `.opencode/opencode.json`, verify `.codex/config.toml`, and delete root `.mcp.json`**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**

---

### Task 2: Implement Daily Update Script (`automation/plugin-mcp-skills-update/update.sh`)

**Files:**
- Create: `automation/plugin-mcp-skills-update/update.sh`
- Create: `automation/plugin-mcp-skills-update/logs/.gitkeep`
- Test: `tests/test_update_script.sh`

- [ ] **Step 1: Write test verifying update script arguments and log generation**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement `update.sh` covering Superpowers, Xerj MCP, and `npx skills update`**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**

---

### Task 3: Build Launchd Automation Plist and Lifecycle Scripts

**Files:**
- Create: `automation/plugin-mcp-skills-update/com.tai.development-space.update.plist`
- Create: `automation/plugin-mcp-skills-update/install-launchd.sh`
- Create: `automation/plugin-mcp-skills-update/uninstall-launchd.sh`
- Create: `automation/plugin-mcp-skills-update/status.sh`
- Create: `automation/plugin-mcp-skills-update/README.md`
- Test: `tests/test_launchd_plist.sh`

- [ ] **Step 1: Write test verifying plist syntax and lifecycle scripts**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement launchd plist and install/uninstall/status scripts**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**
