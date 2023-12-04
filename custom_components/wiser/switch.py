"""
Switch  Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""
import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from inspect import signature
import logging
from typing import Any

from aioWiserHeatAPI.const import (
    TEXT_CLOSE,
    TEXT_NO_CHANGE,
    TEXT_OFF,
    TEXT_UNKNOWN,
)
from aioWiserHeatAPI.devices import _WiserDeviceTypeEnum as DeviceType
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom
from custom_components.wiser.schedules import WiserScheduleEntity
import voluptuous as vol

from homeassistant.components.switch import (
    SwitchEntity,
    SwitchEntityDescription,
)
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DATA, DOMAIN, MANUFACTURER, ROOM
from .helpers import (
    WiserDeviceAttribute,
    WiserHubAttribute,
    get_device_name,
    get_identifier,
    get_room_name,
    get_unique_id,
)

_LOGGER = logging.getLogger(__name__)

ATTR_PLUG_MODE = "plug_mode"
ATTR_HOTWATER_MODE = "hotwater_mode"

SET_PLUG_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_PLUG_MODE, default="Auto"): vol.Coerce(str),
    }
)


@dataclass
class WiserSwitchEntityDescription(SwitchEntityDescription):
    """A class that describes Wiser switch entities."""

    sensor_type: str | None = None
    function_key: str | None = None
    available_fn: Callable[[Any], bool] | None = None
    turn_off_fn: Callable[[Any], Awaitable[None]] | None = None
    turn_on_fn: Callable[[Any], Awaitable[None]] | None = None
    value_fn: Callable[[Any], bool] | None = None
    icon_fn: Callable[[Any], str] | None = None
    extra_state_attributes: dict[
        str, Callable[[Any], float | str]
    ] | None = None


SYSTEM_SWITCHES: tuple[WiserSwitchEntityDescription, ...] = (
    WiserSwitchEntityDescription(
        key="away_mode",
        name="Away Mode",
        sensor_type="device",
        function_key="system",
        icon="mdi:beach",
        value_fn=lambda x: x.away_mode_enabled,
        turn_off_fn=lambda x: x.set_away_mode_enabled(False),
        turn_on_fn=lambda x: x.set_away_mode_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="valve_protection",
        name="Valve Protection",
        sensor_type="device",
        function_key="system",
        icon="mdi:snowflake-alert",
        value_fn=lambda x: x.valve_protection_enabled,
        turn_off_fn=lambda x: x.set_valve_protection_enabled(False),
        turn_on_fn=lambda x: x.set_valve_protection_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="eco_mode",
        name="Eco Mode",
        sensor_type="device",
        function_key="system",
        icon="mdi:leaf",
        value_fn=lambda x: x.eco_mode_enabled,
        turn_off_fn=lambda x: x.set_eco_mode_enabled(False),
        turn_on_fn=lambda x: x.set_eco_mode_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="away_mode_affects_hotwater",
        name="Away Mode Affects Hot Water",
        sensor_type="device",
        function_key="system",
        icon="mdi:water",
        value_fn=lambda x: x.away_mode_affects_hotwater,
        turn_off_fn=lambda x: x.set_away_mode_affects_hotwater(False),
        turn_on_fn=lambda x: x.set_away_mode_affects_hotwater(True),
    ),
    WiserSwitchEntityDescription(
        key="comfort_mode_enabled",
        name="Comfort Mode",
        sensor_type="device",
        function_key="system",
        icon="mdi:sofa",
        value_fn=lambda x: x.comfort_mode_enabled,
        turn_off_fn=lambda x: x.set_comfort_mode_enabled(False),
        turn_on_fn=lambda x: x.set_comfort_mode_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="automatic_daylight_saving_enabled",
        name="Daylight Saving",
        sensor_type="device",
        function_key="system",
        icon="mdi:leaf",
        value_fn=lambda x: x.automatic_daylight_saving_enabled,
        turn_off_fn=lambda x: x.set_automatic_daylight_saving_enabled(False),
        turn_on_fn=lambda x: x.set_automatic_daylight_saving_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="window_detection_active",
        name="Window Detection",
        sensor_type="device",
        function_key="system",
        icon="mdi:leaf",
        value_fn=lambda x: x.window_detection_active,
        turn_off_fn=lambda x: x.set_window_detection_active(False),
        turn_on_fn=lambda x: x.set_window_detection_active(True),
    ),
)

ALL_DEVICE_SWITCHES: tuple[WiserSwitchEntityDescription, ...] = (
    WiserSwitchEntityDescription(
        key="window_detection_active",
        name="Window Detection",
        sensor_type="room",
        icon="mdi:window-closed",
        value_fn=lambda x: x.window_detection_active,
        turn_off_fn=lambda x: x.set_window_detection_active(False),
        turn_on_fn=lambda x: x.set_window_detection_active(True),
    ),
    WiserSwitchEntityDescription(
        key="device_lock_enabled",
        name="Device Lock",
        sensor_type="device",
        icon="mdi:lock",
        value_fn=lambda x: x.device_lock_enabled,
        turn_off_fn=lambda x: x.set_device_lock_enabled(False),
        turn_on_fn=lambda x: x.set_device_lock_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="identify",
        name="Identify",
        sensor_type="device",
        icon="mdi:alarm-light",
        value_fn=lambda x: x.identify,
        turn_off_fn=lambda x: x.set_identify(False),
        turn_on_fn=lambda x: x.set_identify(True),
    ),
)

LIGHT_SWITCHES: tuple[WiserSwitchEntityDescription, ...] = (
    WiserSwitchEntityDescription(
        key="light_away_action",
        name="Away Mode Turns Off",
        sensor_type="device",
        icon="mdi:lightbulb-off-outline",
        value_fn=lambda x: x.away_mode_action == TEXT_OFF,
        turn_off_fn=lambda x: x.set_away_mode_action(TEXT_NO_CHANGE),
        turn_on_fn=lambda x: x.set_away_mode_action(TEXT_OFF),
    ),
)

SHUTTER_SWITCHES: tuple[WiserSwitchEntityDescription, ...] = (
    WiserSwitchEntityDescription(
        key="shutter_away_action",
        name="Away Mode Closes",
        sensor_type="device",
        icon="mdi:window-shutter",
        value_fn=lambda x: x.away_mode_action == TEXT_CLOSE,
        turn_off_fn=lambda x: x.set_away_mode_action(TEXT_NO_CHANGE),
        turn_on_fn=lambda x: x.set_away_mode_action(TEXT_CLOSE),
    ),
)

SMARTPLUG_SWITCHES: tuple[WiserSwitchEntityDescription, ...] = (
    WiserSwitchEntityDescription(
        key="smartplug_away_action",
        name="Away Mode Turns Off",
        sensor_type="device",
        icon="mdi:power-socket-uk",
        value_fn=lambda x: x.away_mode_action == TEXT_OFF,
        turn_off_fn=lambda x: x.set_away_mode_action(TEXT_NO_CHANGE),
        turn_on_fn=lambda x: x.set_away_mode_action(TEXT_OFF),
    ),
)

ROOM_SWITCHES: tuple[WiserSwitchEntityDescription, ...] = (
    WiserSwitchEntityDescription(
        key="window_detection",
        name="Window Detection Active",
        sensor_type="room",
        icon="mdi:window-closed",
        value_fn=lambda x: x.window_detection_active,
        turn_off_fn=lambda x: x.set_window_detection_active(False),
        turn_on_fn=lambda x: x.set_window_detection_active(True),
    ),
    WiserSwitchEntityDescription(
        key="passive_mode",
        name="Passive Mode",
        sensor_type="room",
        icon="mdi:thermostat-box",
        available_fn=lambda x: x.number_of_smartvalves > 0,
        value_fn=lambda x: x.passive_mode_enabled,
        turn_off_fn=lambda x: x.set_passive_mode(False),
        turn_on_fn=lambda x: x.set_passive_mode(True),
    ),
)


SYSTEM_SWITCH_ENTITIES = {"HUB": SYSTEM_SWITCHES}

ROOM_SWITCH_ENTITIES = {"ROOMS": ROOM_SWITCHES}

DEVICE_SWITCH_ENTITIES = {
    "ALL_DEVICES": ALL_DEVICE_SWITCHES,
    DeviceType.OnOffLight: LIGHT_SWITCHES,
    DeviceType.DimmableLight: LIGHT_SWITCHES,
    DeviceType.Shutter: SHUTTER_SWITCHES,
}

WISER_SWITCHES = []


def _attr_exist(
    data: dict, device: _WiserDevice, sensor_desc: WiserSwitchEntityDescription
) -> bool:
    """Check if an attribute exists for device."""
    try:
        no_of_params = len(signature(sensor_desc.value_fn).parameters)
        if no_of_params == 2:
            r = sensor_desc.value_fn(data, device)
        else:
            r = sensor_desc.value_fn(device)
        if r is not None and r != TEXT_UNKNOWN:
            return True
        return False
    except AttributeError:
        return False


async def async_setup_entry(
    hass: HomeAssistant, config_entry, async_add_entities
):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    wiser_system_switches = [
        WiserSwitch2(
            data, switch_desc, getattr(data.wiserhub, switch_desc.function_key)
        )
        for device_type, switch_descs in SYSTEM_SWITCH_ENTITIES.items()
        for switch_desc in switch_descs
        if _attr_exist(
            data.wiserhub,
            getattr(data.wiserhub, switch_desc.function_key),
            switch_desc,
        )
    ]

    wiser_device_switches = [
        WiserSwitch2(data, switch_desc, device)
        for device_type, switch_descs in DEVICE_SWITCH_ENTITIES.items()
        for switch_desc in switch_descs
        for device in data.wiserhub.devices.all
        if _attr_exist(data.wiserhub, device, switch_desc)
        and (
            device_type == "ALL_DEVICES"
            or device.product_type == device_type.name
        )
    ]

    wiser_room_switches = [
        WiserSwitch2(data, switch_desc, room)
        for device_type, switch_descs in ROOM_SWITCH_ENTITIES.items()
        for switch_desc in switch_descs
        for room in data.wiserhub.rooms.all
        if _attr_exist(data.wiserhub, room, switch_desc)
        and (
            switch_desc.available_fn(room)
            if switch_desc.available_fn
            else True
        )
        and len(room.devices) > 0
    ]

    # Add Defined Switches
    wiser_switches = []
    for switch in WISER_SWITCHES:
        if switch["type"] == "room":
            for room in [
                room
                for room in data.wiserhub.rooms.all
                if len(room.devices) > 0
            ]:
                wiser_switches.append(
                    WiserRoomSwitch(
                        data,
                        switch["name"],
                        switch["key"],
                        switch["icon"],
                        room.id,
                    )
                )
        elif switch["type"] == "system":
            wiser_switches.append(
                WiserSystemSwitch(
                    data, switch["name"], switch["key"], switch["icon"]
                )
            )

        elif switch["type"] == "device":
            for device in [
                device
                for device in data.wiserhub.devices.all
                if hasattr(device, switch["key"])
            ]:
                wiser_switches.append(
                    WiserDeviceSwitch(
                        data,
                        switch["name"],
                        switch["key"],
                        switch["icon"],
                        device.id,
                    )
                )

    # Add Lights (if any)
    # for light in data.wiserhub.devices.lights.all:
    #    wiser_switches.extend(
    #        [WiserLightAwayActionSwitch(data, light.id, f"Wiser {light.name}")]
    #    )

    # Add Shutters (if any)
    # for shutter in data.wiserhub.devices.shutters.all:
    #    wiser_switches.extend(
    #        [
    #            WiserShutterAwayActionSwitch(

    #                data, shutter.id, f"Wiser {shutter.name}"
    #            )
    #        ]
    #    )

    # Add SmartPlugs (if any)
    # for plug in data.wiserhub.devices.smartplugs.all:
    #    wiser_switches.extend(
    #        [
    #            WiserSmartPlugSwitch(data, plug.id, f"Wiser {plug.name}"),
    #            WiserSmartPlugAwayActionSwitch(
    #                data, plug.id, f"Wiser {plug.name}"
    #            ),
    #        ]
    #    )

    # Add Room passive mode switches
    # if data.enable_automations_passive_mode:
    #    for room in data.wiserhub.rooms.all:
    #        if room.number_of_smartvalves > 0:
    #            wiser_switches.append(
    #                WiserPassiveModeSwitch(
    #                    hass, data, room.id, f"Wiser Passive Mode {room.name}"
    #                )
    #            )

    wiser_switches.extend(wiser_system_switches)
    wiser_switches.extend(wiser_device_switches)
    wiser_switches.extend(wiser_room_switches)

    async_add_entities(wiser_switches)

    return True


class WiserSwitch2(CoordinatorEntity, SwitchEntity):
    """Switch to set the status of a Wiser boolean attribute"""

    entity_description: WiserSwitchEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserSwitchEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._data = coordinator
        self._device = device
        self.entity_description = description
        self._attr_unique_id = get_unique_id(
            self._data,
            "sensor",
            description.key,
            (
                device.id
                if isinstance(self._device, _WiserDevice)
                or isinstance(self._device, _WiserRoom)
                else 0
            ),
        )
        self._attr_name = description.name

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            await asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if isinstance(self._device, _WiserDevice):
            self._device = self._data.wiserhub.devices.get_by_id(
                self._device.id
            )
        elif isinstance(self._device, _WiserRoom):
            self._device = self._data.wiserhub.rooms.get_by_id(self._device.id)
        elif self.entity_description.function_key:
            self._device = getattr(
                self._data.wiserhub, self.entity_description.function_key
            )
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(
                self._data,
                self._device.id
                if isinstance(self._device, _WiserDevice)
                or isinstance(self._device, _WiserRoom)
                else 0,
                self.entity_description.sensor_type,
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data,
                        self._device.id
                        if isinstance(self._device, _WiserDevice)
                        or isinstance(self._device, _WiserRoom)
                        else 0,
                        self.entity_description.sensor_type,
                    ),
                )
            },
            "manufacturer": MANUFACTURER,
            "model": ROOM
            if self.entity_description.sensor_type.lower() == ROOM.lower()
            else self._device.product_type
            if isinstance(self._device, _WiserDevice)
            else self._data.wiserhub.system.product_type,
            "sw_version": self._device.firmware_version
            if isinstance(self._device, _WiserDevice)
            else self._data.wiserhub.system.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def is_on(self):
        """Return the state of the switch."""
        ret_val = self._get_switch_state()
        if ret_val is None:
            return False
        if isinstance(ret_val, bool):
            return ret_val
        return False

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        if self.entity_description.turn_off_fn is None:
            raise NotImplementedError()
        if self.is_on:
            await self.entity_description.turn_off_fn(self._device)
            await self.async_force_update()

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        if self.entity_description.turn_on_fn is None:
            raise NotImplementedError()
        if not self.is_on:
            await self.entity_description.turn_on_fn(self._device)
            await self.async_force_update()

    def _get_switch_state(self):
        """Get current switch state"""
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(self._device)

        return None


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

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        raise NotImplementedError

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

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""

        fn = getattr(self._data.wiserhub.system, "set_" + self._key)
        await fn(True)
        await self.async_force_update()
        return True

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

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        fn = getattr(self._room, "set_" + self._key)
        await fn(True)
        await self.async_force_update()
        return True

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

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        fn = getattr(self._device, "set_" + self._key)
        await fn(True)
        await self.async_force_update()
        return True

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
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._device_id))
            },
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
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._device_id))
            },
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
        if (
            self._data.wiserhub.rooms.get_by_id(self._device.room_id)
            is not None
        ):
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
            attrs["next_schedule_change"] = str(
                self._device.schedule.next.time
            )
            attrs["next_schedule_datetime"] = str(
                self._device.schedule.next.datetime
            )
            attrs["next_schedule_state"] = self._device.schedule.next.setting
        return attrs

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._device.turn_on()
        await self.async_force_update(2)
        return True

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
        self._smartplug = self._data.wiserhub.devices.get_by_id(
            self._smart_plug_id
        )
        self._is_on = (
            True if self._smartplug.away_mode_action == "Off" else False
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._smartplug = self._data.wiserhub.devices.get_by_id(
            self._smart_plug_id
        )
        self._is_on = (
            True if self._smartplug.away_mode_action == "Off" else False
        )
        self.async_write_ha_state()

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
            self._smart_plug_id,
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._smart_plug_id),
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._smart_plug_id))
            },
            "manufacturer": MANUFACTURER,
            "model": self._smartplug.product_type,
            "sw_version": self._smartplug.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._smartplug.set_away_mode_action("Off")
        await self.async_force_update()
        return True

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
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._light_id))
            },
            "manufacturer": MANUFACTURER,
            "model": self._light.product_type,
            "sw_version": self._light.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._light.set_away_mode_action("Off")
        await self.async_force_update()
        return True

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
        self._is_on = (
            True if self._shutter.away_mode_action == "Close" else False
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Async Update to HA."""
        super()._handle_coordinator_update()
        self._shutter = self._data.wiserhub.devices.get_by_id(self._shutter_id)
        self._is_on = (
            True if self._shutter.away_mode_action == "Close" else False
        )
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the Device."""
        return (
            f"{get_device_name(self._data, self._shutter_id)} Away Mode Closes"
        )

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
            "identifiers": {
                (DOMAIN, get_identifier(self._data, self._shutter_id))
            },
            "manufacturer": MANUFACTURER,
            "model": self._shutter.product_type,
            "sw_version": self._shutter.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._shutter.set_away_mode_action("Close")
        await self.async_force_update()
        return True

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
        return f"""
            {get_device_name(self._data, self._room_id, 'room')} Passive Mode
        """

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

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        await self._data.wiserhub.rooms.get_by_id(
            self._room_id
        ).set_passive_mode(True)
        await self.async_force_update()
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        await room.set_passive_mode(False)
        await room.cancel_overrides()
        await self.async_force_update()
        return True
