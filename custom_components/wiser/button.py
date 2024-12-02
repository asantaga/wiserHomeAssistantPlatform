"""Button entities."""

import asyncio
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DATA, DOMAIN, HOT_WATER, MANUFACTURER
from .helpers import get_device_name, get_identifier, get_unique_id, hub_error_handler

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    _LOGGER.debug("Setting up Heating buttons")
    wiser_buttons = [
        WiserBoostAllHeatingButton(data),
        WiserCancelHeatingOverridesButton(data),
    ]

    if data.wiserhub.hotwater:
        _LOGGER.debug("Setting up Hot Water buttons")
        wiser_buttons.extend(
            [
                WiserBoostHotWaterButton(data),
                WiserCancelHotWaterOverridesButton(data),
            ]
        )
        if not data.enable_hw_climate:
            wiser_buttons.append(WiserOverrideHotWaterButton(data))

    if data.wiserhub.moments:
        _LOGGER.debug("Setting up Moments buttons")
        wiser_buttons.extend(
            [
                WiserMomentsButton(data, moment.id)
                for moment in data.wiserhub.moments.all
            ]
        )

    async_add_entities(wiser_buttons, True)


class WiserButton(CoordinatorEntity, ButtonEntity):
    """Class to handle a button entity."""

    def __init__(self, coordinator, name="Button") -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._name = name
        _LOGGER.debug("%s %s initialise", self._data.wiserhub.system.name, self.name)

    async def async_force_update(self, delay: int = 0):
        """Force an update from the hub."""
        _LOGGER.debug("Hub update initiated by %s", self.name)
        if delay:
            asyncio.sleep(delay)
        state = await self.async_get_last_state()
        if state is not None and state.state is not None:
            self.__last_pressed = (  # pylint: disable=unused-private-member
                dt_util.parse_datetime(state.state)
            )
        await self._data.async_refresh()

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(self._data, "button", self._name, 0)

    @property
    def name(self):
        """Return entity name."""
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


class WiserBoostAllHeatingButton(WiserButton):
    """Class to handle Heating button."""

    def __init__(self, data) -> None:
        """Init."""
        super().__init__(data, "Boost All Heating")

    @hub_error_handler
    async def async_press(self):
        """Handle button press."""
        boost_time = self._data.boost_time
        boost_temp = self._data.boost_temp
        await self._data.wiserhub.system.boost_all_rooms(boost_temp, boost_time)
        await self.async_force_update()

    @property
    def icon(self):
        """Return icon."""
        return "mdi:fire"


class WiserCancelHeatingOverridesButton(WiserButton):
    """Class to handle heating overrides button."""

    def __init__(self, data) -> None:
        """Init."""
        super().__init__(data, "Cancel All Heating Overrides")

    @hub_error_handler
    async def async_press(self):
        """Handle button press."""
        await self._data.wiserhub.system.cancel_all_overrides()
        await self.async_force_update()

    @property
    def icon(self):
        """Return icon."""
        return "mdi:fire-off"


class WiserBoostHotWaterButton(WiserButton):
    """Class to handle hot water button."""

    def __init__(self, data) -> None:
        """Init."""
        super().__init__(data, "Boost Hot Water")

    @hub_error_handler
    async def async_press(self):
        """Handle button press."""
        boost_time = self._data.hw_boost_time
        await self._data.wiserhub.hotwater.boost(boost_time)
        await self.async_force_update()

    @property
    def icon(self):
        """Return icon."""
        return "mdi:water-plus"

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(
                self._data, self._data.wiserhub.hotwater.id, "Hot Water"
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data, self._data.wiserhub.hotwater.id, "hot_water"
                    ),
                )
            },
            "manufacturer": MANUFACTURER,
            "model": HOT_WATER.title(),
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


class WiserCancelHotWaterOverridesButton(WiserButton):
    """Class to handle cancel hot water overrides button."""

    def __init__(self, data) -> None:
        """Init."""
        super().__init__(data, "Cancel Hot Water Overrides")

    @hub_error_handler
    async def async_press(self):
        """Handle button press."""
        await self._data.wiserhub.hotwater.cancel_overrides()
        await self.async_force_update()

    @property
    def icon(self):
        """Return icon."""
        return "mdi:water-off"

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(
                self._data, self._data.wiserhub.hotwater.id, "Hot Water"
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data, self._data.wiserhub.hotwater.id, "hot_water"
                    ),
                )
            },
            "manufacturer": MANUFACTURER,
            "model": HOT_WATER.title(),
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


class WiserOverrideHotWaterButton(WiserButton):
    """Class to handle hot water override button."""

    def __init__(self, data) -> None:
        """Init."""
        super().__init__(data, "Toggle Hot Water")

    @hub_error_handler
    async def async_press(self):
        """Handle button press."""
        await self._data.wiserhub.hotwater.override_state(
            "Off" if self._data.wiserhub.hotwater.current_state == "On" else "On"
        )
        await self.async_force_update()

    @property
    def icon(self):
        """Return icon."""
        return "mdi:water-boiler"

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(
                self._data, self._data.wiserhub.hotwater.id, "Hot Water"
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data, self._data.wiserhub.hotwater.id, "hot_water"
                    ),
                )
            },
            "manufacturer": MANUFACTURER,
            "model": HOT_WATER.title(),
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


class WiserMomentsButton(WiserButton):
    """Class to handle moments button."""

    def __init__(self, data, moment_id) -> None:
        """Init."""
        self._moment_id = moment_id
        super().__init__(
            data, f"Moments {data.wiserhub.moments.get_by_id(moment_id).name}"
        )

    @hub_error_handler
    async def async_press(self):
        """Handle button press."""
        await self._data.wiserhub.moments.get_by_id(self._moment_id).activate()
        await self.async_force_update()

    @property
    def icon(self):
        """Return icon."""
        return "mdi:home-thermometer"
