# Phase 1: think and decide the vision

Scope: the first phase of the platform track. No product code in this phase. `superpowers:brainstorming` leads, and the user starts it by typing `/brainstorming`.

| Step | Skill | Output |
|---|---|---|
| 1 | `superpowers:brainstorming` | Vision, goals, non-goals, scope of the first version |
| 2 | `domain-modeling` | `GLOSSARY.md` in the tool |
| 3 | `agent-skill-stack` | A short list of outside skills and plugins that fit the stack, once the stack is known |

## Optional pre-step: read the code first

If the tool already has code, read it before the vision conversation. Run `graphify update .` and `xerj`, then `codebase-design`, and write the problems and the test inventory into `docs/superpowers/specs/`. A vision written without that reading is a guess.

This is a suggestion, not a gate. A new tool with no code skips it. Phase 2 step 2 still runs the full read later.

Decisions that outlive a session go in the tool's `AGENTS.md`, under a `Decisions` heading: what was chosen, the date, and the reason. Open questions go in an `Open questions` heading in the same file.

There is no per-tool phases file. Phase state is read from the artifacts on disk (see [gates.yaml](gates.yaml)), so a second hand-maintained status document would only drift from them.

## Propose skills during brainstorming

While brainstorming, propose a skill when its trigger appears. Name the skill and say why. Run it only after the user agrees. Make proposals before the design doc is approved, because after approval only `superpowers:writing-plans` may follow.

| Trigger | Propose |
|---|---|
| Existing code is large or unclear | `graphify`, `xerj` |
| Wanting to understand what an existing tool or system does | `graphify`, `xerj`, `codebase-design` |
| A picture would settle the question | `archify` |
| The design rests on an unproven claim | `create-technical-spike` |
| A choice is hard to reverse, surprising, and a real trade-off | an ADR |
| A term is vague or used two ways | `domain-modeling` |
| The stack is fixed and outside skills might help | `agent-skill-stack` |
| Charts or figures are part of the product | `dataviz` |
| The user interface direction is open | `impeccable` |
| Tauri 2 is in scope | The Tauri skills in `.claude/skills` |
| Rust is in scope | The Rust CLI Skills plugin, when installed |
| AI agents are part of the product | `agent-architecture` |

## Third-party skills and plugins

Propose first. Install only after the user says yes. Before installing:

1. Read every file. Accept markdown only, with no hooks and no tool permissions.
2. Check the licence. Keep copies of unlicensed skills untracked when the repository is public.
3. Record the source URL and commit in the tool's `AGENTS.md`.
