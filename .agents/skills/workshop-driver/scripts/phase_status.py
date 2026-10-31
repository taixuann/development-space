#!/usr/bin/env python3
"""Read the phase state of a workshop tool from the artifacts on disk.

Read-only. Never writes, never runs a build, never touches git state beyond
`git log` and `git worktree list`.

Usage:
    phase_status.py --list
    phase_status.py raw-viewer
    phase_status.py tools/research/raw-viewer
    phase_status.py . --text
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover - environment guard
    sys.stderr.write(
        "phase_status.py needs PyYAML. Install it with: python3 -m pip install pyyaml\n"
    )
    raise SystemExit(1)

SOURCE_EXTS = {
    ".py": "Python",
    ".swift": "Swift",
    ".rs": "Rust",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".go": "Go",
    ".rb": "Ruby",
    ".sh": "Shell",
}

PLATFORM_MARKERS = [
    "frontend",
    "web",
    "src-tauri",
    "Sources",
    "Package.swift",
]

SKIP_DIRS = {
    ".git", ".venv", "node_modules", "build", "dist", "__pycache__",
    ".pytest_cache", ".quality-cache", "graphify-out", ".mypy_cache",
}


def find_workshop_root(start: Path) -> Path | None:
    for candidate in [start, *start.parents]:
        if (candidate / "docs" / "rules" / "gates.yaml").is_file():
            return candidate
    return None


def load_rules(root: Path) -> dict:
    path = root / "docs" / "rules" / "gates.yaml"
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def iter_tools(root: Path) -> list[dict]:
    tools = []
    for path in sorted((root / "tools").glob("*/*")):
        if not path.is_dir() or not (path / "AGENTS.md").is_file():
            continue
        tools.append({"name": path.name, "space": path.parent.name, "path": path})
    return tools


def resolve_tool(root: Path, value: str, cwd: Path) -> Path:
    raw = Path(value).expanduser()
    if raw.is_dir():
        return raw.resolve()
    for tool in iter_tools(root):
        if tool["name"] == value or tool["name"].startswith(value):
            return tool["path"].resolve()
    if cwd.is_dir() and (cwd / "AGENTS.md").is_file():
        return cwd.resolve()
    raise SystemExit(f"Unknown tool: {value}")


def walk_source(tool: Path) -> tuple[dict[str, int], int]:
    langs: dict[str, int] = {}
    total = 0
    for path in tool.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(tool).parts):
            continue
        lang = SOURCE_EXTS.get(path.suffix)
        if not lang:
            continue
        langs[lang] = langs.get(lang, 0) + 1
        total += 1
    return langs, total


def git(tool: Path, *args: str) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(tool), *args],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def count_globs(tool: Path, patterns: list[str]) -> int:
    seen: set[Path] = set()
    for pattern in patterns:
        for match in tool.glob(pattern):
            if match.is_file():
                seen.add(match)
    return len(seen)


def evidence_ok(tool: Path, gate: dict) -> tuple[bool, list[str]]:
    if gate.get("check") == "worktrees":
        trees = [line.split()[0] for line in git(tool, "worktree", "list").splitlines() if line.strip()]
        return len(trees) > 1, trees
    patterns = gate.get("evidence")
    if not patterns:
        return False, []
    if isinstance(patterns, str):
        patterns = [patterns]
    found = sorted({
        str(match.relative_to(tool))
        for pattern in patterns
        for match in tool.glob(pattern)
        if match.is_file() or match.is_dir()
    })
    if not found:
        return False, []
    contains = gate.get("contains")
    if contains:
        for rel in found:
            path = tool / rel
            if not path.is_file():
                continue
            try:
                if contains in path.read_text(encoding="utf-8", errors="ignore"):
                    return True, found
            except OSError:
                continue
        return False, found
    return True, found


def guess_tier(tool: Path) -> tuple[str, list[str], dict[str, int], int]:
    langs, total = walk_source(tool)
    reasons: list[str] = []
    if len(langs) >= 2:
        reasons.append(f"{len(langs)} source languages: {', '.join(sorted(langs))}")
    for marker in PLATFORM_MARKERS:
        if (tool / marker).exists():
            reasons.append(f"has {marker}")
    plans = count_globs(tool, ["docs/superpowers/plans/*.md"])
    specs = count_globs(tool, ["docs/superpowers/specs/*.md", "docs/superpowers/specs/**/*.md"])
    if plans or specs:
        reasons.append("has a design and plan trail")
    if total > 60:
        reasons.append(f"{total} source files")
    if not langs:
        return "undecided", ["no source code yet"], langs, total
    if reasons:
        return "platform", reasons, langs, total
    return "small_tool", [f"one language ({next(iter(langs))}), no second front end"], langs, total


def phase_report(tool: Path, phase_id: str, phase: dict) -> dict:
    gates = phase.get("gates", []) or []
    passed, missing, manual, pending_manual = [], [], [], []
    for gate in gates:
        if gate.get("optional"):
            continue
        if gate.get("kind") == "manual":
            manual.append(gate["id"])
            has_evidence, found = evidence_ok(tool, gate) if gate.get("evidence") or gate.get("check") else (None, [])
            pending_manual.append({
                "id": gate["id"],
                "label": gate.get("label", gate["id"]),
                "action": gate.get("action", ""),
                "skill": gate.get("skill"),
                "kind": "manual",
                "evidence_present": has_evidence,
                "evidence_found": found,
            })
            continue
        ok, found = evidence_ok(tool, gate)
        if ok:
            passed.append({"id": gate["id"], "evidence": found})
        else:
            missing.append({
                "id": gate["id"],
                "label": gate.get("label", gate["id"]),
                "action": gate.get("action", ""),
                "skill": gate.get("skill"),
                "kind": "artifact",
                "evidence": gate.get("evidence"),
            })
    total = len(passed) + len(missing)
    if total == 0:
        state = "manual_only"
    elif not passed:
        state = "not_started"
    elif missing:
        state = "in_progress"
    else:
        state = "artifacts_complete"
    return {
        "id": phase_id,
        "label": phase.get("label", phase_id),
        "rule": phase.get("rule"),
        "skill": phase.get("skill"),
        "state": state,
        "artifact_gates": {"passed": len(passed), "total": total, "passed_ids": [p["id"] for p in passed]},
        "manual_gates_pending": manual,
        "missing": missing,
        "manual": pending_manual,
    }


def build_report(root: Path, tool: Path) -> dict:
    rules = load_rules(root)
    tier, reasons, langs, total = guess_tier(tool)
    track_key = tier if tier in rules.get("tracks", {}) else "platform"
    track = rules["tracks"][track_key]
    sequence = track.get("sequence", [])

    phases = [phase_report(tool, pid, rules["phases"][pid]) for pid in sequence if pid in rules.get("phases", {})]

    current = next((p for p in phases if p["state"] != "artifacts_complete"), None)
    next_actions = []
    if current:
        next_actions.extend(current["missing"])
        next_actions.extend(current["manual"])
    if not next_actions and phases:
        next_actions.append({
            "id": "done",
            "label": "Every artifact gate passes. Ask the user what to do next.",
            "action": "Confirm each manual gate with the user, then pick the next piece of work.",
            "skill": None,
            "kind": "manual",
        })

    worktrees = [line.split()[0] for line in git(tool, "worktree", "list").splitlines() if line.strip()]

    return {
        "tool": tool.name,
        "path": str(tool),
        "workshop": str(root),
        "tier_guess": tier,
        "tier_reasons": reasons,
        "track": track_key,
        "current_phase": current["id"] if current else "done",
        "phases": phases,
        "next_actions": next_actions,
        "signals": {
            "languages": langs,
            "source_files": total,
            "specs": count_globs(tool, ["docs/superpowers/specs/*.md", "docs/superpowers/specs/**/*.md"]),
            "plans": count_globs(tool, ["docs/superpowers/plans/*.md"]),
            "spikes": count_globs(tool, ["docs/spikes/*.md"]),
            "adrs": count_globs(tool, ["docs/adr/*.md"]),
            "has_agents_md": (tool / "AGENTS.md").is_file(),
            "has_glossary": (tool / "GLOSSARY.md").is_file() or (tool / "docs" / "GLOSSARY.md").is_file(),
            "has_readme": (tool / "README.md").is_file(),
            "worktrees": worktrees,
            "last_commit": git(tool, "log", "-1", "--format=%cs"),
        },
    }


def render_text(report: dict) -> str:
    lines = [
        f"{report['tool']}  ({report['path']})",
        f"tier: {report['tier_guess']}  [{'; '.join(report['tier_reasons'])}]",
        f"phase: {report['current_phase']}",
        "",
    ]
    for phase in report["phases"]:
        mark = "x" if phase["state"] == "artifacts_complete" else " "
        gates = phase["artifact_gates"]
        manual = len(phase["manual"])
        note = f", {manual} to confirm" if manual else ""
        lines.append(f"[{mark}] {phase['label']}  artifacts {gates['passed']}/{gates['total']}{note}")
        for item in phase["missing"]:
            lines.append(f"      missing: {item['label']}")
        for item in phase["manual"]:
            suffix = ""
            if item.get("evidence_present") is True:
                suffix = "  [file present]"
            elif item.get("evidence_present") is False:
                suffix = "  [file missing]"
            lines.append(f"      confirm: {item['label']}{suffix}")
    if report["next_actions"]:
        lines.append("")
        lines.append("next:")
        for action in report["next_actions"]:
            skill = f"  ({action['skill']})" if action.get("skill") else ""
            lines.append(f"  - {action['action'] or action['label']}{skill}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read the phase state of a workshop tool.")
    parser.add_argument("tool", nargs="?", help="Tool name or path. Defaults to the current directory.")
    parser.add_argument("--list", action="store_true", help="List workshop tools and their tier and phase.")
    parser.add_argument("--text", action="store_true", help="Print a human summary instead of JSON.")
    parser.add_argument("--root", help="Workshop root. Defaults to walking up from here.")
    args = parser.parse_args(argv)

    cwd = Path.cwd()
    root = Path(args.root).expanduser().resolve() if args.root else find_workshop_root(cwd)
    if not root:
        sys.stderr.write("Cannot find the workshop root (docs/rules/gates.yaml).\n")
        return 2

    if args.list:
        items = []
        for tool in iter_tools(root):
            tier, reasons, _, _ = guess_tier(tool["path"])
            items.append({
                "name": tool["name"],
                "space": tool["space"],
                "path": str(tool["path"]),
                "tier_guess": tier,
                "tier_reasons": reasons,
            })
        if args.text:
            for item in items:
                print(f"{item['space']}/{item['name']}  tier={item['tier_guess']}")
        else:
            print(json.dumps(items, indent=2))
        return 0

    tool = resolve_tool(root, args.tool or ".", cwd)
    report = build_report(root, tool)
    print(render_text(report) if args.text else json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
