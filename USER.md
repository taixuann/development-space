# Collaboration with Tai

Use Vietnamese when Tai uses Vietnamese. Preserve technical names, flags, and file paths.
Use simple English for code comments, commit messages, and maintained technical documents unless Tai asks for another language.

## Interaction principles

- Lead with the result, recommendation, or diff. Keep explanations concise and scannable.
- Distinguish confirmed evidence from assumptions or inferences.
- When Tai asks to discuss or brainstorm, explore and verify before making changes.
- When Tai approves a bounded change, implement it cleanly and run verification before reporting completion.
- Ask for a decision only when missing information alters scope, security, or data integrity.
- Never force-push, rewrite shared git history, or delete existing code/tests without explicit approval.

## Engineering standards & The driving triad

All technical work in `development-space` is driven by three pillars:
1. **Superpowers**: Strict planning (`writing-plans`), test-driven development (`test-driven-development`), systematic debugging, and verification before declaring completion.
2. **Codebase Design**: Enforce **deep modules** with small public interfaces. Apply [Standard tool layout](docs/standard-tool-layout.md) and [Small-tool contract](docs/small-tool-contract.md).
3. **XERJ Retrieval**: Query `xerj def` and `xerj search` for AST-accurate definitions and code passages before reading whole files.

## Skill & tool layer boundaries

- **Folder-to-skill discipline**: Activate specialist skills strictly according to the folder being edited (e.g., `impeccable` only for `frontend/`, `cli-developer` only for `backend/`).
- **Zero bloat**: Do not load UI or frontend skills for headless CLI tools.
- **Independent tool repos**: Every tool under `tools/<space>/<tool-name>/` maintains its own Git repository and release tags, completely decoupled from the workshop root.
- **Packaging distribution**: Distribute CLI executables universally via `uv tool install <tool-path> --force` into `~/.local/bin/`.
