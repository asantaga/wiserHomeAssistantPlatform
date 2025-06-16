"""
Switch  Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""

import asyncio
import datetime as dt
import logging
import voluptuous as vol

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.helpers import config_validation as cv
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA, DOMAIN, HOT_WATER, MANUFACTURER, MANUFACTURER_SCHNEIDER
from .helpers import (
    get_device_name,
    get_identifier,
    get_room_name,
    get_unique_id,
    hub_error_handler,
)
from custom_components.wiser.schedules import WiserScheduleEntity

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
        "key": "valve_protection_enabled",
        "icon": "mdi:snowflake-alert",
        "type": "system",
    },
    {
        "name": "Eco Mode",
        "key": "eco_mode_enabled",
        "icon": "mdi:leaf",
        "type": "system",
    },
    {
        "name": "Away Mode Affects Hot Water",
        "key": "away_mode_affects_hotwater",
        "icon": "mdi:water",
        "type": "system",
    },
    {
        "name": "Comfort Mode",
        "key": "comfort_mode_enabled",
        "icon": "mdi:sofa",
        "type": "system",
    },
    {
        "name": "Away Mode",
        "key": "away_mode_enabled",
        "icon": "mdi:beach",
        "type": "system",
    },
    {
        "name": "Daylight Saving",
        "key": "automatic_daylight_saving_enabled",
        "icon": "mdi:clock-time-one",
        "type": "system",
    },
    {
        "name": "Summer Comfort Enabled",
        "key": "summer_comfort_enabled",
        "icon": "mdi:sofa",
        "type": "system",
    },
    {
        "name": "Window Detection",
        "key": "window_detection_active",
        "icon": "mdi:window-closed",
        "type": "room",
    },
    {
        "name": "Include In Summer Comfort",
        "key": "include_in_summer_comfort",
        "icon": "mdi:sofa",
        "type": "room",
    },
    # added by LGO , App V7
    {
        "name": "Seasonal Comfort Enabled",
        "key": "seasonal_comfort_enabled",
        "icon": "mdi:sofa",
        "type": "system",
    },    
    {
        "name": "Device Lock",
        "key": "device_lock_enabled",
        "icon": "mdi:lock",
        "type": "device",
    },
    {
        "name": "Identify",
        "key": "identify",
        "icon": "mdi:alarm-light",
        "type": "device",
    },
    {
        "name": "Enable Notification switch",
        "key": "enablenotification",
        "icon": "mdi:check-circle",
        "type": "device",
    },
    {
        "name": "Over Power Notification Enabled",
        "key": "enabled",
        "icon": "mdi:check-circle",
        "type": "device",
    },
    {
        "name": "Under Power Notification Enabled",
        "key": "enabled",
        "icon": "mdi:check-circle",
        "type": "device",
    },

]


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    # Add Defined Switches
    wiser_switches = []
    for switch in WISER_SWITCHES:
        if switch["type"] == "room":
            for room in [
                room for room in data.wiserhub.rooms.all if len(room.devices) > 0
            ]:
                if getattr(room, switch["key"]) is not None:
                    wiser_switches.append(
                        WiserRoomSwitch(
                            data, switch["name"], switch["key"], switch["icon"], room.id
                        )
                    )
        elif (
            switch["type"] == "system"
            and getattr(data.wiserhub.system, switch["key"]) is not None
        ):
            wiser_switches.append(
                WiserSystemSwitch(data, switch["name"], switch["key"], switch["icon"])
            )

        elif switch["type"] == "device":
            for device in [
                device
                for device in data.wiserhub.devices.all
                if hasattr(device, switch["key"])
            ]:
                wiser_switches.append(
                    WiserDeviceSwitch(
                        data, switch["name"], switch["key"], switch["icon"], device.id
                    )
                )

    # Add Lights (if any)
    for light in data.wiserhub.devices.lights.all:
        wiser_switches.extend(
            [WiserLightAwayActionSwitch(data, light.id, f"Wiser {light.name}")]
        )

    # Add Shutters (if any)
    for shutter in data.wiserhub.devices.shutters.all:
        wiser_switches.extend(
            [WiserShutterAwayActionSwitch(data, shutter.id, f"Wiser {shutter.name}")]
        )
        if data.hub_version == 2:
#            wiser_switches.append(
            wiser_switches.extend(                
                [
                WiserShutterSummerComfortSwitch(data, shutter.id, f"Wiser {shutter.name}"),
                WiserShutterSeasonalComfortSwitch(data, shutter.id, f"Wiser {shutter.name}"),
                ]
            )

    # Add SmartPlugs (if any)
    for plug in data.wiserhub.devices.smartplugs.all:
        wiser_switches.extend(
            [
                WiserSmartPlugSwitch(data, plug.id, f"Wiser {plug.name}"),
                WiserSmartPlugAwayActionSwitch(data, plug.id, f"Wiser {plug.name}"),
            ]
        )

    # Add smokealarm  (if any)
    for smokealarm in data.wiserhub.devices.smokealarms.all:
        wiser_switches.extend(
            [
                WiserDeviceEnableNotificationSwitch(data, smokealarm.id, f"Wiser {smokealarm.name}"),
            ]
        )

    # Add PTCs
    for ptc in data.wiserhub.devices.power_tags_c.all:
        wiser_switches.extend(
            [
                WiserSmartPlugSwitch(data, ptc.id, f"Wiser {ptc.name}"),
                WiserSmartPlugAwayActionSwitch(data, ptc.id, f"Wiser {ptc.name}"),
            ]
        )

    # Add threshold sensor interacts with room climate switch
    for device in data.wiserhub.devices.all:
        if hasattr(device, "interacts_with_room_climate"):
            wiser_switches.extend(
                [
                    WiserInteractsRoomClimateSwitch(
                        data,
                        device.id,
                        f"Wiser {device.name}",
                        is_threshold=False,
                    ),
                ]
            )
        if hasattr(device, "threshold_sensors"):
            for threshold_sensor in getattr(device, "threshold_sensors"):
                wiser_switches.extend(
                    [
                        WiserInteractsRoomClimateSwitch(
                            data,
                            device.id,
                            f"Wiser {device.name}",
                            is_threshold=True,
                            ancillary_sensor_id=threshold_sensor.id,
                            ancillary_sensor_type=threshold_sensor.quantity,
                        ),
                    ]
                )

    # Add Equipments (if any)
    for device in data.wiserhub.devices.all:
       if hasattr(device, "equipment"): 
            
            if hasattr(device.equipment.over_power_notification,"period_mins"):
                wiser_switches.append(

#                    WiserEquipmentEnableNotificationSwitch1(
#                        data,switch["name"], switch["key"],switch["icon"], device.id
#                    ),
                    WiserEquipmentEnableNotificationSwitch1(
                        data,"Over Power Notification", "enabled","mdi:check-circle", device.id
                    ),
                )
           

            if hasattr(device.equipment.under_power_notification,"period_mins"):
                wiser_switches.append(
                    WiserEquipmentEnableNotificationSwitch1(
                        data,"Under Power Notification", switch["key"], "mdi:check-circle", device.id
                    ),    
#                    WiserEquipmentEnableNotificationSwitch1(
#                        data,switch["name"], switch["key"], switch["icon"], device.id
#                    )
                )

    # Add Room passive mode switches
    if data.enable_automations_passive_mode:
        for room in data.wiserhub.rooms.all:
            if room.number_of_smartvalves > 0:
                wiser_switches.append(
                    WiserPassiveModeSwitch(
                        hass, data, room.id, f"Wiser Passive Mode {room.name}"
                    )
                )

    # Add hw climate switches
    if data.enable_hw_climate and not data.hw_climate_experimental_mode:
        wiser_switches.append(WiserHWClimateManualHeatSwitch(data, 0, "Manual Heat"))

    async_add_entities(wiser_switches)

    return True


class WiserSwitch(CoordinatorEntity, SwitchEntity):
    """Switch to set the status of the Wiser Operation Mode (Away/Normal)."""

    def __init__(self, coordinator, name, key, device_type, icon) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._key = key
        self._icon = icon
        self._name = name
        self._is_on = False
        self._type = device_type
        self._away_temperature = None
        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} init")

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            await asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} switch update requested")

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
    def is_on(self):
        """Return true if device is on."""
        return self._is_on

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        raise NotImplementedError

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        raise NotImplementedError


class WiserSystemSwitch(WiserSwitch):
    """Switch to set the status of a system switch"""

    def __init__(self, data, name, key, icon) -> None:
        """Initialize the sensor."""
        super().__init__(data, name, key, "system", icon)
        self._away_temperature = None
        self._is_on = getattr(self._data.wiserhub.system, self._key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._is_on = getattr(self._data.wiserhub.system, self._key)
        if self._name == "Away Mode":
            self._away_temperature = (
                self._data.wiserhub.system.away_mode_target_temperature
            )
        self.async_write_ha_state()

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""

        fn = getattr(self._data.wiserhub.system, "set_" + self._key)
        await fn(True)
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        fn = getattr(self._data.wiserhub.system, "set_" + self._key)
        await fn(False)
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

        if self._name == "Daylight Saving":
            attrs["hub_time"] = self._data.wiserhub.system.hub_time

        return attrs


class WiserRoomSwitch(WiserSwitch):
    """Switch to set the status of a system switch"""

    def __init__(self, data, name, key, icon, room_id) -> None:
        """Initialize the sensor."""
        self._room_id = room_id
        super().__init__(data, name, key, "room", icon)
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._is_on = getattr(self._room, self._key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._is_on = getattr(self._room, self._key)
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_room_name(self._data, self._room_id)} {self._name}"

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        fn = getattr(self._room, "set_" + self._key)
        await fn(True)
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        fn = getattr(self._room, "set_" + self._key)
        await fn(False)
        await self.async_force_update()
        return True

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


class WiserDeviceSwitch(WiserSwitch):
    """Switch to set the status of a TRV/Roomstat switch"""

    def __init__(self, data, name, key, icon, device_id) -> None:
        """Initialize the sensor."""
        self._device_id = device_id
        super().__init__(data, name, key, "device-switch", icon)
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._is_on = getattr(self._device, self._key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._is_on = getattr(self._device, self._key)
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._device_id)} {self._name}"

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        fn = getattr(self._device, "set_" + self._key)
        await fn(True)
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        fn = getattr(self._device, "set_" + self._key)
        await fn(False)
        await self.async_force_update()
        return True

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, self._device.product_type, self._name, self._device_id
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
        return f"{get_device_name(self._data, self._device_id)} Switch"

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
        attrs["control_source"] = self._device.control_source
        attrs["manual_state"] = self._device.manual_state
        attrs["mode"] = self._device.mode
        attrs["name"] = self._device.name
        attrs["output_state"] = "On" if self._device.is_on else "Off"
        # Switches could be not allocated to room (issue:209)
        if self._data.wiserhub.rooms.get_by_id(self._device.room_id) is not None:
            attrs["room"] = self._data.wiserhub.rooms.get_by_id(
                self._device.room_id
            ).name
        else:
            attrs["room"] = "Unassigned"
        attrs["away_mode_action"] = self._device.away_mode_action
        attrs["scheduled_state"] = self._device.scheduled_state
        attrs["schedule_id"] = self._device.schedule_id
        if self._device.schedule:
            attrs["schedule_name"] = self._device.schedule.name
            attrs["next_day_change"] = str(self._device.schedule.next.day)
            attrs["next_schedule_change"] = str(self._device.schedule.next.time)
            attrs["next_schedule_datetime"] = str(self._device.schedule.next.datetime)
            attrs["next_schedule_state"] = self._device.schedule.next.setting
        return attrs

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._device.turn_on()
        await self.async_force_update(2)
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self._device.turn_off()
        await self.async_force_update(2)
        return True


class WiserSmartPlugAwayActionSwitch(WiserSwitch):
    """Plug SwitchEntity Class."""

    def __init__(self, data, plugId, name) -> None:
        """Initialize the sensor."""
        self._name = name
        self._smart_plug_id = plugId
        super().__init__(data, name, "", "smartplug", "mdi:power-socket-uk")
        self._smartplug = self._data.wiserhub.devices.get_by_id(self._smart_plug_id)
        self._is_on = True if self._smartplug.away_mode_action == "Off" else False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._smartplug = self._data.wiserhub.devices.get_by_id(self._smart_plug_id)
        self._is_on = True if self._smartplug.away_mode_action == "Off" else False
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._smart_plug_id)} Away Mode Turns Off"

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, self._smartplug.product_type, self.name, self._smart_plug_id
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

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._smartplug.set_away_mode_action("Off")
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self._smartplug.set_away_mode_action("NoChange")
        await self.async_force_update()
        return True


class WiserLightAwayActionSwitch(WiserSwitch):
    """Plug SwitchEntity Class."""

    def __init__(self, data, LightId, name) -> None:
        """Initialize the sensor."""
        self._name = name
        self._light_id = LightId
        super().__init__(data, name, "", "light", "mdi:lightbulb-off-outline")
        self._light = self._data.wiserhub.devices.get_by_id(self._light_id)
        self._is_on = True if self._light.away_mode_action == "Off" else False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._light = self._data.wiserhub.devices.get_by_id(self._light_id)
        self._is_on = True if self._light.away_mode_action == "Off" else False
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._light_id)} Away Mode Turns Off"

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, self._light.product_type, self.name, self._light_id
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._light_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._light_id))},
            "manufacturer": MANUFACTURER,
            "model": self._light.product_type,
            "sw_version": self._light.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._light.set_away_mode_action("Off")
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self._light.set_away_mode_action("NoChange")
        await self.async_force_update()
        return True


class WiserShutterAwayActionSwitch(WiserSwitch):
    """Plug SwitchEntity Class."""

    def __init__(self, data, ShutterId, name) -> None:
        """Initialize the sensor."""
        self._name = name
        self._shutter_id = ShutterId
        super().__init__(data, name, "", "shutter", "mdi:window-shutter")
        self._shutter = self._data.wiserhub.devices.get_by_id(self._shutter_id)
        self._is_on = True if self._shutter.away_mode_action == "Close" else False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._shutter = self._data.wiserhub.devices.get_by_id(self._shutter_id)
        self._is_on = True if self._shutter.away_mode_action == "Close" else False
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._shutter_id)} Away Mode Closes"

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
            "manufacturer": MANUFACTURER,
            "model": self._shutter.product_type,
            "sw_version": self._shutter.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._shutter.set_away_mode_action("Close")
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        await self._shutter.set_away_mode_action("NoChange")
        await self.async_force_update()
        return True


class WiserPassiveModeSwitch(WiserSwitch):
    """Room Passive Mode SwitchEntity Class."""

    def __init__(self, hass: HomeAssistant, data, room_id, name) -> None:
        """Initialize the sensor."""
        self._name = name
        self._room_id = room_id
        self._hass = hass
        super().__init__(data, name, "", "passive-mode", "mdi:thermostat-box")
        self._is_on = self._data.wiserhub.rooms.get_by_id(
            self._room_id
        ).passive_mode_enabled

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._is_on = self._data.wiserhub.rooms.get_by_id(
            self._room_id
        ).passive_mode_enabled
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._room_id, 'room')} Passive Mode"

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data, "passive-mode-switch", self.name, self._room_id
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._room_id, "room"),
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._room_id, "room"))
            },
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def extra_state_attributes(self):
        """Return set of device state attributes."""
        attrs = {}
        return attrs

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._data.wiserhub.rooms.get_by_id(self._room_id).set_passive_mode(True)
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        await room.set_passive_mode(False)
        await room.cancel_overrides()
        await self.async_force_update()
        return True


class WiserShutterSummerComfortSwitch(WiserSwitch):
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
            "manufacturer": MANUFACTURER,
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

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the respect summer comfort on."""
        await self._shutter.set_respect_summer_comfort("true")
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the respect summer comfort off."""
        await self._shutter.set_respect_summer_comfort("false")
        await self.async_force_update()
        return True

class WiserShutterSeasonalComfortSwitch(WiserSwitch):
    """Shutter Respect Seasonal Comfort Class."""

    def __init__(self, data, ShutterId, name) -> None:
        """Initialize the sensor."""
        self._name = name
        self._shutter_id = ShutterId
        super().__init__(data, name, "", "shutter", "mdi:sofa")
        self._shutter = self._data.wiserhub.devices.get_by_id(self._shutter_id)
        self._is_on = True if self._shutter.respect_seasonal_comfort == False else False

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._shutter = self._data.wiserhub.devices.get_by_id(self._shutter_id)
        self._is_on = True if self._shutter.respect_seasonal_comfort == True else False
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._shutter_id)} Respect Seasonal Comfort"

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
        # Seasonal comfort Added LGO
        attrs["respect_seasonal_comfort"] = self._shutter.respect_seasonal_comfort
        attrs["room_with_temperature_sensor"] = self._shutter.room_with_temperature_sensor
        attrs["use_average_temperature"] = self._shutter.use_average_temperature
        if self._shutter.covering_type == "Door":
            attrs["covering_type"] = self._shutter.covering_type
       
        attrs["seasonal_target_lift"] = self._shutter.seasonal_target_lift
        attrs["facade"] = self._shutter.facade
        attrs["seasonal_derogation_utc_timestamp"] = self._shutter.seasonal_derogation_utc_timestamp
        return attrs

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the respect seasonal comfort on."""
        await self._shutter.set_respect_seasonal_comfort("true")
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the respect seasonal comfort off."""
        await self._shutter.set_respect_seasonal_comfort("false")
        await self.async_force_update()
        return True

class WiserInteractsRoomClimateSwitch(WiserSwitch):
    """Shutter Respect Summer Comfort Class."""

    def __init__(
        self,
        data,
        device_id,
        name,
        is_threshold: bool = False,
        ancillary_sensor_id: int = 0,
        ancillary_sensor_type: str | None = None,
    ) -> None:
        """Initialize the sensor."""
        self._name = name
        self._device_id = device_id
        self._is_threshold = is_threshold
        self._ancillary_sensor_id = ancillary_sensor_id
        self._ancillary_sensor_type = ancillary_sensor_type
        super().__init__(data, name, "", "interactsroomclimate", "mdi:sofa")
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return unique Id."""
        uid = get_unique_id(
            self._data, self._device.product_type, self.name, self._device_id
        )
        return (
            f"{uid}_{self._ancillary_sensor_id}" if self._ancillary_sensor_id else uid
        )

    @property
    def is_on(self) -> bool:
        """Return the state of the entity."""
        if self._is_threshold:
            for th_sensor in self._data.wiserhub.devices.get_by_id(
                self._device_id
            ).threshold_sensors:
                if th_sensor.id == self._ancillary_sensor_id:
                    return th_sensor.interacts_with_room_climate
        else:
            return self._device.interacts_with_room_climate
        return False

    @property
    def name(self):
        """Return the name of the Device."""
        if self._ancillary_sensor_type:
            return f"{get_device_name(self._data, self._device_id)} {self._ancillary_sensor_type} Interacts With Room Climate"
        return f"{get_device_name(self._data, self._device_id)} Interacts With Room Climate"

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

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn the respect summer comfort on."""
        if self._is_threshold:
            for th_sensor in self._data.wiserhub.devices.get_by_id(
                self._device_id
            ).threshold_sensors:
                if th_sensor.id == self._ancillary_sensor_id:
                    await th_sensor.set_interacts_with_room_climate(True)
                    await self.async_force_update()
                    return True
        else:
            await self._device.set_interacts_with_room_climate(True)
        return False

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn the respect summer comfort off."""
        if self._is_threshold:
            for th_sensor in self._data.wiserhub.devices.get_by_id(
                self._device_id
            ).threshold_sensors:
                if th_sensor.id == self._ancillary_sensor_id:
                    await th_sensor.set_interacts_with_room_climate(False)
                    await self.async_force_update()
                    return True
        else:
            await self._device.set_interacts_with_room_climate(False)
        return False


