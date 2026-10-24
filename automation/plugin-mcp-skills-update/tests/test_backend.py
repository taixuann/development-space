"""Unit tests for automation/plugin-mcp-skills-update backend modules."""
from __future__ import annotations

import datetime
import json
import os
import shutil
import sys
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch

# Add backend directory to sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(os.path.dirname(TEST_DIR), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from mcp_syncer import check_and_sync_mcp
from plugins_checker import check_superpowers_plugin
from skills_updater import update_skills
from main import run_maintenance, cleanup_old_runs

WORKSPACE_ROOT = "/Users/tai/development-space"


class TestBackend(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_maintenance_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_skills_updater(self):
        res = update_skills(WORKSPACE_ROOT)
        self.assertIn("success", res)
        self.assertIn("exit_code", res)
        self.assertTrue(res["success"], f"Skills update failed: {res['output']}")

    def test_plugins_checker(self):
        res = check_superpowers_plugin()
        self.assertTrue(res["success"], f"Plugins check failed: {res.get('error')}")
        self.assertIsNotNone(res["head_sha"])
        self.assertGreater(len(res["head_sha"]), 8)

    def test_mcp_syncer(self):
        res = check_and_sync_mcp(WORKSPACE_ROOT)
        self.assertTrue(res["success"], f"MCP sync failed: {res.get('error')}")
        self.assertTrue(res["agents_mcp_ok"])
        self.assertTrue(res["opencode_mcp_ok"])
        self.assertTrue(res["codex_mcp_ok"])

    def test_cleanup_old_runs(self):
        runs_dir = os.path.join(self.temp_dir, "runs")
        os.makedirs(runs_dir, exist_ok=True)
        now = time.time()
        old_time = now - (35 * 86400)  # 35 days ago
        recent_time = now - (5 * 86400)  # 5 days ago

        old_file = os.path.join(runs_dir, "run_old.json")
        recent_file = os.path.join(runs_dir, "run_recent.json")
        latest_file = os.path.join(self.temp_dir, "latest-result.json")

        with open(old_file, "w") as f:
            f.write("{}")
        os.utime(old_file, (old_time, old_time))

        with open(recent_file, "w") as f:
            f.write("{}")
        os.utime(recent_file, (recent_time, recent_time))

        with open(latest_file, "w") as f:
            f.write("{}")
        os.utime(latest_file, (old_time, old_time))  # even if old, must be preserved

        deleted_count = cleanup_old_runs(self.temp_dir, max_age_days=30)
        self.assertEqual(deleted_count, 1)
        self.assertFalse(os.path.exists(old_file))
        self.assertTrue(os.path.exists(recent_file))
        self.assertTrue(os.path.exists(latest_file))

    @patch("main.submit_or_update_ticket")
    def test_run_maintenance_failure_escalation(self, mock_submit):
        mock_submit.return_value = {"success": True, "action": "created", "page_id": "test-page"}
        with patch("main.update_skills") as mock_skills:
            mock_skills.return_value = {
                "success": False,
                "exit_code": 1,
                "output": "404 Not Found: skill remote repo deleted",
                "target_dir": "/mock",
            }
            exit_code = run_maintenance(
                workspace_root=WORKSPACE_ROOT,
                report_root=self.temp_dir,
                dry_run=False,
            )
            self.assertEqual(exit_code, 1)
            mock_submit.assert_called_once()
            call_kwargs = mock_submit.call_args[1]
            self.assertEqual(call_kwargs["target_space"], "Development")
            self.assertEqual(call_kwargs["system_component"], "Automations & Runtime")
            self.assertEqual(call_kwargs["request_type"], "Fix")
            self.assertEqual(call_kwargs["status"], "Blocked")
            self.assertIn("404 Not Found", call_kwargs["body"])

    def test_run_maintenance_dry_run(self):
        exit_code = run_maintenance(
            workspace_root=WORKSPACE_ROOT,
            report_root=self.temp_dir,
            dry_run=True,
        )
        self.assertEqual(exit_code, 0)
        latest_path = os.path.join(self.temp_dir, "latest-result.json")
        self.assertTrue(os.path.isfile(latest_path))
        with open(latest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["outcome"], "cached")

    def test_run_maintenance_live(self):
        exit_code = run_maintenance(
            workspace_root=WORKSPACE_ROOT,
            report_root=self.temp_dir,
            dry_run=False,
        )
        self.assertEqual(exit_code, 0)
        latest_path = os.path.join(self.temp_dir, "latest-result.json")
        self.assertTrue(os.path.isfile(latest_path))
        with open(latest_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            self.assertEqual(data["outcome"], "success")
            self.assertIn("skills", data["details"])
            self.assertIn("plugins", data["details"])
            self.assertIn("mcp", data["details"])


if __name__ == "__main__":
    unittest.main()
