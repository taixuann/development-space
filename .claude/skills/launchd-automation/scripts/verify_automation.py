#!/usr/bin/env python3
"""Validate a launchd automation source folder.

Static mode is the default and never starts the job. It reads files, lints the
plist, and uses only read-only `launchctl print`.

Live mode is opt-in, may kickstart the job, and proves a terminal outcome. A
kickstart exit code of 0 proves dispatch only, never completion.

Usage:
    python3 verify_automation.py /path/to/automation/job --static
    python3 verify_automation.py /path/to/automation/job --static --compare-installed
    python3 verify_automation.py /path/to/automation/job --live --timeout 600

Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

TERMINAL_OUTCOMES = ("success", "cached", "failed", "skipped_locked")
SUCCESS_OUTCOMES = ("success", "cached")
DEFAULT_RESULT_NAME = "latest-result.json"


class Checker:
    """Collect PASS/FAIL lines and print a machine-readable summary."""

    def __init__(self, mode: str) -> None:
        self.mode = mode
        self.failures = 0
        self.count = 0

    def record(self, ok: bool, check_id: str, detail: str) -> None:
        self.count += 1
        if not ok:
            self.failures += 1
        print(f"{'PASS' if ok else 'FAIL'} {check_id} {detail}")

    def skip(self, check_id: str, detail: str) -> None:
        print(f"SKIP {check_id} {detail}")

    def summary(self) -> int:
        print(
            f"SUMMARY mode={self.mode} checks={self.count} "
            f"failed={self.failures}"
        )
        ok = self.failures == 0
        print(f"RESULT {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1


def run_command(args: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(args, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def load_plist(path: Path) -> dict | None:
    try:
        with path.open("rb") as handle:
            data = plistlib.load(handle)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def string_list(value) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


def snapshot_sizes(paths: list[Path]) -> dict[Path, int]:
    sizes: dict[Path, int] = {}
    for path in paths:
        try:
            sizes[path] = path.stat().st_size
        except OSError:
            sizes[path] = 0
    return sizes


def appended_text(path: Path, offset: int) -> str:
    try:
        with path.open("rb") as handle:
            handle.seek(offset)
            return handle.read().decode("utf-8", errors="replace")
    except OSError:
        return ""


def terminal_from_result(path: Path, started: float) -> tuple[str, dict] | None:
    if not path.is_file():
        return None
    if path.stat().st_mtime < started - 1:
        return None
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    outcome = str(data.get("outcome") or data.get("status") or "")
    if outcome not in TERMINAL_OUTCOMES:
        return None
    return outcome, data


def terminal_from_logs(paths: list[Path], offsets: dict[Path, int]) -> tuple[str, str] | None:
    for path in paths:
        text = appended_text(path, offsets.get(path, 0))
        for line in reversed(text.splitlines()):
            match = re.search(r"terminal=([a-z_]+)", line)
            if match and match.group(1) in TERMINAL_OUTCOMES:
                return match.group(1), line.strip()
    return None


def installed_plist(label: str) -> Path:
    return Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"


def validate_static(args: argparse.Namespace, checker: Checker, job_dir: Path) -> dict:
    """Run read-only checks. Return state the live mode needs."""

    state: dict = {"label": None, "report_root": None, "result_file": None}

    readme = job_dir / "README.md"
    agents = job_dir / "AGENTS.md"
    checker.record(readme.is_file(), "file-readme", str(readme))
    checker.record(agents.is_file(), "file-agents", str(agents))

    if job_dir.parent.name != "automation":
        checker.record(
            False,
            "layout",
            f"{job_dir} is not automation/<job-name>",
        )
    else:
        checker.record(True, "layout", "automation/<job-name>")

    plists = sorted(job_dir.glob("*.plist"))
    checker.record(
        len(plists) == 1,
        "file-plist",
        f"{len(plists)} source plist(s): " + ", ".join(p.name for p in plists),
    )
    if len(plists) != 1:
        return state

    plist_path = plists[0]
    data = load_plist(plist_path)
    checker.record(data is not None, "plist-parse", str(plist_path))
    if data is None:
        return state

    label = str(data.get("Label") or "")
    state["label"] = label
    contents_ok = bool(label) and (args.label is None or label == args.label)
    checker.record(
        contents_ok,
        "plist-label",
        f"label={label or '<missing>'} source={plist_path.name}"
        + (f" expected={args.label}" if args.label else ""),
    )
    if not label:
        return state

    plutil = shutil.which("plutil")
    if plutil:
        code, out, err = run_command([plutil, "-lint", str(plist_path)])
        checker.record(code == 0, "plist-lint", (out or err).strip() or f"exit={code}")
    else:
        checker.record(False, "plist-lint", "plutil not found")

    argv = string_list(data.get("ProgramArguments"))
    if not argv:
        checker.record(False, "program-absolute", "ProgramArguments is missing or empty")
    else:
        program = argv[0]
        absolute = os.path.isabs(program)
        checker.record(absolute, "program-absolute", program)
        if absolute:
            program_path = Path(program)
            checker.record(program_path.is_file(), "program-exists", program)
            checker.record(os.access(program_path, os.X_OK), "program-executable", program)

        missing_args = [
            token
            for token in argv[1:]
            if os.path.isabs(token) and not Path(token).exists()
        ]
        if missing_args and args.allow_missing_args:
            checker.skip("argument-path", "allowed missing: " + ", ".join(missing_args))
        else:
            checker.record(
                not missing_args,
                "argument-path",
                "missing: " + ", ".join(missing_args) if missing_args else "all absolute arguments exist",
            )

        wrapper_script = None
        if Path(program).name in ("bash", "sh", "zsh") and len(argv) > 1:
            wrapper_script = Path(argv[1])
        if wrapper_script is not None:
            checker.record(
                wrapper_script.is_file() and os.access(wrapper_script, os.X_OK),
                "wrapper-executable",
                f"{wrapper_script} executable={wrapper_script.is_file() and os.access(wrapper_script, os.X_OK)}",
            )

    working = data.get("WorkingDirectory")
    if working is None:
        checker.skip("working-directory", "not declared; the job needs absolute paths")
    elif not os.path.isabs(str(working)):
        checker.record(False, "working-directory", f"not absolute: {working}")
    else:
        checker.record(Path(str(working)).is_dir(), "working-directory", str(working))

    stdout_path = data.get("StandardOutPath")
    stderr_path = data.get("StandardErrorPath")
    logs_ok = bool(stdout_path) and bool(stderr_path)
    logs_ok = logs_ok and os.path.isabs(str(stdout_path)) and os.path.isabs(str(stderr_path))
    if logs_ok:
        out_parent = Path(str(stdout_path)).parent
        err_parent = Path(str(stderr_path)).parent
        logs_ok = out_parent == err_parent
        logs_ok = logs_ok and out_parent.is_absolute() and out_parent.is_dir()
        detail = f"{stdout_path} | {stderr_path}"
    else:
        detail = f"stdout={stdout_path} stderr={stderr_path}"
    checker.record(logs_ok, "log-paths", detail)
    if not stdout_path:
        return state
    if not os.path.isabs(str(stdout_path)):
        checker.record(False, "report-outside-source", f"not absolute: {stdout_path}")
        return state

    report_root = Path(str(stdout_path)).parent.resolve()
    state["report_root"] = report_root
    local_logs_allowed = getattr(args, "allow_local_logs", False) or (
        job_dir in report_root.parents and (report_root / ".gitignore").is_file()
    )
    outside = (report_root != job_dir and job_dir not in report_root.parents) or local_logs_allowed
    checker.record(outside, "report-outside-source", f"{report_root} vs {job_dir}")
    if not logs_ok:
        return state
    if args.report_root:
        requested = Path(args.report_root)
        match = str(requested.resolve()) == str(report_root)
        checker.record(match, "report-root-match",
                       f"declared={report_root} requested={requested.resolve()}")

    result_file = Path(args.result_file) if args.result_file else report_root / DEFAULT_RESULT_NAME
    state["result_file"] = result_file
    checker.record(result_file.parent.is_dir(), "result-path", str(result_file))

    duplicates = []
    agents_dir = Path.home() / "Library" / "LaunchAgents"
    if agents_dir.is_dir():
        for candidate in sorted(agents_dir.glob("*.plist")):
            other = load_plist(candidate)
            if other and str(other.get("Label") or "") == label:
                duplicates.append(candidate.name)
    checker.record(
        len(duplicates) <= 1,
        "duplicate-label",
        f"{len(duplicates)} installed plist(s) with label {label}: "
        + (", ".join(duplicates) or "none"),
    )

    if args.compare_installed:
        target = installed_plist(label)
        if not target.is_file():
            checker.record(False, "installed-match", f"missing installed plist {target}")
        else:
            source_bytes = plist_path.read_bytes()
            installed_bytes = target.read_bytes()
            checker.record(
                source_bytes == installed_bytes,
                "installed-match",
                f"{target} identical={source_bytes == installed_bytes}",
            )
    else:
        checker.skip("installed-match", "pass --compare-installed to compare the installed copy")

    if args.skip_launchctl:
        checker.skip("launchd-loaded", "launchctl print skipped")
    else:
        launchctl = shutil.which("launchctl")
        if not launchctl:
            checker.skip("launchd-loaded", "launchctl not found")
        else:
            target = installed_plist(label)
            code, out, err = run_command(
                [launchctl, "print", f"gui/{os.getuid()}/{label}"]
            )
            if code == 0:
                loaded_path = ""
                for line in out.splitlines():
                    stripped = line.strip()
                    if stripped.startswith("path = "):
                        loaded_path = stripped[len("path = "):]
                        break
                matches = bool(loaded_path) and Path(loaded_path) == target
                checker.record(
                    matches,
                    "launchd-loaded",
                    f"loaded path={loaded_path or '<unknown>'} expected={target}",
                )
            else:
                checker.record(True, "launchd-loaded", "not loaded (static check only)")

    return state


def validate_live(
    args: argparse.Namespace,
    checker: Checker,
    job_dir: Path,
    state: dict,
    static_failed: bool,
) -> None:
    label = state.get("label")
    if static_failed:
        checker.record(False, "live-precondition", "static checks failed; live run not started")
        return
    if not label:
        checker.record(False, "live-precondition", "no label from plist contents")
        return

    launchctl = shutil.which("launchctl")
    if not launchctl:
        checker.record(False, "live-precondition", "launchctl not found")
        return

    report_root = state["report_root"]
    result_file = state["result_file"]
    stdout_log = report_root / "stdout.log"
    stderr_log = report_root / "stderr.log"
    watched = [stdout_log, stderr_log]
    offsets = snapshot_sizes(watched)
    started = time.time()

    print(
        "INFO live-dispatch kickstart proves dispatch only; "
        "completion needs a terminal outcome from the job"
    )
    code, out, err = run_command(
        [launchctl, "kickstart", f"gui/{os.getuid()}/{label}"]
    )
    if code != 0:
        checker.record(
            False,
            "live-dispatch",
            f"kickstart exit={code} {err.strip() or out.strip()}",
        )
        return
    checker.record(True, "live-dispatch", "kickstart accepted; polling for a terminal outcome")

    deadline = started + args.timeout
    found: tuple[str, str] | None = None
    while time.time() < deadline:
        result = terminal_from_result(result_file, started)
        if result:
            outcome, record = result
            found = (
                outcome,
                f"run_id={record.get('run_id', '<none>')} source=result-file",
            )
            break
        log_hit = terminal_from_logs(watched, offsets)
        if log_hit:
            found = (log_hit[0], f"line={log_hit[1]!r} source=log")
            break
        time.sleep(max(args.poll_interval, 0.05))

    if not found:
        checker.record(
            False,
            "live-terminal",
            f"no terminal outcome within {args.timeout}s; looked for {result_file} "
            f"or a 'terminal=' line in {stdout_log}",
        )
        return

    outcome, detail = found
    checker.record(True, "live-terminal", f"outcome={outcome} {detail}")
    checker.record(
        outcome in SUCCESS_OUTCOMES,
        "live-outcome",
        f"outcome={outcome} expected one of {SUCCESS_OUTCOMES}",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify a launchd automation source folder")
    parser.add_argument("job_dir", help="Path to automation/<job-name>")
    parser.add_argument("--static", action="store_true",
                        help="Read-only checks (default). Never starts the job")
    parser.add_argument("--live", action="store_true",
                        help="Opt-in: kickstart, then poll for a terminal outcome")
    parser.add_argument("--report-root", default=None,
                        help="Expected absolute report root; compares with the plist")
    parser.add_argument("--result-file", default=None,
                        help=f"Terminal result file (default: <report root>/{DEFAULT_RESULT_NAME})")
    parser.add_argument("--label", default=None, help="Expected label from plist contents")
    parser.add_argument("--compare-installed", action="store_true",
                        help="Compare the source plist with ~/Library/LaunchAgents/<label>.plist")
    parser.add_argument("--allow-missing-args", action="store_true",
                        help="Do not fail when an absolute ProgramArguments token does not exist")
    parser.add_argument("--allow-local-logs", action="store_true",
                        help="Allow report-root to be inside the job directory (e.g. for space-contained logs)")
    parser.add_argument("--skip-launchctl", action="store_true",
                        help="Skip the read-only launchctl print check")
    parser.add_argument("--timeout", type=int, default=300,
                        help="Live mode: seconds to wait for a terminal outcome")
    parser.add_argument("--poll-interval", type=float, default=5.0,
                        help="Live mode: seconds between polls")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.static and args.live:
        parser.error("choose --static or --live, not both")

    job_dir = Path(args.job_dir)
    if not job_dir.is_dir():
        print(f"FAIL job-dir not a directory: {job_dir}")
        print("SUMMARY mode=%s checks=1 failed=1" % ("live" if args.live else "static"))
        print("RESULT FAIL")
        return 1
    job_dir = job_dir.resolve()

    mode = "live" if args.live else "static"
    checker = Checker(mode)
    state = validate_static(args, checker, job_dir)
    static_failed = checker.failures > 0

    if mode == "live":
        validate_live(args, checker, job_dir, state, static_failed)

    return checker.summary()


if __name__ == "__main__":
    sys.exit(main())