class WiserHWClimateManualHeatSwitch(WiserSwitch):
    """Class for HW Climate Manual Heating Switch."""

    def __init__(
        self,
        data,
        device_id,
        name,
    ) -> None:
        """Initialize the sensor."""
        self._name = name
        self._device_id = device_id
        self._hotwater = data.wiserhub.hotwater
        super().__init__(data, name, "", "hwclimatemanualheat", "mdi:sofa")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._hotwater = self._data.wiserhub.hotwater
        self.async_write_ha_state()

    @property
    def is_on(self) -> bool:
        """Return the state of the entity."""
        return self._hotwater.manual_heat

    @property
    def name(self):
        """Return Name of device."""
        return get_device_name(self._data, self._hotwater.id, "Manual Heat")

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._hotwater.id, "Hot Water"),
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._hotwater.id, "hot_water"))
            },
            "manufacturer": MANUFACTURER,
            "model": HOT_WATER.title(),
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """Turn on hw climate manual heat."""
        await self._data.wiserhub.hotwater.set_manual_heat(True)
        await self.async_force_update()

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Turn off hw climate manual heat."""
        await self._data.wiserhub.hotwater.set_manual_heat(False)
        await self.async_force_update()


class WiserDeviceEnableNotificationSwitch(WiserSwitch):
    """Enable notification for a device Class."""

    def __init__(self, data, DeviceId, name) -> None:
        """Initialize the sensor."""
        self._name = name
        self._device_id = DeviceId
#        self._device_id= data.id
        super().__init__(data, name, "enable_notification", "", "mdi:check_circle")
#        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._device = self._data.wiserhub.devices.smokealarms.get_by_id(self._device_id)

        self._is_on = getattr(self._device, self._key)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.smokealarms.get_by_id(self._device_id)
#        self._is_on = True if self._device.enable_notification == "true" else False
        self._is_on = getattr(self._device, "enable_notification")
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._device_id)} Enable Notification"

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
#            self._data, self._device_id.product_type, self.name, self._device_id
            self._data,self._device.product_type , self.name, self._device_id

        )

    @property
    def icon(self):
        """Return the name of the Device."""
        return "mdi:check-circle"

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

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """enable notification."""
        _LOGGER.warning(f"**************************LGO Debug Enable Notification {self._device.device_type_id} fn {getattr(self._device, "set_" + self._key)} ********************************** "
                )

        await self._device.set_enable_notification("true")
        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Disable notification."""
        _LOGGER.warning(f"**************************LGO Debug Disable Notification {self._device.device_type_id} fn {getattr(self._device, "set_" + self._key)} ********************************** "
                )
        await self._device.set_enable_notification("false")
        await self.async_force_update()
        return True

    @property
    def extra_state_attributes(self):
        """Return the device state attributes for the attribute card."""
        attrs = {}
        attrs["name"] = self._device.name
        attrs["device_id"] = self._device.id
        attrs["id"] = self._device.device_type_id
        attrs["notification"] = self._device.enable_notification
        return attrs


