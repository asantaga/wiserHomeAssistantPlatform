"""Binary sensors."""

import logging

from config.custom_components.wiser.helpers import (
    get_device_name,
    get_identifier,
    get_unique_id,
)
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA, DOMAIN, MANUFACTURER

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    binary_sensors = []

    # Smoke alarm sensors
    for device in data.wiserhub.devices.smokealarms.all:
        binary_sensors.extend(
            [
                WiserSmokeAlarm(data, device.id, "Smoke Alarm"),
                WiserHeatAlarm(data, device.id, "Heat Alarm"),
                WiserTamperAlarm(data, device.id, "Tamper Alarm"),
                WiserFaultWarning(data, device.id, "Fault"),
                WiserRemoteAlarm(data, device.id, "Remote Alarm"),
            ]
        )

    async_add_entities(binary_sensors)


class BaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base binary sensor class."""

    def __init__(self, coordinator, device_id=0, sensor_type="") -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._device = self._data.wiserhub.devices.get_by_id(device_id)
        self._device_id = device_id
        self._device_name = None
        self._sensor_type = sensor_type
        self._room = self._data.wiserhub.rooms.get_by_device_id(self._device_id)
        _LOGGER.debug(
            f"{self._data.wiserhub.system.name} {self.name} {'in room ' + self._room.name if self._room else ''} initalise"  # noqa: E501
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} device update requested")

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_device_name(self._data, self._device_id)} {self._sensor_type}"

    @property
    def unique_id(self):
        """Return uniqueid."""
        return get_unique_id(self._data, "sensor", self._sensor_type, self._device_id)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
            "manufacturer": MANUFACTURER,
            "model": self._data.wiserhub.system.product_type,
            "sw_version": self._data.wiserhub.system.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


class WiserSmokeAlarm(BaseBinarySensor):
    """Smoke Alarm sensor."""

    _attr_device_class = BinarySensorDeviceClass.SMOKE

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return self._device.smoke_alarm

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the battery."""
        attrs = {}
        attrs["led_brightness"] = self._device.led_brightness
        attrs["alarm_sound_mode"] = self._device.alarm_sound_mode
        attrs["alarm_sound_level"] = self._device.alarm_sound_level
        attrs["life_time"] = self._device.life_time
        attrs["hush_duration"] = self._device.hush_duration
        return attrs


class WiserHeatAlarm(BaseBinarySensor):
    """Smoke Alarm sensor."""

    _attr_device_class = BinarySensorDeviceClass.HEAT

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return self._device.heat_alarm


class WiserTamperAlarm(BaseBinarySensor):
    """Smoke Alarm sensor."""

    _attr_device_class = BinarySensorDeviceClass.TAMPER

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return self._device.tamper_alarm


class WiserFaultWarning(BaseBinarySensor):
    """Smoke Alarm sensor."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return self._device.fault_warning


class WiserRemoteAlarm(BaseBinarySensor):
    """Smoke Alarm sensor."""

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return self._device.remote_alarm
