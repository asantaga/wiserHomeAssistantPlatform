"""Version detection for installed schedule card bundles."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
# Test the pure reader from the registration module without loading HA.
import ast
from hashlib import sha256
import re
from types import SimpleNamespace
source = (ROOT / "custom_components/wiser/frontend/__init__.py").read_text()
reader = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == "card_version")
namespace = {"Path": Path, "sha256": sha256, "re": re}
exec(compile(ast.Module(body=[reader], type_ignores=[]), "frontend/__init__.py", "exec"), namespace)
module = SimpleNamespace(card_version=namespace["card_version"])


class CardVersionTest(unittest.TestCase):
    def version(self, source):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "wiser-schedule-card.js"
            path.write_text(source)
            return module.card_version(path)

    def test_legacy_banner_ignores_library_versions(self):
        self.assertEqual(self.version('const library="3.3.3";const $t="1.5.6";console.info(`WISER-SCHEDULE-CARD ${Vt("common.version")} ${$t}`)'), "1.5.6")

    def test_minified_dev_version(self):
        self.assertEqual(self.version('const ye="2.0.0-dev.60";console.info(`WISER-SCHEDULE-CARD ${He("common.version")} ${ye}`)'), "2.0.0-dev.60")

    def test_unknown_build_uses_stable_content_hash(self):
        first = self.version('const library="3.3.3"')
        self.assertTrue(first.startswith("sha256-"))
        self.assertEqual(first, self.version('const library="3.3.3"'))
        self.assertNotEqual(first, self.version('const library="4.0.0"'))

    def test_missing_file_returns_missing(self):
        with TemporaryDirectory() as directory:
            self.assertEqual(module.card_version(Path(directory) / "missing.js"), "missing")

    def test_installed_bundle_has_readable_version(self):
        version = module.card_version(ROOT / "custom_components/wiser/frontend/wiser-schedule-card.js")
        self.assertRegex(version, r"^\d+\.\d+\.\d+")

    def test_explicit_version_marker(self):
        self.assertEqual(self.version('/*! WISER-CARD-VERSION wiser-schedule-card 4.0.0-dev.9 */\nconst library="3.3.3";'), "4.0.0-dev.9")

    def test_other_card_marker_is_ignored(self):
        self.assertTrue(self.version('/*! WISER-CARD-VERSION wiser-zigbee-card 4.0.0 */').startswith("sha256-"))
