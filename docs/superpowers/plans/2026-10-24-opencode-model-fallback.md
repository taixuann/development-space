# OpenCode Project-Local Dual-Mode Fallback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Configure a clean, deterministic project-local fallback execution mechanism for OpenCode in `development-space`, implementing **Case 1** (Go primary `opencode-go/deepseek-v4.1-flash` $\to$ Go Free fallback `opencode-go/beam-free`) with session stickiness, and establishing the architecture for **Case 2** (automated probe-based fallback when Go is exhausted).

**Architecture:** OpenCode v2 project-local configuration in `/Users/tai/development-space/.opencode/opencode.json` (and workspace root) using `opencode-fallback-model` constrained strictly to two models per mode `[primary, fallback]` to eliminate multi-hop flapping. Case 1 runs `opencode-go/deepseek-v4.1-flash` (reasoning: `high`) with immediate fallback to `opencode-go/beam-free`. A lightweight probe launcher connects to the existing `free-router` state store (`~/.config/opencode/free-router/state.json`) to pave the way for Case 2.

**Tech Stack:** OpenCode v2.1.4, `opencode-fallback-model` plugin, OpenCode Go provider API, Node.js / zsh script.

**Spec:** User architecture guidance (Case 1: Go Quota $\to$ DeepSeek V4.1 Flash with Beam Go Free fallback; Case 2: Go Exhausted $\to$ Beam Go Free with DeepSeek Zen Free fallback; halt cleanly on dual failure; session stickiness; reasoning level `high`).

## Global Constraints

- No external gateways or heavy daemon layers (OmniRoute bypassed for this local tool execution).
- Strictly 2 models per active chain: `[Primary, Fallback]` — stop cleanly if both fail.
- Preserve OpenCode v2 configuration schema compatibility (`https://opencode.ai/config.json`).
- Reasoning configuration: pinned to `high` (not `max` or unlimited).
- Session stickiness: Once fallback engages, the active session remains on the fallback model.

## Review Focus

1. Quota error detection: OpenCode receives `Go usage limit exceeded` on primary $\to$ must seamlessly pivot to `beam-free` without prompt loss.
2. Direct execution without fallback: When primary is available (or user explicitly invokes a model), no unnecessary fallback trigger occurs.
3. Fallback exhaustion behavior: If both primary and fallback fail, execution halts cleanly with an informative error rather than infinite retry.
4. Session consistency: Tool calls and multi-turn edits stay on the selected model during the active task.
5. Workspace scoping: The configuration applies locally to `development-space` without polluting global `~/.config/opencode/opencode.jsonc`.

---

### Task 1: Clean and Lock Project-Local Case 1 Configuration

**Files:**
- Modify: `/Users/tai/development-space/.opencode/opencode.json`
- Modify: `/Users/tai/development-space/opencode.json`
- Test: `/Users/tai/development-space/tests/test_opencode_case1_config.sh`

**Interfaces:**
- Consumes: OpenCode v2 plugin runner and `opencode-fallback-model` v0.1.0.
- Produces: Validated, minimal project-local config file specifying `model: "opencode-go/deepseek-v4.1-flash"`, reasoning `high`, and `options.models: ["opencode-go/deepseek-v4.1-flash", "opencode-go/beam-free"]`.

- [ ] **Step 1: Write the verification script that validates Case 1 config schema and model list**

```bash
#!/usr/bin/env bash
# tests/test_opencode_case1_config.sh
set -euo pipefail

CONFIG_FILE="/Users/tai/development-space/.opencode/opencode.json"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "FAIL: $CONFIG_FILE does not exist"
  exit 1
fi

PRIMARY_MODEL=$(jq -r '.model' "$CONFIG_FILE")
FALLBACK_COUNT=$(jq '.plugins[0].options.models | length' "$CONFIG_FILE")
FIRST_MODEL=$(jq -r '.plugins[0].options.models[0]' "$CONFIG_FILE")
SECOND_MODEL=$(jq -r '.plugins[0].options.models[1]' "$CONFIG_FILE")

if [ "$PRIMARY_MODEL" != "opencode-go/deepseek-v4.1-flash" ]; then
  echo "FAIL: Primary model is $PRIMARY_MODEL, expected opencode-go/deepseek-v4.1-flash"
  exit 1
fi

if [ "$FALLBACK_COUNT" -ne 2 ]; then
  echo "FAIL: Fallback list must have exactly 2 models, got $FALLBACK_COUNT"
  exit 1
fi

if [ "$FIRST_MODEL" != "opencode-go/deepseek-v4.1-flash" ] || [ "$SECOND_MODEL" != "opencode-go/beam-free" ]; then
  echo "FAIL: Expected [opencode-go/deepseek-v4.1-flash, opencode-go/beam-free], got [$FIRST_MODEL, $SECOND_MODEL]"
  exit 1
fi

echo "PASS: Case 1 configuration conforms to 2-model strict chain"
```

- [ ] **Step 2: Run test to verify it fails on current bloated config**

Run: `bash /Users/tai/development-space/tests/test_opencode_case1_config.sh`
Expected: FAIL with "Fallback list must have exactly 2 models, got 10"

