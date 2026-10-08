"""Drayton Wiser Compoment for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
msparker@sky.com
"""

import asyncio
from functools import partial
import logging
import re

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.storage import Store

from .const import (
    CONF_AUTOMATIONS_HW_AUTO_MODE,
    CONF_AUTOMATIONS_HW_CLIMATE,
    CONF_AUTOMATIONS_HW_HEAT_MODE,
    CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID,
    CONF_AUTOMATIONS_PASSIVE,
    CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT,
    CONF_DEPRECATED_HW_TARGET_TEMP,
    CONF_LEGACY_NAMING,
    CONF_OPENTHERM_EVER_CONNECTED,
    CONF_WISER_ROOM_NAMES,
    DATA,
    DOMAIN,
    ENTITY_PREFIX,
    MANUFACTURER,
    UPDATE_LISTENER,
    WISER_PLATFORMS,
    WISER_SERVICES,
    HWCycleModes,
)
from .coordinator import WiserUpdateCoordinator
from .device import (
    assign_device_area_if_unset,
    confirmed_deleted_room_ids,
    find_physical_device_candidates,
    known_wiser_room_area_name,
    merge_legacy_hub_device,
    migrate_entity_unique_id_duplicates,
    migrate_physical_device,
    migrate_room_entities,
    migrate_room_device,
    move_devices_from_managed_area,
    register_hub_device,
    register_room_assigned_device,
    remove_room_devices,
    room_names_with_pending_deletions,
)
from .entity_migration import migrate_entity_unique_ids
from .frontend import JSModuleRegistration
from .frontend.entry_updates import async_handle_entry_update, integration_reload_settings
from .frontend.wiser_sidebar import async_update_wiser_panel
from .helpers import (
    active_wiser_rooms,
    build_light_unique_id_migration,
    build_physical_entity_unique_id_migration,
    get_device_name,
    get_hub_device_name,
    get_identifier,
    get_instance_count,
    get_legacy_device_identifier,
    get_legacy_room_identifier,
    get_physical_entity_unique_id,
    get_room_entity_unique_id,
    get_unique_id,
)
from .opentherm_detection import (
    opentherm_entity_unique_ids,
    opentherm_is_detected,
)
from .services import async_setup_services
from .update import async_unload_card_updates
from .websockets import async_register_websockets

ROOM_NAMES_STORAGE_VERSION = 1
ROOM_NAMES_STORAGE_KEY = f"{DOMAIN}.{{}}.room_names"
ROOM_NAMES_STORE = "room_names_store"

_LOGGER = logging.getLogger(__name__)


def _initial_room_names(stored_room_names, config_entry_room_names):
    """Return validated migration and runtime room-name state."""
    if isinstance(stored_room_names, dict):
        room_names = dict(stored_room_names)
        return room_names, room_names
    if isinstance(config_entry_room_names, dict):
        room_names = dict(config_entry_room_names)
        return room_names, room_names
    return {}, None


async def async_migrate_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug(
        "Migrating configuration from version %s.%s",
        config_entry.version,
        config_entry.minor_version,
    )

    if config_entry.version == 1:
        new_options = {**config_entry.options}
        if config_entry.minor_version < 3:
            # move passive mode options into new section
            if new_options.get(CONF_AUTOMATIONS_PASSIVE) is not None:
                # detect if failed last upgrade to minor version 2
                if isinstance(new_options.get(CONF_AUTOMATIONS_PASSIVE), bool):
                    new_options[CONF_AUTOMATIONS_PASSIVE] = {
                        CONF_AUTOMATIONS_PASSIVE: new_options[CONF_AUTOMATIONS_PASSIVE]
                    }
                    for item in [
                        CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT,
                    ]:
                        if new_options.get(item):
                            new_options[CONF_AUTOMATIONS_PASSIVE][item] = new_options[
                                item
                            ]
                            del new_options[item]

            # hw climate
            if new_options.get(CONF_AUTOMATIONS_HW_CLIMATE) is not None:
                # detect if failed last upgrade to minor version 2
                if isinstance(new_options.get(CONF_AUTOMATIONS_HW_CLIMATE), bool):
                    if new_options.get(CONF_DEPRECATED_HW_TARGET_TEMP):
                        del new_options[CONF_DEPRECATED_HW_TARGET_TEMP]

                    new_options[CONF_AUTOMATIONS_HW_CLIMATE] = {
                        CONF_AUTOMATIONS_HW_CLIMATE: new_options[
                            CONF_AUTOMATIONS_HW_CLIMATE
                        ]
                    }
                    for item in [
                        CONF_AUTOMATIONS_HW_AUTO_MODE,
                        CONF_AUTOMATIONS_HW_HEAT_MODE,
                        CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID,
                    ]:
                        if value := new_options.get(item):
                            if value == "Normal":
                                value = HWCycleModes.CONTINUOUS
                            if value == "Override":
                                value = HWCycleModes.ONCE
                            new_options[CONF_AUTOMATIONS_HW_CLIMATE][item] = value
                            del new_options[item]

        if config_entry.minor_version < 4:
            migrated_count = migrate_entity_unique_ids(hass, config_entry.entry_id)
            _LOGGER.info(
                "Migrated %s Wiser entity unique IDs to UUIDv5",
                migrated_count,
            )

        if config_entry.minor_version < 5:
            # Keep room context visible for installations upgrading to UI options.
            new_options.setdefault(CONF_LEGACY_NAMING, True)

        hass.config_entries.async_update_entry(
            config_entry, options=new_options, minor_version=5, version=1
        )

    _LOGGER.debug(
        "Migration to configuration version %s.%s successful",
        config_entry.version,
        config_entry.minor_version,
    )

    return True


