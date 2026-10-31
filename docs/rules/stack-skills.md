# Stack → skills

Reference for which skills to propose per stack. Used by `workshop-driver` (Step 4)
and by each tool's `AGENTS.md` stack profile table.

## Languages / runtimes

- **Python CLI**: `python-pypi-package-builder`, `folder-structure-blueprint-generator`, `cli-creator`
- **Rust CLI**: rust skills (when installed), `cli-creator`
- **TypeScript/Node CLI**: `cli-creator`
- **Shell scripts**: `batch-script-progress`

## Domains

- **CLI design**: `cli-creator` (command contract, auth, --json, --dry-run, companion skill)
- **Frontend / UI**: `impeccable`, `anti-ui-slop`
- **Agent systems**: `agent-architecture`, `agent-owasp-compliance`
- **Documentation**: `technical-documentation`, `docs-sync-audit`, `create-readme`
- **Security**: `mcp-security-audit`, `github-actions-hardening`
- **Diagrams**: `archify`, `pretty-mermaid`

## How to use

1. `workshop-driver` reads this file during Step 4 when proposing skills.
2. Each tool records its chosen skills in its own `AGENTS.md` stack profile table.
3. Propose first, install only after the user agrees (see `docs/AGENTS.md` § "Third-party skills and plugins").