class WiserEquipmentEnableNotificationSwitch(WiserSwitch):
    """Plug SwitchEntity Class."""

    def __init__(self, data, name, key, icon, device_id) -> None:
        """Initialize the sensor."""
        self._name = name
        self._device_id = device_id
        self._key = key
        self._data = data
        super().__init__(data, name, key, "equip-switch", icon)
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        if (self._name.replace(" ", "_").lower()== "under_power_notification"):     
            self._is_on = self._device.equipment.under_power_notification

        if (self._name.replace(" ", "_").lower()== "over_power_notification"):     
            self._is_on = self._device.equipment.over_power_notification

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
   
        if (self._name.replace(" ", "_").lower()== "under_power_notification_enabled"):  
            self._is_on = self._device.equipment.under_power_notification.enabled

        if (self._name.replace(" ", "_").lower()== "over_power_notification"):        
            self._is_on = self._device.equipment.over_power_notification

        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._device_id)} {self._name}"

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(
            self._data,self._device.product_type , self._name, self._device_id

        )
    @property
    def icon(self):
        """Return the icon of the Device."""
        return self._icon

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

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """enable notification."""
        if (self._name.replace(" ", "_").lower()== "over_power_notification"):       
            await self._device.equipment.over_power_notification.set_enabled ("true")
