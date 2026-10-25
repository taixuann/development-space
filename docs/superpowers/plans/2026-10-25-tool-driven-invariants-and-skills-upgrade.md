# Tool-Driven Development Invariants & Skills Upgrade Plan

Date: 2026-10-25
Status: In Progress

## 1. Goal
Upgrade Development Space core operational guidelines (`AGENTS.md`, `small-tool-contract.md`) and specialist skills (`tool-scaffolding`, `cli-developer`) to enforce strict tool-driven development invariants derived from recent operational learnings.

## 2. Invariants to Codify
1. **Config Separation & XDG Invariant**:
   - Repositories contain stateless code, tests, and tracked config templates (`*.example.yaml`).
   - Personal/local configuration (`register.yaml`, `config.yaml`, local `AGENTS.md`) MUST be gitignored.
   - Config precedence: CLI flag -> Local override -> User XDG directory (`~/.config/<tool>/`) -> Repository example template.
2. **CLI-First Invariant**:
   - When tools maintain registries or state, they must provide CLI subcommands (`consumer [list|add|set|remove]`, `config [get|set]`).
   - Agents must invoke CLI subcommands rather than hand-editing raw YAML/JSON.
3. **Zero Hardcoded Paths Invariant**:
   - Completely forbid hardcoded user paths (`/Users/...`). All scripts, plists, and binaries must dynamically resolve `$HOME` and environment paths.
4. **3-Tier Delivery & Production Isolation**:
   - Tier 1: CLI binary via `uv tool` to `~/.local/bin/`.
   - Tier 2: Dashboard/UI (`--ui`).
   - Tier 3: Automation LaunchAgent decoupled into `~/.agents/automation/`.

## 3. Execution Steps
- Task 1: Update `development-space/AGENTS.md`
- Task 2: Update `development-space/docs/small-tool-contract.md`
- Task 3: Upgrade `tool-scaffolding/SKILL.md`
- Task 4: Upgrade `cli-developer/SKILL.md`
- Task 5: Verification & Git Commit
