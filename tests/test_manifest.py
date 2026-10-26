"""Regression tests for the integration manifest."""

import json
from pathlib import Path
import unittest


MANIFEST = (
    Path(__file__).parents[1] / "custom_components/wiser/manifest.json"
)


class ManifestTest(unittest.TestCase):
    def test_manifest_keys_follow_hassfest_order(self):
        manifest = json.loads(MANIFEST.read_text())

        self.assertEqual(
            list(manifest),
            ["domain", "name", *sorted(set(manifest) - {"domain", "name"})],
        )

    def test_history_stats_is_declared_as_an_after_dependency(self):
        manifest = json.loads(MANIFEST.read_text())

        self.assertIn("history_stats", manifest["after_dependencies"])


if __name__ == "__main__":
    unittest.main()
