#!/usr/bin/env python3
"""Scaffold a launchd job source folder plus its runtime report root.

Two source layouts are supported:

  tool   <tool-repo>/automation/<job-name>/   branch admin/<tool-name>_<request-id>
  space  ~/.agents/automation/<job-name>/     branch automation/<job-name>

Both kinds write runtime reports to an explicit absolute report root, normally
/Users/tai/.agents/automation/<stable-job-name>/logs/. That root is outside the
source folder and git-ignored.

Usage:
    python3 scaffold_automation.py \
        --layout space \
        --target-dir /Users/tai/.agents/automation/nightly-report \
        --report-root /Users/tai/.agents/automation/nightly-report-runtime/logs \
        --label com.tai.nightly.report \
        --title "Nightly report" \
        --schedule "0 4 * * *" \
        --program /opt/homebrew/bin/python3 \
        --command "/Users/tai/.agents/automation/nightly-report/run.py"

Standard library only.
"""

from __future__ import annotations

import argparse
import plistlib
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from xml.sax.saxutils import escape

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES_DIR = SKILL_DIR / "templates"
ADMIN_ROOT = Path.home() / ".agents"
REQUIRED_FILES = ("README.md", "AGENTS.md", "launchd.plist")
DEFAULT_PATH = (
    "/opt/homebrew/bin:/opt/homebrew/sbin:/usr/local/bin:/usr/local/sbin:"
    "{home}/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
)


class ScaffoldError(Exception):
    """A refused or invalid scaffold request."""


def base_path() -> str:
    return DEFAULT_PATH.format(home=Path.home())


def emit(message: str) -> None:
    print(message)


def find_enclosing_repo(path: Path) -> Path | None:
    """Return the nearest ancestor (or self) holding a .git entry."""
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    return None


def build_schedule(schedule: str) -> tuple[str, str]:
    """Render a schedule string into an indented plist block and readable text."""
    text = schedule.strip()
    if not text:
        raise ScaffoldError("--schedule is empty")

    interval = re.fullmatch(r"interval:(\d+)", text)
    if interval:
        seconds = int(interval.group(1))
        if seconds < 10:
            raise ScaffoldError("interval must be at least 10 seconds")
        block = (
            "    <key>StartInterval</key>\n"
            f"    <integer>{seconds}</integer>"
        )
        return block, f"Every {seconds} seconds"

    daily = re.fullmatch(r"daily:(\d{1,2}):(\d{2})", text)
    if daily:
        hour, minute = int(daily.group(1)), int(daily.group(2))
        if hour > 23 or minute > 59:
            raise ScaffoldError("daily:HH:MM is out of range")
        block = (
            "    <key>StartCalendarInterval</key>\n"
            "    <dict>\n"
            f"        <key>Hour</key>\n        <integer>{hour}</integer>\n"
            f"        <key>Minute</key>\n        <integer>{minute}</integer>\n"
            "    </dict>"
        )
        return block, f"Daily at {hour:02d}:{minute:02d} local time"

    parts = text.split()
    if len(parts) != 5:
        raise ScaffoldError(
            "unknown schedule %r; use '0 4 * * *', 'daily:04:00', or 'interval:3600'"
            % schedule
        )

    names = ("Minute", "Hour", "Day", "Month", "Weekday")
    lines = ["    <key>StartCalendarInterval</key>", "    <dict>"]
    readable = []
    for field, value in zip(names, parts):
        if value == "*":
            continue
        if not value.isdigit():
            raise ScaffoldError(
                "unsupported cron field %r; this scaffold accepts digits or '*'" % value
            )
        number = int(value)
        limits = {"Minute": 59, "Hour": 23, "Day": 31, "Month": 12, "Weekday": 7}
        if number > limits[field]:
            raise ScaffoldError(f"cron {field} {number} is out of range")
        lines.append(f"        <key>{field}</key>")
        lines.append(f"        <integer>{number}</integer>")
        readable.append(f"{field.lower()} {number}")
    lines.append("    </dict>")
    return "\n".join(lines), "Scheduled at " + ", ".join(readable) + " local time"


