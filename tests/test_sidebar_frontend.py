"""Run sidebar shell behavior tests with Node's dependency-free test runner."""

from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "Node.js is required for frontend behavior tests")
class SidebarFrontendTest(unittest.TestCase):
    def test_lazy_panel_loading_and_navigation(self):
        result = subprocess.run(
            [NODE, "--test", str(ROOT / "tests/frontend/wiser-panel.test.cjs")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
