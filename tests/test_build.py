"""Test automatic card source selection and integration packaging."""

import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from test_card_releases import FETCH, release

SPEC = importlib.util.spec_from_file_location(
    "wiser_build", Path(__file__).resolve().parents[1] / "scripts/build.py"
)
BUILD = importlib.util.module_from_spec(SPEC)
with patch.dict(sys.modules, {"fetch_card_releases": FETCH}):
    SPEC.loader.exec_module(BUILD)


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "integration"
        frontend = self.source / "frontend"
        frontend.mkdir(parents=True)
        self.output = self.root / "dist/wiser.zip"
        self.payloads = {
            "schedule": b"// local wiser-schedules-panel",
            "zigbee": b"// local wiser-zigbee-panel",
        }
        for card, panel in (("schedule", "schedules"), ("zigbee", "zigbee")):
            (frontend / f"{panel}_sidebar.py").touch()
            (frontend / f"wiser-{card}-card.js").write_bytes(b"old tracked bundle")
        (frontend / "__pycache__").mkdir()
        (frontend / "__pycache__/old.pyc").touch()

    def local(self, card):
        path = self.root / f"wiser-{card}-card/dist/wiser-{card}-card.js"
        path.parent.mkdir(parents=True)
        path.write_bytes(self.payloads[card])
        return path

    def build(self):
        return BUILD.build(self.source, self.output, self.root, "dev", FETCH.CARD_REPOSITORIES)

    def test_local_bundles_win_without_network_and_tracked_files_are_untouched(self):
        for card in self.payloads:
            self.local(card)
        with patch.object(FETCH, "list_releases") as releases:
            report = self.build()
        releases.assert_not_called()
        self.assertEqual([r["source"] for r in report], ["local", "local"])
        with ZipFile(self.output) as archive:
            for card, payload in self.payloads.items():
                self.assertEqual(archive.read(f"frontend/wiser-{card}-card.js"), payload)
                self.assertEqual(
                    (self.source / f"frontend/wiser-{card}-card.js").read_bytes(),
                    b"old tracked bundle",
                )
            self.assertEqual(json.loads(archive.read("frontend/card-releases.json")), report)
            self.assertFalse(any("__pycache__" in name for name in archive.namelist()))

    def test_missing_local_bundle_falls_back_independently(self):
        self.local("zigbee")
        with patch.object(FETCH, "list_releases", return_value=[release("v1", "2026", card="schedule")]) as releases, patch.object(FETCH, "download_asset", return_value=(self.payloads["schedule"], "sha256:test")):
            report = self.build()
        releases.assert_called_once_with(FETCH.CARD_REPOSITORIES["schedule"])
        self.assertEqual([r["source"] for r in report], ["release", "local"])

    def test_no_local_bundles_downloads_both_releases(self):
        with patch.object(FETCH, "list_releases", side_effect=[
            [release("v1", "2026", card="schedule")],
            [release("v2", "2026", card="zigbee")],
        ]), patch.object(FETCH, "download_asset", side_effect=[
            (self.payloads["schedule"], "sha256:schedule"),
            (self.payloads["zigbee"], "sha256:zigbee"),
        ]):
            report = self.build()
        self.assertEqual([r["source"] for r in report], ["release", "release"])
        with ZipFile(self.output) as archive:
            for card, payload in self.payloads.items():
                self.assertEqual(archive.read(f"frontend/wiser-{card}-card.js"), payload)

    def test_failed_fallback_keeps_previous_package(self):
        self.local("schedule")
        self.output.parent.mkdir()
        self.output.write_bytes(b"previous package")
        with patch.object(FETCH, "list_releases", side_effect=ValueError("unavailable")):
            with self.assertRaisesRegex(ValueError, "unavailable"):
                self.build()
        self.assertEqual(self.output.read_bytes(), b"previous package")

    def test_invalid_local_bundle_fails_instead_of_using_old_tracked_card(self):
        self.local("schedule").write_bytes(b"old card without panel")
        with patch.object(FETCH, "list_releases") as releases:
            with self.assertRaisesRegex(ValueError, "does not include the sidebar panel"):
                self.build()
        releases.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_release_builds_ignore_local_bundles_for_both_channels(self):
        for card in self.payloads:
            self.local(card)
        for channel, explicit_release in (("dev", True), ("stable", True), ("stable", False)):
            with self.subTest(channel=channel, explicit_release=explicit_release):
                with patch.object(FETCH, "list_releases", side_effect=[
                    [release("v1", "2026", card="schedule")],
                    [release("v2", "2026", card="zigbee")],
                ]), patch.object(FETCH, "download_asset", side_effect=[
                    (b"// published wiser-schedules-panel", "sha256:schedule"),
                    (b"// published wiser-zigbee-panel", "sha256:zigbee"),
                ]) as download:
                    report = BUILD.build(
                        self.source, self.output, self.root, channel,
                        FETCH.CARD_REPOSITORIES, release=explicit_release,
                    )
                self.assertEqual(download.call_count, 2)
                self.assertEqual([r["source"] for r in report], ["release", "release"])
                with ZipFile(self.output) as archive:
                    self.assertEqual(
                        archive.read("frontend/wiser-zigbee-card.js"),
                        b"// published wiser-zigbee-panel",
                    )

    def test_release_failure_does_not_fall_back_to_local_bundles(self):
        for card in self.payloads:
            self.local(card)
        with patch.object(FETCH, "list_releases", side_effect=ValueError("unavailable")):
            with self.assertRaisesRegex(ValueError, "unavailable"):
                BUILD.build(
                    self.source, self.output, self.root, "dev",
                    FETCH.CARD_REPOSITORIES, release=True,
                )
        self.assertFalse(self.output.exists())
