"""Regression tests for the light unique_id migration (#681/#683).

Verifies build_light_unique_id_migration() rebuilds the pre-fix unique_ids and
maps them to the new per-channel light_id scheme, without any Home Assistant
runtime dependency.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/helpers.py"

ENTITY_PREFIX = "Wiser"
SYSTEM_NAME = "WiserHeatTEST"


def _module(name: str, **attributes: object) -> ModuleType:
    """Create and register a lightweight module stub."""
    module = ModuleType(name)
    module.__dict__.update(attributes)
    sys.modules[name] = module
    return module


def _load_helpers_module() -> ModuleType:
    """Load helpers.py with only the imports it needs stubbed out."""
    _module(
        "aioWiserHeatAPI",
    )
    _module(
        "aioWiserHeatAPI.wiserhub",
        WiserHubConnectionError=type("WiserHubConnectionError", (Exception,), {}),
        WiserHubAuthenticationError=type(
            "WiserHubAuthenticationError", (Exception,), {}
        ),
        WiserHubRESTError=type("WiserHubRESTError", (Exception,), {}),
    )
    _module("homeassistant")
    _module("homeassistant.core", HomeAssistant=object)

    package = _module("wiser")
    package.__path__ = []
    _module(
        "wiser.const", DOMAIN="wiser", ENTITY_PREFIX=ENTITY_PREFIX, MANUFACTURER="Drayton"
    )

    spec = importlib.util.spec_from_file_location("wiser.helpers", SOURCE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _light(*, device_id: int, light_id: int, product_type: str, name: str):
    return SimpleNamespace(
        id=device_id, light_id=light_id, product_type=product_type, name=name
    )


def _hub_data():
    """A hub with two single-gang lights and one two-gang dimmer (shared id)."""
    lights = [
        _light(device_id=101, light_id=1, product_type="DimmableLight", name="Diele"),
        _light(device_id=102, light_id=2, product_type="OnOffLight", name="Flur"),
        # Two-gang dimmer: both channels share physical device id 200.
        _light(device_id=200, light_id=3, product_type="DimmableLight", name="Bad Dusche"),
        _light(device_id=200, light_id=4, product_type="DimmableLight", name="Bad Wanne"),
    ]
    # get_device_name resolves the physical device; only single-gang ids should
    # ever be looked up (multi-gang is skipped before this is called). Raising on
    # an unexpected id turns an accidental multi-gang resolution into a failure.
    devices_by_id = {
        101: SimpleNamespace(id=101, product_type="DimmableLight", name="Diele"),
        102: SimpleNamespace(id=102, product_type="OnOffLight", name="Flur"),
    }
    rooms_by_device = {
        101: SimpleNamespace(name="Diele"),
        102: None,  # exercise the no-room name path
    }

    def get_by_id(device_id: int):
        return devices_by_id[device_id]

    def get_by_device_id(device_id: int):
        return rooms_by_device[device_id]

    return SimpleNamespace(
        wiserhub=SimpleNamespace(
            system=SimpleNamespace(name=SYSTEM_NAME),
            rooms=SimpleNamespace(get_by_device_id=get_by_device_id),
            devices=SimpleNamespace(
                get_by_id=get_by_id,
                lights=SimpleNamespace(all=lights),
            ),
        )
    )


class LightUniqueIdMigrationTest(unittest.TestCase):
    """Tests for build_light_unique_id_migration()."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.helpers = _load_helpers_module()

    def _mapping(self):
        return self.helpers.build_light_unique_id_migration(_hub_data())

    def _unique_id(self, device_type, entity_type, device_id):
        return self.helpers.get_unique_id(_hub_data(), device_type, entity_type, device_id)

    def test_light_entity_maps_name_to_light_id(self) -> None:
        mapping = self._mapping()
        old = self._unique_id(
            "device", "light", "Wiser DimmableLight Diele Diele Light"
        )
        self.assertEqual(mapping[old], self._unique_id("device", "light", 1))

    def test_selects_map_device_id_to_light_id(self) -> None:
        mapping = self._mapping()
        for kind in ("mode-select", "led-indicator", "power_on_behaviour_select"):
            old = self._unique_id("DimmableLight", kind, 101)
            self.assertEqual(mapping[old], self._unique_id("DimmableLight", kind, 1))

    def test_away_switch_maps_name_and_id(self) -> None:
        mapping = self._mapping()
        old = self._unique_id(
            "DimmableLight",
            "Wiser DimmableLight Diele Diele Away Mode Turns Off",
            101,
        )
        new = self._unique_id(
            "DimmableLight", "Wiser Diele Away Mode Turns Off", 1
        )
        self.assertEqual(mapping[old], new)

    def test_capability_binary_sensors_map_name(self) -> None:
        mapping = self._mapping()
        old = self._unique_id(
            "binary_sensor",
            "Is Dimmable",
            "Wiser DimmableLight Diele Diele Is Dimmable",
        )
        new = self._unique_id(
            "binary_sensor", "Is Dimmable", "Wiser Diele Is Dimmable"
        )
        self.assertEqual(mapping[old], new)

    def test_no_room_light_uses_type_and_name(self) -> None:
        mapping = self._mapping()
        old = self._unique_id("device", "light", "Wiser OnOffLight Flur Light")
        self.assertEqual(mapping[old], self._unique_id("device", "light", 2))

    def test_multi_gang_channels_are_skipped(self) -> None:
        mapping = self._mapping()
        # No mapping may reference the shared physical device id 200 ...
        for kind in ("mode-select", "led-indicator", "power_on_behaviour_select"):
            shared_id = self._unique_id("DimmableLight", kind, 200)
            self.assertNotIn(shared_id, mapping)
            self.assertNotIn(shared_id, mapping.values())
        # ... nor target the multi-gang channels' light_ids (3, 4).
        self.assertNotIn(self._unique_id("device", "light", 3), mapping.values())
        self.assertNotIn(self._unique_id("device", "light", 4), mapping.values())

    def test_no_noop_entries_and_exact_count(self) -> None:
        mapping = self._mapping()
        # Every entry is a real rename.
        self.assertTrue(all(old != new for old, new in mapping.items()))
        # 2 single-gang lights x (1 light + 3 selects + 1 away + 4 binary) = 18.
        self.assertEqual(len(mapping), 18)


if __name__ == "__main__":
    unittest.main()
