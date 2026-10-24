#!/usr/bin/env bash
# automation/plugin-mcp-skills-update/status.sh
set -euo pipefail

LABEL="com.tai.development-space.update"
PLIST_NAME="${LABEL}.plist"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/${PLIST_NAME}"
LOGS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/logs"

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

echo "--- Recent update logs ---"
if [ -d "$LOGS_DIR" ]; then
  ls -lh "$LOGS_DIR"/*.log 2>/dev/null | tail -n 5 || echo "No logs generated yet."
else
  echo "Logs directory does not exist."
fi
