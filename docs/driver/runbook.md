# Driver runbook

Scope: standard procedures for this workshop. Each section is a checklist. Run the section that matches the gate or task in front of you. Trailing links point to the rule that explains why.

State is not recorded here. Read it with `workshop-driver` and `phase_status.py`.

## New tool

1. Ask the user which tier applies (small tool or platform/app). See [rules/tiers.md](../rules/tiers.md).
2. Create `tools/<space>/<name>/` with `AGENTS.md`, `README.md`, `.gitignore`.
3. For a platform, create `docs/PHASES.md` is not used: record decisions in `AGENTS.md` under `Decisions`.
4. Run `superpowers:brainstorming` (short form for a small tool, full for a platform).
5. Record the stack profile table in `AGENTS.md` once the parts exist. See [rules/stack-profile.md](../rules/stack-profile.md).
6. Commit the Phase 1 files before any worktree.

## Inspect existing code

Use when the tool already has code and Phase 1 is not complete.

1. Run `graphify update .` and `xerj`.
2. Read with `codebase-design`.
3. Write problems and the test inventory into `docs/superpowers/specs/`.
4. Then run `superpowers:brainstorming`.

This is a suggestion, not a gate. A new tool with no code skips it.

## Run a spike

1. Create a spike worktree with `superpowers:using-git-worktrees`.
2. Write the question, the time limit and the go/no-go in `docs/spikes/<category>-<topic>-spike.md`.
3. Run the experiment in the worktree only.
4. Record go or no-go.
5. Delete the experiment code. Never copy it into the product.

See [rules/phase-2-plan.md](../rules/phase-2-plan.md) for the full spike rules.

## Write an ADR

1. Use the `domain-modeling` format (not `create-architectural-decision-record` unless the user asks for the longer format).
2. One file in `docs/adr/` per hard-to-reverse choice.
3. Name the choice, the context, the decision and the consequences.

## Write a design doc

1. Run `superpowers:brainstorming` and write the spec to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`.
2. Get a fresh reviewer to read it.
3. Get the user's approval before any plan or code.

The design doc is the spec of record. `create-specification` is only for a standalone interface contract the design doc links to.

## Write a plan

1. Run `superpowers:writing-plans` with one acceptance check and one command per task.
2. Fill in the Review Focus section.
3. Hand it to a fresh reviewer and fix every finding.
4. Get the user's approval.

## Release

1. Run the tests and read the output.
2. Run `docs-sync-audit`.
3. Bump the version with `scripts/release.sh patch|minor|major`.
4. Commit, tag `vX.Y.Z`, distribute to `~/.local/bin/`.

See the tool's own `AGENTS.md` for its Release Workflow.
