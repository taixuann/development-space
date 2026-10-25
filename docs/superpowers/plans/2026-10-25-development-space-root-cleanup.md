# Development Space root cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Requester:** forge
**Space:** ~/development-space
**Scope:** Remove SOUL.md, USER.md, IDEA.md, RELEASE_GATE.md, and memories/ (README.md, decisions.md, learnings.md) from the repository root. Fold still-needed rules into AGENTS.md. Update ARCHITECTURE.md so it no longer references removed files. Leave LICENSE, dot-directories, docs/, tools/, scripts/, tests/, automation/, worktree/, worktrees/ and any existing uncommitted work untouched.

**Checks:**
- `ls ~/development-space/*.md` lists only AGENTS.md, README.md, ARCHITECTURE.md.
- `test ! -e ~/development-space/memories`
- `grep -rnE 'SOUL\.md|USER\.md|IDEA\.md|RELEASE_GATE|memories/' ~/development-space/AGENTS.md ~/development-space/README.md ~/development-space/ARCHITECTURE.md` returns no matches.
- Every relative link in AGENTS.md, README.md, ARCHITECTURE.md resolves (run `python3 automation/check_docs.py` and note CORE_DOCS staleness as follow-up if it fails).

**Report:** merge commit, check results, and what was folded in or dropped.

**Goal:** Keep only AGENTS.md, README.md, and ARCHITECTURE.md as Space documents at the repository root; profile/identity now lives in ~/.agents/docs/profiles/forge/ and ~/.hermes/profiles/forge/SOUL.md, and memory is default Hermes memory.

**Architecture:** Edit AGENTS.md to absorb USER.md's language/comment conventions, interaction principles, and RELEASE_GATE.md's release checks; edit ARCHITECTURE.md to drop directory-layout and responsibility references to removed files; delete the approved files with `git rm`. No code changes.

**Tech Stack:** Git, Markdown.

## Global Constraints

- Do not modify LICENSE, dot-directories, docs/, tools/, scripts/, tests/, automation/, worktree/, worktrees/.
- Do not touch existing uncommitted work (docs/superpowers/plans/2026-10-25-remote-self-contained-installer.md, docs/superpowers/specs/).
- Commit only the files in scope plus this plan file.
- Preserve all technical names, flags, and file paths verbatim.

## Task 1: Fold USER.md rules into AGENTS.md

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Add a Communication section to AGENTS.md** (after `## Scope`, before `## Agent skills` or at end of Methodology). Content:
  - Language: Use Vietnamese when Tai uses Vietnamese; preserve technical names, flags, and file paths. Use simple English for code comments, commit messages, and maintained technical documents unless Tai asks otherwise.
  - Interaction: lead with result/recommendation/diff; keep explanations concise; distinguish confirmed evidence from assumptions; explore and verify before changes when brainstorming; implement cleanly and verify when a bounded change is approved; ask for a decision only when missing information alters scope, security, or data integrity; never force-push, rewrite shared history, or delete code/tests without explicit approval.
- [ ] **Step 2: Commit checkpoint** (will be part of final commit).

## Task 2: Fold RELEASE_GATE.md checks into AGENTS.md

**Files:**
- Modify: `AGENTS.md`

- [ ] **Step 1: Add a Release gate subsection under `## Safety`** listing:
  - `git diff --cached --check` clean.
  - Secret scan over tracked set (sk-, ghp_, gho_, API_KEY, TOKEN, PASSWORD, SECRET, bearer/JWT): no credential values.
  - Filename scan (.env, databases, keys, private, secret): none tracked.
  - Mojibake scan clean.
  - `git status`: branch in sync with origin before tagging.
- [ ] **Step 2: Fold git sub-repository isolation learning** into `## Repository boundaries`: note that root ignores `tools/` and `worktrees/` so nested tool repositories stay decoupled.

## Task 3: Update ARCHITECTURE.md references

**Files:**
- Modify: `ARCHITECTURE.md`

- [ ] **Step 1: Edit responsibility item 3** from `Engineering discipline, verification, and test-driven development (`RELEASE_GATE.md`).` to `Engineering discipline, verification, and test-driven development (AGENTS.md).`
- [ ] **Step 2: Remove directory-layout lines** for `USER.md`, `SOUL.md`, and `RELEASE_GATE.md`.
- [ ] **Step 3: Verify no relative link in ARCHITECTURE.md is broken.**

## Task 4: Delete approved files

**Files:**
- Delete: `SOUL.md`, `USER.md`, `IDEA.md`, `RELEASE_GATE.md`, `memories/README.md`, `memories/decisions.md`, `memories/learnings.md`
- Remove empty dir: `memories/`

- [ ] **Step 1: `git rm` each file and `rmdir memories`.**
- [ ] **Step 2: Verify `memories/` no longer exists.**

## Task 5: Verify acceptance checks

- [ ] **Step 1: Run `ls *.md` -> only AGENTS.md, README.md, ARCHITECTURE.md.**
- [ ] **Step 2: Run `test ! -e memories`.**
- [ ] **Step 3: Run grep for stale references on the three files -> no matches.**
- [ ] **Step 4: Run `python3 automation/check_docs.py` and record output (expect CORE_DOCS staleness follow-up).**

## Task 6: Commit

- [ ] **Step 1: `git add AGENTS.md ARCHITECTURE.md docs/superpowers/plans/2026-10-25-development-space-root-cleanup.md` plus deletions.**
- [ ] **Step 2: Commit with message `chore: remove root Space identity/memory docs; fold rules into AGENTS.md`.**
- [ ] **Step 3: Push to origin master.**

## Review Focus

- Relative links in the three remaining files resolve.
- No stale references to removed files in the three files.
- Existing uncommitted work (installer plan, specs) untouched.
- Plan file itself not accidentally deleting other content.

## Folded vs dropped

Folded into AGENTS.md:
- USER.md language and comment conventions.
- USER.md interaction principles.
- RELEASE_GATE.md release checks.
- learnings.md git sub-repository isolation note.

Dropped (stale or now elsewhere):
- SOUL.md identity (now in ~/.hermes/profiles/forge/SOUL.md).
- IDEA.md product idea.
- memories/decisions.md (duplicated in AGENTS.md/ARCHITECTURE.md).
- learnings.md Hindsight provider quirk.
- RELEASE_GATE.md intentional-exceptions notes.
- memories/README.md structure doc.