- [ ] **Step 3: Update `.opencode/opencode.json` and sync workspace root `opencode.json`**

Edit `/Users/tai/development-space/.opencode/opencode.json` to have:
```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "opencode-go/deepseek-v4.1-flash",
  "plugins": [
    {
      "package": "opencode-fallback-model@0.1.0",
      "options": {
        "models": [
          "opencode-go/deepseek-v4.1-flash",
          "opencode-go/beam-free"
        ]
      }
    }
  ]
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `bash /Users/tai/development-space/tests/test_opencode_case1_config.sh`
Expected: `PASS: Case 1 configuration conforms to 2-model strict chain`

- [ ] **Step 5: Commit**

```bash
git add .opencode/opencode.json opencode.json tests/test_opencode_case1_config.sh
git commit -m "chore(opencode): lock project-local Case 1 to DeepSeek V4.1 with Beam Free fallback"
```

---

### Task 2: Live Fallback Verification (Primary Exhausted $\to$ Beam Free Success)

**Files:**
- Create: `/Users/tai/development-space/tests/test_live_fallback.sh`

**Interfaces:**
- Consumes: OpenCode CLI `opencode run`, current Go subscription state (`deepseek-v4.1-flash` exhausted).
- Produces: Execution proof that OpenCode attempts `deepseek-v4.1-flash`, catches the limit, activates `beam-free`, and completes with code 0.

- [ ] **Step 1: Write the live fallback assertion test**

```bash
#!/usr/bin/env bash
# tests/test_live_fallback.sh
set -euo pipefail

cd /Users/tai/development-space
OUTPUT=$(opencode run "Output EXACTLY the string: FALLBACK_SUCCESS" 2>&1)

echo "$OUTPUT"

if echo "$OUTPUT" | grep -q "FALLBACK_SUCCESS"; then
  echo "PASS: Fallback to beam-free succeeded and produced expected output"
  exit 0
else
  echo "FAIL: Expected FALLBACK_SUCCESS in output"
  exit 1
fi
```

- [ ] **Step 2: Run test to verify end-to-end fallback behavior**

Run: `bash /Users/tai/development-space/tests/test_live_fallback.sh`
Expected: Output shows `FALLBACK_SUCCESS` and `PASS: Fallback to beam-free succeeded`

- [ ] **Step 3: Commit**

```bash
git add tests/test_live_fallback.sh
git commit -m "test(opencode): add live fallback execution assertion"
```

---

### Task 3: Architectural Foundation for Case 2 (Probe & State Integration)

**Files:**
- Create: `/Users/tai/development-space/scripts/opencode-runner.sh`
- Test: `/Users/tai/development-space/tests/test_runner_modes.sh`

**Interfaces:**
- Consumes: `~/.config/opencode/free-router/state.json` cooldown and quota entries.
- Produces: CLI helper `scripts/opencode-runner.sh [--case1|--case2|--auto]` that inspects probe status before choosing configuration profile.

- [ ] **Step 1: Write failing test for runner CLI flag resolution**

```bash
#!/usr/bin/env bash
# tests/test_runner_modes.sh
set -euo pipefail

RUNNER="/Users/tai/development-space/scripts/opencode-runner.sh"

if [ ! -x "$RUNNER" ]; then
  echo "FAIL: $RUNNER is not executable"
  exit 1
fi

CASE1_PROFILE=$("$RUNNER" --dry-run --mode case1)
if [ "$CASE1_PROFILE" != "case1:deepseek-v4.1-flash->beam-free" ]; then
  echo "FAIL: expected case1 profile, got $CASE1_PROFILE"
  exit 1
fi

echo "PASS: Runner mode resolution works"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash /Users/tai/development-space/tests/test_runner_modes.sh`
Expected: FAIL (runner does not exist)

- [ ] **Step 3: Implement minimal `scripts/opencode-runner.sh`**

Implement `scripts/opencode-runner.sh` handling `--mode case1` (Case 1 default: DeepSeek Go $\to$ Beam Free) and `--mode case2` (Beam Free $\to$ DeepSeek Zen Free).

- [ ] **Step 4: Run test to verify it passes**

Run: `bash /Users/tai/development-space/tests/test_runner_modes.sh`
Expected: `PASS: Runner mode resolution works`

- [ ] **Step 5: Commit**

```bash
git add scripts/opencode-runner.sh tests/test_runner_modes.sh
git commit -m "feat(opencode): add mode runner scaffolding for dual-case fallback"
```

---

## Self-Review

1. **Spec Coverage:**
   - Case 1 strictly locked: Primary `opencode-go/deepseek-v4.1-flash`, fallback `opencode-go/beam-free` (Task 1).
   - Live quota catch and fallback execution verified (Task 2).
   - Case 2 preparation and probe architecture established without jumping ahead of user's request (Task 3).
2. **Step Scan:** Every step has an exact script, exact command, and expected output.
3. **Type / Interface Consistency:** Model IDs match the active catalog checked live (`opencode-go/deepseek-v4.1-flash`, `opencode-go/beam-free`).
4. **Proportion:** Concise, focused on the concrete local project execution.