def validate_report_root(value: str, source_dir: Path) -> Path:
    raw = value.strip()
    if not raw:
        raise ScaffoldError("--report-root is required")
    candidate = Path(raw)
    if not candidate.is_absolute():
        raise ScaffoldError(
            f"--report-root must be absolute, got {raw!r}. "
            "launchd does not expand '~' or resolve a working directory."
        )
    resolved = candidate.resolve()
    if resolved == source_dir or source_dir in resolved.parents:
        raise ScaffoldError(
            f"--report-root {resolved} is inside the source folder {source_dir}. "
            "Runtime reports must live outside the source tree."
        )
    if resolved in source_dir.parents:
        raise ScaffoldError(
            f"--report-root {resolved} contains the source folder. "
            "Pick a report root beside the source, not above it."
        )
    return resolved


def validate_layout(args: argparse.Namespace, source_dir: Path) -> tuple[Path, str, str]:
    """Return (repo_root, layout_description, branch)."""
    enclosing = find_enclosing_repo(source_dir.parent)

    if args.layout == "space":
        repo_root = enclosing or ADMIN_ROOT
        if enclosing is None and ADMIN_ROOT not in source_dir.parents:
            emit(f"  warning: no Git repository above {source_dir}; "
                 f"treating the owner as {ADMIN_ROOT}")
        if enclosing and enclosing != ADMIN_ROOT and not args.allow_foreign_repo:
            raise ScaffoldError(
                f"space layout expects a job under {ADMIN_ROOT}, but {source_dir} "
                f"is inside the Git repository {enclosing}. Use --layout tool when "
                "the job belongs to a tool repository, or --allow-foreign-repo to override."
            )
        layout_text = f"Space-owned (Admin `automation/<job-name>`)"
        return repo_root, layout_text, f"automation/{source_dir.name}"

    if args.layout == "tool":
        if source_dir.parent.name != "automation":
            raise ScaffoldError(
                "tool layout expects <tool-repo>/automation/<job-name>; "
                f"got {source_dir}"
            )
        repo_root = source_dir.parent.parent
        if not (repo_root / ".git").exists():
            raise ScaffoldError(
                f"{repo_root} is not a Git repository. Tool-owned jobs live inside "
                "the tool's own repository."
            )
        tool_name = repo_root.name
        request_id = args.request_id or "<request-id>"
        if request_id and request_id != "<request-id>" and not re.fullmatch(r"\d+", request_id):
            raise ScaffoldError("--request-id must keep its digits, for example 008")
        return (
            repo_root,
            f"Tool-owned (`{tool_name}/automation/<job-name>`)",
            f"admin/{tool_name}_{request_id}",
        )

    raise ScaffoldError(f"unknown layout {args.layout!r}")


def check_existing(source_dir: Path) -> None:
    existing = [name for name in REQUIRED_FILES if (source_dir / name).exists()]
    existing.extend(sorted(p.name for p in source_dir.glob("*.plist")))
    wrapper = source_dir / "scripts" / "run.sh"
    if wrapper.exists():
        existing.append("scripts/run.sh")
    existing = sorted(set(existing))
    if existing:
        raise ScaffoldError(
            "refusing to overwrite an existing scaffold in "
            f"{source_dir}: {', '.join(existing)}"
        )


def program_arguments(args: argparse.Namespace, source_dir: Path) -> tuple[list[str], str]:
    """Return argv for the plist and the command line a wrapper should run."""
    if args.wrapper:
        runner = source_dir / "scripts" / "run.sh"
        argv = ["/bin/bash", str(runner)]
        if args.program:
            tokens = [args.program, *shlex.split(args.command or "")]
            command_line = " ".join(shlex.quote(token) for token in tokens)
        else:
            if not args.command:
                raise ScaffoldError("--wrapper needs --program or --command")
            command_line = args.command
        return argv, command_line

    if not args.program:
        raise ScaffoldError(
            "direct execution needs --program with an absolute path. "
            "Pass --wrapper only when a wrapper does work the job needs."
        )
    program = Path(args.program)
    if not program.is_absolute():
        raise ScaffoldError(f"--program must be absolute, got {args.program!r}")
    if not program.exists():
        raise ScaffoldError(f"--program does not exist: {program}")
    if not program.is_file() or not (program.stat().st_mode & 0o111):
        raise ScaffoldError(f"--program is not an executable file: {program}")

    tokens = shlex.split(args.command or "")
    for token in tokens:
        if token.startswith("-") or "/" not in token:
            continue
        path = Path(token)
        if not path.is_absolute():
            raise ScaffoldError(
                f"argument path {token!r} is relative. launchd sets no working "
                "directory in this template; pass an absolute path."
            )
        if not path.exists():
            emit(f"  warning: argument path does not exist yet: {path}")
    return [args.program, *tokens], " ".join(shlex.quote(t) for t in [args.program, *tokens])


