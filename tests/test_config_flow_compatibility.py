"""Regression tests for Home Assistant config-flow compatibility."""

import ast
import json
from pathlib import Path
import unittest


COMPONENT = Path(__file__).parents[1] / "custom_components/wiser"


class ConfigFlowCompatibilityTest(unittest.TestCase):
    def test_connection_class_is_declared_only_in_manifest(self):
        """The deprecated ConfigFlow CONNECTION_CLASS must not be restored."""
        tree = ast.parse((COMPONENT / "config_flow.py").read_text())
        flow = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "WiserFlowHandler"
        )

        assignments = {
            target.id
            for node in flow.body
            if isinstance(node, (ast.Assign, ast.AnnAssign))
            for target in (
                node.targets if isinstance(node, ast.Assign) else [node.target]
            )
            if isinstance(target, ast.Name)
        }
        self.assertNotIn("CONNECTION_CLASS", assignments)

        manifest = json.loads((COMPONENT / "manifest.json").read_text())
        self.assertEqual(manifest["iot_class"], "local_polling")


if __name__ == "__main__":
    unittest.main()
