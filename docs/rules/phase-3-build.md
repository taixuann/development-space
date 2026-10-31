# Phase 3: build and verify

Scope: the third phase of the platform track. The first tasks of the plan scaffold the tree.

| Step | Skill | Output |
|---|---|---|
| 1 | `create-agentsmd` | The tool's `AGENTS.md`, with the stack profile from [stack-profile.md](stack-profile.md). Diff the result. Keep every invariant already in the file. |
| 2 | `folder-structure-blueprint-generator` | A blueprint of the scaffold. It records the layout. It does not set one. |
| 3 | `create-readme`, `technical-documentation` | The README and the docs |

Then, for the work:

- `superpowers:test-driven-development` and `superpowers:subagent-driven-development`.
- `superpowers:systematic-debugging` for every bug.
- `code-exemplars-blueprint-generator` after the first reviewed slice, so it pins the new language and not the old one.
- `superpowers:requesting-code-review` before merge.
- `superpowers:verification-before-completion`, then `docs-sync-audit`, before any claim of done.
- `python-pypi-package-builder` for Python command-line tools only.
