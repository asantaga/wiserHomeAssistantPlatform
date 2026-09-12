"""Integration contract for the externally built schedule card/panel bundle.

Card behaviour is tested in the wiser-schedule-card source repository.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "custom_components/wiser"
CARD = ROOT / "frontend/wiser-schedule-card.js"
WEBSOCKETS = ROOT / "websockets.py"


class ScheduleCardBundleTest(unittest.TestCase):
    def test_matching_card_and_panel_are_bundled_together(self):
        source = CARD.read_text()
        self.assertIn('wiser-schedules-panel', source)
        self.assertIn('wiser-schedule-card-editor', source)
        self.assertIn('panelApiVersion', source)

    def test_delete_websocket_reconciles_ambiguous_hub_errors(self):
        websocket_source = WEBSOCKETS.read_text()

        self.assertTrue(
            "from aioWiserHeatAPI.exceptions import WiserScheduleError"
            in websocket_source,
            "delete websocket should identify schedule transport errors",
        )
        self.assertTrue(
            "except WiserScheduleError as ex:" in websocket_source,
            "delete websocket should reconcile an ambiguous schedule transport error",
        )
        self.assertTrue(
            "await d.async_refresh()" in websocket_source,
            "delete websocket should refresh hub state after a transport error",
        )
        self.assertTrue(
            "if d.wiserhub.schedules.get_by_id(schedule_type_enum, schedule_id):"
            in websocket_source,
            "delete websocket should report an error only when the schedule remains",
        )
