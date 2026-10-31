# Development Space

A software-development workshop for engineering skills, agent workflows, and local checkouts of active tool repositories.

## Overview

This repository is a thin workshop. It owns:

- Shared engineering skills under `.agents/skills/`
- Workshop policy and routing (`AGENTS.md`, `docs/`)
- Optional local product checkouts under `repos/<tool-name>/` (each an independent Git repository)

It does **not** own scheduled automation, consumer-space data, or a nested `tools/<space>/` tree. Product source of truth for active cloud work (for example raw-viewer) lives in the cloud environment / GitHub; clone into `repos/` only when you need a local fix.

## Work Phases

Tools here use Python, Swift, or Rust. A tool-level `AGENTS.md` overrides the Python wording below.

For a platform or app, work in three phases: think and decide, lay the foundation, then build. During `/brainstorming`, read [docs/AGENTS.md](docs/AGENTS.md) and propose the skills it lists. Run a proposed skill only after the user agrees.

## Upstream Skills & Standards

All agent operations in this workspace strictly follow the [Agent Skills specification](https://agentskills.io/) and official upstream skills from `github/awesome-copilot`:

- **Package & CLI Architecture**: `python-pypi-package-builder` (PyPA standard `src/` layout, `pyproject.toml`, SemVer, `uv` tool packaging).
- **Modularity & Structure**: `folder-structure-blueprint-generator` (dynamic Separation of Concerns) and `code-exemplars-blueprint-generator` (canonical style enforcement).
- **Execution Discipline**: Superpowers methodology (`superpowers:writing-plans`, `superpowers:subagent-driven-development`, `superpowers:test-driven-development`, `superpowers:systematic-debugging`).
- **Stream & Batch Formatting**: `batch-script-progress` (clean `stdout` for data/JSON, `stderr` for progress/diagnostics, standardized exit codes).
- **Quality & Security Gates**: `agentic-eval` (self-critique schema validation), `agent-owasp-compliance`, `mcp-security-audit`, and `docs-sync-audit` (zero doc drift).
- **UI & Presentation**: `impeccable` for product-grade webview/frontend design.
- **Local Persistence**: `sqlite-data-modeling` (planned, not installed) for embedded databases and offline caches.

## Development Workflow

### 1. Planning & Scaffolding
- Before writing code, use `create-technical-spike` for uncertain technical proofs and `create-specification` / `create-architectural-decision-record` for architectural clarity.
- Break implementation down into small, verifiable steps using `superpowers:writing-plans`.
- Convert plan phases into GitHub tracking issues via `create-github-issues-feature-from-implementation-plan`.
- Scaffold new tools using `python-pypi-package-builder` with standard `pyproject.toml` and clean `src/` package layout.

### 2. Implementation & Testing
- Use `superpowers:subagent-driven-development` to execute tasks in isolated contexts.
- Strictly adhere to `superpowers:test-driven-development`: write failing tests first, implement the minimum code to pass, then refactor.
- When bugs occur, run `superpowers:systematic-debugging` to trace root causes before proposing fixes.
- Run tests inside the product repository (for example `pytest` under `repos/<tool>/`), not at the workshop root.

### 3. Verification & Delivery
- Prior to completing a task, enforce `superpowers:verification-before-completion` with fresh execution logs.
- Run `agentic-eval` to validate payloads against JSON schemas.
- Run `docs-sync-audit` to ensure README, CLI help text, and documentation match code changes with zero drift.

## Core Engineering Conventions

1. **Path Agnosticism**: Never hardcode user home paths. Use `pathlib.Path.home()`, `$HOME`, or environment variables.
2. **Configuration Standards**: Store user-specific configuration outside repositories in standard XDG paths (`~/.config/<tool-name>/`), using tracked `*.example.yaml` templates in source.
3. **CLI Design**: Support standard flags (`--help`, `-h`, `--json`), non-interactive overrides (`--yes`/`--force`), and predictable exit codes (`0` success, `1` runtime error, `2` validation error).
4. **Local checkouts**: Active local checkouts live under `repos/<tool-name>/`. Each is its own Git repository and is ignored by the workshop root Git. Prefer cloning from the remote/cloud source of truth when starting local work.
5. **Git safety**: Never force-push or merge unverified changes to `main`.
