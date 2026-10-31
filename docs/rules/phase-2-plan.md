# Phase 2: detect, prove, plan

Scope: the second phase of the platform track. No product code in this phase, except throwaway spikes. The phase ends with a valid plan.

| Step | Skill | Output |
|---|---|---|
| 1 | Commit the Phase 1 files | The worktrees start from them |
| 2 | `graphify` (run `graphify update .`), `xerj`, `codebase-design` | The problems in the existing code, found by reading it. Include a list of existing tests mapped to the new modules. |
| 3 | `superpowers:using-git-worktrees` | A spike worktree, kept apart from the main branch |
| 4 | `create-technical-spike` | One spike document per risky unknown in `docs/spikes/`, with a recorded go or no-go. Experiments only. |
| 5 | `domain-modeling` ADR format | One record in `docs/adr/` per hard-to-reverse choice |
| 6 | `superpowers:brainstorming` design doc | The spec of record, in `docs/superpowers/specs/`. A reviewer reads it, then the user approves it. |
| 7 | `impeccable`, when the product has a UI | A design brief that fixes the look and the web framework before any UI task |
| 8 | `superpowers:using-git-worktrees` | The foundation worktree |
| 9 | `superpowers:writing-plans` | The plan, with its self-review and Review Focus section |
| 10 | A fresh reviewer, optionally `/advisor` | A review of the plan |

Two choices made on 2026-10-29:

- ADRs use the `domain-modeling` format. Use `create-architectural-decision-record` only when the user asks for its longer format.
- The brainstorming design doc is the spec of record. Use `create-specification` only for a standalone interface contract that the design doc links to.

## Spikes

Use `create-technical-spike` for experiments only, and only in Phase 2.

- A spike answers one yes-or-no question about something unproven, with a time limit.
- Write the question, the time limit and the result in `docs/spikes/<category>-<topic>-spike.md`.
- Run any experiment code in the spike worktree. Delete that code when the spike ends. Never copy spike code into the product. Rewrite it under the plan.
- Start a spike only after the user agrees to it. Installing tools or dependencies for a spike needs the same agreement.

## A valid plan

Build nothing until every gate in [gates.yaml](gates.yaml) under `phase_2` is satisfied. In words:

1. The design doc is approved by the user.
2. Each spike has a recorded go or no-go.
3. Each hard-to-reverse choice has an ADR.
4. Each task names its acceptance check, tied to a contract section or an existing test, and the command that runs it.
5. The `superpowers:writing-plans` self-review is done and its Review Focus section is filled in.
6. A fresh reviewer has read the plan and the findings are fixed.
7. The user approves the plan.

Gates 1, 5, 6 and 7 are human judgements. Record the approval in the tool's `AGENTS.md` under `Decisions`; the other gates leave a file on disk that a script can find.
