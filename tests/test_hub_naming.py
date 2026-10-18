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
    const = ModuleType("homeassistant.const")
    const.MAJOR_VERSION = 2025
    const.MINOR_VERSION = 5
    sys.modules["homeassistant.const"] = const
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
        self.helpers.MAJOR_VERSION = 2025
        self.helpers.MINOR_VERSION = 5

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

    def test_hub_entity_object_id_does_not_repeat_device_mac_suffix(self) -> None:
        self.assertEqual(
            self.helpers.get_hub_entity_object_id(
                self.data, "Away Mode", "Wiser HeatHub (058A52)"
            ),
            "away_mode",
        )

    def test_renamed_hub_entity_object_id_keeps_mac_suffix(self) -> None:
        self.assertEqual(
            self.helpers.get_hub_entity_object_id(
                self.data, "Away Mode", "Test"
            ),
            "058a52_away_mode",
        )

    def test_active_rooms_exclude_nothing_assigned_records(self) -> None:
        active = SimpleNamespace(_data={}, id=1)
        deleted = SimpleNamespace(
            _data={"Invalid": "NothingAssigned"}, id=2
        )
        self.data.wiserhub.rooms.all = [active, deleted]

        self.assertEqual(self.helpers.active_wiser_rooms(self.data), [active])

    def test_hub_parent_uses_compatible_identifier(self) -> None:
        self.assertEqual(
            self.helpers.get_hub_via_device_info(self.data),
            {"via_device": ("wiser", "WiserHeatNOTUSED")},
        )

    def test_hub_parent_uses_device_id_on_current_home_assistant(self) -> None:
        self.helpers.MAJOR_VERSION = 2026
        self.helpers.MINOR_VERSION = 8
        self.data.hub_device_id = "physical-hub-id"

        self.assertEqual(
            self.helpers.get_hub_via_device_info(self.data),
            {"via_device_id": "physical-hub-id"},
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

        renamed_entity = HubEntity(self.data)
        renamed_entity.device_entry = SimpleNamespace(
            name="Wiser HeatHub (058A52)", name_by_user="Test"
        )
        self.assertEqual(
            renamed_entity.suggested_object_id,
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
            "WiserHeatNOTUSED device 21",
        )
        self.assertEqual(
            self.helpers.get_legacy_device_identifier(self.data, 21),
            "WiserHeatNOTUSED Wiser RoomStat Andys Bedroom",
        )

    def test_legacy_naming_restores_room_context_without_changing_identity(self):
        for device_type, device_id, expected in (
            ("room", 7, "Wiser Andys Bedroom"),
            ("device", 21, "Wiser Thermostat Andys Bedroom"),
        ):
            self.data.legacy_naming = False
            identifier = self.helpers.get_identifier(self.data, device_id, device_type)
            unique_id = self.helpers.get_unique_id(self.data, "sensor", "Temperature", device_id)
            self.data.legacy_naming = True
            self.assertEqual(
                self.helpers.get_device_name(self.data, device_id, device_type), expected
            )
            self.assertEqual(
                self.helpers.get_identifier(self.data, device_id, device_type), identifier
            )
            self.assertEqual(
                self.helpers.get_unique_id(self.data, "sensor", "Temperature", device_id), unique_id
            )

    def test_legacy_temperature_sensor_name_and_unassigned_fallback(self):
        self.data.wiserhub.devices.get_by_id = lambda device_id: SimpleNamespace(
            id=device_id, name="Sensor 31", product_type="TemperatureHumiditySensor"
        )
        self.data.legacy_naming = False
        identifier = self.helpers.get_identifier(self.data, 31)
        self.data.legacy_naming = True
        self.assertEqual(
            self.helpers.get_device_name(self.data, 31),
            "Wiser Temperature/Humidity Sensor Andys Bedroom",
        )
        self.assertEqual(self.helpers.get_identifier(self.data, 31), identifier)
        self.data.wiserhub.rooms.get_by_device_id = lambda _id: None
        self.assertEqual(
            self.helpers.get_device_name(self.data, 31),
            "Wiser Temperature/Humidity Sensor Sensor 31",
        )
        self.data.legacy_naming = False
        self.assertEqual(
            self.helpers.get_device_name(self.data, 31),
            "Wiser Temperature/Humidity Sensor",
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
            "WiserHeatNOTUSED device 31",
        )
        self.assertEqual(
            self.helpers.get_legacy_device_identifier(self.data, 31),
            "WiserHeatNOTUSED Wiser TemperatureHumiditySensor "
            "Andys Bedroom Kitchen Temperature Sensor",
        )
        self.assertEqual(
            self.helpers.get_legacy_device_name(self.data, 31),
            "Wiser TemperatureHumiditySensor "
            "Andys Bedroom Kitchen Temperature Sensor",
        )

    def test_itrv_name_respects_legacy_option_without_changing_identity(self):
        self.data.wiserhub.devices.get_by_id = lambda device_id: SimpleNamespace(
            id=device_id,
            product_type="iTRV",
        )
        self.data.wiserhub.rooms.get_by_device_id = lambda _device_id: SimpleNamespace(
            id=7,
            name="Andys Bedroom",
            number_of_smartvalves=1,
            smartvalve_ids=[31],
        )

        self.data.legacy_naming = False
        self.assertEqual(self.helpers.get_device_name(self.data, 31), "Wiser iTRV")
        self.assertEqual(
            self.helpers.get_legacy_device_name(self.data, 31),
            "Wiser iTRV Andys Bedroom",
        )
        identifier = self.helpers.get_identifier(self.data, 31)
        self.assertEqual(identifier, "WiserHeatNOTUSED device 31")

        self.data.legacy_naming = True
        self.assertEqual(
            self.helpers.get_device_name(self.data, 31),
            "Wiser iTRV Andys Bedroom",
        )
        self.assertEqual(self.helpers.get_identifier(self.data, 31), identifier)

    def test_room_assigned_device_names_respect_legacy_option(self):
        room = SimpleNamespace(
            id=7,
            name="Andys Bedroom",
            number_of_heating_actuators=1,
            heating_actuator_ids=[31],
        )
        devices = {
            31: SimpleNamespace(
                id=31,
                name="Actuator",
                product_type="HeatingActuator",
                room_id=7,
            ),
            32: SimpleNamespace(
                id=32,
                name="Blind",
                product_type="Shutter",
                room_id=7,
            ),
            33: SimpleNamespace(
                id=33,
                name="Smoke Alarm",
                product_type="SmokeAlarmDevice",
                room_id=7,
            ),
        }
        self.data.wiserhub.devices.get_by_id = lambda device_id: devices[device_id]
        self.data.wiserhub.rooms.get_by_id = lambda _room_id: room
        self.data.wiserhub.rooms.get_by_device_id = lambda _device_id: room

        self.data.legacy_naming = False
        self.assertEqual(
            self.helpers.get_device_name(self.data, 31),
            "Wiser HeatingActuator",
        )
        self.assertEqual(
            self.helpers.get_device_name(self.data, 32),
            "Wiser Shutter Blind",
        )
        self.assertEqual(
            self.helpers.get_device_name(self.data, 33),
            "Wiser Smoke Alarm 33",
        )

        self.data.legacy_naming = True
        self.assertEqual(
            self.helpers.get_device_name(self.data, 31),
            "Wiser HeatingActuator Andys Bedroom",
        )
        self.assertEqual(
            self.helpers.get_device_name(self.data, 32),
            "Wiser Shutter Andys Bedroom Blind",
        )
        self.assertEqual(
            self.helpers.get_device_name(self.data, 33),
            "Wiser Andys Bedroom Smoke Alarm",
        )

    def test_historical_device_names_ignore_legacy_option(self):
        room = SimpleNamespace(
            id=7,
            name="Andys Bedroom",
            number_of_heating_actuators=1,
            heating_actuator_ids=[31],
        )
        device = SimpleNamespace(
            id=31,
            name="Actuator",
            product_type="HeatingActuator",
            room_id=7,
        )
        self.data.wiserhub.devices.get_by_id = lambda _device_id: device
        self.data.wiserhub.rooms.get_by_device_id = lambda _device_id: room

        self.data.legacy_naming = False
        modern_name = self.helpers.get_device_name(self.data, 31)
        historical_name = self.helpers.get_legacy_device_name(self.data, 31)

        self.assertEqual(modern_name, "Wiser HeatingActuator")
        self.assertEqual(
            historical_name,
            "Wiser HeatingActuator Andys Bedroom",
        )
        self.assertEqual(
            self.helpers.get_legacy_device_identifier(self.data, 31),
            "WiserHeatNOTUSED Wiser HeatingActuator Andys Bedroom",
        )

    def test_physical_entity_migration_uses_historical_itrv_name(self):
        device = SimpleNamespace(id=31, product_type="iTRV")
        room = SimpleNamespace(
            id=7,
            name="Andys Bedroom",
            number_of_smartvalves=1,
            smartvalve_ids=[31],
        )
        self.data.legacy_naming = False
        self.data.wiserhub.devices = SimpleNamespace(
            all=[device],
            get_by_id=lambda _device_id: device,
        )
        self.data.wiserhub.rooms.get_by_device_id = lambda _device_id: room

        mapping = self.helpers.build_physical_entity_unique_id_migration(
            self.data
        )
        old_unique_id = self.helpers.get_unique_id(
            self.data,
            "binary_sensor",
            "Controllable",
            "Wiser iTRV Andys Bedroom Controllable",
        )

        self.assertEqual(
            mapping[old_unique_id],
            self.helpers.get_physical_entity_unique_id(
                self.data, "binary_sensor", 31, "Controllable"
            ),
        )

    def test_physical_entity_unique_id_does_not_use_room_name(self):
        before = self.helpers.get_physical_entity_unique_id(
            self.data, "sensor", 31, "smartvalve_temp"
        )
        self.data.wiserhub.rooms.get_by_device_id = lambda _device_id: SimpleNamespace(
            id=7,
            name="Renamed Room",
        )
        self.assertEqual(
            self.helpers.get_physical_entity_unique_id(
                self.data, "sensor", 31, "smartvalve_temp"
            ),
            before,
        )

    def test_all_physical_device_identifiers_use_immutable_device_id(self):
        self.data.wiserhub.devices.get_by_id = lambda _device_id: (
            _ for _ in ()
        ).throw(
            AssertionError(
                "physical identifiers must not inspect mutable device data"
            )
        )

        self.assertEqual(
            self.helpers.get_identifier(self.data, 42),
            "WiserHeatNOTUSED device 42",
        )

    def test_physical_entity_migration_replaces_name_based_ids(self):
        device = SimpleNamespace(
            id=42,
            name="Bedroom Blind",
            product_type="Shutter",
        )
        self.data.wiserhub.devices = SimpleNamespace(
            all=[device],
            get_by_id=lambda _device_id: device,
        )

        mapping = self.helpers.build_physical_entity_unique_id_migration(
            self.data
        )
        old_cover_id = self.helpers.get_uuid_unique_id(
            "WiserHeatNOTUSED-Wisershutter-42-"
            "Wiser Shutter Andys Bedroom Bedroom Blind Control"
        )
        self.assertEqual(
            mapping[old_cover_id],
            self.helpers.get_physical_entity_unique_id(
                self.data, "cover", 42, "control"
            ),
        )

    def test_physical_entity_migration_uses_registry_device_names(self):
        device = SimpleNamespace(
            id=42,
            name="Bedroom Blind",
            product_type="Shutter",
        )
        self.data.wiserhub.devices = SimpleNamespace(
            all=[device],
            get_by_id=lambda _device_id: device,
        )

        mapping = self.helpers.build_physical_entity_unique_id_migration(
            self.data,
            legacy_device_names_by_id={
                42: {"Wiser Shutter Previous Bedroom Bedroom Blind"}
            },
            device_ids={42},
        )
        old_binary_id = self.helpers.get_unique_id(
            self.data,
            "binary_sensor",
            "Is Open",
            "Wiser Shutter Previous Bedroom Bedroom Blind Is Open",
        )
        old_cover_id = self.helpers.get_uuid_unique_id(
            "WiserHeatNOTUSED-Wisershutter-42-"
            "Wiser Shutter Previous Bedroom Bedroom Blind Control"
        )

        self.assertEqual(
            mapping[old_binary_id],
            self.helpers.get_physical_entity_unique_id(
                self.data, "binary_sensor", 42, "Is Open"
            ),
        )
        self.assertEqual(
            mapping[old_cover_id],
            self.helpers.get_physical_entity_unique_id(
                self.data, "cover", 42, "control"
            ),
        )

    def test_physical_sensor_migration_covers_humidity_power_and_energy(self):
        room = SimpleNamespace(
            id=7,
            name="Andys Bedroom",
            number_of_heating_actuators=1,
            heating_actuator_ids=[42],
        )
        devices = [
            SimpleNamespace(
                id=41,
                name="Roomstat",
                product_type="RoomStat",
            ),
            SimpleNamespace(
                id=42,
                name="Actuator",
                product_type="HeatingActuator",
            ),
        ]
        self.data.wiserhub.devices = SimpleNamespace(
            all=devices,
            get_by_id=lambda device_id: next(
                device for device in devices if device.id == device_id
            ),
        )
        self.data.wiserhub.rooms.get_by_device_id = lambda _device_id: room

        mapping = self.helpers.build_physical_entity_unique_id_migration(
            self.data,
            {"7": "Previous Bedroom"},
        )

        expected = {
            self.helpers.get_unique_id(
                self.data,
                "sensor",
                "LTS Humidity Andys Bedroom",
                41,
            ): self.helpers.get_physical_entity_unique_id(
                self.data, "sensor", 41, "humidity"
            ),
            self.helpers.get_unique_id(
                self.data,
                "sensor",
                "LTS Power Andys Bedroom",
                42,
            ): self.helpers.get_physical_entity_unique_id(
                self.data, "sensor", 42, "power"
            ),
            self.helpers.get_unique_id(
                self.data,
                "sensor",
                "LTS Energy Andys Bedroom",
                42,
            ): self.helpers.get_physical_entity_unique_id(
                self.data, "sensor", 42, "energy"
            ),
            self.helpers.get_unique_id(
                self.data,
                "sensor",
                "LTS Humidity Previous Bedroom",
                41,
            ): self.helpers.get_physical_entity_unique_id(
                self.data, "sensor", 41, "humidity"
            ),
            self.helpers.get_unique_id(
                self.data,
                "sensor",
                "LTS Power Previous Bedroom",
                42,
            ): self.helpers.get_physical_entity_unique_id(
                self.data, "sensor", 42, "power"
            ),
        }
        for old_unique_id, new_unique_id in expected.items():
            self.assertEqual(mapping[old_unique_id], new_unique_id)

    def test_room_entity_unique_id_does_not_use_room_name(self):
        before = self.helpers.get_room_entity_unique_id(
            self.data, 7, "current_temp"
        )
        self.data.wiserhub.rooms.get_by_id = lambda room_id: SimpleNamespace(
            id=room_id,
            name="Renamed Room",
        )
        self.assertEqual(
            self.helpers.get_room_entity_unique_id(
                self.data, 7, "current_temp"
            ),
            before,
        )


if __name__ == "__main__":
    unittest.main()