async def async_migrate_physical_entity_unique_ids(
    hass: HomeAssistant,
    config_entry,
    data,
    previous_room_names=None,
) -> None:
    """Preserve physical entities while adopting stable unique IDs.

    This includes the multi-gang light migration and physical entities whose
    historical unique IDs included mutable device or room names.
    """
    mapping = {
        **build_physical_entity_unique_id_migration(
            data, previous_room_names
        ),
        # Light channels need the more specific per-channel migration when a
        # physical device exposes more than one light.
        **build_light_unique_id_migration(data),
    }
    if not mapping:
        return

    ent_reg = er.async_get(hass)

    @callback
    def _migrate(entry: er.RegistryEntry) -> dict | None:
        new_unique_id = mapping.get(entry.unique_id)
        if not new_unique_id:
            return None
        # The original migration could create the target entry while the
        # capability binary sensors continued to register with their old
        # unique_id. Keep both registry records so history is recoverable;
        # the legacy-ID entry becomes unavailable after platform setup.
        target_entity_id = ent_reg.async_get_entity_id(
            entry.domain, entry.platform, new_unique_id
        )
        if target_entity_id:
            target_entry = ent_reg.async_get(target_entity_id)
            if (
                target_entry
                and target_entry.config_entry_id == config_entry.entry_id
            ):
                _LOGGER.warning(
                    "Wiser: retaining duplicate legacy entity %s; target is %s",
                    entry.entity_id,
                    target_entity_id,
                )
                return None
            _LOGGER.warning(
                "Wiser: not migrating unique_id %s -> %s, target already exists",
                entry.unique_id,
                new_unique_id,
            )
            return None
        _LOGGER.info(
            "Wiser: migrating entity unique_id %s -> %s",
            entry.unique_id,
            new_unique_id,
        )
        return {"new_unique_id": new_unique_id}

    await er.async_migrate_entries(hass, config_entry.entry_id, _migrate)


