import logging
from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER
)
from .helpers import get_device_name, get_identifier, get_unique_id
from wiserHeatAPIv2.wiserhub import (
    TEMP_MINIMUM,
    TEMP_MAXIMUM
)
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.helpers.dispatcher import async_dispatcher_connect

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_numbers = []

    _LOGGER.debug("Setting up Away Mode setpoint setter")
    wiser_numbers.extend([WiserAwayModeTempNumber(data, "Away Mode Target Temperature")])

    async_add_entities(wiser_numbers)


class WiserAwayModeTempNumber(NumberEntity):
    def __init__(self, data, name):
        """Initialize the sensor."""
        self._data = data
        self._name = name
        _LOGGER.info(f"Away Mode target temperature initalise")

    async def async_force_update(self):
        await self._data.async_update(no_throttle=True)

    @property
    def min_value(self) -> float:
        """Return the minimum value."""
        return TEMP_MINIMUM

    @property
    def max_value(self) -> float:
        """Return the maximum value."""
        return TEMP_MAXIMUM

    @property
    def step(self) -> float:
        return 0.5

    @property
    def mode(self) -> NumberMode:
        """Return the mode of the entity."""
        return NumberMode.AUTO

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, 0, self._name)}"

    @property
    def icon(self):
        """Icon for device"""
        return "mdi:thermometer-low"


    @property
    def unique_id(self):
        return get_unique_id(self._data, "system", "number", self.name)

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

    @property
    def value(self) -> float:
        """Return the entity value to represent the entity state."""
        return self._data.wiserhub.system.away_mode_target_temperature

    def set_value(self, value: float) -> None:
        """Set new value."""
        _LOGGER.debug(f"Setting {self._name} to {value}C")
        self._data.wiserhub.system.away_mode_target_temperature = value
        self.hass.async_create_task(self.async_force_update())

    async def async_set_value(self, value: float) -> None:
        """Set new value."""
        await self.hass.async_add_executor_job(self.set_value, value)

    async def async_added_to_hass(self):
        """Subscribe for update from the hub."""

        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._data.wiserhub.system.name}-HubUpdateMessage", async_update_state
            )
        )