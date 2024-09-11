"""
Binary Sensor Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""
import asyncio
import logging
import voluptuous as vol

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import config_validation as cv
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA, DOMAIN, MANUFACTURER, MANUFACTURER_SCHNEIDER
from .helpers import (
    get_device_name,
    get_identifier,
    get_room_name,
    get_unique_id,
)
#from custom_components.wiser.schedules import WiserScheduleEntity

_LOGGER = logging.getLogger(__name__)

ATTR_PLUG_MODE = "plug_mode"
ATTR_HOTWATER_MODE = "hotwater_mode"

SET_PLUG_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_PLUG_MODE, default="Auto"): vol.Coerce(str),
    }
)

WISER_BINARYSENSORS = [
    {
        "name": "Smoke Alarm",
        "key": "smoke_alarm",
        "icon": "mdi:smoke",
        "type": "device",
        "device_class":  "smoke",
    },
    {
        "name": "Tamper Alarm",
        "key": "tamper_alarm",
        "icon": "mdi:smoke-detector-alert",
        "type": "device",
        "device_class": "tamper",
    },
    {
        "name": "Heat Alarm",
        "key": "heat_alarm",
        "icon": "mdi:fire-alert",
        "type": "device",
        "device_class": "heat",
    },
        {
        "name": "Remote Alarm",
        "key": "remote_alarm",
        "icon": "mdi:fire-alert",
        "type": "device",
        "device_class": "heat",
    },
        {
        "name": "Battery Defect",
        "key": "battery_defect",
        "icon": "mdi:battery-alert",
        "type": "device",
        "device_class": "problem",
    },
    {
        "name": "Is Dimmable",
        "key": "is_dimmable",
        "icon": "mdi:lightbulb-on-40",
        "type": "device",
        "device_class": "light"
    },    
    {
        "name": "Is LED Indicator Supported",
        "key": "is_led_indicator_supported",
        "icon": "mdi:led-on",
        "type": "device",
        "device_class": "light",
    },
    {
        "name": "Is Tilt Supported",
        "key": "is_tilt_supported",
        "icon": "mdi:led-on",
        "type": "device",
        "device_class": "cover",
    },
    {
        "name": "Is Open",
        "key": "is_open",
        "icon": "mdi:window-shutter-open",
        "type": "device",
        "device_class": "cover",
    },
    {
        "name": "Is Closed",
        "key": "is_closed",
        "icon": "mdi:window-shutter",
        "type": "device",
        "device_class": "cover",
    },
    {
        "name": "Active",
        "key": "active",
        "icon": "mdi:led-on",
        "type": "device",
        "device_class": "door",
    },
    {
        "name": "Summer Discomfort Prevention",
        "key": "summer_discomfort_prevention",
        "icon": "mdi:sofa",
        "type": "system",
        "device_class": "heat",
    },
    {
        "name": "Summer comfort available",
        "key": "summer_comfort_available",
        "icon": "mdi:sofa",
        "type": "system",
        "device_class": "heat",
    },
    {
        "name": "PCM device limit reached",
        "key": "pcm_device_limit_reached",
        "icon": "mdi:lighting-bolt",
        "type": "system",
        "device_class": "power",
    },
    {
        "name": "Can activate PCM",
        "key": "can_activate_pcm",
        "icon": "mdi:lighting-bolt",
        "type": "system",
        "device_class": "power",
    },
    {
        "name": "Windows State",
        "key": "window_state",
        "icon": "mdi:window-open",
        "type": "room",
        "device_class": "window",
    },
    {
        "name": "Controllable",
        "key": "controllable",
        "icon": "mdi:lighting-bolt",
        "type": "equipment",
        "device_class": "power",
    },
    {
        "name": "Monitored",
        "key": "monitored",
        "icon": "mdi:home-automation",
        "type": "equipment",
        "device_class": "power",
    },
                
    

]


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add the Wiser System BinarySensors entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    # Add Defined BinarySensors
    wiser_binary_sensors= []
    for binary_sensor in WISER_BINARYSENSORS:
        if binary_sensor["type"] == "room":
            for room in [
                room for room in data.wiserhub.rooms.all if len(room.devices) > 0
            ]:
                if getattr(room, binary_sensor["key"]) is not None:
                    wiser_binary_sensors.append(
                        WiserRoomBinarySensor(
                            data, binary_sensor["name"], binary_sensor["key"], binary_sensor["icon"], binary_sensor["device_class"], room.id
                        )
                    )
        elif (
            binary_sensor["type"] == "system"
            and getattr(data.wiserhub.system, binary_sensor["key"]) is not None
        ):
            wiser_binary_sensors.append(
                WiserSystemBinarySensor(data, binary_sensor["name"], binary_sensor["key"], binary_sensor["icon"], binary_sensor["device_class"])
            )

        elif binary_sensor["type"] == "device":
            for device in [
                device
                for device in data.wiserhub.devices.all
                if hasattr(device, binary_sensor["key"])
            ]:
                wiser_binary_sensors.append(
                    WiserDeviceBinarySensor(
                        data, binary_sensor["name"], binary_sensor["key"], binary_sensor["icon"], device.id, binary_sensor["device_class"]
                    )
                )
        elif binary_sensor["type"] == "equipment":
            for device in [
                device
                for device in data.wiserhub.devices.all
                if hasattr(device, "equipment")
#                and device.equipment.device_id > 0
            ]:
                wiser_binary_sensors.append(
                    WiserEquipmentBinarySensor(
                        data, binary_sensor["name"], binary_sensor["key"], binary_sensor["icon"], device.id, binary_sensor["device_class"]
                    )
                )
    async_add_entities(wiser_binary_sensors)

    return True

class WiserBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """BinarySensors to set the status of the Wiser Operation Mode (Away/Normal)."""

    def __init__(self, coordinator, name, key, device_type, icon, device_class) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._key = key
        self._icon = icon
        self._name = name
        self.device_class= device_class
        self._type = device_type
        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} init")

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            await asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} binary_sensor update requested")

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, 0, self._name)}"

    @property
    def icon(self):
        """Return icon."""
        return self._icon

    @property
    def unique_id(self):
        return get_unique_id(self._data, self._type, "binary_sensor", self.name)

class WiserSystemBinarySensor(WiserBinarySensor):
    """BinarySensors to set the status of a system binary_sensor"""

    def __init__(self, data, name, key, icon,device_class) -> None:
        """Initialize the sensor."""
#        self._device_id = device_id
        self._device_class = device_class

        super().__init__(data, name, key, "system", icon, device_class)


    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._state = getattr(self._data.wiserhub.system, self._key)
        self.async_write_ha_state()

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return getattr(self._data.wiserhub.system, self._key)
 
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
    def extra_state_attributes(self):
        """Return the device state attributes for the attribute card."""
        attrs = {}

        if self._name == "Summer Discomfort Prevention":
            attrs["indoor_discomfort_temperature"] = self._data.wiserhub.system.indoor_discomfort_temperature
            attrs["outdoor_discomfort_temperature"] = self._data.wiserhub.system.outdoor_discomfort_temperature
        return attrs

class WiserRoomBinarySensor(WiserBinarySensor):
    """BinarySensors to set the status of a system binary_sensor"""

    def __init__(self, data, name, key, icon,device_class, room_id) -> None:
        """Initialize the sensor."""
        self._room_id = room_id
        super().__init__(data, name, key, "room", icon, device_class)
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
#        self._is_on = getattr(self._room, self._key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._state = getattr(self._room, self._key)
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_room_name(self._data, self._room_id)} {self._name}"

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return getattr(self._room, self._key)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._room_id, "room"),
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._room_id, "room"))
            },
            "manufacturer": MANUFACTURER,
            "model": "Room",
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def extra_state_attributes(self):
        """Return the device state attributes for the attribute card."""
        attrs = {}

        return attrs

class WiserDeviceBinarySensor(WiserBinarySensor):
    """BinarySensors to set the status of a binary_sensor"""

    def __init__(self, data, name, key, icon, device_id, device_class)-> None:
        """Initialize the sensor."""
        self._device_id = device_id
        self._device_class = device_class

        super().__init__(data, name, key, "device-binary_sensor", icon, device_class)
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._state = getattr(self._device, self._key)



    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
       
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._device_id)} {self._name}"

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, self._device.product_type, self._name, self._device_id
        )
    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return getattr(self._device, self._key)
        
    
    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
            "manufacturer": MANUFACTURER_SCHNEIDER,
            "model": self._device.product_type,
            "sw_version": self._device.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def extra_state_attributes(self):
        """Return the device state attributes for the attribute card."""
        attrs = {}       
        return attrs

class WiserSmartPlugBinarySensor(WiserBinarySensor):
    """Plug BinarySensorsEntity Class."""

    def __init__(self, data, plugId, name) -> None:
        """Initialize the sensor."""
        self._name = name
        self._device_id = plugId
        super().__init__(data, name, "", "smartplug", "mdi:power-socket-uk")
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self._is_on = self._device.is_on

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self._is_on = self._device.is_on
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._device_id)} BinarySensors"

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, self._device.product_type, self.name, self._device_id
        )

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

    @property
    def extra_state_attributes(self):
        """Return set of device state attributes."""
        attrs = {}
        return attrs

class WiserShutterSummerComfortBinarySensor(WiserBinarySensor):
    """Shutter Respect Summer Comfort Class."""

    def __init__(self, data, ShutterId, name) -> None:
        """Initialize the sensor."""
        self._name = name
        self._shutter_id = ShutterId
        super().__init__(data, name, "", "shutter", "mdi:sofa")
        self._shutter = self._data.wiserhub.devices.get_by_id(self._shutter_id)
        self._is_on = True if self._shutter.respect_summer_comfort == False else False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._shutter = self._data.wiserhub.devices.get_by_id(self._shutter_id)
        self._is_on = True if self._shutter.respect_summer_comfort == True else False
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._shutter_id)} Respect Summer Comfort"

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, self._shutter.product_type, self.name, self._shutter_id
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._shutter_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._shutter_id))},
            "manufacturer": MANUFACTURER_SCHNEIDER,
            "model": self._shutter.product_type,
            "sw_version": self._shutter.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def extra_state_attributes(self):
        """Return the device state attributes for the attribute card."""
        attrs = {}

        attrs["summer_comfort_lift"] = self._shutter.summer_comfort_lift
        attrs["summer_comfort_tilt"] = self._shutter.summer_comfort_tilt
        return attrs

class WiserEquipmentBinarySensor(WiserBinarySensor):
    """Equipment Binary sensor Class."""

    def __init__(self, data, name, key, icon, device_id, device_class)-> None:
        """Initialize the sensor."""
        self._device_id = device_id
        self._device_class = device_class

        super().__init__(data, name, key, "equipment-binary_sensor", icon, device_class)
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._state = getattr(self._device.equipment, self._key)



    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
       
        self.async_write_ha_state()


    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._device_id)} equipment {self._name}"

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, self._device.product_type, self._name, self._device.equipment.id
        )
    
    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return getattr(self._device.equipment, self._key)
        
    
    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
            "manufacturer": MANUFACTURER_SCHNEIDER,
            "model": self._device.product_type,
            "sw_version": self._device.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def extra_state_attributes(self):
        """Return the device state attributes for the attribute card."""
        attrs = {}
        return attrs

