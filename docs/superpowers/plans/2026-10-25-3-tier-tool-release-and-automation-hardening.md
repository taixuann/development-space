# 3-Tier Tool Release, LaunchAgent Decoupling, and Guidelines Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor script folder to lowercase `scripts/`, implement automated release script with SemVer bumping and git tagging, add `--ui` flag for the frontend dashboard, decouple system LaunchAgent `com.tai.model-control-sync` completely from `development-space` into `~/.agents/automation/model-control/`, and update both tool and workshop documentation/rules.

**Architecture:**
- **Tier 1 (Backend):** Global CLI `opencode-model-router` via `~/.local/bin/` with `--ui` capability to open `frontend/index.html`.
- **Tier 2 (Frontend):** Zero-dependency dashboard accessible via `opencode-model-router --ui` or `scripts/dashboard.sh`.
- **Tier 3 (Automation):** Production LaunchAgent `com.tai.model-control-sync.plist` rewired strictly to `~/.agents/automation/model-control/run-sync.sh` with logs in `~/.agents/automation/model-control/logs/`.
- **Release Automation:** `scripts/release.sh` to handle SemVer bump (`patch`, `minor`, `major`), git commit, tag `vX.Y.Z`, and distribution execution.
- **Workshop Standards:** Update `tools/admin/opencode-model-router/AGENTS.md`, `README.md`, and `development-space/docs/tool-lifecycle.md` / `standard-tool-layout.md`.

**Tech Stack:** Python 3.11+, bash, git, macOS LaunchAgent / launchctl, uv tool.

**Spec:** User requirements for lowercase `scripts/`, release versioning, comprehensive docs, and 3-tier launch verification with complete isolation from development-space cron triggers.

## Global Constraints
- Development space owns only development source; consumer spaces (`~/.agents`) own execution state and automated runners.
- Zero cron/launchd processes are permitted to execute against `development-space` source trees.
- All CLI modifications must conform to Small-tool contract (return code 0 on success, stderr for diagnostics, json on request).

## Review Focus
1. **LaunchAgent Target Drift:** Plist pointing to development-space will fail if development-space is dirty or branched. Test: Plist ProgramArguments must strictly point to `/Users/tai/.agents/automation/model-control/run-sync.sh`.
2. **Path Resolution for `--ui`:** Calling `opencode-model-router --ui` from an arbitrary directory (e.g. `/tmp`) must resolve the actual `frontend/index.html` via package metadata or target space link.
3. **SemVer Regex & Git Tag Collision:** `release.sh` bumping a version that already has an existing tag must fail fast with a descriptive error.
4. **Folder Case Sensitivity on macOS:** Renaming `Scripts` to `scripts` on APFS (case-insensitive by default) requires explicit git mv handling (`git mv Scripts scripts_temp && git mv scripts_temp scripts`).
5. **Launchctl reload failure:** Reloading plist must not crash if the job is currently running; use graceful unload/load or bootout/bootstrap.

---

### Task 1: Lowercase Script Folder Refactoring (`Scripts/` -> `scripts/`)

**Files:**
- Rename: `tools/admin/opencode-model-router/Scripts/` -> `tools/admin/opencode-model-router/scripts/`
- Modify: `tools/admin/opencode-model-router/scripts/setup.sh`
- Modify: `tools/admin/opencode-model-router/README.md`

- [ ] **Step 1: Perform case-safe git mv for script folder**
- [ ] **Step 2: Verify `scripts/setup.sh` runs cleanly**
- [ ] **Step 3: Update references in `README.md` from `Scripts/` to `scripts/`**
- [ ] **Step 4: Commit**

---

### Task 2: Implement Frontend Dashboard Launch Seam (`--ui`)

**Files:**
- Modify: `tools/admin/opencode-model-router/backend/cli.py`
- Modify: `tools/admin/opencode-model-router/tests/test_cli.py`
- Create: `tools/admin/opencode-model-router/scripts/dashboard.sh`

- [ ] **Step 1: Write test for `--ui` flag in `test_cli.py`**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement `--ui` flag in `backend/cli.py` and `scripts/dashboard.sh`**
- [ ] **Step 4: Run test to verify it passes**
- [ ] **Step 5: Commit**

---

### Task 3: Decouple LaunchAgent from `development-space` to Target Space (`~/.agents`)

**Files:**
- Modify: `/Users/tai/Library/LaunchAgents/com.tai.model-control-sync.plist`
- Modify: `development-space/scripts/distribute-tool.sh`

- [ ] **Step 1: Update `com.tai.model-control-sync.plist` with target space paths**
- [ ] **Step 2: Automate plist verification & reload in `distribute-tool.sh`**
- [ ] **Step 3: Verify LaunchAgent status via `launchctl` and verify 0 matches for `development-space`**
- [ ] **Step 4: Commit changes in development-space distributor**

---

### Task 4: Implement Release Automation Script (`scripts/release.sh`)

**Files:**
- Create: `tools/admin/opencode-model-router/scripts/release.sh`

- [ ] **Step 1: Write `scripts/release.sh` (SemVer bump, commit, tag, setup)**
- [ ] **Step 2: Test release script with patch bump (`0.1.0` -> `0.1.1`)**
- [ ] **Step 3: Verify git tag `v0.1.1` and installed binary version**

---

### Task 5: Documentation Hardening & Workshop Guidelines Update

**Files:**
- Modify: `tools/admin/opencode-model-router/README.md`
- Modify: `tools/admin/opencode-model-router/AGENTS.md`
- Modify: `development-space/docs/standard-tool-layout.md`
- Modify: `development-space/docs/tool-lifecycle.md`

- [ ] **Step 1: Update `tools/admin/opencode-model-router/README.md`**
- [ ] **Step 2: Update `tools/admin/opencode-model-router/AGENTS.md`**
- [ ] **Step 3: Update `development-space/docs/standard-tool-layout.md` & `tool-lifecycle.md`**
- [ ] **Step 4: Commit documentation and guidelines**
