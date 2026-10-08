"""Tests for Wiser device-registry migration helpers."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    created_at: datetime | None = None


@dataclass
class EntityEntry:
    """Minimal entity-registry entry used by the tests."""

    entity_id: str
    device_id: str | None
    domain: str = "sensor"
    platform: str = "wiser"
    unique_id: str = ""
    created_at: datetime | None = None
    translation_key: str | None = None
    device_class: str | None = None
    original_device_class: str | None = None


@dataclass
class AreaEntry:
    """Minimal area-registry entry used by the tests."""

    id: str
    name: str = ""


class AreaRegistry:
    """Minimal Home Assistant area registry."""

    def __init__(self) -> None:
        self.requested = []
        self.areas = {}

    def async_get_or_create(self, name):
        self.requested.append(name)
        area = self.async_get_area_by_name(name)
        if area is None:
            area = AreaEntry(name.lower().replace(" ", "_"), name)
            self.areas[area.id] = area
        return area

    def async_get_area_by_name(self, name):
        return next(
            (area for area in self.areas.values() if area.name == name),
            None,
        )

    def async_get_area(self, area_id):
        return self.areas.get(area_id)


class EntityRegistry:
    """Minimal Home Assistant entity registry."""

    def __init__(self, entities=None) -> None:
        self.entities = entities or {}
        self.updated = []
        self.removed = []

    def async_get_entity_id(self, domain, platform, unique_id):
        return next(
            (
                entry.entity_id
                for entry in self.entities.values()
                if entry.domain == domain
                and entry.platform == platform
                and entry.unique_id == unique_id
            ),
            None,
        )

    def async_get(self, entity_id):
        return self.entities.get(entity_id)

    def async_update_entity(self, entity_id, **kwargs) -> None:
        self.updated.append((entity_id, kwargs))

    def async_remove(self, entity_id) -> None:
        self.removed.append(entity_id)


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


class AssignDeviceAreaIfUnsetTest(unittest.TestCase):
    """Test conservative assignment of Wiser devices to areas."""

    def test_assigns_unassigned_device_to_wiser_room_area(self) -> None:
        device_registry = DeviceRegistry()
        area_registry = AreaRegistry()

        result = DEVICE.assign_device_area_if_unset(
            device_registry,
            area_registry,
            DeviceEntry("room-device"),
            "Andys Bedroom",
        )

        self.assertEqual(area_registry.requested, ["Andys Bedroom"])
        self.assertEqual(
            device_registry.updated,
            [("room-device", {"area_id": "andys_bedroom"})],
        )
        self.assertEqual(result.id, "room-device")

    def test_preserves_existing_user_area(self) -> None:
        device_registry = DeviceRegistry()
        area_registry = AreaRegistry()
        device = DeviceEntry("room-device", area_id="custom_area")

        result = DEVICE.assign_device_area_if_unset(
            device_registry, area_registry, device, "Andys Bedroom"
        )

        self.assertIs(result, device)
        self.assertEqual(area_registry.requested, [])
        self.assertEqual(device_registry.updated, [])

    def test_moves_only_devices_still_in_previous_managed_area(self) -> None:
        device_registry = DeviceRegistry()
        area_registry = AreaRegistry()
        area_registry.areas["test"] = AreaEntry("test", "Test")
        devices = [
            DeviceEntry("room-device", area_id="test"),
            DeviceEntry("itrv", area_id="test"),
            DeviceEntry("manually-moved", area_id="upstairs"),
        ]

        moved = DEVICE.move_devices_from_managed_area(
            device_registry,
            area_registry,
            devices,
            "Test",
            "Test2",
        )

        self.assertEqual(moved, 2)
        self.assertEqual(
            device_registry.updated,
            [
                ("room-device", {"area_id": "test2"}),
                ("itrv", {"area_id": "test2"}),
            ],
        )


class MigrateRoomDeviceTest(unittest.TestCase):
    """Test migration of logical Wiser room devices."""

    identifier = ("wiser", "WiserHeat123456 room 7")
    legacy_identifier = ("wiser", "WiserHeat123456 Wiser Andys Bedroom")
    config_entry_id = "entry-id"

    def test_creates_missing_room_device_before_entity_setup(self) -> None:
        device_registry = DeviceRegistry()
        area_registry = AreaRegistry()

        result = DEVICE.migrate_room_device(
            device_registry,
            EntityRegistry(),
            self.config_entry_id,
            self.identifier,
            self.legacy_identifier,
            "Wiser Room",
            via_device=("wiser", "WiserHeat123456"),
        )
        result = DEVICE.assign_device_area_if_unset(
            device_registry, area_registry, result, "Test"
        )

        self.assertEqual(result.id, "new-hub")
        self.assertEqual(
            device_registry.created,
            [
                {
                    "config_entry_id": self.config_entry_id,
                    "identifiers": {self.identifier},
                    "name": "Wiser Room",
                    "via_device": ("wiser", "WiserHeat123456"),
                }
            ],
        )
        self.assertEqual(area_registry.requested, ["Test"])
        self.assertEqual(
            device_registry.updated,
            [("new-hub", {"area_id": "test"})],
        )

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
            "Wiser Room",
        )

        self.assertEqual(result.id, "room-device")
        self.assertEqual(registry.updated[0][0], "room-device")
        self.assertEqual(
            registry.updated[0][1]["new_identifiers"], {self.identifier}
        )
        self.assertEqual(registry.updated[0][1]["name"], "Wiser Room")
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
            "Wiser Room",
        )

        self.assertEqual(result.id, "stable-room")
        self.assertEqual(
            entity_registry.updated,
            [("sensor.temperature", {"device_id": "stable-room"})],
        )
        self.assertEqual(registry.removed, ["legacy-room"])

    def test_preserves_legacy_area_when_merging_duplicate_room(self) -> None:
        registry = DeviceRegistry(
            {
                (self.identifier, self.config_entry_id): DeviceEntry("stable-room"),
                (self.legacy_identifier, self.config_entry_id): DeviceEntry(
                    "legacy-room", area_id="custom_area"
                ),
            }
        )

        DEVICE.migrate_room_device(
            registry,
            EntityRegistry(),
            self.config_entry_id,
            self.identifier,
            self.legacy_identifier,
            "Wiser Room",
        )

        self.assertEqual(registry.updated[0][0], "stable-room")
        self.assertEqual(registry.updated[0][1]["area_id"], "custom_area")


class RemoveRoomDevicesTest(unittest.TestCase):
    """Test cleanup of rooms removed from the Wiser system."""

    config_entry_id = "entry-id"
    stable_identifier = ("wiser", "WiserHeat123456 room 7")
    legacy_identifier = ("wiser", "WiserHeat123456 Wiser Test")

    def test_removes_room_device_and_its_entities(self) -> None:
        room = DeviceEntry("room-device")
        registry = DeviceRegistry(
            {
                (self.stable_identifier, self.config_entry_id): room,
                (self.legacy_identifier, self.config_entry_id): room,
            }
        )
        entities = EntityRegistry(
            {
                "climate.test": EntityEntry("climate.test", "room-device"),
                "sensor.other": EntityEntry("sensor.other", "other-device"),
            }
        )

        removed = DEVICE.remove_room_devices(
            registry,
            entities,
            self.config_entry_id,
            (self.stable_identifier, self.legacy_identifier),
        )

        self.assertEqual(removed, 1)
        self.assertEqual(entities.removed, ["climate.test"])
        self.assertEqual(registry.removed, ["room-device"])

    def test_ignores_unknown_room_identifiers(self) -> None:
        registry = DeviceRegistry()
        entities = EntityRegistry()

        removed = DEVICE.remove_room_devices(
            registry,
            entities,
            self.config_entry_id,
            (self.stable_identifier,),
        )

        self.assertEqual(removed, 0)
        self.assertEqual(entities.removed, [])
        self.assertEqual(registry.removed, [])


class MigratePhysicalDeviceTest(unittest.TestCase):
    """Test migration of room-derived physical device records."""

    def test_uses_identifier_parent_only_when_creating_device(self) -> None:
        registry = DeviceRegistry()

        result = DEVICE.migrate_physical_device(
            registry,
            EntityRegistry(),
            "entry-id",
            ("wiser", "WiserHeat123456 device 31"),
            [],
            "Wiser iTRV",
            via_device=("wiser", "WiserHeat123456"),
            via_device_id="physical-hub-id",
            model="iTRV",
        )

        self.assertEqual(result.id, "new-hub")
        self.assertEqual(
            registry.created,
            [
                {
                    "config_entry_id": "entry-id",
                    "identifiers": {
                        ("wiser", "WiserHeat123456 device 31")
                    },
                    "name": "Wiser iTRV",
                    "via_device": ("wiser", "WiserHeat123456"),
                    "model": "iTRV",
                }
            ],
        )

    def test_keeps_oldest_device_and_merges_renamed_duplicate(self) -> None:
        old = DeviceEntry(
            "old-device",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        renamed = DeviceEntry(
            "renamed-device",
            created_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        )
        registry = DeviceRegistry()
        entities = EntityRegistry(
            {
                "sensor.old_temperature": EntityEntry(
                    "sensor.old_temperature", "old-device"
                ),
                "sensor.signal": EntityEntry("sensor.signal", "renamed-device"),
            }
        )

        result = DEVICE.migrate_physical_device(
            registry,
            entities,
            "entry-id",
            ("wiser", "WiserHeat123456 device 31"),
            [renamed, old],
            "Wiser iTRV",
            via_device=("wiser", "WiserHeat123456"),
            via_device_id="physical-hub-id",
            model="iTRV",
        )

        self.assertEqual(result.id, "old-device")
        self.assertEqual(registry.updated[0][0], "old-device")
        self.assertEqual(
            registry.updated[0][1]["new_identifiers"],
            {("wiser", "WiserHeat123456 device 31")},
        )
        self.assertEqual(
            registry.updated[0][1]["via_device_id"], "physical-hub-id"
        )
        self.assertNotIn("via_device", registry.updated[0][1])
        self.assertEqual(
            entities.updated,
            [("sensor.signal", {"device_id": "old-device"})],
        )
        self.assertEqual(registry.removed, ["renamed-device"])

    def test_keeps_oldest_temperature_entity_and_removes_duplicate(self) -> None:
        old = EntityEntry(
            "sensor.room_temperature",
            "old-device",
            unique_id="old-room-id",
            created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
        renamed = EntityEntry(
            "sensor.test_temperature",
            "renamed-device",
            unique_id="renamed-room-id",
            created_at=datetime(2026, 10, 1, tzinfo=timezone.utc),
        )
        entities = EntityRegistry(
            {old.entity_id: old, renamed.entity_id: renamed}
        )

        result = DEVICE.migrate_entity_unique_id_duplicates(
            entities,
            [renamed, old],
            "stable-id",
        )

        self.assertEqual(result.entity_id, "sensor.room_temperature")
        self.assertEqual(
            entities.updated,
            [("sensor.room_temperature", {"new_unique_id": "stable-id"})],
        )
        self.assertEqual(entities.removed, ["sensor.test_temperature"])

    def test_migrates_all_room_name_derived_entity_types(self) -> None:
        entities = {}
        definitions = (
            ("climate", None, None, "climate"),
            ("switch", "window_detection", None, "switch_window_detection"),
            ("sensor", "heating_demand", None, "heating_demand"),
            ("sensor", "target_temperature", "temperature", "current_target_temp"),
            ("sensor", None, "temperature", "current_temp"),
        )
        for domain, translation_key, device_class, expected_type in definitions:
            for suffix, created_at in (
                ("old", datetime(2026, 1, 1, tzinfo=timezone.utc)),
                ("new", datetime(2026, 10, 1, tzinfo=timezone.utc)),
            ):
                entity_id = f"{domain}.{expected_type}_{suffix}"
                entities[entity_id] = EntityEntry(
                    entity_id,
                    "room-device",
                    domain=domain,
                    unique_id=f"{expected_type}-{suffix}",
                    created_at=created_at,
                    translation_key=translation_key,
                    device_class=device_class,
                )
        registry = EntityRegistry(entities)

        DEVICE.migrate_room_entities(
            registry,
            "room-device",
            lambda entity_type: f"stable-{entity_type}",
        )

        self.assertEqual(len(registry.updated), len(definitions))
        self.assertEqual(len(registry.removed), len(definitions))
        self.assertEqual(
            {update[1]["new_unique_id"] for update in registry.updated},
            {f"stable-{definition[3]}" for definition in definitions},
        )
