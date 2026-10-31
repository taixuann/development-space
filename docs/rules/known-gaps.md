# Known gaps

Scope: places where this routing is known to be incomplete or untested. Read before trusting a gate report.

- No skill checks that a scientific result is valid. Write one during the first science tool.
- `sqlite-data-modeling` is cited in the root `AGENTS.md` but does not exist on disk.
- `folder-structure-blueprint-generator` and `code-exemplars-blueprint-generator` list no Rust or Swift. Check their output before trusting it.
- `xerj` needs a running node at `localhost:9200`. Start one only when the user agrees.
- Untested: whether brainstorming follows the proposal table, and whether a session started at the workshop root loads skills from a tool's `.claude/skills`. Try both in a fresh session.
- `automation/check_docs.py` already reports 10 problems from before these edits. Fix them in their own task.
- The old layer-to-skill map is kept in `docs/archive/skills-index-2026-10-27.yaml`.

## Resolved

- 2026-10-30: the per-tool `docs/PHASES.md` is retired. Phase state is derived from artifacts listed in [gates.yaml](gates.yaml), and durable decisions live in each tool's `AGENTS.md`. `raw-viewer` was migrated.
