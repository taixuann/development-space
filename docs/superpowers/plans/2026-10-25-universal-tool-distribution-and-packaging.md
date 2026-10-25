# Universal Tool Distribution & Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## Goal
Build a universal, reusable tool packaging and distribution mechanism for `development-space` that packages tools as first-class CLI packages (via `uv tool`), deploys them to target spaces (`admin` at `~/.agents/`, `research`, etc.), isolates production execution from development worktrees, and verifies repository care guidelines.

## Architecture & Layout
```text
~/development-space/
├── scripts/
│   └── distribute-tool.sh       # Universal distributor across spaces
└── tools/
    └── admin/
        └── opencode-model-router/
            ├── pyproject.toml   # Standardized package manifest (backend* discovery)
            ├── .gitignore       # Clean ignore rules (cache, locks, runtimes)
            ├── README.md        # Complete runbook with distribution commands
            └── Scripts/
                └── setup.sh     # Tool-local shortcut invoking distributor
```

## Tasks

### Task 1: Standardize `pyproject.toml` Package Discovery
- [ ] In `tools/admin/opencode-model-router/pyproject.toml`:
  - Add `[tool.setuptools.packages.find]` with `include = ["backend*"]` to resolve setuptools multi-package build errors.
  - Ensure entrypoint `opencode-model-router = "backend.cli:main"` is configured.
  - Verify build locally with `uv tool install --editable . --force`.

### Task 2: Build Universal Tool Distributor (`scripts/distribute-tool.sh`)
- [ ] Create `~/development-space/scripts/distribute-tool.sh`:
  - Parse tool path argument (e.g. `tools/<space>/<tool-name>`).
  - Detect space category (`admin`, `research`, `personal`, `shared`).
  - Step 1: Install tool CLI to `~/.local/bin/<tool-name>` via `uv tool install --editable <tool-path> --force`.
  - Step 2: Target Space Binding:
    - If space is `admin`:
      - Ensure `~/.agents/tools/<tool-name>` is linked/synced.
      - If tool contains `automation/<job-name>/`, wire `~/.agents/automation/<job-name>/run-sync.sh` to invoke `~/.local/bin/<tool-name>`.
      - Wire `~/.agents/automation/<job-name>/launchd.plist` if present.
  - Step 3: Health check verification:
    - Execute `<tool-name> --help` and verify exit code 0.
- [ ] Make `scripts/distribute-tool.sh` executable (`chmod +x`).

### Task 3: Tool-Local Setup Shortcut (`Scripts/setup.sh`)
- [ ] Create `tools/admin/opencode-model-router/Scripts/setup.sh`:
  - Simple wrapper calling `~/development-space/scripts/distribute-tool.sh "$REPO_ROOT"`.
  - Makes it intuitive for any operator to run `./Scripts/setup.sh` inside the tool repo.

### Task 4: GitHub Repo Care Audit & Privacy Gate
- [ ] Inspect `.gitignore` in `tools/admin/opencode-model-router` to ensure secrets, caches, and locks are excluded.
- [ ] Run privacy scan:
  - Check for credentials, hardcoded keys, tokens, or personal paths using `rg`.
- [ ] Update `README.md` to document the package distribution command (`uv tool install .` / `./Scripts/setup.sh`).

### Task 5: Full Execution, Verification & Gate Check
- [ ] Run `./Scripts/setup.sh` live.
- [ ] Run `opencode-model-router --status` from outside `development-space` (e.g. from `/private/tmp`).
- [ ] Run `automation/model-sync/run-sync.sh` and verify execution from `~/.local/bin`.
- [ ] Run full test suite: `python3 -m unittest discover tests`.
