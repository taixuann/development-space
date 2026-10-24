#!/usr/bin/env bash
# automation/plugin-mcp-skills-update/uninstall-launchd.sh
set -euo pipefail

LABEL="com.tai.development-space.update"
PLIST_NAME="${LABEL}.plist"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/${PLIST_NAME}"

UID_VAL="$(id -u)"

echo "Unloading $LABEL from launchctl..."
launchctl bootout "gui/$UID_VAL/$LABEL" 2>/dev/null || launchctl unload "$TARGET_PLIST" 2>/dev/null || true

if [ -f "$TARGET_PLIST" ]; then
  rm -f "$TARGET_PLIST"
  echo "✔ Removed $TARGET_PLIST"
else
  echo "✔ Plist file not present in $TARGET_DIR"
fi
