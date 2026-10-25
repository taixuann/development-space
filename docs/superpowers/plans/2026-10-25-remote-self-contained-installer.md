# Remote Self-Contained Installer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a standalone remote installer script (`scripts/install.sh`) in `opencode-model-router` for 1-line installation via curl/gh from GitHub, update documentation, and upgrade the scaffolding template.

**Architecture:** A standalone POSIX shell script runnable via pipe (`curl ... | bash` or `gh api ... | bash`) that uses `uv tool` to install the package from Git, sets up user XDG configs from template if missing, configures LaunchAgent automation, and verifies execution.

**Tech Stack:** Bash, uv tool, git, macOS LaunchAgent (`launchctl`), GitHub CLI (`gh`).

**Spec:** `docs/superpowers/specs/2026-10-25-remote-self-contained-installer-design.md`

## Global Constraints
- Zero hardcoded user paths (`/Users/tai`); strictly resolve `$HOME` and environment dynamically.
- Config preservation: NEVER overwrite existing `~/.config/opencode-model-router/register.yaml`.
- Atomic and safe LaunchAgent loading.
- Must support private GitHub repository authentication (via `gh` or token).

## Review Focus
1. `uv` binary missing on user's machine -> Script must detect and provide clear instruction or fallback to install `uv`.
2. Existing user configuration present -> Script must preserve it without modification.
3. Pipe execution (`curl ... | bash`) -> Script must not rely on `$0` directory context.
4. Git remote clone authentication -> Script must use Git credentials or GH token.
5. LaunchAgent reload -> Gracefully unload previous plist without failing before reloading.

---

### Task 1: Create `scripts/install.sh` in `opencode-model-router`

**Files:**
- Create: `tools/admin/opencode-model-router/scripts/install.sh`

- [ ] **Step 1: Write `scripts/install.sh`**
Implement the standalone installer:
- Check for `uv` (if not found, curl install uv).
- Run `uv tool install git+https://github.com/taixuann/opencode-model-router.git --force`.
- Ensure `$HOME/.config/opencode-model-router/` exists.
- If `$HOME/.config/opencode-model-router/register.yaml` does not exist, fetch `register.example.yaml` from GitHub or use `uv tool run` python helper to generate it.
- Deploy runner `~/.agents/automation/model-control/run-sync.sh`.
- Deploy LaunchAgent plist `~/Library/LaunchAgents/com.tai.model-control-sync.plist`.
- Run health check: `opencode-model-router --help`.
- [ ] **Step 2: Make executable and verify locally**
Run: `chmod +x tools/admin/opencode-model-router/scripts/install.sh && bash tools/admin/opencode-model-router/scripts/install.sh`
Expected: Return 0, successful deployment.
- [ ] **Step 3: Commit**
`git add scripts/install.sh && git commit -m "feat(installer): add self-contained remote install.sh script"`

---

### Task 2: Update `README.md` with Remote Installation Guide

**Files:**
- Modify: `tools/admin/opencode-model-router/README.md`

- [ ] **Step 1: Overhaul Installation section in README.md**
Add exact copy-pasteable commands:
- 1-line installation for Private repo (via `gh api` or `curl -H "Authorization: token $(gh auth token)"`).
- 1-line installation for Public repo (`curl -fsSL https://raw.githubusercontent.com/... | bash`).
- Manual fallback: `uv tool install git+https://github.com/taixuann/opencode-model-router.git`.
- [ ] **Step 2: Commit**
`git add README.md && git commit -m "docs: add remote curl and gh api 1-line installation instructions"`

---

### Task 3: Upgrade `tool-scaffolding` Skill Template

**Files:**
- Modify: `development-space/.agents/skills/tool-scaffolding/SKILL.md`

- [ ] **Step 1: Add `scripts/install.sh` remote installer template to `tool-scaffolding`**
Document the remote installer pattern as standard for all scaffolded tools.
- [ ] **Step 2: Commit in development-space**
`git add .agents/skills/tool-scaffolding/SKILL.md && git commit -m "docs(tool-scaffolding): add remote self-contained install.sh template"`

---

### Task 4: Release `v0.1.3` and Verify Live Remote Installation

**Files:**
- Modify: `tools/admin/opencode-model-router/pyproject.toml`

- [ ] **Step 1: Bump version to `0.1.3` via release script or git tag**
- [ ] **Step 2: Push commits and tag to GitHub**
- [ ] **Step 3: Create GitHub release `v0.1.3`**
- [ ] **Step 4: Execute live remote installation test via pipe**
Run: `gh api repos/taixuann/opencode-model-router/contents/scripts/install.sh -H "Accept: application/vnd.github.v3.raw" | bash`
Expected: Return 0, output `[SUCCESS] opencode-model-router is fully installed and active!`.
