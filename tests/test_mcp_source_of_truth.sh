#!/usr/bin/env bash
# tests/test_mcp_source_of_truth.sh
set -euo pipefail

ROOT_DIR="/Users/tai/development-space"
REGISTRY="$ROOT_DIR/.agents/mcp.json"
ROOT_MCP="$ROOT_DIR/.mcp.json"
OPENCODE_CONFIG="$ROOT_DIR/.opencode/opencode.json"
CODEX_CONFIG="$ROOT_DIR/.codex/config.toml"

# 1. Root .mcp.json must NOT exist
if [ -f "$ROOT_MCP" ]; then
  echo "FAIL: Root .mcp.json still exists! Root must be clean."
  exit 1
fi

# 2. .agents/mcp.json must exist and declare xerj
if [ ! -f "$REGISTRY" ]; then
  echo "FAIL: $REGISTRY does not exist"
  exit 1
fi

if ! jq -e '.mcpServers.xerj' "$REGISTRY" >/dev/null; then
  echo "FAIL: .agents/mcp.json does not define mcpServers.xerj"
  exit 1
fi

# 3. .opencode/opencode.json must define mcp.servers.xerj
if ! jq -e '.mcp.servers.xerj' "$OPENCODE_CONFIG" >/dev/null; then
  echo "FAIL: .opencode/opencode.json does not define mcp.servers.xerj"
  exit 1
fi

# 4. .codex/config.toml must define [mcp_servers.xerj]
if ! grep -q "\[mcp_servers.xerj\]" "$CODEX_CONFIG"; then
  echo "FAIL: .codex/config.toml does not define [mcp_servers.xerj]"
  exit 1
fi

echo "PASS: MCP source of truth established and root is clean"
