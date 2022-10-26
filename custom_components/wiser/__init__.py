"""
Drayton Wiser Compoment for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
msparker@sky.com
"""
import asyncio
import logging

from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC

from .coordinator import WiserUpdateCoordinator
from .frontend import WiserCardRegistration
from .helpers import get_device_name, get_identifier, get_instance_count
from .services import async_setup_services
from .websockets import async_register_websockets

from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
    UPDATE_LISTENER,
    WISER_PLATFORMS,
    WISER_SERVICES,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry):
    """Set up Wiser from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = WiserUpdateCoordinator(hass, config_entry)

    await coordinator.async_config_entry_first_refresh()

    if not coordinator.wiserhub.system:
        raise ConfigEntryNotReady

    # Update listener for config option changes
    update_listener = config_entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][config_entry.entry_id] = {
        DATA: coordinator,
        UPDATE_LISTENER: update_listener,
    }

    # Setup platforms
    for platform in WISER_PLATFORMS:
        hass.async_add_job(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    # Setup websocket services for frontend cards
    await async_register_websockets(hass, coordinator)

    # Setup services
    await async_setup_services(hass, coordinator)

    # Add hub as device
    await async_update_device_registry(hass, config_entry)

    # Register custom cards
    cards = WiserCardRegistration(hass)
    await cards.async_register()
    await cards.async_remove_gzip_files()

    _LOGGER.info(
        f"Wiser Component Setup Completed ({coordinator.wiserhub.system.name})"
    )
    return True


async def async_update_device_registry(hass, config_entry):
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


async def _async_update_listener(hass, config_entry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_remove_config_entry_device(hass, config_entry, device_entry) -> bool:
    """Delete device if not entities"""
    if device_entry.model == "Controller":
        _LOGGER.error(
            "You cannot delete the Wiser Controller device via the device delete method.  Please remove the integration instead."
        )
        return False
    return True


async def async_unload_entry(hass, config_entry):
    """Unload a config entry"""

    if get_instance_count(hass) == 0:
        # Unload lovelace module resource if only instance
        _LOGGER.debug("Remove Wiser Lovelace cards")
        cards = WiserCardRegistration(hass)
        await cards.async_unregister()

        # Deregister services if only instance
        _LOGGER.debug("Unregister Wiser services")
        for k, service in WISER_SERVICES.items():
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
