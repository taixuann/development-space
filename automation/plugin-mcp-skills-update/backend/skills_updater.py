"""Skills updater module using vercel-labs/skills CLI scoped to .agents/."""
from __future__ import annotations

import os
import shutil
import subprocess
from typing import TypedDict


class SkillsUpdateResult(TypedDict):
    success: bool
    exit_code: int
    output: str
    target_dir: str


def find_npx() -> str:
    # 1. Check in current PATH
    found = shutil.which("npx")
    if found:
        return found

    # 2. Check known fnm installation paths
    candidate_paths = [
        "/Users/tai/.local/share/fnm/node-versions/v22.22.3/installation/bin/npx",
        "/usr/local/bin/npx",
        "/opt/homebrew/bin/npx",
    ]
    for p in candidate_paths:
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p

    return "npx"


def update_skills(workspace_root: str) -> SkillsUpdateResult:
    target_dir = os.path.join(workspace_root, ".agents")
    if not os.path.isdir(target_dir):
        return {
            "success": False,
            "exit_code": 1,
            "output": f"Directory not found: {target_dir}",
            "target_dir": target_dir,
        }

    npx_bin = find_npx()

    try:
        proc = subprocess.run(
            [npx_bin, "--yes", "skills", "update", "-p", "-y"],
            cwd=target_dir,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        combined_output = (proc.stdout + "\n" + proc.stderr).strip()
        return {
            "success": proc.returncode == 0,
            "exit_code": proc.returncode,
            "output": combined_output,
            "target_dir": target_dir,
        }
    except Exception as exc:
        return {
            "success": False,
            "exit_code": -1,
            "output": f"Exception running npx skills: {exc}",
            "target_dir": target_dir,
        }
