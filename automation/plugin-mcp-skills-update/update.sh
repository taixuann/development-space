#!/usr/bin/env bash
# automation/plugin-mcp-skills-update/update.sh
# Thin wrapper executing Python modular backend
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPORT_ROOT="$SCRIPT_DIR/logs"
PYTHON_BIN="/opt/miniconda3/envs/core/bin/python3"

exec "$PYTHON_BIN" "$SCRIPT_DIR/backend/main.py" --report-root "$REPORT_ROOT" "$@"
