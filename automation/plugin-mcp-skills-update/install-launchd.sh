#!/usr/bin/env bash
# automation/plugin-mcp-skills-update/install-launchd.sh
set -euo pipefail

LABEL="com.tai.development-space.update"
PLIST_NAME="${LABEL}.plist"
SOURCE_PLIST="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/${PLIST_NAME}"
TARGET_DIR="$HOME/Library/LaunchAgents"
TARGET_PLIST="$TARGET_DIR/${PLIST_NAME}"

mkdir -p "$TARGET_DIR"

echo "Installing $LABEL into $TARGET_DIR..."
cp -f "$SOURCE_PLIST" "$TARGET_PLIST"

UID_VAL="$(id -u)"

# Unload previous instance if present
launchctl bootout "gui/$UID_VAL/$LABEL" 2>/dev/null || launchctl unload "$TARGET_PLIST" 2>/dev/null || true

# Bootstrap / load new instance
if launchctl bootstrap "gui/$UID_VAL" "$TARGET_PLIST" 2>/dev/null; then
  echo "✔ Successfully bootstrapped $LABEL with launchctl (gui/$UID_VAL)"
elif launchctl load "$TARGET_PLIST" 2>/dev/null; then
  echo "✔ Successfully loaded $LABEL with launchctl load"
else
  echo "⚠ Warning: Could not auto-load with launchctl. Plist copied to $TARGET_PLIST"
fi