async def async_setup_entry(hass: HomeAssistant, config_entry):
    """Set up Wiser from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = WiserUpdateCoordinator(hass, config_entry)

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_status == "Success":
        raise ConfigEntryNotReady

    room_names_store = Store(
        hass,
        ROOM_NAMES_STORAGE_VERSION,
        ROOM_NAMES_STORAGE_KEY.format(config_entry.entry_id),
    )
    stored_room_names = await room_names_store.async_load()
    previous_room_names, runtime_room_names = _initial_room_names(
        stored_room_names,
        config_entry.data.get(CONF_WISER_ROOM_NAMES),
    )

    # This must run before both the update listener and reload-settings snapshot.
    # A setup-time flag change is then included in the initial snapshot without
    # scheduling a reload; a later change is observed and reloads exactly once.
    # This prevents a standard boiler's dormant OpenTherm endpoint from creating
    # entities while allowing a real installation to survive temporary outages.
    _remember_opentherm_connection(hass, config_entry, coordinator)

    hass.data[DOMAIN][config_entry.entry_id] = {
        DATA: coordinator,
        CONF_WISER_ROOM_NAMES: runtime_room_names,
        ROOM_NAMES_STORE: room_names_store,
    }

    # If OpenTherm connects for the first time after startup, saving the flag
    # causes one integration reload so its entities are added. Future outages
    # retain those entities and their registry/history records.
    config_entry.async_on_unload(
        coordinator.async_add_listener(
            partial(
                _remember_opentherm_connection,
                hass,
                config_entry,
                coordinator,
            )
        )
    )

    update_hub_device_names(hass)

    # Register the physical hub before its entities and connected devices.
    hub_device = await async_update_device_registry(hass, config_entry)
    coordinator.hub_device_id = hub_device.id

    # Physical device identifiers used to contain mutable room or device names.
    # Migrate them before platform setup so renames cannot duplicate devices.
    migrate_physical_device_registry(
        hass,
        config_entry,
        hub_device.id,
        previous_room_names,
    )

    # Create physical devices in their Wiser room's Home Assistant area. Later
    # room renames move devices only while they remain in that managed area.
    register_room_assigned_devices(hass, config_entry)

    # Move existing hub entities off the old virtual Controller record.
    merge_legacy_hub_device_registry(hass, config_entry)

    # Give logical room devices stable IDs and concise device names.
    migrate_room_device_registry(hass, config_entry)

    current_room_names = _current_wiser_room_names(coordinator)
    confirmed_deleted_ids = _confirmed_deleted_room_ids(
        hass,
        config_entry,
        previous_room_names,
        current_room_names,
    )
    remove_deleted_room_devices(
        hass,
        config_entry,
        previous_room_names,
        confirmed_deleted_ids,
    )
    sync_wiser_room_areas(hass, config_entry, previous_room_names)
    _store_wiser_room_names(
        hass,
        config_entry,
        room_names_with_pending_deletions(
            previous_room_names,
            current_room_names,
            confirmed_deleted_ids,
        ),
    )

    # Register listeners only after setup-time registry and config migrations.
    update_listener = config_entry.add_update_listener(_async_update_listener)
    hass.data[DOMAIN][config_entry.entry_id].update(
        {
            UPDATE_LISTENER: update_listener,
            "reload_settings": integration_reload_settings(config_entry),
        }
    )
    config_entry.async_on_unload(
        coordinator.async_add_listener(
            partial(
                _sync_wiser_room_names,
                hass,
                config_entry,
                coordinator,
            )
        )
    )

    # Remap historical name-based entity IDs before platform setup so existing
    # entities, history, and dashboard references are retained.
    await async_migrate_physical_entity_unique_ids(
        hass,
        config_entry,
        coordinator,
        previous_room_names,
    )

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, WISER_PLATFORMS)

    # Setup websocket services for frontend cards
    await async_register_websockets(hass, coordinator)

    # Setup services
    await async_setup_services(hass, coordinator)

    # Register custom cards
    moodule_register = JSModuleRegistration(hass)
    await moodule_register.async_register()
    await async_update_wiser_panel(hass)

    _LOGGER.info(
        "Wiser Component Setup Completed (%s)", coordinator.wiserhub.system.name
    )
    return True


@callback
def _remember_opentherm_connection(hass, config_entry, coordinator) -> None:
    """Persist a confirmed OpenTherm connection until it is disabled.

    The flag intentionally lives in config-entry data so the existing entry
    update listener reloads platforms when runtime detection changes. A Store
    would persist the state but would not trigger that reload.
    """
    system = getattr(coordinator.wiserhub, "system", None)
    if system is None:
        return

    opentherm = getattr(system, "opentherm", None)
    remembered = config_entry.data.get(CONF_OPENTHERM_EVER_CONNECTED, False)

    if getattr(opentherm, "enabled", None) is False:
        if remembered:
            entry_data = dict(config_entry.data)
            entry_data.pop(CONF_OPENTHERM_EVER_CONNECTED, None)
            hass.config_entries.async_update_entry(config_entry, data=entry_data)
        remembered = False
    elif (
        not remembered
        and getattr(opentherm, "connection_status", None) == "Connected"
    ):
        hass.config_entries.async_update_entry(
            config_entry,
            data={**config_entry.data, CONF_OPENTHERM_EVER_CONNECTED: True},
        )
        remembered = True

    detected = bool(opentherm and remembered)
    if getattr(coordinator, "_wiser_opentherm_detected", None) is detected:
        return

    coordinator._wiser_opentherm_detected = detected
    _sync_opentherm_entity_registry(
        hass,
        config_entry,
        coordinator,
        detected=detected,
    )


@callback
def _sync_opentherm_entity_registry(
    hass, config_entry, coordinator, detected=None
) -> None:
    """Hide false OpenTherm entities while preserving their registry data."""
    system = getattr(coordinator.wiserhub, "system", None)
    if system is None:
        return

    opentherm = getattr(system, "opentherm", None)
    if detected is None:
        detected = opentherm_is_detected(config_entry, opentherm)
    unique_ids = opentherm_entity_unique_ids(coordinator)
    registry = er.async_get(hass)

    for entry in er.async_entries_for_config_entry(registry, config_entry.entry_id):
        if (entry.domain, entry.unique_id) not in unique_ids:
            continue
        if not detected and entry.disabled_by is None:
            registry.async_update_entity(
                entry.entity_id,
                disabled_by=er.RegistryEntryDisabler.INTEGRATION,
            )
        elif detected and entry.disabled_by == er.RegistryEntryDisabler.INTEGRATION:
            registry.async_update_entity(entry.entity_id, disabled_by=None)


async def async_update_device_registry(hass: HomeAssistant, config_entry):
    """Update device registry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    device_registry = dr.async_get(hass)
    return register_hub_device(
        device_registry,
        config_entry.entry_id,
        (DOMAIN, data.wiserhub.system.name),
        (DOMAIN, get_identifier(data, 0)),
        (CONNECTION_NETWORK_MAC, data.wiserhub.system.network.mac_address),
        manufacturer=MANUFACTURER,
        name=get_hub_device_name(data),
        model=data.wiserhub.system.model,
        sw_version=data.wiserhub.system.firmware_version,
    )


