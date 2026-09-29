"""Test automatic card source selection and integration packaging."""

import importlib.util
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from test_card_releases import FETCH, release, CARD_MANIFEST, CARD_REPOSITORIES

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
            "schedule": b'customElements.define("wiser-schedule-card",class{});customElements.define("wiser-schedules-panel",class{})',
            "zigbee": b'customElements.define("wiser-zigbee-card",class{});customElements.define("wiser-zigbee-panel",class{})',
            "rooms": (
                b'customElements.define("wiser-rooms-card",class{});'
                b'customElements.define("wiser-rooms-panel",class{})'
            ),
        }
        registry = self.root / "WiserFrontendPanelConfig/dist/cards.json"
        registry.parent.mkdir(parents=True)
        registry.write_text(
            json.dumps(CARD_MANIFEST), encoding="utf-8"
        )
        for card, panel in (("schedule", "schedules"), ("zigbee", "zigbee")):
            (frontend / f"{panel}_sidebar.py").touch()
            (frontend / f"wiser-{card}-card.js").write_bytes(b"old tracked bundle")
        (frontend / "wiser-rooms-card.js").write_bytes(b"old tracked bundle")
        (frontend / "__pycache__").mkdir()
        (frontend / "__pycache__/old.pyc").touch()

    def local(self, card):
        path = self.root / f"wiser-{card}-card/dist/wiser-{card}-card.js"
        path.parent.mkdir(parents=True)
        path.write_bytes(self.payloads[card])
        return path

    def build(self):
        return BUILD.build(self.source, self.output, self.root, "dev", CARD_REPOSITORIES)

    def test_local_bundles_win_without_network_and_tracked_files_are_untouched(self):
        for card in self.payloads:
            self.local(card)
        with patch.object(FETCH, "list_releases") as releases:
            report = self.build()
        releases.assert_not_called()
        self.assertEqual([r["source"] for r in report], ["local", "local", "local"])
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
        self.local("rooms")
        with patch.object(FETCH, "list_releases", return_value=[release("v1", "2026", card="schedule")]) as releases, patch.object(FETCH, "download_asset", return_value=(self.payloads["schedule"], "sha256:test")):
            report = self.build()
        releases.assert_called_once_with(CARD_REPOSITORIES["schedule"])
        self.assertEqual([r["source"] for r in report], ["release", "local", "local"])

    def test_no_local_bundles_downloads_all_releases(self):
        with patch.object(FETCH, "list_releases", side_effect=[
            [release("v1", "2026", card="schedule")],
            [release("v2", "2026", card="zigbee")],
            [release("v3", "2026", card="rooms")],
        ]), patch.object(FETCH, "download_asset", side_effect=[
            (self.payloads["schedule"], "sha256:schedule"),
            (self.payloads["zigbee"], "sha256:zigbee"),
            (self.payloads["rooms"], "sha256:rooms"),
        ]):
            report = self.build()
        self.assertEqual([r["source"] for r in report], ["release", "release", "release"])
        with ZipFile(self.output) as archive:
            for card, payload in self.payloads.items():
                self.assertEqual(archive.read(f"frontend/wiser-{card}-card.js"), payload)

    def test_external_registry_alone_adds_an_unknown_card_and_repository(self):
        for card in self.payloads:
            self.local(card)
        definition = {
            "id": "metering", "name": "Electricity",
            "filename": "wiser-electricity-card.js", "repository": "example/monitoring",
            "component": "wiser-electricity-card", "panel": "wiser-electricity-panel",
        }
        manifest = [*CARD_MANIFEST, definition]
        (self.root / "WiserFrontendPanelConfig/dist/cards.json").write_text(json.dumps(manifest))
        bundle = self.root / "monitoring/dist/wiser-electricity-card.js"
        bundle.parent.mkdir(parents=True)
        bundle.write_bytes(b"customElements.define('wiser-electricity-card',class{});customElements.define('wiser-electricity-panel',class{})")
        with patch.object(FETCH, "list_releases") as releases:
            report = BUILD.build(self.source, self.output, self.root, "dev")
        releases.assert_not_called()
        self.assertEqual(report[-1]["repository"], "example/monitoring")
        with ZipFile(self.output) as archive:
            self.assertEqual(json.loads(archive.read("frontend/cards.json")), manifest)
            self.assertEqual(archive.read("frontend/wiser-electricity-card.js"), bundle.read_bytes())

    def test_build_rejects_bundle_using_removed_settings_endpoint(self):
        self.local("schedule").write_bytes(self.payloads["schedule"] + b';const api="wiser/anything_panel/configure";')
        with self.assertRaisesRegex(ValueError, "generic settings API"):
            self.build()
        self.assertFalse(self.output.exists())

    def test_failed_fallback_keeps_previous_package(self):
        self.local("schedule")
        self.local("rooms")
        self.output.parent.mkdir()
        self.output.write_bytes(b"previous package")
        with patch.object(FETCH, "list_releases", side_effect=ValueError("unavailable")):
            with self.assertRaisesRegex(ValueError, "unavailable"):
                self.build()
        self.assertEqual(self.output.read_bytes(), b"previous package")

    def test_invalid_local_bundle_fails_instead_of_using_old_tracked_card(self):
        self.local("schedule").write_bytes(b"wiser-schedule-card without panel")
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
                with patch.object(BUILD, "fetch_panel_config", return_value=(
                    CARD_MANIFEST,
                    {"repository": FETCH.PANEL_CONFIG_REPOSITORY, "source": "release"},
                )), patch.object(FETCH, "list_releases", side_effect=[
                    [release("v1", "2026", card="schedule")],
                    [release("v2", "2026", card="zigbee")],
                    [release("v3", "2026", card="rooms")],
                ]), patch.object(FETCH, "download_asset", side_effect=[
                    (self.payloads["schedule"], "sha256:schedule"),
                    (self.payloads["zigbee"], "sha256:zigbee"),
                    (
                        b'customElements.define("wiser-rooms-card",class{});'
                        b'customElements.define("wiser-rooms-panel",class{})',
                        "sha256:rooms",
                    ),
                ]) as download:
                    report = BUILD.build(
                        self.source, self.output, self.root, channel,
                        CARD_REPOSITORIES, release=explicit_release,
                    )
                self.assertEqual(download.call_count, 3)
                self.assertEqual([r["source"] for r in report], ["release", "release", "release"])
                with ZipFile(self.output) as archive:
                    self.assertEqual(
                        archive.read("frontend/wiser-zigbee-card.js"),
                        self.payloads["zigbee"],
                    )
                    self.assertEqual(
                        json.loads(archive.read("frontend/cards.json")),
                        CARD_MANIFEST,
                    )
                    self.assertEqual(
                        json.loads(archive.read("frontend/panel-config-release.json"))["source"],
                        "release",
                    )

    def test_release_failure_does_not_fall_back_to_local_bundles(self):
        for card in self.payloads:
            self.local(card)
        with patch.object(FETCH, "list_releases", side_effect=ValueError("unavailable")):
            with self.assertRaisesRegex(ValueError, "unavailable"):
                BUILD.build(
                    self.source, self.output, self.root, "dev",
                    CARD_REPOSITORIES, release=True,
                )
        self.assertFalse(self.output.exists())
