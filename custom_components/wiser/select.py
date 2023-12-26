import logging
import asyncio
from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
)

from .helpers import get_device_name, get_unique_id, get_identifier, hub_error_handler
from .schedules import WiserScheduleEntity

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    wiser_selects = []

    if data.wiserhub.hotwater:
        _LOGGER.debug("Setting up Hot Water mode select")
        wiser_selects.extend([WiserHotWaterModeSelect(data)])

    # Add SmartPlugs (if any)
    if data.wiserhub.devices.smartplugs.count > 0:
        _LOGGER.debug("Setting up Smartplug mode select")
        for plug in data.wiserhub.devices.smartplugs.all:
            wiser_selects.extend([WiserSmartPlugModeSelect(data, plug.id)])

    if data.wiserhub.devices.lights.count > 0:
        _LOGGER.debug("Setting up Light mode select")
        for light in data.wiserhub.devices.lights.all:
            wiser_selects.extend([WiserLightModeSelect(data, light.id)])

    if data.wiserhub.devices.shutters.count > 0:
        _LOGGER.debug("Setting up Shutter mode select")
        for shutter in data.wiserhub.devices.shutters.all:
            wiser_selects.extend([WiserShutterModeSelect(data, shutter.id)])

    async_add_entities(wiser_selects)


class WiserSelectEntity(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initalise")

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} updating")

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._device_id)} Mode"

    @property
    def options(self) -> list[str]:
        return self._options

    @property
    def current_option(self) -> str:
        return self._device.mode

    @hub_error_handler
    async def async_select_option(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} to {option}")
        if option in self._options:
            await self.async_set_mode(option)
            await self.async_force_update()
        else:
            _LOGGER.error(
                f"{option} is not a valid {self.name}.  Please choose from {self._options}"
            )

    async def async_set_mode(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} mode to {option}")
        await self._device.set_mode(option)

    @property
    def unique_id(self):
        """Return unique ID of device"""
        return get_unique_id(
            self._data, self._device.product_type, "mode-select", self._device_id
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
            "manufacturer": MANUFACTURER,
            "model": self._device.product_type,
            "sw_version": self._device.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


class WiserHotWaterModeSelect(WiserSelectEntity, WiserScheduleEntity):
    def __init__(self, data) -> None:
        """Initialize the sensor."""
        super().__init__(data)
        self._hotwater = self._data.wiserhub.hotwater
        self._device_id = self._hotwater.id
        self._options = self._hotwater.available_modes
        self._schedule = self._hotwater.schedule
        self._state = self._hotwater.mode

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._hotwater = self._data.wiserhub.hotwater
        self._schedule = self._hotwater.schedule
        self.async_write_ha_state()

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, 0, 'Hot Water')} Mode"

    @property
    def current_option(self) -> str:
        return self._hotwater.mode

    async def async_set_mode(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} mode to {option}")
        if self._hotwater.is_override:
            await self._hotwater.cancel_overrides()
        await self._hotwater.set_mode(option)

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(self._data, "hotwater", "mode-select", 0)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, 0),
            "identifiers": {(DOMAIN, get_identifier(self._data, 0))},
            "manufacturer": MANUFACTURER,
            "model": self._data.wiserhub.system.product_type,
            "sw_version": self._data.wiserhub.system.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


class WiserSmartPlugModeSelect(WiserSelectEntity, WiserScheduleEntity):
    def __init__(self, data, smartplug_id) -> None:
        """Initialize the sensor."""
        self._device_id = smartplug_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.smartplugs.get_by_id(self._device_id)
        self._options = self._device.available_modes
        self._schedule = self._device.schedule

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.smartplugs.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self.async_write_ha_state()


class WiserLightModeSelect(WiserSelectEntity, WiserScheduleEntity):
    def __init__(self, data, light_id) -> None:
        """Initialize the sensor."""
        self._device_id = light_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._options = self._device.available_modes
        self._schedule = self._device.schedule

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self.async_write_ha_state()


class WiserShutterModeSelect(WiserSelectEntity, WiserScheduleEntity):
    def __init__(self, data, shutter_id) -> None:
        """Initialize the sensor."""
        self._device_id = shutter_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.shutters.get_by_id(self._device_id)
        self._options = self._device.available_modes
        self._schedule = self._device.schedule

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.shutters.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self.async_write_ha_state()