def merge_legacy_hub_device_registry(hass: HomeAssistant, config_entry):
    """Merge the legacy virtual Controller into the physical HeatHub."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    return merge_legacy_hub_device(
        dr.async_get(hass),
        er.async_get(hass),
        config_entry.entry_id,
        (DOMAIN, data.wiserhub.system.name),
        (DOMAIN, get_identifier(data, 0)),
    )


def register_room_assigned_devices(hass: HomeAssistant, config_entry):
    """Register physical Wiser devices in their matching Wiser room."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    area_registry = ar.async_get(hass)
    device_registry = dr.async_get(hass)

    for device in data.wiserhub.devices.all:
        room = data.wiserhub.rooms.get_by_device_id(device.id)
        if room is None:
            continue
        device_entry = register_room_assigned_device(
            device_registry,
            config_entry.entry_id,
            (DOMAIN, get_identifier(data, device.id)),
            (DOMAIN, data.wiserhub.system.name),
            room.name,
            manufacturer=MANUFACTURER,
            name=get_device_name(data, device.id),
            model=device.product_type,
            sw_version=device.firmware_version,
        )
        assign_device_area_if_unset(
            device_registry, area_registry, device_entry, room.name
        )


def migrate_physical_device_registry(
    hass: HomeAssistant,
    config_entry,
    hub_device_id: str,
    previous_room_names=None,
):
    """Migrate physical devices from name-derived to stable identifiers."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)
    registry_devices = list(
        dr.async_entries_for_config_entry(
            device_registry, config_entry.entry_id
        )
    )
    registry_entities = list(
        er.async_entries_for_config_entry(
            entity_registry, config_entry.entry_id
        )
    )
    itrv_identifier_prefix = (
        f"{data.wiserhub.system.name} {ENTITY_PREFIX} iTRV "
    )
    previous_room_names = previous_room_names or {}
    physical_entity_migration = build_physical_entity_unique_id_migration(
        data, previous_room_names
    )
    physical_entity_ids_by_target = {}
    for old_unique_id, new_unique_id in physical_entity_migration.items():
        physical_entity_ids_by_target.setdefault(new_unique_id, set()).add(
            old_unique_id
        )
    for device in data.wiserhub.devices.all:
        stable_identifier = (DOMAIN, get_identifier(data, device.id))
        legacy_identifier = (
            DOMAIN,
            get_legacy_device_identifier(data, device.id),
        )
        stable_entity_ids = {
            get_unique_id(data, "sensor", device.product_type, device.id),
            get_unique_id(data, "sensor", "Battery", device.id),
        }
        stable_entity_ids.update(
            {
                get_physical_entity_unique_id(
                    data, "sensor", device.id, entity_type
                )
                for entity_type in (
                    "power",
                    "energy",
                    "energy_received",
                )
            }
        )
        possible_devices = find_physical_device_candidates(
            registry_devices,
            registry_entities,
            {stable_identifier, legacy_identifier},
            stable_entity_ids,
        )
        identifier_prefix = f"{data.wiserhub.system.name} "
        historical_device_names = {
            value[len(identifier_prefix):]
            for candidate in possible_devices
            for domain, value in candidate.identifiers
            if domain == DOMAIN and value.startswith(identifier_prefix)
        }
        historical_entity_migration = (
            build_physical_entity_unique_id_migration(
                data,
                previous_room_names,
                {device.id: historical_device_names},
                {device.id},
            )
        )
        for old_unique_id, new_unique_id in historical_entity_migration.items():
            matching_entries = [
                entry
                for entry in registry_entities
                if entry.platform == DOMAIN
                and entry.unique_id in {old_unique_id, new_unique_id}
            ]
            migrate_entity_unique_id_duplicates(
                entity_registry,
                matching_entries,
                new_unique_id,
            )
        room = data.wiserhub.rooms.get_by_device_id(device.id)
        temperature_type = None
        old_temperature_names = set()
        possible_room_names = set()
        if room is not None:
            possible_room_names.add(room.name)
            if previous_name := previous_room_names.get(str(room.id)):
                possible_room_names.add(previous_name)

        if device.product_type == "iTRV":
            temperature_type = "smartvalve_temp"
            for entry in registry_devices:
                if entry.model != "iTRV":
                    continue
                for domain, value in entry.identifiers:
                    if domain != DOMAIN or not value.startswith(
                        itrv_identifier_prefix
                    ):
                        continue
                    suffix = value[len(itrv_identifier_prefix):]
                    possible_room_names.add(suffix)
                    possible_room_names.add(re.sub(r"-\d+$", "", suffix))
            old_temperature_names.update(
                f"LTS Temperature iTRV {room_name}"
                for room_name in possible_room_names
            )
        elif device.product_type == "SmokeAlarmDevice":
            temperature_type = "smokealarm_temp"
            if room is not None:
                old_temperature_names.add(
                    f"{room.name} {device.name}  Temperature"
                )
            else:
                old_temperature_names.add(
                    f"{device.name} {device.id} Temperature"
                )
        elif device.product_type == "UnderFloorHeating":
            temperature_type = "ufh_measured_temp"
            old_temperature_names.add(f"{device.name} Measured Temperature")
        elif device.product_type in {"HeatingActuator", "CFMT"} and getattr(
            device, "floor_temperature_sensor", None
        ):
            temperature_type = "floor_current_temp"
            old_temperature_names.add(
                f"LTS Floor Temperature "
                f"{room.name if room is not None else device.name}"
            )

        sensor_id_migrations = {}
        if temperature_type is not None:
            sensor_id_migrations[
                get_physical_entity_unique_id(
                    data, "sensor", device.id, temperature_type
                )
            ] = {
                get_unique_id(data, "sensor", name, device.id)
                for name in old_temperature_names
            }

        room_attached_sensor_ids = set()
        for entity_type in (
            "humidity",
            "power",
            "energy",
            "energy_received",
        ):
            stable_sensor_id = get_physical_entity_unique_id(
                data, "sensor", device.id, entity_type
            )
            old_sensor_ids = physical_entity_ids_by_target.get(
                stable_sensor_id, set()
            )
            if old_sensor_ids:
                sensor_id_migrations[stable_sensor_id] = old_sensor_ids
            if entity_type == "humidity":
                # Room-stat humidity is displayed on the logical room device.
                # Its entity must not make that room device a physical-device
                # migration candidate.
                room_attached_sensor_ids.add(stable_sensor_id)

        for stable_sensor_id, old_sensor_ids in sensor_id_migrations.items():
            matching_sensor_entries = [
                entry
                for entry in registry_entities
                if entry.domain == "sensor"
                and entry.platform == DOMAIN
                and entry.unique_id
                in old_sensor_ids | {stable_sensor_id}
            ]
            matching_device_ids = {
                entry.device_id
                for entry in matching_sensor_entries
                if entry.device_id is not None
            }

            if stable_sensor_id not in room_attached_sensor_ids:
                possible_devices.extend(
                    entry
                    for entry in registry_devices
                    if entry.id in matching_device_ids
                )

            migrate_entity_unique_id_duplicates(
                entity_registry,
                matching_sensor_entries,
                stable_sensor_id,
            )

        device_entry = migrate_physical_device(
            device_registry,
            entity_registry,
            config_entry.entry_id,
            stable_identifier,
            possible_devices,
            get_device_name(data, device.id),
            manufacturer=MANUFACTURER,
            model=device.product_type,
            sw_version=device.firmware_version,
            via_device=(DOMAIN, data.wiserhub.system.name),
            via_device_id=hub_device_id,
        )
        if room is not None:
            assign_device_area_if_unset(
                device_registry,
                ar.async_get(hass),
                device_entry,
                room.name,
            )


def migrate_room_device_registry(hass: HomeAssistant, config_entry):
    """Migrate all logical room devices away from name-derived identifiers."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    area_registry = ar.async_get(hass)
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    for room in active_wiser_rooms(data):
        device_entry = migrate_room_device(
            device_registry,
            entity_registry,
            config_entry.entry_id,
            (DOMAIN, get_identifier(data, room.id, "room")),
            (DOMAIN, get_legacy_room_identifier(data, room.id)),
            get_device_name(data, room.id, "room"),
            via_device=(DOMAIN, data.wiserhub.system.name),
        )
        assign_device_area_if_unset(
            device_registry, area_registry, device_entry, room.name
        )
        migrate_room_entities(
            entity_registry,
            device_entry.id,
            lambda entity_type: get_room_entity_unique_id(
                data, room.id, entity_type
            ),
        )


