# Technical learnings and gotchas

This file records technical quirks, library bugs, and operational lessons discovered while developing tools in `development-space`.

## 2026-10-24: Hindsight ingestion & provider configuration
- **Symptom**: `RuntimeError: Fact extraction failed: Claude Code reported an error: Not logged in / [claude-code:unrecognized_model]`
- **Root cause**: `HINDSIGHT_API_LLM_PROVIDER=claude-code` was paired with `HINDSIGHT_API_LLM_MODEL=gemini-3.8-flash`. Claude Code CLI only understands Claude model names (e.g., `claude-3-7-sonnet`, `claude-3-5-haiku`), not Google Gemini models.
- **Resolution**: Pair the provider with a model supported natively by that provider (or use Gemini via direct provider configuration `HINDSIGHT_API_LLM_PROVIDER=gemini`).

## 2026-10-24: Git sub-repository isolation
- **Symptom**: Parent repository tries to track sub-tools as submodules or dirty tree entries.
- **Root cause**: Git treats directories containing `.git` as submodules unless explicitly ignored.
- **Resolution**: Add `tools/` and `worktrees/` directly to root `.gitignore` so tools develop completely decoupled.
