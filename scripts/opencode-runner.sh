#!/usr/bin/env bash
# scripts/opencode-runner.sh
# Dual-mode launcher for OpenCode in development-space
set -euo pipefail

MODE="case1"
DRY_RUN=false
STATE_FILE="$HOME/.config/opencode/free-router/state.json"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      break
      ;;
  esac
done

resolve_profile() {
  case "$MODE" in
    case1)
      echo "case1:deepseek-v4.1-flash->beam-free"
      ;;
    case2)
      echo "case2:beam-free->deepseek-v4.1-flash-free"
      ;;
    auto)
      # In auto mode, inspect free-router state or probe Go primary
      if [ -f "$STATE_FILE" ] && grep -q '"opencode-go/deepseek-v4.1-flash"' "$STATE_FILE" 2>/dev/null; then
        echo "case2:beam-free->deepseek-v4.1-flash-free"
      else
        echo "case1:deepseek-v4.1-flash->beam-free"
      fi
      ;;
    *)
      echo "Unknown mode: $MODE" >&2
      exit 1
      ;;
  esac
}

PROFILE=$(resolve_profile)

if [ "$DRY_RUN" = true ]; then
  echo "$PROFILE"
  exit 0
fi

# Run opencode with configured command arguments
exec opencode "$@"
