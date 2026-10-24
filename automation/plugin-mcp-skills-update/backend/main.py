#!/usr/bin/env python3
"""Main entrypoint for daily plugin, MCP, and skills maintenance."""
from __future__ import annotations

import argparse
import datetime
import json
import os
import sys
import tempfile
import time
import uuid

# Add parent directory to sys.path so backend package can be imported directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Add ticket-submit skill script directory to sys.path
TICKET_SUBMIT_DIR = os.path.expanduser("~/.agents/skills/ticket-submit/scripts")
if TICKET_SUBMIT_DIR not in sys.path and os.path.isdir(TICKET_SUBMIT_DIR):
    sys.path.insert(0, TICKET_SUBMIT_DIR)

try:
    from ticket_submit import submit_or_update_ticket
except ImportError:
    # Soft fallback if skill script is missing
    def submit_or_update_ticket(**kwargs):  # type: ignore
        return {"success": False, "action": "failed", "error": "ticket_submit module not found"}

from mcp_syncer import check_and_sync_mcp
from plugins_checker import check_superpowers_plugin
from skills_updater import update_skills

LABEL = "com.tai.development-space.update"
DEFAULT_WORKSPACE = "/Users/tai/development-space"


def write_atomic_json(filepath: str, data: dict) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    temp_fd, temp_path = tempfile.mkstemp(
        dir=os.path.dirname(filepath),
        prefix=".tmp_result_",
        suffix=".json",
    )
    with os.fdopen(temp_fd, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(temp_path, filepath)


def cleanup_old_runs(report_root: str, max_age_days: int = 30) -> int:
    """Purge run records and rotated logs older than max_age_days.
    
    latest-result.json, active logs, and git-tracked files are strictly preserved.
    """
    cutoff_time = time.time() - (max_age_days * 86400)
    deleted_count = 0

    protected_basenames = {
        "latest-result.json",
        "stdout.log",
        "stderr.log",
        ".gitkeep",
        ".gitignore",
    }

    # 1. Inspect runs directory
    runs_dir = os.path.join(report_root, "runs")
    if os.path.isdir(runs_dir):
        for fname in os.listdir(runs_dir):
            if fname in protected_basenames:
                continue
            fpath = os.path.join(runs_dir, fname)
            if os.path.isfile(fpath):
                try:
                    if os.path.getmtime(fpath) < cutoff_time:
                        os.remove(fpath)
                        deleted_count += 1
                except Exception:
                    pass

    # 2. Inspect rotated log snapshots in report_root
    if os.path.isdir(report_root):
        for fname in os.listdir(report_root):
            if fname in protected_basenames:
                continue
            if fname.startswith("stdout.log.") or fname.startswith("stderr.log.") or fname.startswith("run_"):
                fpath = os.path.join(report_root, fname)
                if os.path.isfile(fpath):
                    try:
                        if os.path.getmtime(fpath) < cutoff_time:
                            os.remove(fpath)
                            deleted_count += 1
                    except Exception:
                        pass

    return deleted_count


def run_maintenance(
    workspace_root: str,
    report_root: str,
    dry_run: bool = False,
) -> int:
    run_id = f"run_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    start_dt = datetime.datetime.now(datetime.timezone.utc)
    start_time_iso = start_dt.isoformat()
    t0 = time.time()

    os.makedirs(report_root, exist_ok=True)
    stdout_log = os.path.join(report_root, "stdout.log")
    stderr_log = os.path.join(report_root, "stderr.log")

    def log(msg: str) -> None:
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        line = f"[{ts}] {msg}"
        print(line)
        try:
            with open(stdout_log, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    def log_err(msg: str) -> None:
        ts = datetime.datetime.now(datetime.timezone.utc).isoformat()
        line = f"[{ts}] ERROR: {msg}"
        print(line, file=sys.stderr)
        try:
            with open(stderr_log, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except Exception:
            pass

    log(f"=== Starting maintenance {run_id} (dry_run={dry_run}) ===")

    # Enforce 30-day retention
    cleaned = cleanup_old_runs(report_root, max_age_days=30)
    if cleaned > 0:
        log(f"Retention: purged {cleaned} run/log file(s) older than 30 days.")

    if dry_run:
        log("DRY RUN: skipping mutations.")
        details = {
            "skills": {"dry_run": True},
            "plugins": {"dry_run": True},
            "mcp": {"dry_run": True},
        }
        outcome = "cached"
        exit_code = 0
    else:
        # Step 1: Update Skills
        log("Phase 1: Updating skills in .agents/...")
        skills_res = update_skills(workspace_root)
        if skills_res["success"]:
            log(f"Phase 1: Skills update OK (exit {skills_res['exit_code']})")
        else:
            log_err(f"Phase 1: Skills update failed: {skills_res['output']}")

        # Step 2: Check Superpowers Plugin
        log("Phase 2: Checking Superpowers plugin upstream...")
        plugins_res = check_superpowers_plugin()
        if plugins_res["success"]:
            log(f"Phase 2: Superpowers check OK (HEAD: {plugins_res['head_sha'][:12] if plugins_res['head_sha'] else 'unknown'})")
        else:
            log_err(f"Phase 2: Superpowers check error: {plugins_res['error']}")

        # Step 3: Check MCP Xerj & Sync
        log("Phase 3: Checking MCP Xerj and config sync...")
        mcp_res = check_and_sync_mcp(workspace_root)
        if mcp_res["success"]:
            log(f"Phase 3: MCP sync OK (xerj ver: {mcp_res['xerj_version']})")
        else:
            log_err(f"Phase 3: MCP sync failed: {mcp_res['error']}")

        # Determine outcome
        all_ok = skills_res["success"] and plugins_res["success"] and mcp_res["success"]
        outcome = "success" if all_ok else "failed"
        exit_code = 0 if all_ok else 1

        details = {
            "skills": skills_res,
            "plugins": plugins_res,
            "mcp": mcp_res,
        }

        # Incident Escalation to Notion via ticket-submit on failure
        if not all_ok:
            error_reasons = []
            if not skills_res["success"]:
                error_reasons.append(f"Skills: {skills_res.get('output', 'Unknown error')}")
            if not plugins_res["success"]:
                error_reasons.append(f"Plugins: {plugins_res.get('error', 'Unknown error')}")
            if not mcp_res["success"]:
                error_reasons.append(f"MCP: {mcp_res.get('error', 'Unknown error')}")

            err_body = "\n".join(error_reasons)
            log("Escalating failure to Notion Agent Tickets via ticket-submit...")
            ticket_res = submit_or_update_ticket(
                title="[Auto-Sync] Maintenance failure in development-space",
                target_space="Development",
                system_component="Automations & Runtime",
                request_type="Fix",
                status="Blocked",
                current_step="Daily maintenance failure in development-space",
                body=err_body,
                signature="[Auto-Sync] Maintenance failure in development-space",
            )
            log(f"Notion ticket escalation result: {ticket_res}")

    duration = time.time() - t0
    end_dt = datetime.datetime.now(datetime.timezone.utc)
    end_time_iso = end_dt.isoformat()

    result_payload = {
        "run_id": run_id,
        "label": LABEL,
        "start_time": start_time_iso,
        "end_time": end_time_iso,
        "duration_seconds": round(duration, 4),
        "outcome": outcome,
        "exit_code": exit_code,
        "details": details,
    }

    latest_result_path = os.path.join(report_root, "latest-result.json")
    try:
        write_atomic_json(latest_result_path, result_payload)
    except Exception as exc:
        log_err(f"Failed to write latest-result.json: {exc}")

    log(f"=== Maintenance completed with outcome={outcome} (exit_code={exit_code}, duration={duration:.2f}s) ===")
    print(f"terminal={{\"outcome\": \"{outcome}\", \"exit_code\": {exit_code}}}")
    return exit_code


def main() -> None:
    parser = argparse.ArgumentParser(description="Daily maintenance service for development-space.")
    parser.add_argument(
        "--report-root",
        required=True,
        help="Absolute path to runtime report directory (holds logs and latest-result.json)",
    )
    parser.add_argument(
        "--workspace-root",
        default=DEFAULT_WORKSPACE,
        help="Path to development-space workspace",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making network calls or updates",
    )

    args = parser.parse_args()
    code = run_maintenance(
        workspace_root=os.path.abspath(args.workspace_root),
        report_root=os.path.abspath(args.report_root),
        dry_run=args.dry_run,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()
