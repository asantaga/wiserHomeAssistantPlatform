"""Tests for the shared heating and hot-water circuit state logic."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/circuit_state.py"


def _load_circuit_state_module() -> ModuleType:
    """Load circuit_state.py with only the API constants it needs stubbed."""
    sys.modules.setdefault("aioWiserHeatAPI", ModuleType("aioWiserHeatAPI"))
    # Extend any stub another test module registered rather than replacing it.
    const = sys.modules.setdefault(
        "aioWiserHeatAPI.const", ModuleType("aioWiserHeatAPI.const")
    )
    const.TEXT_ON = "On"
    const.TEXT_OFF = "Off"
    const.TEXT_UNKNOWN = "Unknown"

    spec = importlib.util.spec_from_file_location(
        "wiser_circuit_state_test", SOURCE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CircuitStateTest(unittest.TestCase):
    """Tests for the raw circuit state shared by text and binary sensors."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_circuit_state_module()

    @staticmethod
    def _channel(relay: str, demand: str) -> SimpleNamespace:
        return SimpleNamespace(
            heating_relay_status=relay, demand_on_off_output=demand
        )

    def test_heating_uses_relay_when_known(self) -> None:
        self.assertEqual(
            self.module.heating_channel_output_state(self._channel("On", "Off")),
            "On",
        )

    def test_heating_falls_back_to_demand_when_relay_unknown(self) -> None:
        self.assertEqual(
            self.module.heating_channel_output_state(
                self._channel("Unknown", "On")
            ),
            "On",
        )

    def test_heating_unknown_when_both_unknown(self) -> None:
        self.assertEqual(
            self.module.heating_channel_output_state(
                self._channel("Unknown", "Unknown")
            ),
            "Unknown",
        )

    def test_hot_water_reads_current_state(self) -> None:
        self.assertEqual(
            self.module.hot_water_output_state(
                SimpleNamespace(current_state="Off")
            ),
            "Off",
        )

    def test_output_state_is_on(self) -> None:
        self.assertIs(self.module.output_state_is_on("On"), True)
        self.assertIs(self.module.output_state_is_on("Off"), False)
        for raw_state in ("Unknown", "", None):
            with self.subTest(raw_state=raw_state):
                self.assertIsNone(self.module.output_state_is_on(raw_state))


if __name__ == "__main__":
    unittest.main()
