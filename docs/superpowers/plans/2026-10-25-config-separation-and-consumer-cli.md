# Config Separation, Consumer CLI Management & Repo Cleanliness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Clean the Git repository by gitignoring `AGENTS.md` and local `register.yaml`, ship `register.example.yaml` as the tracked template, separate user config into standard XDG location (`~/.config/opencode-model-router/register.yaml`), provide rich CLI commands (`opencode-model-router consumer [list|add|set|remove]`) for programmatic configuration, and rewrite `README.md` into a definitive manual.

**Architecture:**
- **Config Precedence:** CLI `--registry` -> Local `./register.yaml` / `./config/register.yaml` -> XDG `$XDG_CONFIG_HOME/opencode-model-router/register.yaml` (`~/.config/...`) -> Shipped Template `register.example.yaml`.
- **Consumer Management:** Native Python module `backend/consumer_cli.py` with commands `list`, `add`, `set`, `remove` operating safely on the resolved YAML with atomic writes.
- **Git Hygiene:** Remove `AGENTS.md` and `register.yaml` from Git tracking while maintaining `register.example.yaml`.
- **Documentation:** Complete, structured `README.md` explaining 2-tier fallback, CLI commands, consumer setup, and configuration hierarchy.

**Tech Stack:** Python 3.11+, PyYAML, argparse, unittest, git.

**Spec:** User brainstorming alignment on Approach A (Config separation), adding CLI scripts to manage consumers instead of editing raw YAML by hand, gitignoring `AGENTS.md`, and rewriting `README.md`.

## Global Constraints
- All CLI modifications must conform to the Small-tool contract (exit code 0 on success, stderr for diagnostics, JSON on `--json`).
- Modifying YAML configuration must use atomic writes and preserve existing file permissions and structure.
- Absolute paths must never be hardcoded in repository files.

## Review Focus
1. **Config Precedence Fallback:** An environment with no user config must seamlessly fall back to `register.example.yaml` without crashing.
2. **Atomic Modification Safety:** Running `consumer add` or `consumer set` must not corrupt existing fields, comments, or categories.
3. **Validation Gates:** Adding a consumer with an existing ID, an invalid profile, or missing required fields must return exit code 2 with a descriptive error.
4. **Git Tracking Status:** `AGENTS.md` and `register.yaml` must not be tracked in git (`git ls-files` check).
5. **Backwards Compatibility:** Existing `--status` and `--sync` commands must continue to function without requiring changes from existing callers.

---

### Task 1: Git Hygiene & Config Template Creation

**Files:**
- Create: `tools/admin/opencode-model-router/register.example.yaml`
- Modify: `tools/admin/opencode-model-router/.gitignore`
- Untrack: `tools/admin/opencode-model-router/AGENTS.md`, `tools/admin/opencode-model-router/register.yaml`

- [ ] **Step 1: Copy `register.yaml` to `register.example.yaml` and sanitize sample values**
- [ ] **Step 2: Add `register.yaml` and `AGENTS.md` to `.gitignore`**
- [ ] **Step 3: Remove `register.yaml` and `AGENTS.md` from git cache via `git rm --cached`**
- [ ] **Step 4: Commit Git hygiene changes**

---

### Task 2: Configuration Hierarchy & Resolution Engine

**Files:**
- Modify: `tools/admin/opencode-model-router/backend/registry.py`
- Modify: `tools/admin/opencode-model-router/tests/test_registry.py`

- [ ] **Step 1: Write unit tests in `test_registry.py` testing config resolution hierarchy**
- [ ] **Step 2: Run tests to verify failure (RED)**
- [ ] **Step 3: Implement `resolve_registry_path(explicit_path=None)` in `backend/registry.py`**
- [ ] **Step 4: Run tests to verify success (GREEN)**
- [ ] **Step 5: Commit changes**

---

### Task 3: Consumer CLI Management Engine (`consumer [list|add|set|remove]`)

**Files:**
- Create: `tools/admin/opencode-model-router/backend/consumer_cli.py`
- Modify: `tools/admin/opencode-model-router/backend/cli.py`
- Modify: `tools/admin/opencode-model-router/tests/test_cli.py`
- Modify: `tools/admin/opencode-model-router/tests/test_registry.py`

- [ ] **Step 1: Write tests for consumer commands (`add`, `list`, `set`, `remove`)**
- [ ] **Step 2: Run tests to verify failure (RED)**
- [ ] **Step 3: Implement consumer helper methods in `backend/consumer_cli.py` and register subparsers in `backend/cli.py`**
- [ ] **Step 4: Run tests to verify all tests pass (GREEN)**
- [ ] **Step 5: Commit changes**

---

### Task 4: Universal Distributor & Automation Setup Alignment

**Files:**
- Modify: `development-space/scripts/distribute-tool.sh`

- [ ] **Step 1: Update `distribute-tool.sh` to initialize `$XDG_CONFIG_HOME/opencode-model-router/register.yaml` from `register.example.yaml` if not present**
- [ ] **Step 2: Run `./scripts/setup.sh` and verify execution**
- [ ] **Step 3: Commit changes in development-space**

---

### Task 5: User Manual & Documentation Overhaul (`README.md`)

**Files:**
- Modify: `tools/admin/opencode-model-router/README.md`

- [ ] **Step 1: Rewrite `README.md` with full usage instructions, CLI consumer commands, fallback profiles, and troubleshooting**
- [ ] **Step 2: Commit documentation and push to GitHub**
