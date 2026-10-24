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

### Step 1: Create tool directory and initialize Git

Run the following commands:
```bash
mkdir -p tools/<space>/<tool-name>
cd tools/<space>/<tool-name>
git init -b main
```

### Step 2: Determine required folder components

Consult [`docs/standard-tool-layout.md`](../../docs/standard-tool-layout.md).
Create mandatory directories and only the optional directories needed:

```bash
# Always required:
mkdir -p backend tests

# If the tool exposes network or MCP endpoints:
mkdir -p api

# If the tool has a web or native interface:
mkdir -p frontend/src

# If the tool uses local schema migrations:
mkdir -p database/migrations
```

Do not create empty unused directories.

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

Create `backend/__init__.py` and `backend/cli.py` implementing `--help` and basic options.

### Step 4: Write documentation

1. Write `README.md`:
   - Tool purpose and stable CLI invocation.
   - Inputs, outputs, and exit codes.
   - Failure recovery.
2. Write `AGENTS.md`:
   - Boundaries and invariants for this specific tool repository.

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

Install into the user environment:
```bash
uv tool install . --force
```
Verify that `<tool-command> --help` executes successfully from any working directory.
