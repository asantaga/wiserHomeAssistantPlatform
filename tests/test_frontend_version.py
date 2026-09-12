"""Version detection for installed schedule card bundles."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("card_version", ROOT / "custom_components/wiser/frontend/version.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class CardVersionTest(unittest.TestCase):
    def version(self, source):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "card.js"
            path.write_text(source)
            return module.schedule_card_version(path, "1.0.0")

    def test_legacy_banner_ignores_library_versions(self):
        self.assertEqual(self.version('const library="3.3.3";const $t="1.5.6";console.info(`WISER-SCHEDULE-CARD ${Vt("common.version")} ${$t}`)'), "1.5.6")

    def test_minified_dev_version(self):
        self.assertEqual(self.version('const ye="2.0.0-dev.60";console.info(`WISER-SCHEDULE-CARD ${He("common.version")} ${ye}`)'), "2.0.0-dev.60")

    def test_unknown_build_uses_stable_content_hash(self):
        first = self.version('const library="3.3.3"')
        self.assertTrue(first.startswith("sha256-"))
        self.assertEqual(first, self.version('const library="3.3.3"'))
        self.assertNotEqual(first, self.version('const library="4.0.0"'))

    def test_missing_file_keeps_fallback(self):
        with TemporaryDirectory() as directory:
            self.assertEqual(module.schedule_card_version(Path(directory) / "missing.js", "1.5.6"), "1.5.6")

    def test_installed_bundle_has_readable_version(self):
        version = module.schedule_card_version(ROOT / "custom_components/wiser/frontend/wiser-schedule-card.js", "missing")
        self.assertRegex(version, r"^\d+\.\d+\.\d+")