def _current_wiser_room_names(coordinator):
    """Return Wiser room names keyed by their stable room IDs."""
    return {
        str(room.id): room.name for room in active_wiser_rooms(coordinator)
    }


def _store_wiser_room_names(hass, config_entry, room_names) -> None:
    """Persist room names without triggering a config-entry reload."""
    entry_data = hass.data[DOMAIN][config_entry.entry_id]
    if entry_data.get(CONF_WISER_ROOM_NAMES) == room_names:
        return
    room_names = dict(room_names)
    entry_data[CONF_WISER_ROOM_NAMES] = room_names
    entry_data[ROOM_NAMES_STORE].async_delay_save(
        lambda: room_names,
        1,
    )


def _confirmed_deleted_room_ids(
    hass,
    config_entry,
    previous_room_names,
    current_room_names,
):
    """Track missing rooms across successful coordinator refreshes."""
    missing_counts = hass.data[DOMAIN][config_entry.entry_id].setdefault(
        "missing_room_counts", {}
    )
    return confirmed_deleted_room_ids(
        previous_room_names,
        current_room_names,
        missing_counts,
    )


def _device_by_identifier(device_registry, config_entry_id, identifier):
    """Return a device registry entry using current and older HA APIs."""
    get_by_identifier = getattr(
        device_registry, "async_get_device_by_identifier", None
    )
    if get_by_identifier:
        return get_by_identifier(identifier, config_entry_id)
    return device_registry.async_get_device(identifiers={identifier})


