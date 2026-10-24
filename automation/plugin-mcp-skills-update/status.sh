#!/usr/bin/env bash
# automation/plugin-mcp-skills-update/status.sh
set -euo pipefail

LABEL="com.tai.development-space.update"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/${LABEL}.plist"
REPORT_ROOT="/Users/tai/.agents/automation/development-space-update-runtime/logs"

echo "=== Launchd service: $LABEL ==="
if [ -f "$TARGET_PLIST" ]; then
  echo "✔ Plist file present at $TARGET_PLIST"
else
  echo "○ Plist file not installed in $TARGET_DIR"
fi

UID_VAL="$(id -u)"
if launchctl print "gui/$UID_VAL/$LABEL" >/dev/null 2>&1; then
  echo "✔ Service is currently loaded in launchctl"
else
  echo "○ Service is not loaded in launchctl"
fi

echo "--- Recent outcome (latest-result.json) ---"
if [ -f "$REPORT_ROOT/latest-result.json" ]; then
  cat "$REPORT_ROOT/latest-result.json"
else
  echo "No latest-result.json found yet at $REPORT_ROOT"
fi
