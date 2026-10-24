"""MCP synchronizer and health checker module for development-space."""
from __future__ import annotations

import json
import os
import subprocess
from typing import TypedDict


class McpSyncResult(TypedDict):
    success: bool
    xerj_binary: str
    xerj_version: str | None
    agents_mcp_ok: bool
    opencode_mcp_ok: bool
    codex_mcp_ok: bool
    error: str | None


DEFAULT_XERJ_PATH = "/Users/tai/.local/bin/xerj"


def check_and_sync_mcp(
    workspace_root: str,
    xerj_bin: str = DEFAULT_XERJ_PATH,
) -> McpSyncResult:
    # 1. Check binary
    if not (os.path.isfile(xerj_bin) and os.access(xerj_bin, os.X_OK)):
        return {
            "success": False,
            "xerj_binary": xerj_bin,
            "xerj_version": None,
            "agents_mcp_ok": False,
            "opencode_mcp_ok": False,
            "codex_mcp_ok": False,
            "error": f"Binary not found or not executable at {xerj_bin}",
        }

    xerj_ver: str | None = None
    try:
        ver_proc = subprocess.run(
            [xerj_bin, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        xerj_ver = ver_proc.stdout.strip() or ver_proc.stderr.strip()
    except Exception:
        xerj_ver = "unknown"

    # 2. Check .agents/mcp.json
    agents_path = os.path.join(workspace_root, ".agents", "mcp.json")
    agents_ok = False
    if os.path.isfile(agents_path):
        try:
            with open(agents_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                agents_ok = "xerj" in data.get("mcpServers", {})
        except Exception:
            agents_ok = False

    # 3. Check .opencode/opencode.json
    opencode_path = os.path.join(workspace_root, ".opencode", "opencode.json")
    opencode_ok = False
    if os.path.isfile(opencode_path):
        try:
            with open(opencode_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                opencode_ok = "xerj" in data.get("mcp", {}).get("servers", {})
        except Exception:
            opencode_ok = False

    # 4. Check .codex/config.toml
    codex_path = os.path.join(workspace_root, ".codex", "config.toml")
    codex_ok = False
    if os.path.isfile(codex_path):
        try:
            with open(codex_path, "r", encoding="utf-8") as f:
                content = f.read()
                codex_ok = "[mcp_servers.xerj]" in content
        except Exception:
            codex_ok = False

    all_synced = agents_ok and opencode_ok and codex_ok
    err = None if all_synced else "MCP xerj configuration missing from one or more harnesses"

    return {
        "success": all_synced,
        "xerj_binary": xerj_bin,
        "xerj_version": xerj_ver,
        "agents_mcp_ok": agents_ok,
        "opencode_mcp_ok": opencode_ok,
        "codex_mcp_ok": codex_ok,
        "error": err,
    }