def render(template: str, values: dict[str, str]) -> str:
    text = (TEMPLATES_DIR / template).read_text()
    for key, value in values.items():
        text = text.replace("{{" + key + "}}", value)
    unresolved = sorted(set(re.findall(r"\{\{([A-Z_]+)\}\}", text)))
    if unresolved:
        raise ScaffoldError(f"{template} has unresolved placeholders: {unresolved}")
    return text


def deploy(plist_path: Path, label: str) -> None:
    """Copy the plist and bootstrap it. Opt-in, explicit, and reversible."""
    uid = sys.getuid()
    installed = Path.home() / "Library" / "LaunchAgents" / f"{label}.plist"
    previous = installed.with_name(installed.name + ".previous")
    commands = [
        ["launchctl", "bootout", f"gui/{uid}/{label}"],
        ["launchctl", "bootstrap", f"gui/{uid}", str(installed)],
    ]
    emit("\nDeploy is authorized for this run. Exact commands:")
    emit("  " + " ".join(shlex.quote(part) for part in commands[0]))
    if installed.exists():
        emit("  " + " ".join(shlex.quote(part) for part in ["cp", str(installed), str(previous)]))
    emit("  " + " ".join(shlex.quote(part) for part in ["cp", str(plist_path), str(installed)]))
    emit("  " + " ".join(shlex.quote(part) for part in commands[1]))

    bootout = subprocess.run(commands[0], capture_output=True, text=True)
    if bootout.returncode != 0:
        emit(f"  bootout returned {bootout.returncode}; the job was probably not loaded")

    installed.parent.mkdir(parents=True, exist_ok=True)
    if installed.exists():
        shutil.copyfile(installed, previous)
        emit(f"  previous plist saved at {previous}")
    shutil.copyfile(plist_path, installed)

    bootstrap = subprocess.run(commands[1], capture_output=True, text=True)
    if bootstrap.returncode != 0:
        raise ScaffoldError(
            "bootstrap failed: "
            + (bootstrap.stderr.strip() or bootstrap.stdout.strip())
            + f". The job is not loaded. Roll back with the saved copy at {previous}"
        )
    emit(f"  bootstrapped {installed}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scaffold a launchd job source folder and its report root"
    )
    parser.add_argument("--layout", choices=("tool", "space"), required=True,
                        help="tool: <tool-repo>/automation/<job>; space: ~/.agents/automation/<job>")
    parser.add_argument("--target-dir", required=True,
                        help="Absolute path of the job source folder")
    parser.add_argument("--report-root", required=True,
                        help="Absolute report root outside the source folder")
    parser.add_argument("--label", required=True, help="Reverse-DNS label, for example com.tai.bridge.sync")
    parser.add_argument("--title", default="", help="Human title")
    parser.add_argument("--description", default="", help="What the job does")
    parser.add_argument("--schedule", default="0 4 * * *",
                        help="'0 4 * * *', 'daily:04:00', or 'interval:3600'")
    parser.add_argument("--program", default="", help="Absolute executable path")
    parser.add_argument("--command", default="",
                        help="Arguments for --program, or a shell line for --wrapper. "
                             "Write --command='--flag' when the value starts with '-'")
    parser.add_argument("--wrapper", action="store_true",
                        help="Also emit scripts/run.sh (lock, one-line terminal event)")
    parser.add_argument("--run-at-load", action="store_true",
                        help="Also run once at bootstrap (default: schedule only)")
    parser.add_argument("--request-id", default="", help="Admin request id for a tool branch, for example 008")
    parser.add_argument("--deploy", action="store_true",
                        help="Opt-in: copy the plist and bootstrap it now")
    parser.add_argument("--allow-foreign-repo", action="store_true",
                        help="Allow a space layout outside the Admin repository")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        source_dir = Path(args.target_dir)
        if not source_dir.is_absolute():
            raise ScaffoldError(f"--target-dir must be absolute, got {args.target_dir!r}")
        source_dir = source_dir.resolve()
        if source_dir.exists() and not source_dir.is_dir():
            raise ScaffoldError(f"--target-dir is not a directory: {source_dir}")

        report_root = validate_report_root(args.report_root, source_dir)
        repo_root, layout_text, branch = validate_layout(args, source_dir)
        check_existing(source_dir)

        schedule_block, schedule_readable = build_schedule(args.schedule)
        program_path = args.program or (source_dir / "scripts" / "run.sh").as_posix()
        argv, command_line = program_arguments(args, source_dir)

        label = args.label.strip()
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]+", label):
            raise ScaffoldError(f"--label is not a reverse-DNS label: {label!r}")
        title = args.title or label
        description = args.description or f"Scheduled job {label}"

        source_dir.mkdir(parents=True, exist_ok=True)
        report_root.mkdir(parents=True, exist_ok=True)
        plist_path = source_dir / "launchd.plist"

        argument_lines = "\n".join(
            f"        <string>{escape(token)}</string>" for token in argv
        )
        plist_values = {
            "LABEL": label,
            "PROGRAM_ARGUMENTS": argument_lines,
            "PATH_VALUE": escape(base_path()),
            "HOME_DIR": escape(str(Path.home())),
            "STDOUT_LOG": escape(str(report_root / "stdout.log")),
            "STDERR_LOG": escape(str(report_root / "stderr.log")),
            "RUN_AT_LOAD_BLOCK": "    <key>RunAtLoad</key>\n    <true/>" if args.run_at_load else "",
            "SCHEDULE_BLOCK": schedule_block,
        }
        plist_path.write_text(render("plist.template.xml", plist_values))
        with plist_path.open("rb") as handle:
            parsed = plistlib.load(handle)
        if parsed.get("Label") != label:
            raise ScaffoldError("rendered plist label does not match --label")
        emit(f"plist       {plist_path}")
        emit(f"label       {label} (from plist contents)")

        if args.wrapper:
            runner = source_dir / "scripts" / "run.sh"
            runner.parent.mkdir(parents=True, exist_ok=True)
            runner.write_text(
                render(
                    "runner.sh.template",
                    {
                        "JOB_NAME": label,
                        "LABEL": label,
                        "REPORT_ROOT": escape(str(report_root)),
                        "PATH_VALUE": base_path(),
                        "MAIN_EXECUTION_COMMAND": command_line,
                    },
                )
            )
            runner.chmod(0o755)
            emit(f"runner      {runner} (mode 755)")

        readme_values = {
            "SERVICE_TITLE": title,
            "SERVICE_DESCRIPTION": description,
            "LABEL": label,
            "OWNER_DESCRIPTION": f"{layout_text}, repository {repo_root}",
            "BRANCH": branch,
            "WORKING_DIR": str(source_dir),
            "REPORT_ROOT": str(report_root),
            "SCHEDULE_HUMAN_READABLE": schedule_readable,
            "LOCAL_TIMEZONE": time.tzname[0],
            "PROGRAM_PATH": program_path,
            "WRAPPER_LINE": (
                "\nA thin wrapper runs at `scripts/run.sh`. It holds the job lock and "
                "writes one terminal event per run. It loads no other file.\n"
                if args.wrapper
                else "\nThe plist calls the program directly. It has no wrapper.\n"
            ),
            "MANUAL_RUN_COMMAND": command_line,
        }
        (source_dir / "README.md").write_text(render("README.template.md", readme_values))
        emit(f"runbook     {source_dir / 'README.md'}")

        agents_values = {
            "SERVICE_TITLE": title,
            "LABEL": label,
            "REPO_ROOT": str(repo_root),
            "LAYOUT_DESCRIPTION": layout_text,
            "BRANCH": branch,
            "WORKING_DIR": str(source_dir),
            "REPORT_ROOT": str(report_root),
        }
        (source_dir / "AGENTS.md").write_text(render("AGENTS.template.md", agents_values))
        emit(f"contract    {source_dir / 'AGENTS.md'}")
        emit(f"report root {report_root} (outside source, keep it git-ignored)")

        if args.deploy:
            deploy(plist_path, label)

        emit("\nNext:")
        emit(f"  plutil -lint {plist_path}")
        emit(
            "  python3 "
            f"{SKILL_DIR / 'scripts' / 'verify_automation.py'} "
            f"\"{source_dir}\" --static --report-root \"{report_root}\""
        )
        emit("No job was started and no launchd record was changed.")
        return 0
    except ScaffoldError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
