"""Unit tests for automation/plugin-mcp-skills-update backend modules."""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest

# Add backend directory to sys.path
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(os.path.dirname(TEST_DIR), "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from mcp_syncer import check_and_sync_mcp
from plugins_checker import check_superpowers_plugin
from skills_updater import update_skills
from main import run_maintenance

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
