---
name: opencode-model-router
description: >-
  Route, inspect, lock, and synchronize AI models for OpenCode workspaces. Use
  when configuring OpenCode models, updating .opencode/opencode.json, tuning
  reasoning levels, locking a project to a specific model, setting tier priority,
  or automating model fallback and quota recovery.
---

# OpenCode Model Router

`opencode-model-router` is a lightweight, zero-hardcoding developer utility that manages, routes, and synchronizes AI models into OpenCode project configurations (`.opencode/opencode.json` or `opencode.json`).

## Core Invariants

1. **Single Source of Truth**: Persistent configuration lives in exactly **one canonical location**: `~/.config/opencode-model-router/register.yaml` (respects `$XDG_CONFIG_HOME`).
2. **CLI-First Mutation**: Mutate targets, locks, sync flags, and priorities via dedicated CLI commands (`target`, `lock`, `unlock`, `priority`, `apply`). Avoid hand-editing raw YAML.
3. **Zero Hardcoded Whitelists**: Models, reasoning levels, and workspaces are resolved dynamically at runtime without static python model lists.
4. **Fail-Closed Logging**: Any errors or network timeouts log cleanly to `~/.config/opencode-model-router/logs/sync.log` without corrupting working configs.

---

## Quick Reference Commands

### 1. Apply Active Model to a Project

Applies the current best model (or the project's locked model) and updates 2-tier fallback:

```bash
# Apply to current directory (auto-detects .opencode/opencode.json)
opencode-model-router apply

# Apply to a registered target alias
opencode-model-router apply paper-base

# Apply to an arbitrary directory path
opencode-model-router apply ~/my-project

# Override reasoning level on the fly
opencode-model-router apply . --reasoning max

# Force a specific model ID
opencode-model-router apply . --model opencode-go/deepseek-v4.1-flash#max

# JSON output for scripts and automation
opencode-model-router apply paper-base --json
```

### 2. Lock & Unlock a Project

Pin a project to a specific model so background sync or automated swaps never change it:

```bash
# Lock project to a specific model
opencode-model-router lock . --model opencode-go/deepseek-v4.1-flash#max

# Lock by registered target alias
opencode-model-router lock paper-base --model pinned/custom-model

# Unlock to resume dynamic automated routing
opencode-model-router unlock paper-base
```

### 3. Register & Manage Targets (`target`)

Manage projects in `~/.config/opencode-model-router/register.yaml`:

```bash
# List all registered targets
opencode-model-router target list
opencode-model-router target list --json

# Register a new project target with reasoning level
opencode-model-router target add paper-base ~/academic-space/knowledge-space --reasoning max

# Update existing target properties
opencode-model-router target set paper-base --reasoning high --sync
opencode-model-router target set paper-base --no-sync

# Remove a target
opencode-model-router target remove paper-base
```

### 4. Global Priority Ordering (`priority`)

Configure the tier search priority for Primary and Fallback model selection:

```bash
# View current tier priority order
opencode-model-router priority get
# [+] Active routing priority: go > go-free > zen-free

# Set custom tier priority (e.g. prioritize unlimited free models first)
opencode-model-router priority set go-free zen-free go
# [+] Routing priority set to: go-free > zen-free > go
```

### 5. Self-Update (`update`)

Upgrade the CLI in-place:

```bash
opencode-model-router update
```

### 6. Health & Diagnostics

```bash
# Run smoke tests across OpenCode spaces
opencode-model-router check --json

# View current router state and freshness
opencode-model-router --status --json
```

---

## Target Configuration Schema

Targets in `~/.config/opencode-model-router/register.yaml` follow this schema:

```yaml
version: 2
routing:
  priority:
    - go          # OpenCode Go primary tier
    - go-free     # OpenCode Go unlimited free tier
    - zen-free    # OpenCode Zen free tier

targets:
  development:
    path: ~/development-space
    sync: true
    reasoning_level: high
    locked: false

  paper-base:
    path: ~/academic-space/knowledge-space
    sync: true
    reasoning_level: max
    locked: true
    locked_model: opencode-go/deepseek-v4.1-flash#max
    locked_fallback: opencode/deepseek-v4.1-flash-free
```

## Reasoning Levels
Supported reasoning depth levels: `max`, `high`, `medium`, `low`, `none`.
When set on a target, the router dynamically formats the model tag (e.g. `#max`, `#high`). If set to `none`, the model remains unadorned.
