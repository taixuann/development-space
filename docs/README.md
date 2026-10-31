# Workshop Documentation

This repository operates under a **100% Upstream Skill Architecture** powered by the [Agent Skills specification](https://agentskills.io/) and official upstream collections (`github/awesome-copilot`).

## Rules and phases

The workshop's own rules are split by topic in [`rules/`](rules/). Start at [`AGENTS.md`](AGENTS.md), which indexes them:

| Rule | Covers |
| :--- | :--- |
| [`rules/tiers.md`](rules/tiers.md) | Small tool or platform/app |
| [`rules/phase-1-vision.md`](rules/phase-1-vision.md) | Vision, glossary, skill proposals |
| [`rules/phase-2-plan.md`](rules/phase-2-plan.md) | Detect, spikes, ADRs, design doc, plan |
| [`rules/phase-3-build.md`](rules/phase-3-build.md) | Scaffold, build, verify |
| [`rules/stack-profile.md`](rules/stack-profile.md) | The parts table in a tool's `AGENTS.md` |
| [`rules/gates.yaml`](rules/gates.yaml) | Gate contract read by `workshop-driver` |
| [`driver/runbook.md`](driver/runbook.md) | Standard procedures: new tool, inspect, spike, ADR, design doc, plan, release |
| [`rules/known-gaps.md`](rules/known-gaps.md) | What is untested or missing |

Use the `workshop-driver` skill to read the current state of a tool and choose the next step.

## Upstream Skill Architecture

Rather than maintaining rigid in-house layout documents and bespoke custom skills, development in this workshop follows official upstream skills registered in `.agents/skills/`:

| Capability | Upstream Authority | Role in Development |
| :--- | :--- | :--- |
| **Tool Scaffolding & Packaging** | `python-pypi-package-builder` | PyPA-compliant package layouts (`src/`), `pyproject.toml`, SemVer, and distribution via `uv tool`. |
| **Modular Architecture & SoC** | `folder-structure-blueprint-generator` | Enforce dynamic Separation of Concerns (SoC) across backend, frontend, database, and APIs. |
| **Architectural Decisions (ADR)** | `create-architectural-decision-record` | Standardized, AI-readable decision records for significant structural choices. |
| **Agent Instructions & Standards**| `create-agentsmd` & `copilot-instructions-blueprint-generator` | Standardized `AGENTS.md` and Copilot instructions conforming to the agents.md specification. |
| **Code Quality & Style** | `code-exemplars-blueprint-generator` | Pin canonical code exemplars to enforce high-quality coding conventions. |
| **CLI & Batch Progress** | `batch-script-progress` | Standardize stream separation (`stdout`/`stderr`), exit codes, and non-interactive batch execution. |
| **Doc Drift Auditing** | `docs-sync-audit` | Automated detection of doc drift between code changes, CLI options, and documentation. |
| **CI/CD Security & Testing** | `github-actions-hardening` & `gh-fix-ci` | Security hardening for `.github/workflows` and automated failure triage. |

Historical in-house specifications (`small-tool-contract.md`, `standard-tool-layout.md`) are archived in [`docs/archive/`](archive/).