#            await self._device.set_enabled ("true")

        if (self._name.replace(" ", "_").lower()== "under_power_notification"):       
            await self._device.equipment.under_power_notification.set_enabled ("true")

        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Disable notification."""
        if (self._name.replace(" ", "_").lower()== "over_power_notification"):       
#            await self._device.equipment.over_power_notification.set_enabled ("false")
            await self._device.set_enabled ("false")

        if (self._name.replace(" ", "_").lower()== "under_power_notification"):       
            await self._device.equipment.over_power_notification.set_enabled ("false")

        await self.async_force_update()
        return True
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes of Power Notification."""
        attrs = {} 
        _LOGGER.debug(f"add attribute power notification {get_device_name(self._data,self._device_id,"device")}")
        if (self._name.replace(" ", "_").lower()== "over_power_notification"): 
            attrs["over_power_period_mins"] = self._device.equipment.over_power_notification.period_mins
            attrs["over_power_limit"] = self._device.equipment.over_power_notification.limit
            attrs["enabled"] = self._device.equipment.over_power_notification.enabled
            attrs["name"] = self._device.equipment.equipment_name if self._device.equipment.equipment_name != "Unknown" else self._device.equipment.equipment_family

        if (self._name.replace(" ", "_").lower()== "under_power_notification_enabled"): 
            attrs["under_power_period_mins"] = self._device.equipment.under_power_notification.period_mins
            attrs["under_power_limit"] = self._device.equipment.under_power_notification.limit
            attrs["enabled"] = self._device.equipment.under_power_notification.enabled
            attrs["name"] = self._device.equipment.equipment_name if self._device.equipment.equipment_name != "Unknown" else self._device.equipment.equipment_family
        return attrs