def remove_deleted_room_devices(
    hass,
    config_entry,
    previous_room_names,
    deleted_room_ids,
) -> int:
    """Remove registry records for rooms deleted from the Wiser system."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    identifiers = []

    for room_id in deleted_room_ids:
        identifiers.extend(
            (
                (DOMAIN, get_identifier(data, room_id, "room")),
                (
                    DOMAIN,
                    f"{data.wiserhub.system.name} {ENTITY_PREFIX} "
                    f"{previous_room_names[room_id]}",
                ),
            )
        )

    removed = remove_room_devices(
        dr.async_get(hass),
        er.async_get(hass),
        config_entry.entry_id,
        identifiers,
    )
    if removed:
        _LOGGER.info("Removed %s deleted Wiser room device(s)", removed)
    return removed


def sync_wiser_room_areas(hass, config_entry, previous_room_names) -> int:
    """Move Wiser devices when their integration-managed room is renamed."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    device_registry = dr.async_get(hass)
    area_registry = ar.async_get(hass)
    current_rooms = active_wiser_rooms(data)
    current_room_names = {room.name for room in current_rooms}
    moved = 0

    for room in current_rooms:
        room_device = _device_by_identifier(
            device_registry,
            config_entry.entry_id,
            (DOMAIN, get_identifier(data, room.id, "room")),
        )
        previous_name = previous_room_names.get(str(room.id))
        if previous_name is None and room_device and room_device.area_id:
            previous_name = known_wiser_room_area_name(
                area_registry,
                room_device.area_id,
                current_room_names,
            )

        room_devices = [room_device]
        for device in data.wiserhub.devices.all:
            device_room = data.wiserhub.rooms.get_by_device_id(device.id)
            if device_room is None or device_room.id != room.id:
                continue
            room_devices.append(
                _device_by_identifier(
                    device_registry,
                    config_entry.entry_id,
                    (DOMAIN, get_identifier(data, device.id)),
                )
            )

        moved += move_devices_from_managed_area(
            device_registry,
            area_registry,
            room_devices,
            previous_name,
            room.name,
        )

    return moved


