"""Support for Wiser lights vis Wiser Hub"""
import logging

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect


from .const import DATA, DOMAIN, MANUFACTURER
from .helpers import get_device_name, get_identifier, get_room_name, get_unique_id

MAX_BRIGHTNESS = 100
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    wiser_lights = []
    if data.wiserhub.devices.lights:
        _LOGGER.debug("Setting up light entities")
        for light in data.wiserhub.devices.lights.all:
            if light.is_dimmable:
                wiser_lights = [
                WiserDimmerLight(data, light.id) 
                ]
        async_add_entities(wiser_lights, True)


class WiserLight(LightEntity):
    def __init__(self, data, light_id):
        """Initialize the sensor."""
        self._data = data
        self._light_id = light_id
        self._light = self._data.wiserhub.devices.lights.get_by_id(light_id)
        self._name = self._light.name
        _LOGGER.info(f"{self._data.wiserhub.system.name} {self._name} init")

    async def async_force_update(self):
        await self._data.async_update(no_throttle=True)

    async def async_update(self):
        """Async Update to HA."""
        _LOGGER.debug(f"Wiser {self.name} Light Update requested")
        self._light = self._data.wiserhub.devices.lights.get_by_id(self._light_id)

    @property
    def is_on(self):
        """Return the boolean response if the node is on."""
        return self._light.is_on

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._light.id)} {self._name}"

    @property
    def icon(self):
        """Return icon."""
        if self._light.mode == "Auto":
            return "mdi:lightbulb-auto" if self.is_on else "mdi:lightbulb-auto-outline"
        else:
            return "mdi:lightbulb" if self.is_on else "mdi:lightbulb-outline"

    @property
    def unique_id(self):
        return get_unique_id(self._data, "device", "light", self.name)

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._light.id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._light.id))},
                "manufacturer": MANUFACTURER,
                "model": "NHPDimmer",   #This needs api update
                "sw_version": "020519ff",   #This needs api update
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    async def async_added_to_hass(self):
        """Subscribe for update from the hub."""

        async def async_update_state():
            """Update light state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._data.wiserhub.system.name}-HubUpdateMessage", async_update_state
            )
        )


class WiserDimmerLight(WiserLight):
    """A Class for an Wiser light entity."""
    def __init__(self, data, light_id):
        """Initialize the sensor."""
        super().__init__(data, light_id)

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    @property
    def brightness(self):
        """Return the brightness of this light between 0..100."""
        return self._light.current_percentage

    async def async_turn_on(self, **kwargs):
        """Turn light on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS])
        else:
            brightness = self.brightness
        if brightness is not None:
            # Below functions need adding to api first
            """
            await self.hass.async_add_executor_job(
                setattr, self._light, "brightness", brightness
            )
            """
            pass
        else:
            """
            await self.hass.async_add_executor_job(
                self._light.turn_on
            )
            """
            pass
        await self.async_force_update()
        return True

    async def async_turn_off(self, **kwargs):
        """Turn light off."""
        # Below function needs adding to api first
        """
        await self.hass.async_add_executor_job(
            self._light.turn_off
        )
        """
        await self.async_force_update()
        return True

    @property
    def extra_state_attributes(self):
        """Return the device state attributes for the attribute card."""
        attrs = {}
        # Add any attrs here
        return attrs
