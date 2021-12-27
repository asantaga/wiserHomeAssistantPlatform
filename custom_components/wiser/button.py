
from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER
)
from .climate import HVAC_MODE_HASS_TO_WISER
from .helpers import get_device_name, get_unique_id, get_identifier

from homeassistant.components.button import ButtonEntity
from homeassistant.components.climate.const import HVAC_MODE_AUTO
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util

import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler


    _LOGGER.debug("Setting up Heating buttons")
    wiser_buttons = [
        WiserBoostAllHeatingButton(data),
        WiserCancelHeatingOverridesButton(data)
    ]

    if data.wiserhub.hotwater:
        _LOGGER.debug("Setting up Hot Water buttons")
        wiser_buttons.extend([
            WiserBoostHotWaterButton(data),
            WiserCancelHotWaterOverridesButton(data),
            WiserOverrideHotWaterButton(data),
        ])

    if data.enable_moments and data.wiserhub.moments:
        _LOGGER.debug("Setting up Moments buttons")
        for moment in data.wiserhub.moments.all:
            wiser_buttons.append(WiserMomentsButton(data, moment.id))

    async_add_entities(wiser_buttons, True)


class WiserButton(ButtonEntity):
    def __init__(self, data, name = "Button"):
        """Initialize the sensor."""
        self._data = data
        self._name = name
        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} init")

    async def async_force_update(self):
        _LOGGER.debug(f"{self._name} requested hub update")
        await self._data.async_update(no_throttle=True)

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(self._data, "button", self._name, 0)

    @property
    def name(self):
        return get_device_name(self._data, 0, self._name)
    
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


    async def async_added_to_hass(self):
        """Call when the button is added to hass."""
        state = await self.async_get_last_state()
        if state is not None and state.state is not None:
            self.__last_pressed = dt_util.parse_datetime(state.state)

        """Subscribe for update from the hub."""
        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._data.wiserhub.system.name}-HubUpdateMessage", async_update_state
            )
        )


class WiserBoostAllHeatingButton(WiserButton):
    def __init__(self, data):
        super().__init__(data, "Boost All Heating")

    async def async_press(self):
        boost_time = self._data.boost_time
        boost_temp = self._data.boost_temp
        await self.hass.async_add_executor_job(
            self._data.wiserhub.system.boost_all_rooms, boost_temp, boost_time
        )
        await self.async_force_update()

    @property
    def icon(self):
        return "mdi:fire"


class WiserCancelHeatingOverridesButton(WiserButton):
    def __init__(self, data):
        super().__init__(data, "Cancel All Heating Overrides")

    async def async_press(self):
        await self.hass.async_add_executor_job(
            self._data.wiserhub.system.cancel_all_overrides
        )
        await self.async_force_update()

    @property
    def icon(self):
        return "mdi:fire-off"


class WiserBoostHotWaterButton(WiserButton):
    def __init__(self, data):
        super().__init__(data, "Boost Hot Water")

    async def async_press(self):
        boost_time = self._data.hw_boost_time
        await self.hass.async_add_executor_job(
            self._data.wiserhub.hotwater.boost, boost_time
        )
        await self.async_force_update()

    @property
    def icon(self):
        return "mdi:water-plus"


class WiserCancelHotWaterOverridesButton(WiserButton):
    def __init__(self, data):
        super().__init__(data, "Cancel Hot Water Overrides")

    async def async_press(self):
        await self.hass.async_add_executor_job(
            self._data.wiserhub.hotwater.cancel_overrides
        )
        await self.async_force_update()

    @property
    def icon(self):
        return "mdi:water-off"


class WiserOverrideHotWaterButton(WiserButton):
    def __init__(self, data):
        super().__init__(data, "Toggle Hot Water")

    async def async_press(self):
        await self.hass.async_add_executor_job(
            self._data.wiserhub.hotwater.override_state, 
            "Off" if self._data.wiserhub.hotwater.current_state == "On" else "On"
        )
        await self.async_force_update()

    @property
    def icon(self):
        return "mdi:water-boiler"


class WiserMomentsButton(WiserButton):
    def __init__(self, data, moment_id):
        self._moment_id = moment_id
        super().__init__(data, f"Moments {data.wiserhub.moments.get_by_id(moment_id).name}")

    async def async_press(self):
        await self.hass.async_add_executor_job(
            self._data.wiserhub.moments.get_by_id(self._moment_id).activate
        )
        await self.async_force_update()

    @property
    def icon(self):
        return "mdi:home-thermometer"