class WiserEquipmentEnableNotificationSwitch1(WiserSwitch):
    """Plug SwitchEntity Class."""

    def __init__(self, data, name, key, icon, device_id) -> None:
        """Initialize the sensor."""
        self._name = name
        self._device_id = device_id
        self._key = key
        self._data = data
        super().__init__(data, name, key, "equip-switch", icon)
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        if (self._name.replace(" ", "_").lower()== "under_power_notification"):     
            self._is_on = self._device.equipment.under_power_notification

        if (self._name.replace(" ", "_").lower()== "over_power_notification"):     
            self._is_on = self._device.equipment.over_power_notification

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
   
        if (self._name.replace(" ", "_").lower()== "under_power_notification_enabled"):  
            self._is_on = self._device.equipment.under_power_notification.enabled

        if (self._name.replace(" ", "_").lower()== "over_power_notification"):        
            self._is_on = self._device.equipment.over_power_notification

        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return f"{get_device_name(self._data, self._device_id)} {self._name}"

    @property
    def unique_id(self):
        """Return unique Id."""
        _LOGGER.debug(
            f"LGO Debug UNIQUE ID {get_unique_id(
            self._data,self._device.product_type , self._name,self._device_id)} over power on") # {self._equipment.over_power_notification.enabled}" )
        return get_unique_id(
            self._data,self._device.product_type , self._name,'enable-notification' #, self._device_id
        )
    @property
    def icon(self):
        """Return the icon of the Device."""
        return self._icon

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

    @hub_error_handler
    async def async_turn_on(self, **kwargs):
        """enable notification."""
        _LOGGER.debug(
            f"LGO Debug {self._name.replace(" ", "_").lower()} over power on") # {self._equipment.over_power_notification.enabled}" )

        if (self._name.replace(" ", "_").lower()== "over_power_notification"):       
            _LOGGER.debug(
            f"LGO Debug {self._name.replace(" ", "_").lower()} ENABLED ON") # {self._equipment.over_power_notification.enabled}" )

            await self._device.equipment.over_power_notification.set_enabled ("true")
