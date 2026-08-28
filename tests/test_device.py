"""Tests for Wiser device-registry migration helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import unittest


SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/device.py"
SPEC = spec_from_file_location("wiser_device", SOURCE_PATH)
assert SPEC and SPEC.loader
DEVICE = module_from_spec(SPEC)
SPEC.loader.exec_module(DEVICE)


@dataclass
class DeviceEntry:
    """Minimal device-registry entry used by the tests."""

    id: str
    area_id: str | None = None
    labels: set = field(default_factory=set)
    name_by_user: str | None = None


@dataclass
class EntityEntry:
    """Minimal entity-registry entry used by the tests."""

    entity_id: str
    device_id: str | None


class EntityRegistry:
    """Minimal Home Assistant entity registry."""

    def __init__(self, entities=None) -> None:
        self.entities = entities or {}
        self.updated = []

    def async_update_entity(self, entity_id, **kwargs) -> None:
        self.updated.append((entity_id, kwargs))


class DeviceRegistry:
    """Minimal current Home Assistant device registry."""

    def __init__(self, devices=None) -> None:
        self.devices = devices or {}
        self.removed = []
        self.updated = []
        self.created = []

    def async_get_device_by_identifier(self, identifier, config_entry_id):
        return self.devices.get((identifier, config_entry_id))

    def async_remove_device(self, device_id) -> None:
        self.removed.append(device_id)

    def async_update_device(self, device_id, **kwargs):
        self.updated.append((device_id, kwargs))
        return DeviceEntry(device_id)

    def async_get_or_create(self, **kwargs):
        self.created.append(kwargs)
        return DeviceEntry("new-hub")


class RegisterHubDeviceTest(unittest.TestCase):
    """Test registration and migration of the HeatHub device."""

    identifier = ("wiser", "WiserHeat123456")
    legacy_identifier = ("wiser", "WiserHeat123456 Wiser HeatHub")
    connection = ("mac", "aa:bb:cc:dd:ee:ff")
    config_entry_id = "entry-id"
    device_info = {
        "manufacturer": "Drayton Wiser",
        "model": "CCTFR6311G2",
        "name": "Wiser HeatHub (WiserHeat123456)",
        "sw_version": "4.48.2",
    }

    def test_keeps_physical_hub_when_legacy_controller_also_exists(self) -> None:
        registry = DeviceRegistry(
            {
                (self.identifier, self.config_entry_id): DeviceEntry(
                    "empty-hub",
                    area_id="house",
                    labels={"heating"},
                    name_by_user="My HeatHub",
                ),
                (self.legacy_identifier, self.config_entry_id): DeviceEntry(
                    "controller"
                ),
            }
        )

        result = DEVICE.register_hub_device(
            registry,
            self.config_entry_id,
            self.identifier,
            self.legacy_identifier,
            self.connection,
            **self.device_info,
        )

        self.assertEqual(result.id, "empty-hub")
        self.assertEqual(registry.removed, [])
        self.assertEqual(registry.updated[0][0], "empty-hub")
        self.assertEqual(
            registry.updated[0][1]["new_identifiers"], {self.identifier}
        )
        self.assertEqual(
            registry.updated[0][1]["new_connections"], {self.connection}
        )
        self.assertIsNone(registry.updated[0][1]["via_device_id"])
        self.assertEqual(registry.created, [])

    def test_migrates_controller_when_physical_hub_is_missing(self) -> None:
        registry = DeviceRegistry(
            {
                (self.legacy_identifier, self.config_entry_id): DeviceEntry(
                    "controller"
                )
            }
        )

        result = DEVICE.register_hub_device(
            registry,
            self.config_entry_id,
            self.identifier,
            self.legacy_identifier,
            self.connection,
            **self.device_info,
        )

        self.assertEqual(result.id, "controller")
        self.assertEqual(registry.updated[0][0], "controller")
        self.assertEqual(
            registry.updated[0][1]["new_identifiers"], {self.identifier}
        )

    def test_creates_physical_hub_for_new_installation(self) -> None:
        registry = DeviceRegistry()

        result = DEVICE.register_hub_device(
            registry,
            self.config_entry_id,
            self.identifier,
            self.legacy_identifier,
            self.connection,
            **self.device_info,
        )

        self.assertEqual(result.id, "new-hub")
        self.assertEqual(registry.removed, [])
        self.assertEqual(registry.updated, [])
        self.assertEqual(registry.created[0]["identifiers"], {self.identifier})
        self.assertEqual(registry.created[0]["connections"], {self.connection})


    def test_moves_legacy_entities_then_removes_controller(self) -> None:
        registry = DeviceRegistry(
            {
                (self.identifier, self.config_entry_id): DeviceEntry("real-hub"),
                (self.legacy_identifier, self.config_entry_id): DeviceEntry(
                    "controller"
                )
            }
        )
        entity_registry = EntityRegistry(
            {
                "sensor.signal": EntityEntry("sensor.signal", "controller"),
                "climate.room": EntityEntry("climate.room", "room-device"),
            }
        )

        merged = DEVICE.merge_legacy_hub_device(
            registry,
            entity_registry,
            self.config_entry_id,
            self.identifier,
            self.legacy_identifier,
        )

        self.assertTrue(merged)
        self.assertEqual(
            entity_registry.updated,
            [("sensor.signal", {"device_id": "real-hub"})],
        )
        self.assertEqual(registry.removed, ["controller"])

    def test_does_nothing_without_physical_hub(self) -> None:
        registry = DeviceRegistry(
            {
                (self.legacy_identifier, self.config_entry_id): DeviceEntry(
                    "controller"
                )
            }
        )

        entity_registry = EntityRegistry(
            {"sensor.signal": EntityEntry("sensor.signal", "controller")}
        )

        merged = DEVICE.merge_legacy_hub_device(
            registry,
            entity_registry,
            self.config_entry_id,
            self.identifier,
            self.legacy_identifier,
        )

        self.assertFalse(merged)
        self.assertEqual(entity_registry.updated, [])
        self.assertEqual(registry.removed, [])


class RegisterRoomAssignedDeviceTest(unittest.TestCase):
    """Test creation-time area assignment for physical Wiser devices."""

    def test_registers_device_with_area_and_physical_hub_parent(self) -> None:
        registry = DeviceRegistry()

        DEVICE.register_room_assigned_device(
            registry,
            "entry-id",
            ("wiser", "WiserHeat123456 Wiser Thermostat"),
            "physical-hub-id",
            "Andys Bedroom",
            manufacturer="Drayton Wiser",
            name="Wiser Thermostat",
            model="RoomStat",
            sw_version="4.48.2",
        )

        created = registry.created[0]
        self.assertEqual(created["suggested_area"], "Andys Bedroom")
        self.assertEqual(created["via_device_id"], "physical-hub-id")
        self.assertEqual(
            created["identifiers"],
            {("wiser", "WiserHeat123456 Wiser Thermostat")},
        )


class MigrateRoomDeviceTest(unittest.TestCase):
    """Test migration of logical Wiser room devices."""

    identifier = ("wiser", "WiserHeat123456 room 7")
    legacy_identifier = ("wiser", "WiserHeat123456 Wiser Andys Bedroom")
    config_entry_id = "entry-id"

    def test_migrates_legacy_room_identifier_and_name(self) -> None:
        registry = DeviceRegistry(
            {
                (self.legacy_identifier, self.config_entry_id): DeviceEntry(
                    "room-device", area_id="andys_bedroom"
                )
            }
        )

        result = DEVICE.migrate_room_device(
            registry,
            EntityRegistry(),
            self.config_entry_id,
            self.identifier,
            self.legacy_identifier,
            "Wiser Heating",
        )

        self.assertEqual(result.id, "room-device")
        self.assertEqual(registry.updated[0][0], "room-device")
        self.assertEqual(
            registry.updated[0][1]["new_identifiers"], {self.identifier}
        )
        self.assertEqual(registry.updated[0][1]["name"], "Wiser Heating")
        self.assertNotIn("area_id", registry.updated[0][1])
        self.assertEqual(registry.removed, [])

    def test_merges_duplicate_legacy_room_into_stable_room(self) -> None:
        registry = DeviceRegistry(
            {
                (self.identifier, self.config_entry_id): DeviceEntry("stable-room"),
                (self.legacy_identifier, self.config_entry_id): DeviceEntry(
                    "legacy-room"
                ),
            }
        )
        entity_registry = EntityRegistry(
            {
                "sensor.temperature": EntityEntry(
                    "sensor.temperature", "legacy-room"
                )
            }
        )

        result = DEVICE.migrate_room_device(
            registry,
            entity_registry,
            self.config_entry_id,
            self.identifier,
            self.legacy_identifier,
            "Wiser Heating",
        )

        self.assertEqual(result.id, "stable-room")
        self.assertEqual(
            entity_registry.updated,
            [("sensor.temperature", {"device_id": "stable-room"})],
        )
        self.assertEqual(registry.removed, ["legacy-room"])
