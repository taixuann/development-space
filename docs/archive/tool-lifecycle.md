# Tool lifecycle and distribution

This document details the lifecycle of a tool within `development-space`, from design and implementation to global distribution via `uv tool`.

## Lifecycle stages

```mermaid
flowchart LR
    A[1. Requirement / Issue] --> B[2. Isolated Worktree]
    B --> C[3. TDD & Small-tool contract]
    C --> D[4. Release Gate & Merge]
    D --> E[5. uv tool install / update]
    E --> F[6. Universal Consumer Execution]
```

### 1. Requirements and issue
- Tasks come from an Admin request (`admin/<tool-name>_<request-id>`) or an internal development need.
- Public CLI interface, flags, inputs, and outputs must be specified upfront.

### 2. Isolated worktree
- Never develop directly on the canonical branch while other consumers or automations might read it.
- Spawn a dedicated worktree:
  ```bash
  git worktree add worktrees/admin/<tool-name>_<request-id> -b admin/<tool-name>_<request-id>
  ```

### 3. TDD & Small-tool contract
- Write tests first for happy path, invalid inputs, and main failure modes.
- Implement the minimum code that passes the tests ([Ponytail / YAGNI](../SOUL.md)).
- Fulfill all requirements in [Small-tool contract](small-tool-contract.md).

### 4. Release gate & merge
- Run tests in an isolated fixture environment.
- Review diff and verification evidence against [RELEASE_GATE.md](../RELEASE_GATE.md).
- Merge into the tool's `main` branch. Remove the task worktree:
  ```bash
  git worktree remove worktrees/admin/<tool-name>_<request-id>
  ```

### 5. Semantic versioning and release (`scripts/release.sh`)
- Every tool supports automated Semantic Versioning (`patch`, `minor`, `major`) via `scripts/release.sh`:
  ```bash
  ./scripts/release.sh patch  # 0.1.0 -> 0.1.1
  ```
- The release runner validates test suites, bumps `pyproject.toml`, commits with `chore(release): bump version to vX.Y.Z`, tags `vX.Y.Z`, and invokes universal packaging.

### 6. Packaging and distribution (uv tool)
- The tool repository contains a valid `pyproject.toml` with console scripts:
  ```toml
  [project.scripts]
  my-tool = "my_tool.cli:main"
  ```
- Install or refresh the CLI executable in the user environment via universal distributor:
  ```bash
  ./scripts/setup.sh
  # Or via distributor directly:
  /Users/tai/development-space/scripts/distribute-tool.sh .
  ```
- The binary is placed at `~/.local/bin/my-tool`.

### 7. 3-Tier delivery contract & space decoupling
Any Space (`Admin`, `Personal`, `Research`, `Study`) consumes tools across three decoupled tiers without ever touching virtual environments or development repository trees:
1. **Tier 1 (Backend CLI):** Direct terminal invocation via `~/.local/bin/my-tool --option value --json`.
2. **Tier 2 (Frontend Dashboard):** Visual web dashboards accessible via CLI flag `my-tool --ui` or helper script `./scripts/dashboard.sh`.
3. **Tier 3 (Automation & Schedulers):** Production LaunchAgents (`~/Library/LaunchAgents/com.tai.<job-name>.plist`) point strictly to target space runners (`~/.agents/automation/<job-name>/run-sync.sh`) and logs in target space. **Zero cron or launchd processes are permitted to trigger against `development-space` source paths.**

