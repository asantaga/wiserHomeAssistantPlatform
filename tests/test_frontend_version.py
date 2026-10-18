"""Test the shared version contract for any frontend bundle."""

import ast
from hashlib import sha256
from pathlib import Path
import re
from tempfile import TemporaryDirectory
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "custom_components/wiser/frontend/__init__.py"
reader = next(
    node for node in ast.parse(SOURCE.read_text()).body
    if isinstance(node, ast.FunctionDef) and node.name == "card_version"
)
namespace = {"Path": Path, "sha256": sha256, "re": re}
exec(compile(ast.Module(body=[reader], type_ignores=[]), str(SOURCE), "exec"), namespace)
card_version = namespace["card_version"]


class CardVersionTest(unittest.TestCase):
    def version(self, source, filename="wiser-example-card.js"):
        with TemporaryDirectory() as directory:
            path = Path(directory) / filename
            path.write_text(source)
            return card_version(path)

    def test_marker_supports_any_bundle_and_semantic_version(self):
        for name in ("wiser-schedule-card", "wiser-zigbee-card", "wiser-future-card"):
            for version in ("1.2.3", "2.0.0-beta.1-dev.2", "3.0.0+build.42"):
                with self.subTest(name=name, version=version):
                    source = f'/*! WISER-CARD-VERSION {name} {version} */\nconst library="9.9.9";'
                    self.assertEqual(self.version(source, f"{name}.js"), version)

    def test_other_bundle_marker_is_ignored(self):
        self.assertTrue(
            self.version('/*! WISER-CARD-VERSION wiser-other-card 4.0.0 */').startswith("sha256-")
        )

    def test_unmarked_content_never_guesses_a_version_from_javascript(self):
        sources = (
            'const library="3.3.3";const $t="1.5.6";console.info(`WISER-SCHEDULE-CARD ${Vt("common.version")} ${$t}`)',
            'const cardBuild="3.0.0-dev.7";console.info(`WISER-ZIGBEE-CARD ${translate("common.version")} ${cardBuild}`)',
            'html`<div class="version">${this.t("common.version")}: ${"3.0.0"}</div>`',
        )
        for source in sources:
            with self.subTest(source=source):
                expected = f"sha256-{sha256(source.encode()).hexdigest()[:16]}"
                self.assertEqual(self.version(source), expected)

    def test_content_hash_is_stable_and_changes_with_content(self):
        first = self.version('const library="3.3.3"')
        self.assertEqual(first, self.version('const library="3.3.3"'))
        self.assertNotEqual(first, self.version('const library="4.0.0"'))

    def test_missing_file_returns_missing(self):
        with TemporaryDirectory() as directory:
            self.assertEqual(card_version(Path(directory) / "missing.js"), "missing")
