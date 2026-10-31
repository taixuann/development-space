---
name: workshop-driver
description: Use this skill first whenever a user wants to know where a tool or project stands, or what to do about it next. Typical asks: continue or resume a tool, "what's next", "which phase am I in", "what's missing", "is X ready to build yet", "start a new tool/app", or a vague idea where the right track is unclear. Applies to any project status, progress or readiness question, even when no tool is named or when it's written in another language (e.g. Vietnamese). It checks the workshop's phase gates on disk and recommends the next step, before any design, planning or coding. Skip for concrete code edits, running tests or builds, reviewing diffs or PRs, and explaining individual files.
compatibility: Python 3.10+ with PyYAML. Read-only; needs git for worktree and commit signals.
---

# Workshop bootstrap

The workshop has three phases and a short track for small tools. The rules live in `docs/rules/`, and the gates are machine-readable in `docs/rules/gates.yaml`. Nothing enforces them on its own: a session can jump straight to code, skip the design doc, and still look busy.

This skill closes that gap. It reads the real state from disk, names the gates that are still open, and hands the next step to the right skill.

## Step 0: Ask which tool

Never guess from the current directory alone. A session often starts at the workshop root, and more than one tool is in flight.

Run:

```bash
.agents/skills/workshop-driver/scripts/phase_status.py --list --text
```

Show the list to the user and ask which tool they are working on. If the current directory is inside exactly one tool, say which one you detected and ask them to confirm in one line rather than a full question.

If the answer is "a new tool", skip to Step 1 and use the tier question as the first decision.

## Step 1: Confirm the tier

Read [`docs/rules/tiers.md`](../../../docs/rules/tiers.md). The script reports a `tier_guess` with reasons. Repeat the guess and its reason, and ask only when the guess is `undecided` or when the answer would change the track.

A small tool takes the short track. A platform or app takes Phase 1, then 2, then 3. Getting this wrong wastes either a design phase or a whole rewrite, so a one-line confirmation is cheap.

## Step 2: Read the state

```bash
.agents/skills/workshop-driver/scripts/phase_status.py <tool>
```

The script is read-only. It reports, per phase, the artifact gates that pass, the artifact gates that are missing, and the manual gates that only a person can confirm.

Trust the script for what exists, not for what it means. A design doc can exist and still be unapproved; a test folder can exist and still be empty. Say which gates you are inferring and which the script proved.

If the tool already has code and Phase 1 is not complete, run `graphify` and `xerj` on it before reporting, so the vision is grounded in the code. This is the optional pre-step in [`docs/rules/phase-1-vision.md`](../../../docs/rules/phase-1-vision.md); it is a suggestion, not a gate, and it never blocks a tool that has no code yet.

## Step 3: Report in this shape

```
Tool: <name> (<space>)      Tier: <small tool | platform>
Phase: <phase label>

Artifacts: <passed>/<total>
Missing:
  - <gate label> -> <skill>
Confirm with you:
  - <gate label> (file present | file missing | no artifact expected)

Next:
  1. <imperative action> - <skill that does it>
  2. ...
```

Keep it short enough to read in one screen. One or two next actions, not the whole backlog. The script may return six missing gates; pick the two that unblock the others and say why the rest wait.

## Step 4: Propose the skill, then wait

The workshop rule is propose-then-run. Name the skill that clears the gate, say in one sentence why it fits, and stop. Run it only after the user agrees.

### Discovering the right skill

When the gate's suggested skill does not fit, or when you are unsure which skill applies, do not guess. Inspect the whole skill list before proposing:

1. List `.agents/skills/` and `.claude/skills/`, plus the tool's own `.claude/skills/` if it has one.
2. Match the need against the trigger table in [`docs/rules/phase-1-vision.md`](../../../docs/rules/phase-1-vision.md). That table is the workshop's map from situation to skill.
3. If no listed skill matches, propose `agent-skill-stack`: it searches local skills, registries, GitHub and OpenCLI and assembles the smallest compatible set. Propose it, do not install it without consent.
4. Never propose a skill you have not seen on disk. A made-up name sends the user chasing nothing. If a skill is only in `.claude/skills/` and not in `.agents/skills/`, say so and offer to mirror it.

Before proposing, check the skill exists: look in `.agents/skills/`, `.claude/skills/`, or the tool's own `.claude/skills/`. Never propose a skill you have not seen on disk - a made-up name sends the user chasing nothing.

### Runbook

After proposing, check `docs/driver/runbook.md` for a matching section (new tool, inspect existing code, run a spike, write an ADR, write a design doc, write a plan, release). If one exists, name the section so the user can follow the checklist. The runbook is a procedure, not a status: it never overrides `gates.yaml`.

The proposal table in [`docs/rules/phase-1-vision.md`](../../../docs/rules/phase-1-vision.md) lists the common triggers. Use it, then apply judgement.

## Step 5: Record, only when asked

The tool's `AGENTS.md` is the record for durable decisions. After the user makes a call, offer to add it under `Decisions` with the date and the reason. Add open questions under `Open questions`.

Do not write anything without an explicit yes. Do not create a status file: phase state comes from artifacts, and a second hand-maintained document drifts.

## Boundaries

- Read-only by default. No code edits, no builds, no test runs, no git writes.
- Do not declare a phase done. Report artifact gates as passed and manual gates as unconfirmed, and let the user close them.
- Do not smooth over a missing gate because the code looks finished. A missing ADR is still missing.
- If the script fails, say so and fall back to reading the rule files by hand. Do not invent state.

## Why this exists

`docs/AGENTS.md` is a rulebook. Rules that nobody reads at the moment of action do not change behaviour. This skill puts the rulebook in front of the agent at the only moment it matters: the start of work, when the next step is still cheap to choose correctly.
