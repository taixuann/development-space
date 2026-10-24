#!/usr/bin/env bash
# tests/test_update_script.sh
set -euo pipefail

SCRIPT="/Users/tai/development-space/automation/plugin-mcp-skills-update/update.sh"
REPORT_ROOT="/Users/tai/.agents/automation/development-space-update-runtime/logs"

if [ ! -x "$SCRIPT" ]; then
  echo "FAIL: $SCRIPT is not executable"
  exit 1
fi

# Run dry-run
OUTPUT=$("$SCRIPT" --dry-run)
echo "$OUTPUT"

if ! echo "$OUTPUT" | grep -q "DRY RUN"; then
  echo "FAIL: Expected 'DRY RUN' in dry-run output"
  exit 1
fi

# Run a live test run to verify real log generation
"$SCRIPT"

LATEST_RESULT="$REPORT_ROOT/latest-result.json"

if [ ! -f "$LATEST_RESULT" ]; then
  echo "FAIL: Result file $LATEST_RESULT was not generated"
  exit 1
fi

if ! grep -q '"outcome": "success"' "$LATEST_RESULT"; then
  echo "FAIL: Result file does not show outcome: success"
  exit 1
fi

echo "PASS: Update script executed and generated structured logs in report root"
