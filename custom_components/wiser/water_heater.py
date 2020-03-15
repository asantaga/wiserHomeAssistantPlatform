"""Support for wiser water heater."""
from homeassistant.components.water_heater import (
    STATE_OFF,
    STATE_ON,
    SUPPORT_OPERATION_MODE,
    WaterHeaterDevice,
)
from homeassistant.const import TEMP_CELSIUS

from .const import DOMAIN, _LOGGER

STATE_AUTO = "auto"
SUPPORT_FLAGS = SUPPORT_OPERATION_MODE

WISER_TO_HASS_STATE = {"SCHEDULE": STATE_AUTO, "ON": STATE_ON, "OFF": STATE_OFF}
HASS_TO_WISER_STATE = {STATE_AUTO: "SCHEDULE", STATE_ON: "ON", STATE_OFF: "OFF"}
SUPPORT_WATER_HEATER = [STATE_AUTO, STATE_ON, STATE_OFF]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Wiser water heater device."""

    data = hass.data[DOMAIN]
    devices = []

    # Check if hub has hot water function
    if data.wiserhub.getHotwater() is not None:
        devices.append(WiserWaterHeater(hass, data))
    async_add_entities(devices)


class WiserWaterHeater(WaterHeaterDevice):
    """Wiser Water Heater Device."""

    def __init__(self, hass, data):
        self.data = data
        self._name = "Wiser Hot Water Mode"
        self._force_update = False
        _LOGGER.info("{} device init".format(self._name))

    @property
    def unique_id(self):
        """Return unique ID of entity."""
        return "{}-{}".format(self._name, self.data.wiserhub.getWiserHubName)

    @property
    def device_info(self):
        """Return device specific attributes."""
        identifier = self.data.unique_id

        return {
            "identifiers": {(DOMAIN, identifier)},
        }

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def name(self):
        """Return the name of the water heater."""
        return self._name

    @property
    def icon(self):
        return "mdi:water-boiler"

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    @property
    def current_operation(self):
        """Return current operation."""
        return (
            WISER_TO_HASS_STATE[self.data.wiserhub.getHotwater.get("Mode")] or STATE_OFF
        )

    @property
    def operation_list(self):
        """List of available operation modes."""
        return SUPPORT_WATER_HEATER

    def set_operation_mode(self, operation_mode):
        """Set operation mode."""
        new_mode = HASS_TO_WISER_STATE[operation_mode]
        self.data.wiserhub.setHotwaterMode(new_mode)
        self._force_update = True

    async def async_update(self):
        _LOGGER.debug("Update requested for {}".format(self.name))
        if self._force_update:
            await self.data.async_update(no_throttle=True)
            self._force_update = False
        else:
            await self.data.async_update()
