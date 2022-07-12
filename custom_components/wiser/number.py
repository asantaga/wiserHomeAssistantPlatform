from awesomeversion import AwesomeVersion
from homeassistant.const import __version__ as HA_VERSION
from types import FunctionType
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

HA_VERSION_OBJ = AwesomeVersion(HA_VERSION)
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
        self._value = self._data.wiserhub.system.away_mode_target_temperature

        # Support prior to 2022.7.0 Versions without deprecation warning
        if HA_VERSION_OBJ < "2022.7.0":
            self._attr_min_value = self.native_min_value
            self._attr_max_value = self.native_max_value
            self._attr_value = self._data.wiserhub.system.away_mode_target_temperature
            self.set_value = self.set_native_value

        _LOGGER.info(f"Away Mode target temperature initalise")

    async def async_force_update(self):
        await self._data.async_update(no_throttle=True)
        self._value = self._data.wiserhub.system.away_mode_target_temperature

        # Support prior to 2022.7.0 Versions without deprecation warning
        if hasattr(self, "_attr_value"):
            self._attr_value = self._data.wiserhub.system.away_mode_target_temperature

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        return TEMP_MINIMUM

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return TEMP_MAXIMUM

    @property
    def native_step(self) -> float:
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
    def native_value(self):
        """Return device value"""
        return self._value

    def set_native_value(self, value: float) -> None:
        """Set new value."""
        _LOGGER.debug(f"Setting {self._name} to {value}C")
        self._data.wiserhub.system.away_mode_target_temperature = value
        self.hass.async_create_task(self.async_force_update())

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
