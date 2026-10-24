#!/usr/bin/env bash
# automation/plugin-mcp-skills-update/update.sh
# Daily update runner for Skills, Superpowers plugin, and Xerj MCP
set -euo pipefail

WORKSPACE_ROOT="/Users/tai/development-space"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGS_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOGS_DIR"

DRY_RUN=false
if [[ "${1:-}" == "--dry-run" ]]; then
  DRY_RUN=true
fi

TODAY="$(date "+%Y-%m-%d")"
LOG_FILE="$LOGS_DIR/update-${TODAY}.log"

log() {
  local timestamp
  timestamp="$(date -u "+%Y-%m-%dT%H:%M:%SZ")"
  echo "[$timestamp] $*" | tee -a "$LOG_FILE"
}

if [ "$DRY_RUN" = true ]; then
  echo "DRY RUN: Checking update routines without mutating state..."
  echo "1. Skills: would run 'npx skills update -p -y' in $WORKSPACE_ROOT"
  echo "2. Superpowers: would verify latest git commit of obra/superpowers"
  echo "3. MCP Xerj: would verify binary and sync status"
  echo "DRY RUN COMPLETE"
  exit 0
fi

log "=== Daily Maintenance Run Started ==="

# -----------------------------------------------------------------------------
# 1. Update Skills (vercel-labs/skills CLI scoped to .agents/)
# -----------------------------------------------------------------------------
log "Starting Skills update (npx skills update -p -y in .agents/)..."
cd "$WORKSPACE_ROOT/.agents"

SKILLS_OUTPUT=""
if command -v npx >/dev/null 2>&1; then
  if SKILLS_OUTPUT=$(npx --yes skills update -p -y 2>&1); then
    log "Skills update: SUCCESS"
    echo "$SKILLS_OUTPUT" >> "$LOG_FILE"
  else
    log "Skills update: WARNING (exit $?)"
    echo "$SKILLS_OUTPUT" >> "$LOG_FILE"
  fi
else
  log "Skills update: FAILED (npx command not found)"
fi

# -----------------------------------------------------------------------------
# 2. Check Superpowers Plugin
# -----------------------------------------------------------------------------
log "Checking Superpowers plugin upstream..."
REMOTE_REPO="https://github.com/obra/superpowers.git"
REMOTE_SHA=""
if command -v git >/dev/null 2>&1; then
  if REMOTE_SHA=$(git ls-remote "$REMOTE_REPO" HEAD | awk '{print $1}'); then
    log "Superpowers check: SUCCESS (Upstream HEAD: ${REMOTE_SHA:0:12})"
  else
    log "Superpowers check: WARNING (Failed to query remote repo)"
  fi
else
  log "Superpowers check: FAILED (git command not found)"
fi

# -----------------------------------------------------------------------------
# 3. Verify MCP Xerj
# -----------------------------------------------------------------------------
log "Checking MCP Xerj..."
XERJ_BIN="/Users/tai/.local/bin/xerj"
if [ -x "$XERJ_BIN" ]; then
  XERJ_VER=$("$XERJ_BIN" --version 2>&1 || echo "unknown")
  log "MCP Xerj check: SUCCESS (Binary: $XERJ_BIN, Version: $XERJ_VER)"
else
  log "MCP Xerj check: WARNING (Binary not found or not executable at $XERJ_BIN)"
fi

# Verify synchronization between .agents/mcp.json, .opencode, and .codex
if [ -f "$WORKSPACE_ROOT/.agents/mcp.json" ] && \
   grep -q "xerj" "$WORKSPACE_ROOT/.agents/mcp.json" && \
   grep -q "xerj" "$WORKSPACE_ROOT/.opencode/opencode.json" && \
   grep -q "xerj" "$WORKSPACE_ROOT/.codex/config.toml"; then
  log "MCP Sync check: SUCCESS (.agents, .opencode, .codex in sync)"
else
  log "MCP Sync check: WARNING (Configuration drift detected)"
fi

log "=== Daily Maintenance Run Finished ==="
