"""Tests for Wiser room-migration orchestration."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock


COMPONENT_PATH = Path(__file__).parents[1] / "custom_components/wiser"


def _module(name: str, **attributes: object) -> ModuleType:
    module = ModuleType(name)
    module.__dict__.update(attributes)
    sys.modules[name] = module
    return module


def _load_wiser_init() -> ModuleType:
    """Load the integration module with lightweight dependency stubs."""
    _module("homeassistant")
    _module("homeassistant.config_entries", ConfigEntry=object)
    _module("homeassistant.const", CONF_NAME="name")
    _module(
        "homeassistant.core",
        HomeAssistant=object,
        callback=lambda function: function,
    )
    _module("homeassistant.exceptions", ConfigEntryNotReady=RuntimeError)

    area_registry = _module("homeassistant.helpers.area_registry")
    device_registry = _module(
        "homeassistant.helpers.device_registry",
        CONNECTION_NETWORK_MAC="mac",
    )
    entity_registry = _module("homeassistant.helpers.entity_registry")
    _module(
        "homeassistant.helpers",
        area_registry=area_registry,
        device_registry=device_registry,
        entity_registry=entity_registry,
    )
    _module("homeassistant.helpers.storage", Store=object)

    package = _module("wiser_init_test")
    package.__path__ = []
    constants = {
        name: name.lower()
        for name in (
            "CONF_AUTOMATIONS_HW_AUTO_MODE",
            "CONF_AUTOMATIONS_HW_CLIMATE",
            "CONF_AUTOMATIONS_HW_HEAT_MODE",
            "CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID",
            "CONF_AUTOMATIONS_PASSIVE",
            "CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT",
            "CONF_DEPRECATED_HW_TARGET_TEMP",
            "CONF_LEGACY_NAMING",
            "CONF_WISER_ROOM_NAMES",
            "DATA",
            "UPDATE_LISTENER",
        )
    }
    constants.update(
        DOMAIN="wiser",
        ENTITY_PREFIX="Wiser",
        MANUFACTURER="Drayton Wiser",
        WISER_PLATFORMS=[],
        WISER_SERVICES={},
        HWCycleModes=SimpleNamespace(CONTINUOUS="continuous", ONCE="once"),
    )
    _module("wiser_init_test.const", **constants)
    _module("wiser_init_test.coordinator", WiserUpdateCoordinator=object)

    device_helpers = {
        name: Mock(name=name)
        for name in (
            "assign_device_area_if_unset",
            "confirmed_deleted_room_ids",
            "find_physical_device_candidates",
            "known_wiser_room_area_name",
            "merge_legacy_hub_device",
            "migrate_entity_unique_id_duplicates",
            "migrate_physical_device",
            "migrate_room_entities",
            "migrate_room_device",
            "move_devices_from_managed_area",
            "register_hub_device",
            "register_room_assigned_device",
            "remove_room_devices",
            "room_names_with_pending_deletions",
        )
    }
    _module("wiser_init_test.device", **device_helpers)
    _module(
        "wiser_init_test.entity_migration",
        migrate_entity_unique_ids=Mock(),
    )
    _module("wiser_init_test.frontend", JSModuleRegistration=object)
    _module(
        "wiser_init_test.frontend.entry_updates",
        async_handle_entry_update=Mock(),
        integration_reload_settings=Mock(return_value={}),
    )
    _module(
        "wiser_init_test.frontend.wiser_sidebar",
        async_update_wiser_panel=Mock(),
    )
    helper_names = (
        "build_light_unique_id_migration",
        "build_physical_entity_unique_id_migration",
        "get_device_name",
        "get_hub_device_name",
        "get_identifier",
        "get_instance_count",
        "get_legacy_device_identifier",
        "get_legacy_room_identifier",
        "get_physical_entity_unique_id",
        "get_room_entity_unique_id",
        "get_unique_id",
    )
    _module(
        "wiser_init_test.helpers",
        **{name: Mock(name=name) for name in helper_names},
    )
    _module("wiser_init_test.services", async_setup_services=Mock())
    _module("wiser_init_test.update", async_unload_card_updates=Mock())
    _module("wiser_init_test.websockets", async_register_websockets=Mock())

    spec = importlib.util.spec_from_file_location(
        "wiser_init_test.__init__", COMPONENT_PATH / "__init__.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeStore:
    """Record delayed Home Assistant storage writes."""

    def __init__(self) -> None:
        self.saved = []

    def async_delay_save(self, data, delay) -> None:
        self.saved.append((data(), delay))


class RoomMigrationOrchestrationTest(unittest.TestCase):
    """Test composition of the room-migration helpers."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.wiser = _load_wiser_init()

    def setUp(self) -> None:
        self.entry = SimpleNamespace(entry_id="entry-id")
        self.room = SimpleNamespace(id=7, name="Lounge")
        self.coordinator = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(name="WiserHeat123456"),
                rooms=SimpleNamespace(all=[self.room]),
                devices=SimpleNamespace(all=[]),
            )
        )
        self.store = FakeStore()
        self.hass = SimpleNamespace(
            data={
                "wiser": {
                    "entry-id": {
                        "data": self.coordinator,
                        "conf_wiser_room_names": {"7": "Living Room"},
                        "room_names_store": self.store,
                        "missing_room_counts": {},
                    }
                }
            },
            config_entries=SimpleNamespace(
                async_update_entry=Mock(
                    side_effect=AssertionError("must not update config entry")
                )
            ),
        )

    def test_refresh_moves_areas_and_saves_names_without_config_reload(self) -> None:
        self.wiser._confirmed_deleted_room_ids = Mock(return_value=set())
        self.wiser.remove_deleted_room_devices = Mock()
        self.wiser.sync_wiser_room_areas = Mock()
        self.wiser.room_names_with_pending_deletions = Mock(
            return_value={"7": "Lounge"}
        )

        self.wiser._sync_wiser_room_names(
            self.hass, self.entry, self.coordinator
        )

        self.wiser.remove_deleted_room_devices.assert_called_once_with(
            self.hass,
            self.entry,
            {"7": "Living Room"},
            set(),
        )
        self.wiser.sync_wiser_room_areas.assert_called_once_with(
            self.hass,
            self.entry,
            {"7": "Living Room"},
        )
        self.assertEqual(self.store.saved, [({"7": "Lounge"}, 1)])
        self.assertEqual(
            self.hass.data["wiser"]["entry-id"]["conf_wiser_room_names"],
            {"7": "Lounge"},
        )

    def test_confirmed_room_removal_passes_only_deleted_room_identifiers(self) -> None:
        self.wiser.get_identifier = Mock(
            return_value="WiserHeat123456 room 7"
        )
        self.wiser.remove_room_devices = Mock(return_value=1)
        self.wiser.dr.async_get = Mock(return_value="device-registry")
        self.wiser.er.async_get = Mock(return_value="entity-registry")

        removed = self.wiser.remove_deleted_room_devices(
            self.hass,
            self.entry,
            {"7": "Living Room", "8": "Kitchen"},
            {"7"},
        )

        self.assertEqual(removed, 1)
        self.wiser.remove_room_devices.assert_called_once_with(
            "device-registry",
            "entity-registry",
            "entry-id",
            [
                ("wiser", "WiserHeat123456 room 7"),
                ("wiser", "WiserHeat123456 Wiser Living Room"),
            ],
        )

    def test_physical_migration_composes_power_and_energy_migrations(self) -> None:
        device = SimpleNamespace(
            id=42,
            product_type="HeatingActuator",
            firmware_version="1.0",
            floor_temperature_sensor=None,
        )
        physical_device = SimpleNamespace(
            id="physical-device",
            identifiers={("wiser", "legacy-device")},
        )
        power = SimpleNamespace(
            entity_id="sensor.power",
            unique_id="old-power",
            device_id="physical-device",
            domain="sensor",
            platform="wiser",
        )
        energy = SimpleNamespace(
            entity_id="sensor.energy",
            unique_id="old-energy",
            device_id="physical-device",
            domain="sensor",
            platform="wiser",
        )
        device_registry = SimpleNamespace()
        entity_registry = SimpleNamespace(entities={})
        self.coordinator.wiserhub.devices.all = [device]
        self.coordinator.wiserhub.rooms.get_by_device_id = Mock(
            return_value=self.room
        )
        self.wiser.dr.async_get = Mock(return_value=device_registry)
        self.wiser.dr.async_entries_for_config_entry = Mock(
            return_value=[physical_device]
        )
        self.wiser.er.async_get = Mock(return_value=entity_registry)
        self.wiser.er.async_entries_for_config_entry = Mock(
            return_value=[power, energy]
        )
        self.wiser.ar.async_get = Mock(return_value="area-registry")
        self.wiser.get_identifier = Mock(return_value="stable-device")
        self.wiser.get_legacy_device_identifier = Mock(
            return_value="legacy-device"
        )
        self.wiser.get_unique_id = Mock(
            side_effect=lambda _data, _domain, entity_type, _device_id: (
                f"base-{entity_type}"
            )
        )
        self.wiser.get_physical_entity_unique_id = Mock(
            side_effect=lambda _data, _domain, device_id, entity_type: (
                f"stable-{entity_type}-{device_id}"
            )
        )
        self.wiser.build_physical_entity_unique_id_migration = Mock(
            return_value={
                "old-power": "stable-power-42",
                "old-energy": "stable-energy-42",
            }
        )
        self.wiser.find_physical_device_candidates = Mock(
            return_value=[physical_device]
        )
        self.wiser.migrate_entity_unique_id_duplicates = Mock()
        self.wiser.migrate_physical_device = Mock(
            return_value=physical_device
        )
        self.wiser.get_device_name = Mock(return_value="Wiser HeatingActuator")
        self.wiser.assign_device_area_if_unset = Mock()

        self.wiser.migrate_physical_device_registry(
            self.hass,
            self.entry,
            "hub-device",
            {"7": "Living Room"},
        )

        migrations = {
            call.args[2]: {entry.entity_id for entry in call.args[1]}
            for call in self.wiser.migrate_entity_unique_id_duplicates.call_args_list
        }
        self.assertEqual(
            migrations,
            {
                "stable-power-42": {"sensor.power"},
                "stable-energy-42": {"sensor.energy"},
            },
        )
        self.wiser.migrate_physical_device.assert_called_once()

    def test_area_sync_composes_room_and_physical_devices(self) -> None:
        room_device = SimpleNamespace(id="room-device", area_id="old-area")
        physical_device = SimpleNamespace(id="physical-device", area_id="old-area")
        physical = SimpleNamespace(id=31)
        self.coordinator.wiserhub.devices.all = [physical]
        self.coordinator.wiserhub.rooms.get_by_device_id = Mock(
            return_value=self.room
        )
        self.wiser.dr.async_get = Mock(return_value="device-registry")
        self.wiser.ar.async_get = Mock(return_value="area-registry")
        self.wiser.get_identifier = Mock(
            side_effect=lambda _data, item_id, device_type="device": (
                f"room-{item_id}"
                if device_type == "room"
                else f"device-{item_id}"
            )
        )
        self.wiser._device_by_identifier = Mock(
            side_effect=[room_device, physical_device]
        )
        self.wiser.move_devices_from_managed_area = Mock(return_value=2)

        moved = self.wiser.sync_wiser_room_areas(
            self.hass,
            self.entry,
            {"7": "Living Room"},
        )

        self.assertEqual(moved, 2)
        self.wiser.move_devices_from_managed_area.assert_called_once_with(
            "device-registry",
            "area-registry",
            [room_device, physical_device],
            "Living Room",
            "Lounge",
        )


if __name__ == "__main__":
    unittest.main()
