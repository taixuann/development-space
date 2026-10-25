# Consumer Integration Checks & Decoupled Automation Options Design

Date: 2026-10-25
Author: Codex Operator
Status: Approved

## 1. Intent & Context
Currently, the model router updates consumer configurations (Hermes YAML, OpenCode JSON, Dotenv) based on models probed via OpenCode CLI (`probe_native`). However:
1. It does not verify whether the consumer tool itself (e.g., Hermes) can actually load and execute inference with the newly configured model profile and fallback chain.
2. The user has no explicit, verifiable evidence of whether consumer tools actually work after a sync.
3. Production automation is statically bound to macOS Launchd (`com.tai.model-control-sync`), whereas the user wants multiple automation options, including an explicit prompt/spec for Hermes to set up its own cron schedule.

## 2. Goals & Non-Goals
- **Goals**:
  - Build `backend/integration.py` providing concrete one-word smoke-test verification (`chat -q "hi"` / `run "hi"`) for:
    - **Hermes**: `check_hermes_consumer(consumer_dict)` invoking `hermes -p <profile> chat -q "hi" --yolo`.
    - **OpenCode**: `check_opencode_consumer(consumer_dict)` invoking `opencode run "hi"`.
    - **Custom command**: `check_custom_consumer(consumer_dict)` invoking user-defined `check_cmd`.
  - Expose CLI subcommand `opencode-model-router check [--consumer <id>] [--all] [--json]`.
  - Record live verification results (`last_verified_at`, `verify_status: passed|failed|skipped`, `latency_ms`, `error`) in state and expose in `--status`.
  - Decouple automation options in `scripts/install.sh`:
    - `--automation launchd` (default for macOS daemon)
    - `--automation hermes` (generates Hermes cron task prompt)
    - `--automation none` (on-demand only)
  - Provide `automation/hermes-cron-prompt.md` with instructions for Hermes Agent to create the cron job using `hermes cron create`.
- **Non-Goals**:
  - Running heavy benchmarks during integration checks (strictly lightweight one-word calls with 15s timeouts).

## 3. Architecture
- `backend/integration.py`:
  - `verify_consumer_health(consumer, timeout=15) -> dict`
  - `verify_all_consumers(registry_path, filter_id=None) -> dict`
- `backend/cli.py`:
  - Add `check` subcommand.
- `scripts/install.sh`:
  - Add `--automation [launchd|hermes|none]` flag and prompt.
