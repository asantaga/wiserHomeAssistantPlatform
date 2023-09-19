"""Support for Wiser lights via Wiser Hub"""
import asyncio
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA, DOMAIN, MANUFACTURER_SCHNEIDER
from .helpers import get_device_name, get_identifier, get_unique_id
from .schedules import WiserScheduleEntity

MANUFACTURER = MANUFACTURER_SCHNEIDER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]

    wiser_lights = []
    if data.wiserhub.devices.lights:
        _LOGGER.debug("Setting up light entities")
        for light in data.wiserhub.devices.lights.all:
            if light.is_dimmable:
                wiser_lights.append(WiserDimmableLight(data, light.id))
            else:
                wiser_lights.append(WiserLight(data, light.id))
        async_add_entities(wiser_lights, True)


class WiserLight(CoordinatorEntity, LightEntity, WiserScheduleEntity):
    """WiserLight ClientEntity Object."""

    def __init__(self, coordinator, light_id) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._device_id = light_id
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initialise")

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            await asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        _LOGGER.debug(f"{self.name} updating")
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self.async_write_ha_state()

    @property
    def supported_color_modes(self):
        return {ColorMode.ONOFF}

    @property
    def is_on(self):
        """Return the boolean response if the node is on."""
        return self._device.is_on

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._device.id)} Light"

    @property
    def icon(self):
        """Return icon."""
        if self._device.mode == "Auto":
            return "mdi:lightbulb-auto" if self.is_on else "mdi:lightbulb-auto-outline"
        else:
            return "mdi:lightbulb" if self.is_on else "mdi:lightbulb-outline"

    @property
    def unique_id(self):
        return get_unique_id(self._data, "device", "light", self.name)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
            "manufacturer": MANUFACTURER,
            "model": self._data.wiserhub.devices.get_by_id(self._device_id).model,
            "sw_version": self._device.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        attrs = {}
        # Room
        if self._data.wiserhub.rooms.get_by_id(self._device.room_id) is not None:
            attrs["room"] = self._data.wiserhub.rooms.get_by_id(
                self._device.room_id
            ).name
        else:
            attrs["room"] = "Unassigned"

        # Identification
        attrs["name"] = self._device.name
        attrs["model"] = self._device.model
        attrs["product_type"] = self._device.product_type
        attrs["product_identifier"] = self._device.product_identifier
        attrs["product_model"] = self._device.product_model
        attrs["serial_number"] = self._device.serial_number
        attrs["firmware"] = self._device.firmware_version

        # Settings
        attrs["is_dimmable"] = self._device.is_dimmable
        attrs["mode"] = self._device.mode
        attrs["away_mode_action"] = self._device.away_mode_action

        # Command State
        attrs["control_source"] = self._device.control_source

        # Status
        attrs["current_state"] = self._device.current_state
        attrs["target_state"] = self._device.target_state

        # Schedule
        attrs["schedule_id"] = self._device.schedule_id
        if self._device.schedule:
            attrs["schedule_name"] = self._device.schedule.name
            attrs["next_day_change"] = str(self._device.schedule.next.day)
            attrs["next_schedule_change"] = str(self._device.schedule.next.time)
            attrs["next_schedule_datetime"] = str(self._device.schedule.next.datetime)
            attrs["next_schedule_state"] = self._device.schedule.next.setting

        return attrs

    async def async_turn_on(self, **kwargs):
        """Turn light on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS])
            _LOGGER.debug(
                f"Setting brightness of {self.name} to {round((brightness / 255) * 100)}%"
            )
            await self._device.set_current_percentage(round((brightness / 255) * 100))
        else:
            _LOGGER.debug(f"Turning on {self.name}")
            await self._device.turn_on()
        await self.async_force_update(2)
        return True

    async def async_turn_off(self, **kwargs):
        """Turn light off."""
        _LOGGER.debug(f"Turning off {self.name}")
        await self._device.turn_off()
        await self.async_force_update(2)
        return True


class WiserDimmableLight(WiserLight):
    """A Class for an Wiser light entity."""

    @property
    def supported_color_modes(self):
        return {ColorMode.BRIGHTNESS}

    @property
    def brightness(self):
        """Return the brightness of this light between 0..100."""
        return round((self._device.current_percentage / 100) * 255)

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        attrs = super().extra_state_attributes

        # Settings
        attrs["output_range_min"] = self._device.output_range.minimum
        attrs["output_range_max"] = self._device.output_range.maximum

        # Status
        attrs["current_percentage"] = self._device.current_percentage
        attrs["current_level"] = self._device.current_level
        attrs["target_percentage"] = self._device.target_percentage
        attrs["manual_level"] = self._device.manual_level
        attrs["override_level"] = self._device.override_level

        # Schedule
        if self._device.schedule:
            del attrs["next_schedule_state"]
            attrs["next_schedule_percentage"] = self._device.schedule.next.setting
        return attrs
