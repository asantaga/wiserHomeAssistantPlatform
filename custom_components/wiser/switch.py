"""
Switch  Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""
import asyncio
import logging
from custom_components.wiser.schedules import WiserScheduleEntity
import voluptuous as vol

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .const import DATA, DOMAIN, MANUFACTURER
from .helpers import get_device_name, get_identifier, get_room_name, get_unique_id

_LOGGER = logging.getLogger(__name__)

ATTR_PLUG_MODE = "plug_mode"
ATTR_HOTWATER_MODE = "hotwater_mode"

SET_PLUG_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_PLUG_MODE, default="Auto"): vol.Coerce(str),
    }
)

WISER_SWITCHES = [
    {
        "name": "Valve Protection",
        "key":  "valve_protection_enabled",
        "icon": "mdi:snowflake-alert",
        "type": "system",
    },
    {
        "name": "Eco Mode", 
        "key":  "eco_mode_enabled", 
        "icon": "mdi:leaf",
        "type": "system",
    },
    {
        "name": "Away Mode Affects Hot Water",
        "key":  "away_mode_affects_hotwater",
        "icon": "mdi:water",
        "type": "system",
    },
    {
        "name": "Comfort Mode", 
        "key":  "comfort_mode_enabled", 
        "icon": "mdi:sofa",
        "type": "system",
    },
    {
        "name": "Away Mode",
        "key":  "away_mode_enabled",
        "icon": "mdi:beach",
        "type": "system",
    },
    {
        "name": "Daylight Saving",
        "key":  "automatic_daylight_saving_enabled", 
        "icon": "mdi:clock-time-one",
        "type": "system",
    },
    {
        "name": "Window Detection",
        "key":  "window_detection_active",
        "icon": "mdi:window-closed",
        "type": "room"
    },
    {
        "name": "Device Lock",
        "key":  "device_lock_enabled",
        "icon": "mdi:lock",
        "type": "device"
    },
    {
        "name": "Identify",
        "key":  "identify",
        "icon": "mdi:alarm-light",
        "type": "device"
    },
]


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    # Add Defined Switches
    wiser_switches = []
    for switch in WISER_SWITCHES:
        if switch["type"] == "room":
            for room in [room for room in data.wiserhub.rooms.all if len(room.devices) > 0]:
                wiser_switches.append(
                    WiserRoomSwitch(data, switch["name"], switch["key"], switch["icon"], room.id )
                )
        elif switch["type"] == "system":
            wiser_switches.append(
                WiserSystemSwitch(data, switch["name"], switch["key"], switch["icon"])
            )
        elif switch["type"] == "device":
            for device in [device for device in data.wiserhub.devices.all if hasattr(device, switch["key"])]:
                wiser_switches.append(
                    WiserDeviceSwitch(data, switch["name"], switch["key"], switch["icon"], device.id )
                )
        
    


    # Add SmartPlugs (if any)
    for plug in data.wiserhub.devices.smartplugs.all:
        wiser_switches.extend([
            WiserSmartPlugSwitch(data, plug.id, f"Wiser {plug.name}"),
            WiserSmartPlugAwayActionSwitch(data, plug.id, f"Wiser {plug.name}")
        ])

    async_add_entities(wiser_switches)

    return True


class WiserSwitch(SwitchEntity):
    """Switch to set the status of the Wiser Operation Mode (Away/Normal)."""

    def __init__(self, data, name, key, type, icon):
        """Initialize the sensor."""
        self._data = data
        self._key = key
        self._icon = icon
        self._name = name
        self._is_on = False
        self._type = type
        self._away_temperature = None
        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} init")

    async def async_force_update(self):
        await self._data.async_update(no_throttle=True)

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
        return get_unique_id(self._data, self._type, "switch", self.name)

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        raise NotImplemented

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        raise NotImplemented


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


class WiserSystemSwitch(WiserSwitch):
    """Switch to set the status of a system switch"""

    def __init__(self, data, name, key, icon):
        """Initialize the sensor."""
        super().__init__(data, name, key, "system", icon)
        self._away_temperature = None
        self._is_on = getattr(self._data.wiserhub.system, self._key)

    async def async_update(self):
        """Async Update to HA."""
        _LOGGER.debug(f"Wiser {self.name} Switch Update requested")
        self._is_on = getattr(self._data.wiserhub.system, self._key)
        if self._name == "Away Mode":
            self._away_temperature = self._data.wiserhub.system.away_mode_target_temperature

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.hass.async_add_executor_job(
            setattr, self._data.wiserhub.system, self._key, True
        )
        await self.async_force_update()
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.hass.async_add_executor_job(
            setattr, self._data.wiserhub.system, self._key, False
        )
        await self.async_force_update()
        return True

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

        if self._name == "Away Mode":
            attrs["away_mode_temperature"] = self._away_temperature

        return attrs


class WiserRoomSwitch(WiserSwitch):
    """Switch to set the status of a system switch"""

    def __init__(self, data, name, key, icon, room_id):
        """Initialize the sensor."""
        self._room_id = room_id
        super().__init__(data, name, key, "room", icon)
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._is_on = getattr(self._room, self._key)

    async def async_update(self):
        """Async Update to HA."""
        _LOGGER.debug(f"Wiser {self.name} Switch Update requested")
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._is_on = getattr(self._room, self._key)

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_room_name(self._data, self._room_id)} {self._name}"

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.hass.async_add_executor_job(
            setattr, self._room, self._key, True
        )
        await self.async_force_update()
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.hass.async_add_executor_job(
            setattr, self._room, self._key, False
        )
        await self.async_force_update()
        return True

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._room_id,"room"),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._room_id,"room"))},
                "manufacturer": MANUFACTURER,
                "model": "Room",
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def extra_state_attributes(self):
        """Return the device state attributes for the attribute card."""
        attrs = {}
        return attrs


class WiserDeviceSwitch(WiserSwitch):
    """Switch to set the status of a TRV/Roomstat switch"""

    def __init__(self, data, name, key, icon, device_id):
        """Initialize the sensor."""
        self._device_id = device_id
        super().__init__(data, name, key, "device-switch", icon)
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._is_on = getattr(self._device, self._key)

    async def async_update(self):
        """Async Update to HA."""
        _LOGGER.debug(f"Wiser {self.name} Switch Update requested")
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._is_on = getattr(self._device, self._key)

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._device_id)} {self._name}"

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.hass.async_add_executor_job(
            setattr, self._device, self._key, True
        )
        await self.async_force_update()
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.hass.async_add_executor_job(
            setattr, self._device, self._key, False
        )
        await self.async_force_update()
        return True

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, 
            self._device.product_type, 
            self._name,
            self._device_id
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
        """Return the device state attributes for the attribute card."""
        attrs = {}
        return attrs


class WiserSmartPlugSwitch(WiserSwitch, WiserScheduleEntity):
    """Plug SwitchEntity Class."""

    def __init__(self, data, plugId, name):
        """Initialize the sensor."""
        self._name = name
        self._smart_plug_id = plugId
        super().__init__(data, name, "", "smartplug", "mdi:power-socket-uk")
        self._smartplug = self._data.wiserhub.devices.get_by_id(self._smart_plug_id)
        self._schedule = self._smartplug.schedule
        self._is_on = self._smartplug.is_on

    async def async_force_update(self):
        await asyncio.sleep(2)
        await self._data.async_update(no_throttle=True)

    async def async_update(self):
        """Async Update to HA."""
        _LOGGER.debug(f"Wiser {self.name} Switch Update requested")
        self._smartplug = self._data.wiserhub.devices.get_by_id(self._smart_plug_id)
        self._schedule = self._smartplug.schedule
        self._is_on = self._smartplug.is_on

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._smart_plug_id)} Switch"
    
    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, 
            self._smartplug.product_type, 
            self.name,
            self._smart_plug_id
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._smart_plug_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._smart_plug_id))},
                "manufacturer": MANUFACTURER,
                "model": self._smartplug.product_type,
                "sw_version": self._smartplug.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def extra_state_attributes(self):
        """Return set of device state attributes."""
        attrs = {}
        attrs["control_source"] = self._smartplug.control_source
        attrs["manual_state"] = self._smartplug.manual_state
        attrs["mode"] = self._smartplug.mode
        attrs["name"] = self._smartplug.name
        attrs["output_state"] = "On" if self._smartplug.is_on else "Off"
        # Switches could be not allocated to room (issue:209)
        if  self._data.wiserhub.rooms.get_by_id(self._smartplug.room_id) is not None:
            attrs["room"] = self._data.wiserhub.rooms.get_by_id(self._smartplug.room_id).name
        else:
            attrs["room"] = "Unassigned"     
        attrs["scheduled_state"] = self._smartplug.scheduled_state
        if self._smartplug.schedule:
            attrs["next_schedule_change"] = str(self._smartplug.schedule.next.time)
            attrs["next_schedule_state"] = self._smartplug.schedule.next.setting
        return attrs

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.hass.async_add_executor_job(
            self._smartplug.turn_on
        )
        await self.async_force_update()
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.hass.async_add_executor_job(
            self._smartplug.turn_off
        )
        await self.async_force_update()
        return True


class WiserSmartPlugAwayActionSwitch(WiserSwitch):
    """Plug SwitchEntity Class."""

    def __init__(self, data, plugId, name):
        """Initialize the sensor."""
        self._name = name
        self._smart_plug_id = plugId
        super().__init__(data, name, "", "smartplug", "mdi:power-socket-uk")
        self._smartplug = self._data.wiserhub.devices.get_by_id(self._smart_plug_id)
        self._is_on = True if self._smartplug.away_mode_action == "Off" else False

    async def async_force_update(self):
        await asyncio.sleep(2)
        await self._data.async_update(no_throttle=True)

    async def async_update(self):
        """Async Update to HA."""
        _LOGGER.debug(f"Wiser {self.name} Switch Update requested")
        self._smartplug = self._data.wiserhub.devices.get_by_id(self._smart_plug_id)
        self._is_on = True if self._smartplug.away_mode_action == "Off" else False

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._smart_plug_id)} Away Mode Turns Off"
    
    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, 
            self._smartplug.product_type, 
            self.name,
            self._smart_plug_id
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._smart_plug_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._smart_plug_id))},
                "manufacturer": MANUFACTURER,
                "model": self._smartplug.product_type,
                "sw_version": self._smartplug.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self.hass.async_add_executor_job(
            setattr, self._smartplug, "away_mode_action", "Off"
        )
        await self.async_force_update()
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self.hass.async_add_executor_job(
            setattr, self._smartplug, "away_mode_action", "NoChange"
        )
        await self.async_force_update()
        return True