#            await self._device.set_enabled ("true")

        if (self._name.replace(" ", "_").lower()== "under_power_notification_enabled"):       
            _LOGGER.debug(
            f"LGO Debug {self._name.replace(" ", "_").lower()} ENABLED ON") # {self._equipment.over_power_notification.enabled}" )
            await self._device.equipment.under_power_notification.set_enabled ("true")

        await self.async_force_update()
        return True

    @hub_error_handler
    async def async_turn_off(self, **kwargs):
        """Disable notification."""
        _LOGGER.debug(
            f"LGO Debug {self._name.replace(" ", "_").lower()} over power off" )

        if (self._name.replace(" ", "_").lower()== "over_power_notification"):       
            _LOGGER.debug(
            f"LGO Debug {self._name.replace(" ", "_").lower()} ENABLED OFF") # {self._equipment.over_power_notification.enabled}" )

            await self._device.equipment.over_power_notification.set_enabled ("false")
#            await self._device.equipment.set_enabled ("false")

        if (self._name.replace(" ", "_").lower()== "under_power_notification"):       
            _LOGGER.debug(
            f"LGO Debug {self._name.replace(" ", "_").lower()} ENABLED OFF") # {self._equipment.over_power_notification.enabled}" )

            await self._device.equipment.under_power_notification.set_enabled ("false")

        await self.async_force_update()
        return True
    
    @property
    def extra_state_attributes(self):
        """Return the state attributes of Power Notification."""
        attrs = {} 
        _LOGGER.debug(f"add attribute power notification {get_device_name(self._data,self._device_id,"device")}")
        if (self._name.replace(" ", "_").lower()== "over_power_notification"): 
            attrs["over_power_period_mins"] = self._device.equipment.over_power_notification.period_mins
            attrs["over_power_limit"] = self._device.equipment.over_power_notification.limit
            attrs["enabled"] = self._device.equipment.over_power_notification.enabled
            attrs["name"] = self._device.equipment.equipment_name if self._device.equipment.equipment_name != "Unknown" else self._device.equipment.equipment_family
            attrs["uniq_id"]= self.unique_id
        if (self._name.replace(" ", "_").lower()== "under_power_notification"): 
            attrs["under_power_period_mins"] = self._device.equipment.under_power_notification.period_mins
            attrs["under_power_limit"] = self._device.equipment.under_power_notification.limit
            attrs["enabled"] = self._device.equipment.under_power_notification.enabled            
            attrs["name"] = self._device.equipment.equipment_name if self._device.equipment.equipment_name != "Unknown" else self._device.equipment.equipment_family
            attrs["uniq_id"]= self.unique_id
        return attrs


