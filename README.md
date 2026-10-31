# development-space

A software-development workshop. It owns reusable agent skills and workshop
docs. Optional local product checkouts live under `repos/`. Scheduled
automation and consumer data live elsewhere (Admin / cloud).

## Layout

```text
AGENTS.md                 workshop policy and routing
.agents/skills/           reusable specialist skills
docs/                     workshop references and agent docs
repos/                    local checkouts of active tool repos (ignored by root Git)
```

Each entry under `repos/<tool-name>/` is an independent Git repository.
Prefer the cloud environment / GitHub as source of truth; clone or pull into
`repos/` only when you need a local fix.

## Skills

Methodology (planning, TDD, debugging, review, integration) comes from the
harness plugin. Local specialists live under `.agents/skills/`.

Read `AGENTS.md` for routing and safety rules. Product rules always live in
the product repository, never here.

## License

MIT. See `LICENSE`.
