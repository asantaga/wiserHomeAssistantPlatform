"""Test release-channel selection and safe staging of downloaded card assets."""
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("fetch_card_releases", Path(__file__).resolve().parents[1] / "scripts/fetch_card_releases.py")
FETCH = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FETCH)


def release(tag, date, prerelease=False, card="zigbee", draft=False, asset=True):
    return {
        "tag_name": tag, "published_at": date, "prerelease": prerelease, "draft": draft,
        "assets": [{"id": 1, "name": f"wiser-{card}-card.js", "state": "uploaded", "size": 200,
                    "browser_download_url": f"https://github.com/andyblac/wiser-{card}-card/releases/download/{tag}/wiser-{card}-card.js"}] if asset else [],
    }


class CardReleaseTest(unittest.TestCase):
    def setUp(self):
        self.beta = release("v2.0.0-beta.1", "2026-09-01T00:00:00Z", True)
        self.stable = release("v2.0.1", "2026-09-02T00:00:00Z")
        self.releases = [self.stable, self.beta, release("draft", "2026-09-03T00:00:00Z", True, draft=True)]

    def test_dev_selects_newer_stable_over_older_prerelease(self):
        self.assertEqual(FETCH.select_release(self.releases, "dev"), self.stable)

    def test_dev_selects_newer_prerelease_over_older_stable(self):
        newer_beta = release("v2.1.0-beta.1", "2026-09-04T00:00:00Z", True)
        releases = [newer_beta, *self.releases]
        self.assertEqual(FETCH.select_release(releases, "dev"), newer_beta)
        self.assertEqual(FETCH.select_release(releases, "stable"), self.stable)

    def test_unpublished_releases_are_excluded(self):
        unpublished = release("v4.0.0", None)
        for channel in ("dev", "stable"):
            with self.subTest(channel=channel):
                self.assertEqual(
                    FETCH.select_release([unpublished, *self.releases], channel),
                    self.stable,
                )

    def test_stable_excludes_prereleases_and_drafts(self):
        self.assertEqual(FETCH.select_release(self.releases, "stable"), self.stable)

    def test_dev_falls_back_to_stable(self):
        self.assertEqual(FETCH.select_release([self.stable], "dev"), self.stable)

    def test_stable_does_not_fall_back_to_beta(self):
        with self.assertRaisesRegex(ValueError, "No published stable"):
            FETCH.select_release([self.beta], "stable")

    def test_latest_is_selected_by_publication_date(self):
        older = release("old", "2026-08-01T00:00:00Z", True)
        self.assertEqual(FETCH.select_release([older, self.beta], "dev"), self.beta)

    def test_missing_release_or_asset_fails(self):
        with self.assertRaises(ValueError):
            FETCH.select_release([], "dev")
        with self.assertRaisesRegex(ValueError, "must have one"):
            FETCH.select_asset(release("missing", "2026", asset=False), "wiser-zigbee-card.js")

    def test_plan_does_not_download_or_write(self):
        with TemporaryDirectory() as directory:
            out = Path(directory) / "not-created"
            with patch.object(FETCH, "list_releases", return_value=self.releases), patch.object(FETCH, "download_asset") as download:
                report = FETCH.fetch_cards("dev", out, {"zigbee": "andyblac/wiser-zigbee-card"}, plan=True)
            download.assert_not_called()
            self.assertFalse(out.exists())
            self.assertEqual(report[0]["tag"], "v2.0.1")

    def test_download_failure_does_not_replace_either_card(self):
        with TemporaryDirectory() as directory:
            out = Path(directory)
            (out / "wiser-schedule-card.js").write_bytes(b"old")
            releases = [[release("schedule", "2026", True, card="schedule")], [self.beta]]
            with patch.object(FETCH, "list_releases", side_effect=releases), patch.object(FETCH, "download_asset", side_effect=[(b"new", "sha256:test"), ValueError("download failed")]):
                with self.assertRaises(ValueError):
                    FETCH.fetch_cards("dev", out, FETCH.CARD_REPOSITORIES)
            self.assertEqual((out / "wiser-schedule-card.js").read_bytes(), b"old")
            self.assertFalse((out / "card-releases.json").exists())

    def test_download_written_to_correct_filename_with_provenance(self):
        with TemporaryDirectory() as directory:
            out = Path(directory)
            with patch.object(FETCH, "list_releases", return_value=self.releases), patch.object(FETCH, "download_asset", return_value=(b"new card", "sha256:test")):
                FETCH.fetch_cards("dev", out, {"zigbee": "andyblac/wiser-zigbee-card"})
            self.assertEqual((out / "wiser-zigbee-card.js").read_bytes(), b"new card")
            self.assertEqual(json.loads((out / "card-releases.json").read_text())[0]["digest"], "sha256:test")

    def test_panel_integration_rejects_old_schedule_card(self):
        with TemporaryDirectory() as directory:
            out = Path(directory)
            (out / "schedules_sidebar.py").touch()
            with patch.object(FETCH, "list_releases", return_value=[release("old", "2026", card="schedule")]), patch.object(FETCH, "download_asset", return_value=(b"old card", "sha256:test")):
                with self.assertRaisesRegex(ValueError, "does not include the sidebar panel"):
                    FETCH.fetch_cards("stable", out, {"schedule": "andyblac/wiser-schedule-card"})
