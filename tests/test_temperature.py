"""Tests for effective Wiser room target temperatures."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
import unittest


SOURCE_PATH = (
    Path(__file__).parents[1] / "custom_components/wiser/temperature.py"
)
SPEC = spec_from_file_location("wiser_temperature", SOURCE_PATH)
assert SPEC and SPEC.loader
TEMPERATURE = module_from_spec(SPEC)
SPEC.loader.exec_module(TEMPERATURE)


class RoomTargetTemperatureTest(unittest.TestCase):
    """Test the temperature exposed for active and frost-protection states."""

    def test_returns_room_target_while_heating(self) -> None:
        room = SimpleNamespace(mode="Auto", current_target_temperature=20.5)

        self.assertEqual(
            TEMPERATURE.room_target_temperature(room, 5.0, -20), 20.5
        )

    def test_returns_frost_temperature_when_room_mode_is_off(self) -> None:
        room = SimpleNamespace(mode="Off", current_target_temperature=18.0)

        self.assertEqual(
            TEMPERATURE.room_target_temperature(room, 5.0, -20), 5.0
        )

    def test_returns_frost_temperature_for_off_sentinel(self) -> None:
        room = SimpleNamespace(mode="Manual", current_target_temperature=-20)

        self.assertEqual(
            TEMPERATURE.room_target_temperature(room, 5.0, -20), 5.0
        )
