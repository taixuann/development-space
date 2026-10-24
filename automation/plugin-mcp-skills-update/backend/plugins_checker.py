"""Plugins checker module tracking upstream Superpowers repository."""
from __future__ import annotations

import subprocess
from typing import TypedDict


class PluginCheckResult(TypedDict):
    success: bool
    upstream_url: str
    head_sha: str | None
    error: str | None


SUPERPOWERS_REPO = "https://github.com/obra/superpowers.git"


def check_superpowers_plugin(repo_url: str = SUPERPOWERS_REPO) -> PluginCheckResult:
    try:
        proc = subprocess.run(
            ["git", "ls-remote", repo_url, "HEAD"],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if proc.returncode != 0:
            return {
                "success": False,
                "upstream_url": repo_url,
                "head_sha": None,
                "error": proc.stderr.strip() or f"git ls-remote failed with exit {proc.returncode}",
            }

        first_line = proc.stdout.splitlines()[0] if proc.stdout.splitlines() else ""
        sha = first_line.split()[0] if first_line.split() else None
        return {
            "success": sha is not None,
            "upstream_url": repo_url,
            "head_sha": sha,
            "error": None if sha else "Could not parse HEAD commit from remote",
        }
    except Exception as exc:
        return {
            "success": False,
            "upstream_url": repo_url,
            "head_sha": None,
            "error": str(exc),
        }
