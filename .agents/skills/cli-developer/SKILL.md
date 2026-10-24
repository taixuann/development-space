---
name: cli-developer
description: Design commands, flags, help, exit codes, and non-interactive paths conforming to the Small-tool contract. Use when creating or refining a tool's command-line interface.
---

# CLI Developer

Design robust, predictable, and automation-friendly command-line interfaces for tools in `development-space`.
Every tool must adhere to [Small-tool contract](../../docs/small-tool-contract.md).

## Core requirements

1. **Self-documenting**:
   - Every command and subcommand supports `--help` and `-h`.
   - `--help` displays clear usage, required arguments, optional flags, and brief descriptions.

2. **Predictable exit codes**:
   - `0`: Success.
   - `1`: General application failure (network, runtime error, operational exception).
   - `2`: Invalid argument, bad flag, or input validation failure.
   - `3+`: Domain-specific documented failure codes.

3. **Stream separation**:
   - Structured results for automated consumers go to `stdout` (plain text or `--json` format).
   - Diagnostic messages, progress bars, and operational errors go to `stderr`.

4. **Non-interactive by default**:
   - Scheduled jobs and autonomous agents cannot respond to interactive prompts.
   - Any destructive action must provide a non-interactive override (e.g. `--yes` or `--force`).

5. **Idempotence and failure recovery**:
   - Running the tool twice with the same inputs must not corrupt persistent state.
   - Partial failures must retain the prior valid state and report clean diagnostics to `stderr`.
