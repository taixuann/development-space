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

6. **Configuration & Entity Management Subcommands (CLI-First Mutation)**:
   - When a tool maintains registries, endpoints, profiles, or consumers, it MUST expose dedicated subcommands:
     `<tool-name> <entity> [list|add|set|remove]` (e.g., `opencode-model-router consumer list`, `opencode-model-router consumer add`).
   - Do NOT require automated agents or humans to hand-edit, regex-parse, or serialize raw YAML/JSON configuration files. The CLI must manage serialization, schema validation, and atomic writes.
   - Always implement a `--json` output flag for list and status subcommands for automation.

7. **Standard Configuration Resolution Hierarchy (XDG Precedence)**:
   - Do not assume configuration files exist in the current working directory. Resolve configurations in strict order of precedence:
     1. Explicit CLI argument: `--config <path>` or `--registry <path>`.
     2. Local workspace override: `./config/<file>.yaml` or `./<file>.yaml`.
     3. User standard XDG directory: `$XDG_CONFIG_HOME/<tool-name>/<file>.yaml` (default: `~/.config/<tool-name>/<file>.yaml`).
     4. Tracked template fallback: `<tool-name>/config.example.yaml` in the tool root.
   - Updating or reinstalling a tool repository must NEVER overwrite or delete existing user configurations.

8. **Argparse Subparser Ergonomics (Shared Parent Parsers)**:
   - Shared flags (such as `--config` or `--registry`) should be defined in a reusable parent parser so they can appear either before or after subcommands without syntax errors:
     ```python
     common_p = argparse.ArgumentParser(add_help=False)
     common_p.add_argument('--config', default=None, help='Path to configuration file')

     parser = argparse.ArgumentParser(prog='mytool', parents=[common_p])
     subparsers = parser.add_subparsers(dest='subcommand')
     consumer_p = subparsers.add_parser('consumer', parents=[common_p])
     add_p = consumer_p.add_subparsers().add_parser('add', parents=[common_p])
     ```
   - This ensures both `mytool --config x consumer add` and `mytool consumer add --config x` execute seamlessly.

9. **Zero Hardcoded Paths**:
   - Never hardcode absolute user paths (e.g. `/Users/tai/...` or `/home/user/...`).
   - Resolve home directories dynamically via `pathlib.Path.home()` or `$HOME`.
   - Resolve tool-relative resources via `Path(__file__).resolve().parent`.
