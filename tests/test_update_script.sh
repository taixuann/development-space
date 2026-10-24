#!/usr/bin/env bash
# tests/test_update_script.sh
set -euo pipefail

SCRIPT="/Users/tai/development-space/automation/plugin-mcp-skills-update/update.sh"

if [ ! -x "$SCRIPT" ]; then
  echo "FAIL: $SCRIPT is not executable"
  exit 1
fi

# Run dry-run
OUTPUT=$("$SCRIPT" --dry-run)
echo "$OUTPUT"

if ! echo "$OUTPUT" | grep -q "DRY RUN COMPLETE"; then
  echo "FAIL: Expected 'DRY RUN COMPLETE' in dry-run output"
  exit 1
fi

# Run a live test run to verify real log generation
"$SCRIPT"

TODAY=$(date "+%Y-%m-%d")
LOG_FILE="/Users/tai/development-space/automation/plugin-mcp-skills-update/logs/update-${TODAY}.log"

if [ ! -f "$LOG_FILE" ]; then
  echo "FAIL: Log file $LOG_FILE was not generated"
  exit 1
fi

if ! grep -q "Skills update:" "$LOG_FILE"; then
  echo "FAIL: Log file does not contain skills update status"
  exit 1
fi

if ! grep -q "MCP Xerj check:" "$LOG_FILE"; then
  echo "FAIL: Log file does not contain MCP xerj check status"
  exit 1
fi

if ! grep -q "Superpowers check:" "$LOG_FILE"; then
  echo "FAIL: Log file does not contain Superpowers plugin check status"
  exit 1
fi

echo "PASS: Update script executed and generated structured logs"
