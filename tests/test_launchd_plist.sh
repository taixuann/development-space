#!/usr/bin/env bash
# tests/test_launchd_plist.sh
set -euo pipefail

AUTOMATION_DIR="/Users/tai/development-space/automation/plugin-mcp-skills-update"
PLIST_FILE="$AUTOMATION_DIR/com.tai.development-space.update.plist"
INSTALL_SCRIPT="$AUTOMATION_DIR/install-launchd.sh"
UNINSTALL_SCRIPT="$AUTOMATION_DIR/uninstall-launchd.sh"
STATUS_SCRIPT="$AUTOMATION_DIR/status.sh"

if [ ! -f "$PLIST_FILE" ]; then
  echo "FAIL: $PLIST_FILE does not exist"
  exit 1
fi

# 1. Validate plist syntax using plutil (macOS native)
if ! plutil -lint "$PLIST_FILE" >/dev/null 2>&1; then
  echo "FAIL: Plist file has invalid XML/plist syntax"
  exit 1
fi

# 2. Check executable scripts exist
for script in "$INSTALL_SCRIPT" "$UNINSTALL_SCRIPT" "$STATUS_SCRIPT"; do
  if [ ! -x "$script" ]; then
    echo "FAIL: $script is not executable"
    exit 1
  fi
done

# 3. Test status script (should report registered or not registered without error)
STATUS_OUTPUT=$("$STATUS_SCRIPT")
echo "$STATUS_OUTPUT"
if ! echo "$STATUS_OUTPUT" | grep -q "Launchd service:"; then
  echo "FAIL: status.sh did not produce expected header"
  exit 1
fi

echo "PASS: Launchd plist and lifecycle scripts are valid"
