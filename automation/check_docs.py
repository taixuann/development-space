#!/usr/bin/env python3
"""
Documentation Integrity Checker for development-space.
Verifies file existence, internal markdown links, skill alignment with index.yaml,
and scans for stale references or drift.
"""

import sys
import re
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

CORE_DOCS = [
    "ARCHITECTURE.md",
    "SOUL.md",
    "USER.md",
    "AGENTS.md",
    "README.md",
    "RELEASE_GATE.md",
    "docs/standard-tool-layout.md",
    "docs/tool-lifecycle.md",
    "docs/small-tool-contract.md",
    "docs/doc-maintenance-lifecycle.md",
    ".agents/skills/index.yaml",
    ".agents/skills/README.md",
    ".agents/skills/AGENTS.md",
]

STALE_PATTERNS = [
    (r"taixuann/agent-development", "Old repository name 'agent-development' found"),
]

def check_core_files_exist():
    errors = []
    for doc in CORE_DOCS:
        p = REPO_ROOT / doc
        if not p.exists():
            errors.append(f"Missing core document: {doc}")
    return errors

def check_skills_index_alignment():
    errors = []
    index_file = REPO_ROOT / ".agents/skills/index.yaml"
    if not index_file.exists():
        return ["Missing .agents/skills/index.yaml"]

    try:
        data = yaml.safe_load(index_file.read_text(encoding="utf-8"))
    except Exception as e:
        return [f"Invalid YAML in index.yaml: {e}"]

    mapping = data.get("tool_layer_mapping", {})
    for layer, info in mapping.items():
        skills = info.get("specialist_skills", [])
        for skill in skills:
            name = skill.get("name")
            if not name or name.startswith("superpowers:"):
                continue
            skill_dir = REPO_ROOT / ".agents/skills" / name
            if not skill_dir.exists():
                errors.append(f"Skill '{name}' registered in index.yaml under layer '{layer}' does not exist on disk at {skill_dir}")
            else:
                skill_md = skill_dir / "SKILL.md"
                if not skill_md.exists():
                    errors.append(f"Skill '{name}' is missing SKILL.md")
    return errors

def check_stale_patterns():
    errors = []
    for doc in CORE_DOCS:
        p = REPO_ROOT / doc
        if not p.exists() or p.suffix not in [".md", ".yaml"]:
            continue
        content = p.read_text(encoding="utf-8")
        for pattern, msg in STALE_PATTERNS:
            if re.search(pattern, content):
                errors.append(f"File {doc}: {msg}")
    return errors

def check_markdown_links():
    errors = []
    link_regex = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
    for doc in CORE_DOCS:
        p = REPO_ROOT / doc
        if not p.exists() or p.suffix != ".md":
            continue
        content = p.read_text(encoding="utf-8")
        for match in link_regex.finditer(content):
            target = match.group(2)
            if target.startswith("http://") or target.startswith("https://") or target.startswith("#") or target.startswith("mailto:"):
                continue
            # Handle local anchor inside file
            clean_target = target.split("#")[0]
            if not clean_target:
                continue
            target_path = (p.parent / clean_target).resolve()
            if not target_path.exists():
                errors.append(f"Broken relative link in {doc}: [{match.group(1)}]({target}) -> {target_path} not found")
    return errors

def main():
    print(f"=== Running Documentation Integrity Check for {REPO_ROOT.name} ===")
    all_errors = []

    print("[1/4] Checking core document existence...")
    all_errors.extend(check_core_files_exist())

    print("[2/4] Checking .agents/skills/index.yaml alignment...")
    all_errors.extend(check_skills_index_alignment())

    print("[3/4] Checking for stale repository references...")
    all_errors.extend(check_stale_patterns())

    print("[4/4] Verifying internal markdown relative links...")
    all_errors.extend(check_markdown_links())

    if all_errors:
        print("\n❌ Integrity check FAILED with issues:")
        for err in all_errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("\n✅ All core documents, links, and skill mappings are 100% synchronized and valid.")
        sys.exit(0)

if __name__ == "__main__":
    main()
