---
name: tool-scaffolding
description: Scaffold and initialize a new tool in development-space with standard folders (backend, tests, api, frontend, database) and an independent Git repository. Use when creating a new tool or standardizing an existing tool under tools/<space>/<tool-name>/.
---

# Tool Scaffolding

Scaffold a new tool inside `development-space/tools/<space>/<tool-name>/`.
Every tool must be an independent Git repository that adheres to the Small-tool contract and the Standard tool layout.

## Prerequisites

1. Identify the target consumer space: `admin`, `research`, `personal`, or `shared`.
2. Confirm the tool name in kebab-case: `<tool-name>`.
3. Check that `tools/<space>/<tool-name>/` does not already exist.

## Procedure

### Step 1: Create tool directory, initialize Git and .gitignore

Run the following commands:
```bash
mkdir -p tools/<space>/<tool-name>
cd tools/<space>/<tool-name>
git init -b main
```

Immediately initialize a standard `.gitignore` to enforce the **Config Separation Invariant** from day one:
```bash
cat << 'EOF' > .gitignore
# Python & build artifacts
__pycache__/
*.pyc
.pytest_cache/
*.egg-info/
dist/
build/
.build/

# Runtime & local environment configurations (NEVER commit personal configs)
config.yaml
register.yaml
.env
.env.*
*.local
*.log

# Local agent instructions (gitignored to avoid overriding workspace contracts)
AGENTS.md
EOF
```

### Step 2: Determine required folder components & config template

Consult [`docs/standard-tool-layout.md`](../../docs/standard-tool-layout.md).
Create mandatory directories and only the optional directories needed:

```bash
# Always required:
mkdir -p backend tests scripts

# If the tool exposes network or MCP endpoints:
mkdir -p api

# If the tool has a web or native interface:
mkdir -p frontend/src

# If the tool uses local schema migrations:
mkdir -p database/migrations
```

Do not create empty unused directories.

If the tool requires user configuration or registry definitions, **always create a tracked template** (e.g. `config.example.yaml` or `register.example.yaml`), never a hardcoded personal config:
```bash
cat << 'EOF' > config.example.yaml
# Tracked template. Real user configuration will reside at ~/.config/<tool-name>/config.yaml
version: "1.0"
settings:
  timeout: 30
EOF
```

### Step 3: Write manifest and entrypoint

For a Python tool, create `pyproject.toml` with console scripts:
```toml
[project]
name = "<tool-name>"
version = "0.1.0"
description = "Brief description of the tool"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []

[project.scripts]
<tool-command> = "backend.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Create `backend/__init__.py` and `backend/cli.py` implementing `--help`, standard exit codes, and entity management subcommands if applicable (see `cli-developer` skill).

### Step 4: Add helper scripts and documentation

1. Create `scripts/setup.sh` with **dynamic distributor resolution** for local development (strictly zero hardcoded `/Users/...` paths):
   ```bash
   cat << 'EOF' > scripts/setup.sh
   #!/bin/bash
   set -euo pipefail
   REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
   
   # Dynamically discover workshop distributor script
   DISTRIBUTOR="${DISTRIBUTOR_PATH:-$(cd "${REPO_DIR}/../../.." && pwd)/scripts/distribute-tool.sh}"
   if [ ! -f "$DISTRIBUTOR" ]; then
       DISTRIBUTOR="${HOME}/development-space/scripts/distribute-tool.sh"
   fi
   
   if [ ! -f "$DISTRIBUTOR" ]; then
       echo "[-] Error: distribute-tool.sh not found at ${DISTRIBUTOR}" >&2
       exit 1
   fi
   exec /bin/bash "$DISTRIBUTOR" "$REPO_DIR" "$@"
   EOF
   chmod +x scripts/setup.sh
   ```

2. Create `scripts/install.sh` for **Remote 1-Line Installation via GitHub**:
   This script allows external consumers or target spaces to install the tool via `curl` or `gh` without cloning `development-space`:
   ```bash
   cat << 'EOF' > scripts/install.sh
   #!/bin/bash
   # Remote 1-Line Installer
   set -euo pipefail

   # 1. Ensure uv
   command -v uv >/dev/null 2>&1 || curl -LsSf https://astral.sh/uv/install.sh | sh
   export PATH="${HOME}/.local/bin:${PATH}"

   # 2. Install binary via uv tool from GitHub
   uv tool install git+https://github.com/taixuann/<tool-name>.git --force

   # 3. Bootstrap user config if missing
   CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/<tool-name>"
   CONFIG_FILE="${CONFIG_DIR}/config.yaml"
   mkdir -p "$CONFIG_DIR"
   if [ ! -f "$CONFIG_FILE" ]; then
       # Fetch example template
       curl -fsSL https://raw.githubusercontent.com/taixuann/<tool-name>/main/config.example.yaml -o "$CONFIG_FILE" 2>/dev/null || true
   fi

   # 4. Final verification
   "${HOME}/.local/bin/<tool-command>" --help >/dev/null
   echo "[SUCCESS] <tool-name> installed successfully!"
   EOF
   chmod +x scripts/install.sh
   ```

3. Create `scripts/release.sh` to enforce SemVer bumping, test verification, and automated packaging:
   ```bash
   cat << 'EOF' > scripts/release.sh
   #!/bin/bash
   # Automated SemVer Bumping, Git Tagging & Distribution Release Runner
   set -euo pipefail
   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
   REPO_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
   BUMP_TYPE="${1:-patch}"

   cd "$REPO_DIR"
   echo "[+] Running verification tests..."
   python3 -m unittest discover tests

   echo "[+] Bumping ${BUMP_TYPE} version..."
   # Bump version in pyproject.toml, git commit, git tag, and call ./scripts/setup.sh
   "${SCRIPT_DIR}/setup.sh"
   EOF
   chmod +x scripts/release.sh
   ```

4. Write `README.md`:
   - Tool purpose and stable CLI invocation.
   - Remote 1-line installation via `curl -fsSL .../scripts/install.sh | bash` or `gh api`.
   - 3-Tier delivery layout (CLI binary in `~/.local/bin`, UI dashboard via `--ui`, Automation in `~/.agents/automation/`).
   - Configuration hierarchy: `--config` flag -> local override -> `~/.config/<tool-name>/` -> `config.example.yaml`.
   - Inputs, outputs, and exit codes.
   - Failure recovery.

5. If needed, provide a local `AGENTS.md` (remember it is gitignored by default to keep the repo generic).

### Step 5: Write initial test

Create `tests/test_cli.py`:
- Test `--help` flag execution.
- Test normal execution path.
- Test invalid input failure with non-zero exit code.

### Step 6: Verify and commit initial revision

Run the tests:
```bash
pytest
```
When tests pass, commit the initial revision inside the tool repository:
```bash
git add .
git commit -m "chore: initial scaffold for <tool-name>"
```

### Step 7: Register with uv tool

Install into the user environment using the local setup script:
```bash
./scripts/setup.sh
```
Verify that `<tool-command> --help` executes successfully from any working directory.
