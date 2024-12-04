"""Drayton Wiser Compoment for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
msparker@sky.com
"""

import asyncio
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
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
from .frontend import WiserCardRegistration
from .helpers import get_device_name, get_identifier, get_instance_count
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

        hass.config_entries.async_update_entry(
            config_entry, options=new_options, minor_version=3, version=1
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

    # Setup platforms
    await hass.config_entries.async_forward_entry_setups(config_entry, WISER_PLATFORMS)

    # Setup websocket services for frontend cards
    await async_register_websockets(hass, coordinator)

    # Setup services
    await async_setup_services(hass, coordinator)

    # Add hub as device
    await async_update_device_registry(hass, config_entry)

    # Register custom cards
    cards = WiserCardRegistration(hass)
    await cards.async_register()

    _LOGGER.info(
        "Wiser Component Setup Completed (%s)", coordinator.wiserhub.system.name
    )
    return True


async def async_update_device_registry(hass: HomeAssistant, config_entry):
    """Update device registry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        connections={
            (CONNECTION_NETWORK_MAC, data.wiserhub.system.network.mac_address)
        },
        identifiers={(DOMAIN, get_identifier(data, 0))},
        manufacturer=MANUFACTURER,
        name=get_device_name(data, 0),
        model=data.wiserhub.system.model,
        sw_version=data.wiserhub.system.firmware_version,
    )


async def _async_update_listener(hass: HomeAssistant, config_entry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry, device_entry
) -> bool:
    """Delete device if not entities."""
    if device_entry.model == "Controller":
        _LOGGER.error(
            "You cannot delete the Wiser Controller using device delete.  Please remove the integration instead"
        )
        return False
    return True


async def async_unload_entry(hass: HomeAssistant, config_entry):
    """Unload a config entry."""

    if get_instance_count(hass) == 0:
        # Unload lovelace module resource if only instance
        _LOGGER.debug("Remove Wiser Lovelace cards")
        cards = WiserCardRegistration(hass)
        await cards.async_unregister()

        # Deregister services if only instance
        _LOGGER.debug("Unregister Wiser services")
        for service in WISER_SERVICES.values():
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

    return unload_ok
