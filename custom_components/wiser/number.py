import asyncio
import logging

from .const import DATA, DOMAIN, MANUFACTURER
from .helpers import get_device_name, get_identifier, get_unique_id, hub_error_handler

from aioWiserHeatAPI.wiserhub import TEMP_MINIMUM, TEMP_MAXIMUM

from awesomeversion import AwesomeVersion
from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import __version__ as HA_VERSION
from homeassistant.helpers.update_coordinator import CoordinatorEntity

HA_VERSION_OBJ = AwesomeVersion(HA_VERSION)
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_numbers = []

    _LOGGER.debug("Setting up Away Mode setpoint setter")
    wiser_numbers.extend(
        [WiserAwayModeTempNumber(data, "Away Mode Target Temperature")]
    )

    # Add min, max and offset for any heating actuator floor temp sensors
    for heating_actuator in [
        heating_actuator
        for heating_actuator in data.wiserhub.devices.heating_actuators.all
        if heating_actuator.floor_temperature_sensor
        and heating_actuator.floor_temperature_sensor.sensor_type != "Not_Fitted"
    ]:
        wiser_numbers.extend(
            [
                WiserFloorTempSensorNumber(
                    data, heating_actuator, "temperature_offset"
                ),
            ],
        )
    async_add_entities(wiser_numbers)


class WiserAwayModeTempNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, name) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._name = name
        self._value = self._data.wiserhub.system.away_mode_target_temperature

        # Support prior to 2022.7.0 Versions without deprecation warning
        if HA_VERSION_OBJ < "2022.7.0":
            self._attr_min_value = self.native_min_value
            self._attr_max_value = self.native_max_value
            self._attr_value = self._data.wiserhub.system.away_mode_target_temperature
            self.set_value = self.set_native_value

        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initialise")

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} updating")
        self._value = self._data.wiserhub.system.away_mode_target_temperature
        # Support prior to 2022.7.0 Versions without deprecation warning
        if hasattr(self, "_attr_value"):
            self._attr_value = self._data.wiserhub.system.away_mode_target_temperature

        self.async_write_ha_state()

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

    @hub_error_handler
    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        _LOGGER.debug(f"Setting {self._name} to {value}C")
        await self._data.wiserhub.system.set_away_mode_target_temperature(value)
        await self.async_force_update()


class WiserFloorTempSensorNumber(CoordinatorEntity, NumberEntity):
    def __init__(self, coordinator, actuator, device_type) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._actuator = actuator
        self._name = device_type
        self._value = getattr(self._actuator.floor_temperature_sensor, self._name)

        # Support prior to 2022.7.0 Versions without deprecation warning
        if HA_VERSION_OBJ < "2022.7.0":
            self._attr_min_value = self.native_min_value
            self._attr_max_value = self.native_max_value
            self._attr_value = self._data.wiserhub.system.away_mode_target_temperature
            self.set_value = self.set_native_value

        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initialise")

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} updating")
        self._value = getattr(self._actuator.floor_temperature_sensor, self._name)
        # Support prior to 2022.7.0 Versions without deprecation warning
        if hasattr(self, "_attr_value"):
            self._attr_value = getattr(
                self._actuator.floor_temperature_sensor, self._name
            )

        self.async_write_ha_state()

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        return -9

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return 9

    @property
    def native_step(self) -> float:
        return 1

    @property
    def mode(self) -> NumberMode:
        """Return the mode of the entity."""
        return NumberMode.AUTO

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._actuator.id)} Floor Temp Offset"

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
            "name": get_device_name(self._data, self._actuator.id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._actuator.id))},
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def native_value(self):
        """Return device value"""
        return self._value

    @hub_error_handler
    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        _LOGGER.debug(f"Setting {self._name} to {value}C")
        await self._actuator.floor_temperature_sensor.set_temperature_offset(value)
        await self.async_force_update()
