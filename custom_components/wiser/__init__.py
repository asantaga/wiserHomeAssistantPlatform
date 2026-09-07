"""Drayton Wiser Compoment for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
msparker@sky.com
"""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .const import (
    CONF_AUTOMATIONS_HW_AUTO_MODE,
    CONF_AUTOMATIONS_HW_CLIMATE,
    CONF_AUTOMATIONS_HW_HEAT_MODE,
    CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID,
    CONF_AUTOMATIONS_PASSIVE,
    CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT,
    CONF_DEPRECATED_HW_TARGET_TEMP,
    DATA,
    DOMAIN,
    MANUFACTURER,
    UPDATE_LISTENER,
    WISER_PLATFORMS,
    WISER_SERVICES,
    HWCycleModes,
)
from .coordinator import WiserUpdateCoordinator
from .device import (
    merge_legacy_hub_device,
    migrate_room_device,
    register_hub_device,
    register_room_assigned_device,
)
from .entity_migration import migrate_entity_unique_ids
from .frontend import JSModuleRegistration
from .helpers import (
    get_device_name,
    get_hub_device_name,
    get_identifier,
    get_instance_count,
    get_legacy_room_identifier,
)
from .services import async_setup_services
from .websockets import async_register_websockets

_LOGGER = logging.getLogger(__name__)


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

        hass.config_entries.async_update_entry(
            config_entry, options=new_options, minor_version=4, version=1
        )

    _LOGGER.debug(
        "Migration to configuration version %s.%s successful",
        config_entry.version,
        config_entry.minor_version,
    )

    return True


async def async_setup_entry(hass: HomeAssistant, config_entry):
    """Set up Wiser from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = WiserUpdateCoordinator(hass, config_entry)

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.last_update_status == "Success":
        raise ConfigEntryNotReady

    # Update listener for config option changes
    update_listener = config_entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][config_entry.entry_id] = {
        DATA: coordinator,
        UPDATE_LISTENER: update_listener,
    }

    update_hub_device_names(hass)

    # Register the physical hub before its entities and connected devices.
    hub_device = await async_update_device_registry(hass, config_entry)

    # Create physical devices with their Wiser room as Home Assistant's initial
    # area. The registry keeps any area the user chooses later.
    register_room_assigned_devices(hass, config_entry, hub_device.id)

    # Move existing hub entities off the old virtual Controller record.
    merge_legacy_hub_device_registry(hass, config_entry)

    # Give logical room devices stable IDs and concise device names.
    migrate_room_device_registry(hass, config_entry)

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, WISER_PLATFORMS)

    # Setup websocket services for frontend cards
    await async_register_websockets(hass, coordinator)

    # Setup services
    await async_setup_services(hass, coordinator)

    # Register custom cards
    moodule_register = JSModuleRegistration(hass)
    await moodule_register.async_register()

    _LOGGER.info(
        "Wiser Component Setup Completed (%s)", coordinator.wiserhub.system.name
    )
    return True


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


def register_room_assigned_devices(
    hass: HomeAssistant, config_entry, hub_device_id: str
):
    """Register physical Wiser devices in their matching Wiser room."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    device_registry = dr.async_get(hass)

    for device in data.wiserhub.devices.all:
        room = data.wiserhub.rooms.get_by_device_id(device.id)
        if room is None:
            continue
        register_room_assigned_device(
            device_registry,
            config_entry.entry_id,
            (DOMAIN, get_identifier(data, device.id)),
            hub_device_id,
            room.name,
            manufacturer=MANUFACTURER,
            name=get_device_name(data, device.id),
            model=device.product_type,
            sw_version=device.firmware_version,
        )


def migrate_room_device_registry(hass: HomeAssistant, config_entry):
    """Migrate all logical room devices away from name-derived identifiers."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    device_registry = dr.async_get(hass)
    entity_registry = er.async_get(hass)

    for room in data.wiserhub.rooms.all:
        migrate_room_device(
            device_registry,
            entity_registry,
            config_entry.entry_id,
            (DOMAIN, get_identifier(data, room.id, "room")),
            (DOMAIN, get_legacy_room_identifier(data, room.id)),
            get_device_name(data, room.id, "room"),
        )


def update_hub_device_names(hass: HomeAssistant):
    """Keep physical hub names concise while distinguishing multiple hubs."""
    loaded_entries = hass.data.get(DOMAIN, {})
    show_suffix = len(loaded_entries) > 1
    device_registry = dr.async_get(hass)

    for entry_data in loaded_entries.values():
        data = entry_data[DATA]
        data._wiser_show_hub_suffix = show_suffix
        device = device_registry.async_get_device(
            identifiers={(DOMAIN, data.wiserhub.system.name)}
        )
        if device is not None:
            device_registry.async_update_device(
                device.id, name=get_hub_device_name(data)
            )


async def _async_update_listener(hass: HomeAssistant, config_entry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry, device_entry
) -> bool:
    """Delete device if not entities."""
    if device_entry.model == "Controller" or (
        DOMAIN,
        config_entry.data.get(CONF_NAME),
    ) in device_entry.identifiers:
        _LOGGER.error(
            "You cannot delete the Wiser HeatHub using device delete.  Please remove the integration instead"
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
        hass.data[DOMAIN].pop(config_entry.entry_id)
        update_hub_device_names(hass)

    return unload_ok
