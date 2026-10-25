# Remote Self-Contained Installer (Approach 1) Design

Date: 2026-10-25
Author: Codex Operator
Status: Approved

## 1. Intent & The Why
Previously, tool installation required cloning or having `development-space` checked out locally and running `./scripts/setup.sh` or `uv tool install --editable .`.
This design decouples tool consumption completely from `development-space`. Users and consumer spaces (`~/.agents/`, `academic-space`, external machines) can install and update any tool directly from its remote GitHub repository via a 1-line curl/gh command.

## 2. Goals & Non-Goals
- **Goals**:
  - Provide a standalone, POSIX-compliant `scripts/install.sh` in the tool repository.
  - Support execution via pipe (`curl ... | bash` or `gh api ... | bash`).
  - Automatically install/upgrade Tier 1 binary via `uv tool install git+https://github.com/taixuann/<tool>.git --force`.
  - Automatically bootstrap user configuration (`~/.config/<tool>/register.yaml`) from `register.example.yaml` without overwriting existing configs.
  - Automatically configure Tier 3 LaunchAgent automation (`~/Library/LaunchAgents/com.tai.<job>.plist`) with dynamic `$HOME` paths.
  - Document exact commands in `README.md` for both private and public repository configurations.
  - Standardize the `scripts/install.sh` template in `tool-scaffolding` skill.
- **Non-Goals**:
  - Creating a centralized monorepo hub installer (violates small-tool autonomy).

## 3. Approaches Considered
- **Approach 1: Self-Contained Remote `install.sh` (Selected)**: Each tool repository maintains its own standalone installer. One-line curl/gh invocation.
- **Approach 2: Package Self-Bootstrap**: Rely on `uv tool install` + `tool setup` subcommand. Requires 2 commands instead of one-line curl.
- **Approach 3: Central Installer Hub**: Single central script for all tools. Introduces tight coupling and single point of failure.

## 4. Technical Specification
- **Script Location**: `scripts/install.sh` (executable `chmod +x`).
- **Git Remote**: `https://github.com/taixuann/opencode-model-router.git`.
- **Target Paths**:
  - Binary: `~/.local/bin/opencode-model-router`
  - Config: `~/.config/opencode-model-router/register.yaml`
  - Automation Runner: `~/.agents/automation/model-control/run-sync.sh`
  - LaunchAgent Plist: `~/Library/LaunchAgents/com.tai.model-control-sync.plist`
- **Authentication**:
  - Private repo: Supports `gh api repos/taixuann/<repo>/contents/scripts/install.sh -H "Accept: application/vnd.github.v3.raw" | bash` OR `curl -fsSL -H "Authorization: token $(gh auth token)" ... | bash`.
  - Public repo: `curl -fsSL https://raw.githubusercontent.com/taixuann/<repo>/main/scripts/install.sh | bash`.