def _sync_wiser_room_names(hass, config_entry, coordinator) -> None:
    """Apply Wiser room renames after a coordinator refresh."""
    previous = hass.data[DOMAIN][config_entry.entry_id].get(
        CONF_WISER_ROOM_NAMES, {}
    )
    current = _current_wiser_room_names(coordinator)
    if previous == current:
        hass.data[DOMAIN][config_entry.entry_id].setdefault(
            "missing_room_counts", {}
        ).clear()
        return
    confirmed_deleted_ids = _confirmed_deleted_room_ids(
        hass,
        config_entry,
        previous,
        current,
    )
    remove_deleted_room_devices(
        hass,
        config_entry,
        previous,
        confirmed_deleted_ids,
    )
    sync_wiser_room_areas(hass, config_entry, previous)
    stored_room_names = room_names_with_pending_deletions(
        previous,
        current,
        confirmed_deleted_ids,
    )
    if stored_room_names == previous:
        return
    _store_wiser_room_names(hass, config_entry, stored_room_names)


def update_hub_device_names(hass: HomeAssistant):
    """Keep physical hub names concise while distinguishing multiple hubs."""
    loaded_entries = hass.data.get(DOMAIN, {})
    show_suffix = len(loaded_entries) > 1
    device_registry = dr.async_get(hass)

    for config_entry_id, entry_data in loaded_entries.items():
        data = entry_data[DATA]
        data._wiser_show_hub_suffix = show_suffix
        device = device_registry.async_get_device_by_identifier(
            (DOMAIN, data.wiserhub.system.name), config_entry_id
        )
        if device is not None:
            device_registry.async_update_device(
                device.id, name=get_hub_device_name(data)
            )


async def _async_update_listener(hass: HomeAssistant, config_entry):
    """Handle options update."""
    await async_handle_entry_update(hass, config_entry)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry, device_entry
) -> bool:
    """Allow device removal while protecting the physical HeatHub."""
    data = hass.data.get(DOMAIN, {}).get(config_entry.entry_id, {}).get(DATA)
    hub_name = (
        data.wiserhub.system.name
        if data is not None
        else config_entry.data.get(CONF_NAME)
    )
    if (DOMAIN, hub_name) in device_entry.identifiers:
        _LOGGER.error(
            "You cannot delete the Wiser HeatHub using device delete. Please remove the integration instead"
        )
        return False
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Unload a config entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]

    if get_instance_count(hass) == 0:
        # Unload lovelace module resource if only instance
        _LOGGER.debug("Remove Wiser Lovelace cards")
        module_register = JSModuleRegistration(hass)
        await module_register.async_unregister()

        # Deregister services if only instance
        _LOGGER.debug("Unregister Wiser services")
        for service in WISER_SERVICES.values():
            if not data.wiserhub.hotwater and service == "boost_hotwater":
                continue
            hass.services.async_remove(DOMAIN, service)

    _LOGGER.debug("Unload Wiser integration platforms")
    # Unload a config entry
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, platform)
                for platform in WISER_PLATFORMS
            ]
        )
    )

    _LOGGER.debug("Detach config update listener")
    hass.data[DOMAIN][config_entry.entry_id][UPDATE_LISTENER]()

    _LOGGER.debug("Unload integration")
    if unload_ok:
        await async_unload_card_updates(hass, config_entry)
        hass.data[DOMAIN].pop(config_entry.entry_id)
        await async_update_wiser_panel(hass)
        update_hub_device_names(hass)

    return unload_ok
