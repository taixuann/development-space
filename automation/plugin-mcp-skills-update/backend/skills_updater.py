"""Skills updater module using vercel-labs/skills CLI scoped to .agents/."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Dict, List, Optional, TypedDict


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


def ensure_skills_lock(target_dir: str) -> str:
    """Ensure skills-lock.json exists in target_dir and return its path."""
    lock_path = os.path.join(target_dir, "skills-lock.json")
    if not os.path.isfile(lock_path):
        try:
            with open(lock_path, "w", encoding="utf-8") as f:
                json.dump({"version": 1, "skills": {}}, f, indent=2)
        except Exception:
            pass
    return lock_path


def parse_skills_error(output: str) -> Optional[str]:
    """Extract distinct error signature such as 404 Not Found or Git failure."""
    lines = output.splitlines()
    for line in lines:
        lower = line.lower()
        if "404" in lower or "not found" in lower:
            return line.strip()
        if "fatal:" in lower or "error:" in lower:
            return line.strip()
    return None


def update_skills(workspace_root: str) -> SkillsUpdateResult:
    target_dir = os.path.join(workspace_root, ".agents")
    if not os.path.isdir(target_dir):
        return {
            "success": False,
            "exit_code": 1,
            "output": f"Directory not found: {target_dir}",
            "target_dir": target_dir,
        }

    ensure_skills_lock(target_dir)
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
        is_success = proc.returncode == 0

        # If return code is non-zero, check if it's a 404 or critical failure
        if not is_success:
            err_sig = parse_skills_error(combined_output)
            if err_sig:
                combined_output = f"Skills update error: {err_sig}\n{combined_output}"

        return {
            "success": is_success,
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
