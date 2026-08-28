"""Regression tests for physical HeatHub naming."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from uuid import UUID


SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/helpers.py"
ENTITY_SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/entity.py"


def _load_helpers_module() -> ModuleType:
    """Load helpers with lightweight dependency stubs."""
    wiserhub = ModuleType("aioWiserHeatAPI.wiserhub")
    wiserhub.WiserHubConnectionError = RuntimeError
    wiserhub.WiserHubAuthenticationError = RuntimeError
    wiserhub.WiserHubRESTError = RuntimeError
    sys.modules["aioWiserHeatAPI"] = ModuleType("aioWiserHeatAPI")
    sys.modules["aioWiserHeatAPI.wiserhub"] = wiserhub

    sys.modules["homeassistant"] = ModuleType("homeassistant")
    core = ModuleType("homeassistant.core")
    core.HomeAssistant = object
    sys.modules["homeassistant.core"] = core

    package = ModuleType("wiser_helpers_test")
    package.__path__ = []
    sys.modules[package.__name__] = package
    const = ModuleType("wiser_helpers_test.const")
    const.DOMAIN = "wiser"
    const.ENTITY_PREFIX = "Wiser"
    const.MANUFACTURER = "Drayton Wiser"
    sys.modules[const.__name__] = const

    spec = importlib.util.spec_from_file_location(
        "wiser_helpers_test.helpers", SOURCE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_entity_module() -> ModuleType:
    """Load the shared entity mixin against the helper test package."""
    spec = importlib.util.spec_from_file_location(
        "wiser_helpers_test.entity", ENTITY_SOURCE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class HubNamingTest(unittest.TestCase):
    """Ensure display names and object IDs use the physical hub MAC."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.helpers = _load_helpers_module()
        cls.entity = _load_entity_module()

    def setUp(self) -> None:
        system = SimpleNamespace(
            name="WiserHeatNOTUSED",
            network=SimpleNamespace(mac_address="FC:FE:C2:05:8A:52"),
            model="CCTFR6311G2",
            firmware_version="4.48.2",
        )
        room = SimpleNamespace(id=7, name="Andys Bedroom")
        rooms = SimpleNamespace(
            get_by_id=lambda room_id: SimpleNamespace(
                id=room_id, name="Andys Bedroom"
            ),
            get_by_device_id=lambda _device_id: room,
        )
        devices = SimpleNamespace(
            get_by_id=lambda device_id: SimpleNamespace(
                id=device_id, product_type="RoomStat"
            )
        )
        self.data = SimpleNamespace(
            wiserhub=SimpleNamespace(system=system, rooms=rooms, devices=devices)
        )

    def test_single_hub_has_concise_device_name(self) -> None:
        self.assertEqual(self.helpers.get_hub_device_name(self.data), "Wiser HeatHub")

    def test_multiple_hubs_add_mac_suffix_to_device_name(self) -> None:
        self.data._wiser_show_hub_suffix = True
        self.assertEqual(
            self.helpers.get_hub_device_name(self.data), "Wiser HeatHub (058A52)"
        )

    def test_hub_entity_object_id_uses_mac_suffix(self) -> None:
        self.assertEqual(
            self.helpers.get_hub_entity_object_id(self.data, "Away Mode"),
            "058a52_away_mode",
        )

    def test_hub_entity_mixin_suggests_mac_derived_object_id(self) -> None:
        class DefaultEntity:
            @property
            def suggested_object_id(self):
                return "default"

        class HubEntity(self.entity.WiserEntityMixin, DefaultEntity):
            name = "Away Mode"

            def __init__(entity_self, data) -> None:
                entity_self._data = data

            @property
            def device_info(entity_self):
                return {
                    "identifiers": {
                        ("wiser", entity_self._data.wiserhub.system.name)
                    }
                }

        self.assertEqual(
            HubEntity(self.data).suggested_object_id,
            "058a52_away_mode",
        )

    def test_hub_entity_object_id_does_not_repeat_device_name(self) -> None:
        object_id = self.helpers.get_hub_entity_object_id(self.data, "Away Mode")
        self.assertNotIn("wiser_heathub", object_id)

    def test_legacy_identifier_remains_stable(self) -> None:
        self.assertEqual(
            self.helpers.get_identifier(self.data, 0),
            "WiserHeatNOTUSED Wiser HeatHub (WiserHeatNOTUSED)",
        )

    def test_room_device_name_uses_area_for_room_context(self) -> None:
        self.assertEqual(
            self.helpers.get_device_name(self.data, 7, "room"),
            "Wiser Room",
        )

    def test_room_identifier_uses_stable_room_id(self) -> None:
        self.assertEqual(
            self.helpers.get_identifier(self.data, 7, "room"),
            "WiserHeatNOTUSED room 7",
        )
        self.assertEqual(
            self.helpers.get_legacy_room_identifier(self.data, 7),
            "WiserHeatNOTUSED Wiser Andys Bedroom",
        )

    def test_entity_unique_id_is_a_deterministic_uuid5(self) -> None:
        first = self.helpers.get_unique_id(
            self.data, "sensor", "Temperature", 7
        )
        second = self.helpers.get_unique_id(
            self.data, "sensor", "Temperature", 7
        )

        self.assertEqual(first, second)
        self.assertEqual(UUID(first).version, 5)
        self.assertNotEqual(
            first,
            self.helpers.get_unique_id(
                self.data, "sensor", "Target Temperature", 7
            ),
        )

    def test_uuid_matches_the_legacy_unique_id_migration(self) -> None:
        legacy_unique_id = self.helpers.get_legacy_unique_id(
            self.data, "sensor", "Temperature", 7
        )
        self.assertEqual(
            self.helpers.get_unique_id(
                self.data, "sensor", "Temperature", 7
            ),
            self.helpers.get_uuid_unique_id(legacy_unique_id),
        )

    def test_roomstat_name_uses_area_for_room_context(self) -> None:
        self.assertEqual(
            self.helpers.get_device_name(self.data, 21),
            "Wiser Thermostat",
        )
        self.assertEqual(
            self.helpers.get_identifier(self.data, 21),
            "WiserHeatNOTUSED Wiser RoomStat Andys Bedroom",
        )

    def test_physical_device_suggests_its_wiser_room_as_area(self) -> None:
        self.assertEqual(
            self.helpers.get_device_area_info(self.data, 21),
            {"suggested_area": "Andys Bedroom"},
        )

    def test_unassigned_physical_device_does_not_suggest_an_area(self) -> None:
        self.data.wiserhub.rooms.get_by_device_id = lambda _device_id: None
        self.assertEqual(self.helpers.get_device_area_info(self.data, 21), {})

    def test_temperature_sensor_has_concise_name_and_stable_identifier(self) -> None:
        self.data.wiserhub.devices.get_by_id = lambda device_id: SimpleNamespace(
            id=device_id,
            name="Kitchen Temperature Sensor",
            product_type="TemperatureHumiditySensor",
        )

        self.assertEqual(
            self.helpers.get_device_name(self.data, 31),
            "Wiser Temperature/Humidity Sensor",
        )
        self.assertEqual(
            self.helpers.get_identifier(self.data, 31),
            "WiserHeatNOTUSED Wiser TemperatureHumiditySensor "
            "Andys Bedroom Kitchen Temperature Sensor",
        )
        self.assertEqual(
            self.helpers.get_legacy_device_name(self.data, 31),
            "Wiser TemperatureHumiditySensor "
            "Andys Bedroom Kitchen Temperature Sensor",
        )


if __name__ == "__main__":
    unittest.main()
