# Standard tool layout

This document defines the standard directory structure for every tool developed under `development-space/tools/<space>/<tool-name>/`.
It extends the [Small-tool contract](small-tool-contract.md) and applies [Codebase Design](../.agents/skills/codebase-design/SKILL.md) principles (deep modules with small public interfaces).

## Universal tool layout

Each tool is an independent Git repository. Depending on whether the tool contains a CLI, a web/desktop frontend, a database, or network APIs, it uses the standardized folders below:

```text
tools/<space>/<tool-name>/
├── .git/                      # Independent Git repository
├── README.md                  # Human runbook: purpose, stable CLI invocation, recovery
├── AGENTS.md                  # Agent boundaries and invariants for this tool
├── pyproject.toml             # (Or Cargo.toml, Package.swift, package.json)
│
├── backend/                   # Core application logic and CLI entrypoint
│   ├── __init__.py
│   ├── cli.py                 # Public CLI interface (Small-tool contract)
│   └── <modules>/             # Deep internal logic
│
├── api/                       # (Optional) HTTP/REST/MCP server endpoints
│   ├── __init__.py
│   └── routes.py
│
├── frontend/                  # (Optional) UI views, dashboards, or web applications
│   ├── src/                   # React, Vite, HTML, or SwiftUI sources
│   └── public/
│
├── database/                  # (Optional) Local storage, schema, and migrations
│   ├── migrations/            # Versioned SQL / migration scripts
│   └── schema.sql             # Base SQLite / DuckDB DDL
│
├── automation/                # (Optional) Tool-owned scheduled jobs and background runners
│   └── <job-name>/
│
├── tests/                     # Runnable behavior tests (TDD verification)
│   ├── conftest.py
│   ├── test_cli.py            # CLI contract verification
│   └── fixtures/              # Isolated, temporary test data
│
├── scripts/                   # (Optional) Helper, release, and launcher scripts
│   ├── setup.sh               # 1-click space distribution wrapper
│   ├── release.sh             # SemVer bump, git tagging, and packaging release
│   └── dashboard.sh           # Quick UI/dashboard launcher
│
└── docs/                      # (Optional) Internal tool design notes or specs
```

## Section responsibilities

| Folder | Condition | Responsibility | Public Seam |
| :--- | :--- | :--- | :--- |
| `backend/` | **Mandatory** | Core computation, business logic, CLI entrypoint. | `backend/cli.py` exposes commands, options, and exit codes. |
| `tests/` | **Mandatory** | Runnable checks covering success, invalid inputs, and failure paths. | Test runner commands (`pytest`, `swift test`). |
| `scripts/` | Optional | Local setup, SemVer release, dashboard launcher. | Standard scripts (`setup.sh`, `release.sh`, `dashboard.sh`). |
| `api/` | Optional | Web servers, REST endpoints, MCP server proxies. | Clean OpenAPI / MCP protocol contract. |
| `frontend/` | Optional | Visual interfaces (interactive dashboards, canvas, views). | Browser URL or native app window. |
| `database/` | Optional | SQLite / DuckDB schemas and migrations. | Zero hardcoded mutable databases in source tree; runtime DB stays in user home or explicit data root. |
| `automation/` | Optional | Jobs and schedulers dedicated solely to this tool. | Non-interactive scheduled runner. |

## Layout rules

1. **Independent Git repository**: Every tool must contain its own `.git` directory and never be merged into parent workshop git history.
2. **Deep module enforcement**: Callers and consumers only interact with the tool through its documented public interface (e.g. CLI command `my-tool --option`). They never import private modules across folder boundaries.
3. **No empty placeholders**: Do not create empty `frontend/`, `api/`, or `database/` folders if the tool does not use them. Add folders only when the responsibility exists.
4. **State outside source**: Mutable databases, cache files, and logs must be stored in `~/.local/state/<tool-name>` or an explicit caller-provided `--data-dir`, never tracked in git.
