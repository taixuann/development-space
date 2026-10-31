# Stack profile

Scope: how a finished tool records its parts, so an agent can pick skills without guessing.

Each platform or app records its parts in its own `AGENTS.md`, in one short table.

| Part | Language or store | Skills |
|---|---|---|
| Backend, frontend, database, cache, CLI, API | One row for each part the tool has | The skills that serve that part |

Every skill named in the table must exist on disk, either in the tool's `.claude/skills` or in the workshop. Store a stack-specific skill in the tool's own `.claude/skills` as a backup. Do not copy large shared skills such as `impeccable`.

A name in the table is a claim about the repository, not an intention. Add a row when the part exists, not when it is planned.
