"""Binary sensors."""

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA, DOMAIN, MANUFACTURER
from .helpers import get_device_name, get_identifier, get_room_name, get_unique_id

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    binary_sensors = []

    if data.wiserhub.system:
        binary_sensors.extend(
            [
                WiserSummerDiscomfortPrevention(data, 0, "Summer Discomfort Prevention"),
                WiserSummerComfortAvailable(data, 0, "Summer Comfort Available"),
                WiserPCMDeviceLimitReached(data, 0, "PCM Device Limit Reached")
            ]
        ) 


    # Smoke alarm sensors
    for device in data.wiserhub.devices.smokealarms.all:
        binary_sensors.extend(
            [
                WiserSmokeAlarm(data, device.id, "Smoke Alarm"),
                WiserHeatAlarm(data, device.id, "Heat Alarm"),
                WiserTamperAlarm(data, device.id, "Tamper Alarm"),
                WiserFaultWarning(data, device.id, "Fault Warning"),
                WiserRemoteAlarm(data, device.id, "Remote Alarm"),
                WiserBatteryDefect(data, device.id, "Battery Defect"),
            ]
        )

    # Equipments sensors
    for device in data.wiserhub.devices.all:
        if hasattr(device, "equipment") and device.equipment:
            binary_sensors.extend(
                [
                    WiserEquipment(data, device.id, "Controllable", "equipment"),
                    WiserEquipment(data, device.id, "PCM Mode", "equipment"),
                    WiserEquipment(data, device.id, "PCM Mode", "equipment"),
                ]
            )

    # Room binary sensors
    for room in data.wiserhub.rooms.all:
        binary_sensors.extend(
            [
                WiserRoomWindow(data, room.id, "Window Detection Active"),
#                WiserRoomWindow(data, room.id, "Window State"),
            ]
        )


    # Light sensors
    for device in data.wiserhub.devices.lights.all:
        binary_sensors.extend(
            [
                WiserStateIsDimmable(data, device.id, "Is Dimmable"),
                WiserStateIsDimmable(data, device.id, "Is LED Indicator Supported"),
                WiserStateIsDimmable(data, device.id, "Is Output Mode Supported"),
            ]
        )

    # Shutter binary sensors
    for device in data.wiserhub.devices.shutters.all:
        binary_sensors.extend(
            [
                WiserStateIsTiltSupported(data, device.id, "Is Tilt Supported"),
                WiserStateIsOpen(data, device.id, "Is Open"),
                WiserStateIsClosed(data, device.id, "Is Closed"),
            ]
        )


    # Window Door binary sensors
    for device in data.wiserhub.devices.binary_sensor.all:
        binary_sensors.extend(
            [
                WiserStateActive(data, device.id, "Active"),
#                WiserStateActive(data, device.id, "Interacts with room climate"),
            ]
        )


    async_add_entities(binary_sensors, True)


class BaseBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base binary sensor class."""

    def __init__(
        self, coordinator, device_id=0, sensor_type="", device_data_key: str = ""
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._device = self._data.wiserhub.devices.get_by_id(device_id)
        self._device_id = device_id
        self._device_name = None
        self._sensor_type = sensor_type
        self._device_data_key = device_data_key

        _LOGGER.info(
            f"{self._data.wiserhub.system.name} {self.name} initalise"  # noqa: E501
        )

        if device_data_key and hasattr(self._device, device_data_key):
            self._state = getattr(
                getattr(self._device, device_data_key),
                self._sensor_type.replace(" ", "_").lower(),
            )
        else:
            self._state = getattr(
                self._device, self._sensor_type.replace(" ", "_").lower()
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} device update requested")
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        if self._device_data_key and hasattr(self._device, self._device_data_key):
            self._state = getattr(
                getattr(self._device, self._device_data_key),
                self._sensor_type.replace(" ", "_").lower(),
            )
        else:
            self._state = getattr(
                self._device, self._sensor_type.replace(" ", "_").lower()
            )

        self.async_write_ha_state()

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._state

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
            "model": self._device.product_type,
            "sw_version": self._device.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

class SystemBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base binary sensor class."""

    def __init__(self, coordinator, device_id=0, sensor_type="") -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._device_name = None
        self._sensor_type = sensor_type
        self._state = getattr(self._data.wiserhub.system, self._sensor_type.replace(" ", "_").lower())
        _LOGGER.debug(
            f"{self._data.wiserhub.system.name} {self.name} initalise"  # noqa: E501
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} device update requested")
#        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._state = getattr(self._data.wiserhub.system, self._sensor_type.replace(" ", "_").lower())
        self.async_write_ha_state()

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
#        return f"{get_device_name(self._data, self._data.wiserhub.system)} {self._sensor_type}"
        HeatHub = self._data.wiserhub.system.name
        HeatHub = HeatHub.replace("WiserHeat","HeatHub")
        return f"{HeatHub} {self._sensor_type}"
        

    @property
    def unique_id(self):
        """Return uniqueid."""
        return get_unique_id(self._data, "sensor", self._sensor_type, self.name)

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


class RoomBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Base binary sensor class."""

    def __init__(self, coordinator, room_id=0, sensor_type="") -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._room_id = room_id
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._room_name = None
        self._sensor_type = sensor_type
        self._state = getattr(self._room, self._sensor_type.replace(" ", "_").lower())
        _LOGGER.debug(
            f"{self._data.wiserhub.system.name} {self.name} initalise"  # noqa: E501
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} device update requested")
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._state = getattr(self._room, self._sensor_type.replace(" ", "_").lower())
        self.async_write_ha_state()

    @property
    def is_on(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_room_name(self._data, self._room_id)} {self._sensor_type}"
        #return f"{get_device_name(self._data, self._room_id, "room")}  {self._sensor_type}",  
    
    @property
    def unique_id(self):
        """Return uniqueid."""
        return get_unique_id(self._data, "sensor", self._sensor_type, self._room_id)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_room_name(self._data, self._room_id ),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._room_id, "room"))},
            "manufacturer": MANUFACTURER,
            "model": self._data.wiserhub.system.product_type,
            "sw_version": self._data.wiserhub.system.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


class WiserSmokeAlarm(BaseBinarySensor):
    """Smoke Alarm sensor."""

    _attr_device_class = BinarySensorDeviceClass.SMOKE

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


class WiserTamperAlarm(BaseBinarySensor):
    """Smoke Alarm sensor."""

    _attr_device_class = BinarySensorDeviceClass.TAMPER


class WiserFaultWarning(BaseBinarySensor):
    """Smoke Alarm sensor."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM


class WiserBatteryDefect(BaseBinarySensor):
    """Smoke Alarm battery defect sensor."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:battery-alert"


class WiserRemoteAlarm(BaseBinarySensor):
    """Smoke Alarm sensor."""


class WiserEquipment(BaseBinarySensor):
    """Base binary sensor class."""

## binary sensor of System

class WiserSummerDiscomfortPrevention(SystemBinarySensor):
    """Summer Discomfort Prevention sensor."""    
    _attr_device_class = BinarySensorDeviceClass.HEAT

    @property
    def extra_state_attributes(self):
        """Return the state attributes of Summer discomfort prevention."""
        attrs = {}
        attrs["indoor_discomfort_temperature"] = self._data.wiserhub.system.indoor_discomfort_temperature
        attrs["outdoor_discomfort_temperature"] = self._data.wiserhub.system.outdoor_discomfort_temperature
        return attrs

class WiserSummerComfortAvailable(SystemBinarySensor):
    """Summer Comfort Available sensor."""
    _attr_icon = "mdi:sofa"
    _attr_device_class = BinarySensorDeviceClass.HEAT

class WiserPCMDeviceLimitReached(SystemBinarySensor):
    """Summer Comfort Available sensor."""
#    _attr_icon = "mdi:sofa"
    _attr_device_class = BinarySensorDeviceClass.POWER


class WiserStateIsDimmable(BaseBinarySensor):
    """Light IsDimmable sensor."""

    _attr_icon = "mdi:lightbulb-on-40"


class WiserStateIsTiltSupported(BaseBinarySensor):
    """Shutter Istilt supported  sensor."""


class WiserStateIsOpen(BaseBinarySensor):
    """Light IsDIs Open sensor."""

    _attr_device_class = BinarySensorDeviceClass.OPENING


class WiserStateIsClosed(BaseBinarySensor):
    """Light IsDimmable sensor."""

    _attr_device_class = BinarySensorDeviceClass.OPENING
    _attr_icon = "mdi:window-shutter"

## binary sensor of Room
class WiserRoomWindow(RoomBinarySensor):
    """Window of room sensor."""
    _attr_device_class = BinarySensorDeviceClass.WINDOW

#Windowdoor 
class WiserStateActive(BaseBinarySensor):
    """WindowDoor sensor."""

    @property
    def extra_state_attributes(self):
        """Return the state attributes of WindowDoor sensor."""
        attrs = {}   
        if self._data.wiserhub.devices.binary_sensor.get_by_id(
                self._device_id
            ).type == "Door"  :   
            attrs["device_class"] = BinarySensorDeviceClass.DOOR
        else:  attrs["device_class"] = BinarySensorDeviceClass.WINDOW 
        attrs["type"] = self._data.wiserhub.devices.binary_sensor.get_by_id(
                self._device_id
            ).type 
        return attrs
