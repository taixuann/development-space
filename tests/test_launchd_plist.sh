#!/usr/bin/env bash
# tests/test_launchd_plist.sh
set -euo pipefail

AUTOMATION_DIR="/Users/tai/development-space/automation/plugin-mcp-skills-update"
PLIST_FILE="$AUTOMATION_DIR/launchd.plist"
INSTALL_SCRIPT="$AUTOMATION_DIR/install-launchd.sh"
UNINSTALL_SCRIPT="$AUTOMATION_DIR/uninstall-launchd.sh"
STATUS_SCRIPT="$AUTOMATION_DIR/status.sh"
REPORT_ROOT="/Users/tai/.agents/automation/development-space-update-runtime/logs"

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

# 3. Run launchd-automation verify script
python3 ~/.agents/skills/launchd-automation/scripts/verify_automation.py "$AUTOMATION_DIR" --static --report-root "$REPORT_ROOT"

echo "PASS: Launchd plist and lifecycle scripts conform to launchd-automation contract"
