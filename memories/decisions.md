# Settled engineering decisions

This file records settled architectural choices for `development-space`.
Do not reopen settled choices unless new evidence or real conflicts emerge.

## 2026-10-24: Workshop architecture & tool distribution
- **Core Triad**: Superpowers (workflow/TDD) + Codebase Design (deep modules) + XERJ (AST code retrieval).
- **Centralized Source**: All shared tools reside under `tools/<space>/<tool-name>/` (admin, research, personal, shared).
- **Independent Git repos**: Every tool has its own `.git` directory and standalone version tags. Root workshop ignores `tools/` and `worktrees/`.
- **Packaging distribution**: Distribute CLI executables globally via `uv tool install /Users/tai/development-space/tools/<space>/<tool-name> --force` into `~/.local/bin/`.
- **Folder-to-skill alignment**: Specialist skills are strictly mapped to tool components (`backend/` -> `cli-developer`/`codebase-design`, `frontend/` -> `impeccable`/`swiftui-expert-skill`, `tests/` -> `playwright-cli`/`TDD`).
- **Memory isolation**: Hindsight bank `development-space` is dedicated strictly to this workshop; local markdown files live in `memories/`.
