# Configurable Install Registry Placement and Generic Declarative Adapters Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow users to choose `register.yaml` placement during installation (supporting `--registry`, `REGISTRY_PATH`, interactive TTY prompts, defaulting to `~/.agents/config/opencode-model-router/register.yaml`), and implement Generic Declarative Dot-Path Adapters (`yaml`, `json`, `dotenv`) so any future tool can be dynamically configured without custom code.

**Architecture:**
1. **Registry Placement**: `install.sh` accepts `--registry <path>`, `$REGISTRY_PATH`, or prompts interactively. The chosen path is persisted into LaunchAgent runner script (`OPENCODE_MODEL_ROUTER_REGISTRY="<path>"`). `backend/registry.py` resolves via an extended hierarchy including `OPENCODE_MODEL_ROUTER_REGISTRY`, cwd, `~/.agents/`, and XDG.
2. **Generic Adapters (Direction A)**: `update_yaml_consumer(path, key_path, value)` and `update_json_consumer(path, key_path, value)` support dot-separated paths (e.g., `model.default` or `plugins[0].options.models`). `model_sync.py` routes types `yaml`, `json`, `dotenv` to these generic updaters without bespoke code.

## Global Constraints
- Zero hardcoded paths (`/Users/tai`).
- Preserves existing configs if already present at chosen path.
- Non-interactive safe (no blocking prompts if pipe or CI).
- Backward compatible with existing consumers (`opencode`, `hermes_yaml`, `dotenv`).

## Tasks

### Task 1: Update `backend/registry.py` resolution hierarchy
- Support `OPENCODE_MODEL_ROUTER_REGISTRY` environment variable.
- Support `Path.cwd() / 'register.yaml'` and `Path.cwd() / 'config' / 'register.yaml'`.
- Support `Path.home() / '.agents' / 'config' / 'opencode-model-router' / 'register.yaml'`.
- Support `Path.home() / '.agents' / 'register.yaml'`.
- Fall back to standard XDG and example template.

### Task 2: Implement Generic Declarative Adapters in `backend/registry.py`
- Enhance `update_json_consumer` to handle dot-paths with array indexing (e.g. `plugins[0].options.models`).
- Implement `update_yaml_consumer` for dot-path traversal and atomic write.
- Update `backend/model_sync.py` to route `yaml`, `json`, `dotenv` to generic updaters.
- Add unit tests for generic yaml and json consumers.

### Task 3: Update `scripts/install.sh` with Configurable Placement
- Parse `--registry <path>` flag.
- Read `$REGISTRY_PATH` or `$OPENCODE_MODEL_ROUTER_REGISTRY`.
- If interactive TTY (`[ -t 0 ]`), prompt user with choices:
  1) `~/.agents/config/opencode-model-router/register.yaml` (Admin Space - Recommended)
  2) `~/.config/opencode-model-router/register.yaml` (Standard XDG)
  3) Custom path
- Default to `~/.agents/config/opencode-model-router/register.yaml` if non-interactive.
- Persist the chosen registry into the LaunchAgent runner script.

### Task 4: Testing & Verification
- Unit test generic YAML & JSON adapters.
- Integration test CLI with new types.
- Bump version to `v0.1.4`, push, create GitHub release.
- Test live installation via pipe with custom `--registry`.
