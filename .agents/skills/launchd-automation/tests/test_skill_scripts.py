"""Tests for the launchd-automation skill scripts.

Standard library only. No launchctl mutation and no job execution: every test
that touches launchctl uses a fake on PATH, and static verification must leave
the program's marker file absent.

Run from the skill directory:
    /opt/homebrew/bin/python3 -m unittest discover -s tests -v
"""

from __future__ import annotations

import json
import os
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
SCAFFOLD = SKILL_DIR / "scripts" / "scaffold_automation.py"
VERIFY = SKILL_DIR / "scripts" / "verify_automation.py"
PYTHON = sys.executable


class SkillScriptTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory(prefix="launchd-skill-")
        self.root = Path(self._tmp.name).resolve()
        self.report_root = self.root / "reports" / "job"
        self.marker = self.root / "program-ran.marker"
        self.label = "com.example.skilltest"

        self.program = self.root / "job-program"
        self.program.write_text(
            "#!/bin/sh\n"
            f'echo ran >> "{self.marker}"\n'
            "exit 0\n"
        )
        self.program.chmod(0o755)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # ---------------------------------------------------------------- helpers

    def run_script(self, script: Path, *args: str, env: dict | None = None):
        return subprocess.run(
            [PYTHON, str(script), *args],
            capture_output=True,
            text=True,
            env=env,
        )

    def scaffold(
        self,
        layout: str = "space",
        target: Path | None = None,
        report_root: str | None = None,
        extra: tuple[str, ...] = (),
    ):
        if target is None:
            target = self.root / "space" / "automation" / "job"
        return self.run_script(
            SCAFFOLD,
            "--layout", layout,
            "--target-dir", str(target),
            "--report-root", report_root if report_root is not None else str(self.report_root),
            "--label", self.label,
            "--title", "Skill test job",
            "--description", "Fixture job for the skill tests",
            "--schedule", "daily:04:30",
            "--program", str(self.program),
            *extra,
        )

    def verify(self, target: Path, *extra: str, env: dict | None = None):
        return self.run_script(
            VERIFY, str(target), "--static", "--skip-launchctl", *extra, env=env
        )

    def read_plist(self, target: Path) -> dict:
        with (target / "launchd.plist").open("rb") as handle:
            return plistlib.load(handle)

    def write_plist(self, target: Path, data: dict) -> None:
        with (target / "launchd.plist").open("wb") as handle:
            plistlib.dump(data, handle)

    def make_fake_launchctl(self, kickstart_result: dict | None = None) -> tuple[Path, Path]:
        """Install a fake launchctl that logs argv and never touches the system."""
        bin_dir = self.root / "fakebin"
        bin_dir.mkdir(exist_ok=True)
        log = self.root / "launchctl-calls.log"
        result_file = self.report_root / "latest-result.json"
        write_result = ""
        if kickstart_result is not None:
            write_result = (
                f'mkdir -p "{result_file.parent}"\n'
                f'printf "%s" \'{json.dumps(kickstart_result)}\' > "{result_file}"\n'
            )
        fake = bin_dir / "launchctl"
        fake.write_text(
            "#!/bin/sh\n"
            f'echo "$@" >> "{log}"\n'
            'case "$1" in\n'
            "  print) exit 1 ;;\n"
            "  kickstart)\n"
            f"{write_result}"
            "    exit 0 ;;\n"
            "esac\n"
            "exit 0\n"
        )
        fake.chmod(0o755)
        return bin_dir, log

    def env_with(self, bin_dir: Path) -> dict:
        env = os.environ.copy()
        env["PATH"] = f"{bin_dir}:{env.get('PATH', '/usr/bin:/bin')}"
        return env

    # ------------------------------------------------------------------ layout

    def test_space_layout_emits_files_and_external_report_root(self) -> None:
        target = self.root / "space" / "automation" / "job"
        result = self.scaffold("space", target=target)
        self.assertEqual(result.returncode, 0, result.stderr)

        emitted = sorted(p.name for p in target.iterdir())
        self.assertEqual(emitted, ["AGENTS.md", "README.md", "launchd.plist"])
        self.assertFalse((target / "logs").exists(), "source tree must not hold logs/")
        self.assertFalse((target / "scripts").exists(), "direct form needs no wrapper")

        plist = self.read_plist(target)
        self.assertEqual(plist["Label"], self.label)
        self.assertEqual(plist["ProgramArguments"], [str(self.program)])
        self.assertEqual(
            plist["StandardOutPath"], str(self.report_root / "stdout.log")
        )
        self.assertEqual(
            plist["StandardErrorPath"], str(self.report_root / "stderr.log")
        )
        self.assertNotIn("WorkingDirectory", plist)
        self.assertNotIn("RunAtLoad", plist)

        readme = (target / "README.md").read_text()
        agents = (target / "AGENTS.md").read_text()
        self.assertIn(str(self.report_root), readme)
        self.assertIn(str(self.report_root), agents)
        self.assertIn("automation/job", readme)

    def test_tool_layout_uses_tool_branch_and_optional_wrapper(self) -> None:
        repo = self.root / "tool-repo"
        (repo / ".git").mkdir(parents=True)
        target = repo / "automation" / "refresh"
        result = self.scaffold(
            "tool",
            target=target,
            extra=("--wrapper", "--request-id", "008", "--command", " --once"),
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        emitted = sorted(p.name for p in target.iterdir())
        self.assertEqual(emitted, ["AGENTS.md", "README.md", "launchd.plist", "scripts"])
        runner = target / "scripts" / "run.sh"
        self.assertTrue(runner.is_file())
        self.assertTrue(os.access(runner, os.X_OK))
        self.assertFalse((target / "logs").exists())

        plist = self.read_plist(target)
        self.assertEqual(plist["ProgramArguments"], ["/bin/bash", str(runner)])
        self.assertEqual(plist["StandardOutPath"], str(self.report_root / "stdout.log"))

        readme = (target / "README.md").read_text()
        agents = (target / "AGENTS.md").read_text()
        self.assertIn("admin/tool-repo_008", readme)
        self.assertIn("admin/tool-repo_008", agents)
        self.assertIn(str(self.report_root), readme)
        self.assertIn(str(self.report_root), agents)

        runner_text = runner.read_text()
        for forbidden in (".env", "nvm.sh", "mise activate", "pyenv", "source "):
            self.assertNotIn(forbidden, runner_text)
        self.assertNotIn(str(target / "logs"), runner_text)

    def test_tool_layout_requires_git_repository(self) -> None:
        target = self.root / "not-a-repo" / "automation" / "job"
        result = self.scaffold("tool", target=target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a Git repository", result.stderr)
        self.assertFalse(target.exists())

    def test_space_layout_refuses_foreign_git_repository(self) -> None:
        repo = self.root / "other-repo"
        (repo / ".git").mkdir(parents=True)
        target = repo / "automation" / "job"
        result = self.scaffold("space", target=target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inside the Git repository", result.stderr)

    def test_refuses_to_overwrite_existing_scaffold(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)
        again = self.scaffold("space", target=target)
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("refusing to overwrite", again.stderr)
        self.assertIn("README.md", again.stderr)

    # ------------------------------------------------------------- report root

    def test_relative_report_root_is_refused(self) -> None:
        target = self.root / "space" / "automation" / "job"
        result = self.scaffold("space", target=target, report_root="logs")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be absolute", result.stderr)
        self.assertFalse(target.exists())

    def test_report_root_inside_source_is_refused(self) -> None:
        target = self.root / "space" / "automation" / "job"
        result = self.scaffold("space", target=target, report_root=str(target / "logs"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("inside the source folder", result.stderr)

    # ----------------------------------------------------------- static checks

    def test_static_verification_passes_and_label_comes_from_contents(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)

        renamed = target / "not-the-label.plist"
        (target / "launchd.plist").rename(renamed)
        result = self.verify(target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"PASS plist-label label={self.label} source=not-the-label.plist", result.stdout)
        self.assertIn("RESULT PASS", result.stdout)
        self.assertIn("SUMMARY mode=static checks=", result.stdout)

    def test_static_verification_fails_when_required_file_is_missing(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)
        (target / "AGENTS.md").unlink()

        result = self.verify(target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL file-agents", result.stdout)
        self.assertIn("RESULT FAIL", result.stdout)

    def test_static_verification_fails_on_relative_log_path(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)
        plist = self.read_plist(target)
        plist["StandardOutPath"] = "logs/stdout.log"
        self.write_plist(target, plist)

        result = self.verify(target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL log-paths", result.stdout)
        self.assertIn("FAIL report-outside-source", result.stdout)

    def test_static_verification_fails_on_missing_log_directory(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)
        plist = self.read_plist(target)
        plist["StandardErrorPath"] = str(self.report_root / "absent" / "stderr.log")
        self.write_plist(target, plist)

        result = self.verify(target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL log-paths", result.stdout)

    def test_static_verification_fails_on_missing_program(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)
        plist = self.read_plist(target)
        plist["ProgramArguments"] = [str(self.root / "gone-binary")]
        self.write_plist(target, plist)

        result = self.verify(target)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL program-exists", result.stdout)

    def test_static_verification_fails_on_report_root_mismatch(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)

        result = self.verify(target, "--report-root", str(self.root / "somewhere-else"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL report-root-match", result.stdout)

    def test_installed_copy_comparison_and_duplicate_label(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)

        home = self.root / "home"
        agents = home / "Library" / "LaunchAgents"
        agents.mkdir(parents=True)
        installed = agents / f"{self.label}.plist"
        installed.write_bytes((target / "launchd.plist").read_bytes())
        env = dict(os.environ, HOME=str(home))

        match = self.run_script(VERIFY, str(target), "--static", "--skip-launchctl",
                                "--compare-installed", env=env)
        self.assertEqual(match.returncode, 0, match.stdout + match.stderr)
        self.assertIn("PASS installed-match", match.stdout)

        installed.write_text(installed.read_text().replace("<string>", "<string> ", 1))
        mismatch = self.run_script(VERIFY, str(target), "--static", "--skip-launchctl",
                                   "--compare-installed", env=env)
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertIn("FAIL installed-match", mismatch.stdout)

        duplicate = agents / "another-name.plist"
        duplicate.write_bytes((target / "launchd.plist").read_bytes())
        installed.write_bytes((target / "launchd.plist").read_bytes())
        duplicated = self.run_script(VERIFY, str(target), "--static", "--skip-launchctl", env=env)
        self.assertNotEqual(duplicated.returncode, 0)
        self.assertIn("FAIL duplicate-label", duplicated.stdout)

    def test_static_never_runs_program_or_mutates_launchd(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)
        bin_dir, log = self.make_fake_launchctl()
        result = self.run_script(
            VERIFY, str(target), "--static", "--report-root", str(self.report_root),
            env=self.env_with(bin_dir),
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse(self.marker.exists(), "static verification executed the program")
        calls = log.read_text().splitlines() if log.exists() else []
        self.assertTrue(calls, "the read-only launchctl check should still run")
        for call in calls:
            self.assertTrue(
                call.startswith("print "),
                f"static mode issued a mutating launchctl call: {call}",
            )

    # --------------------------------------------------------------- live mode

    def test_live_requires_static_pass(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)
        (target / "README.md").unlink()
        bin_dir, log = self.make_fake_launchctl()

        result = self.run_script(
            VERIFY, str(target), "--live", "--timeout", "1", "--poll-interval", "0.05",
            env=self.env_with(bin_dir),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL live-precondition", result.stdout)
        self.assertFalse(log.exists() and "kickstart" in log.read_text())

    def test_live_fails_without_a_terminal_outcome(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)
        bin_dir, _ = self.make_fake_launchctl()

        result = self.run_script(
            VERIFY, str(target), "--live", "--timeout", "1", "--poll-interval", "0.05",
            env=self.env_with(bin_dir),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PASS live-dispatch", result.stdout)
        self.assertIn("FAIL live-terminal", result.stdout)
        self.assertIn("RESULT FAIL", result.stdout)

    def test_live_passes_on_a_terminal_result_file(self) -> None:
        target = self.root / "space" / "automation" / "job"
        self.assertEqual(self.scaffold("space", target=target).returncode, 0)
        bin_dir, _ = self.make_fake_launchctl(
            kickstart_result={
                "run_id": "2026-10-23T00:00:00Z-test",
                "outcome": "success",
                "exit_code": 0,
            }
        )

        result = self.run_script(
            VERIFY, str(target), "--live", "--timeout", "5", "--poll-interval", "0.05",
            env=self.env_with(bin_dir),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS live-terminal outcome=success", result.stdout)
        self.assertIn("PASS live-outcome outcome=success", result.stdout)


if __name__ == "__main__":
    unittest.main()
