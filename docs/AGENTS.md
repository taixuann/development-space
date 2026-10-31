# Workshop phases and skill routing

Scope: how work moves from an idea to shipped code in this workshop, in any language. A tool-level `AGENTS.md` overrides this file.

This file is the index. Read the one rule file that matches where you are, not all of them.

## Which rule to read

| When | Read |
|---|---|
| Deciding small tool or platform/app | [rules/tiers.md](rules/tiers.md) |
| Phase 1: vision, glossary, stack skills | [rules/phase-1-vision.md](rules/phase-1-vision.md) |
| Phase 2: detect, prove, plan | [rules/phase-2-plan.md](rules/phase-2-plan.md) |
| Phase 3: scaffold, build, verify | [rules/phase-3-build.md](rules/phase-3-build.md) |
| Recording the parts of a tool | [rules/stack-profile.md](rules/stack-profile.md) |
| Reading a gate by script | [rules/gates.yaml](rules/gates.yaml) |
| Standard procedures (new tool, spike, ADR, ...) | [driver/runbook.md](driver/runbook.md) |
| Known gaps in this routing | [rules/known-gaps.md](rules/known-gaps.md) |

## Precedence

1. A tool's own `AGENTS.md` overrides these rules.
2. A rule file overrides a default.
3. When two rule files disagree, the phase rule wins over the index, and the index wins over nothing.

## State is read, not filed

Phase state comes from artifacts on disk: specs, spikes, ADRs, plans, worktrees, tests, code. A script reads [rules/gates.yaml](rules/gates.yaml) and reports which gates pass.

There is no per-tool phases file to keep in sync. Durable decisions and open questions go in the tool's `AGENTS.md`, under `Decisions` and `Open questions`.

To read the current state and pick the next step, run the `workshop-driver` skill.
