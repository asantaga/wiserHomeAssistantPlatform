"""Version detection for installed Zigbee card bundles."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("card_version", ROOT / "custom_components/wiser/frontend/zigbee_version.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ZigbeeCardVersionTest(unittest.TestCase):
    def version(self, source):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "card.js"
            path.write_text(source)
            return module.zigbee_card_version(path, "1.0.0")

    def test_unknown_build_uses_stable_content_hash(self):
        first = self.version('const library="3.3.3"')
        self.assertTrue(first.startswith("sha256-"))
        self.assertEqual(first, self.version('const library="3.3.3"'))
        self.assertNotEqual(first, self.version('const library="4.0.0"'))

    def test_missing_file_keeps_fallback(self):
        with TemporaryDirectory() as directory:
            self.assertEqual(module.zigbee_card_version(Path(directory) / "missing.js", "2.1.2"), "2.1.2")

    def test_zigbee_banner_ignores_library_versions(self):
        self.assertEqual(self.version('const library="3.3.3";const $t="2.1.2";console.info(`WISER-ZIGBEE-NETWORK-CARD ${Zt("common.version")} ${$t}`)'), "2.1.2")

    def test_zigbee_dev_version(self):
        self.assertEqual(self.version('const cardBuild="3.0.0-dev.7";console.info(`WISER-ZIGBEE-CARD ${translate("common.version")} ${cardBuild}`)'), "3.0.0-dev.7")

    def test_installed_zigbee_bundle_has_readable_version(self):
        version = module.zigbee_card_version(ROOT / "custom_components/wiser/frontend/wiser-zigbee-card.js", "missing")
        self.assertEqual(version, "2.1.2")

    def test_modern_editor_footer_with_inlined_version(self):
        source = 'const library="3.3.3";html`<div class="version">${this.t("common.version")}: ${"3.0.0-dev.65"}</div>`'
        self.assertEqual(self.version(source), "3.0.0-dev.65")

    def test_modern_release_footer(self):
        source = 'html`<div class="version">${this.t("common.version")}: ${"3.0.0"}</div>`'
        self.assertEqual(self.version(source), "3.0.0")

    def test_explicit_version_marker(self):
        self.assertEqual(self.version('/*! WISER-CARD-VERSION wiser-zigbee-card 4.0.0-dev.9 */\nconst library="3.3.3";'), "4.0.0-dev.9")

    def test_other_card_marker_is_ignored(self):
        self.assertTrue(self.version('/*! WISER-CARD-VERSION wiser-schedule-card 4.0.0 */').startswith("sha256-"))
