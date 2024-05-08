"""Switch  Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
import logging
from typing import Any

from aioWiserHeatAPI.const import TEXT_CLOSE, TEXT_NO_CHANGE, TEXT_OFF
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom
from aioWiserHeatAPI.system import _WiserSystem
import voluptuous as vol

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN
from .entity import (
    WiserBaseEntity,
    WiserBaseEntityDescription,
    WiserDeviceAttribute,
    WiserHubAttribute,
)
from .helpers import get_entities

_LOGGER = logging.getLogger(__name__)

ATTR_PLUG_MODE = "plug_mode"
ATTR_HOTWATER_MODE = "hotwater_mode"
ENTITY_TYPE = "switch"

SET_PLUG_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_PLUG_MODE, default="Auto"): vol.Coerce(str),
    }
)


@dataclass(frozen=True, kw_only=True)
class WiserSwitchEntityDescription(SwitchEntityDescription, WiserBaseEntityDescription):
    """A class that describes Wiser switch entities."""

    turn_off_fn: Callable[[Any], Awaitable[None]] | None = None
    turn_on_fn: Callable[[Any], Awaitable[None]] | None = None


WISER_SWITCHES: tuple[WiserSwitchEntityDescription, ...] = (
    WiserSwitchEntityDescription(
        key="away_mode_enabled",
        name="Away Mode",
        device="system",
        icon="mdi:beach",
        value_fn=lambda d: d.away_mode_enabled,
        turn_off_fn=lambda d: d.set_away_mode_enabled(False),
        turn_on_fn=lambda d: d.set_away_mode_enabled(True),
        extra_state_attributes=[
            WiserDeviceAttribute("away_mode_target_temperature"),
        ],
    ),
    WiserSwitchEntityDescription(
        key="valve_protection_enabled",
        name="Valve Protection",
        device="system",
        icon="mdi:snowflake-alert",
        value_fn=lambda x: x.valve_protection_enabled,
        turn_off_fn=lambda x: x.set_valve_protection_enabled(False),
        turn_on_fn=lambda x: x.set_valve_protection_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="eco_mode_enabled",
        name="Eco Mode",
        device="system",
        icon="mdi:leaf",
        value_fn=lambda x: x.eco_mode_enabled,
        turn_off_fn=lambda x: x.set_eco_mode_enabled(False),
        turn_on_fn=lambda x: x.set_eco_mode_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="away_mode_affects_hotwater",
        name="Away Mode Affects Hot Water",
        device="system",
        icon="mdi:water",
        supported=lambda device, hub: hub.hotwater is not None,
        value_fn=lambda x: x.away_mode_affects_hotwater,
        turn_off_fn=lambda x: x.set_away_mode_affects_hotwater(False),
        turn_on_fn=lambda x: x.set_away_mode_affects_hotwater(True),
    ),
    WiserSwitchEntityDescription(
        key="comfort_mode_enabled",
        name="Comfort Mode",
        device="system",
        icon="mdi:sofa",
        value_fn=lambda x: x.comfort_mode_enabled,
        turn_off_fn=lambda x: x.set_comfort_mode_enabled(False),
        turn_on_fn=lambda x: x.set_comfort_mode_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="automatic_daylight_saving_enabled",
        name="Daylight Saving",
        device="system",
        icon="mdi:leaf",
        value_fn=lambda x: x.automatic_daylight_saving_enabled,
        turn_off_fn=lambda x: x.set_automatic_daylight_saving_enabled(False),
        turn_on_fn=lambda x: x.set_automatic_daylight_saving_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="device_lock_enabled",
        name="Device Lock",
        device_collection="devices",
        icon="mdi:lock",
        legacy_type="device",
        value_fn=lambda x: x.device_lock_enabled,
        turn_off_fn=lambda x: x.set_device_lock_enabled(False),
        turn_on_fn=lambda x: x.set_device_lock_enabled(True),
    ),
    WiserSwitchEntityDescription(
        key="identify",
        name="Identify",
        device_collection="devices",
        icon="mdi:alarm-light",
        legacy_type="device",
        value_fn=lambda x: x.identify,
        turn_off_fn=lambda x: x.set_identify(False),
        turn_on_fn=lambda x: x.set_identify(True),
    ),
    WiserSwitchEntityDescription(
        key="light_away_action",
        name="Away Mode Turns Off",
        device_collection="devices.lights",
        icon="mdi:lightbulb-off-outline",
        legacy_type="device-switch",
        value_fn=lambda x: x.away_mode_action == TEXT_OFF,
        turn_off_fn=lambda x: x.set_away_mode_action(TEXT_NO_CHANGE),
        turn_on_fn=lambda x: x.set_away_mode_action(TEXT_OFF),
    ),
    WiserSwitchEntityDescription(
        key="shutter_away_action",
        name="Away Mode Closes",
        device_collection="devices.shutters",
        icon="mdi:window-shutter",
        legacy_type="device-switch",
        value_fn=lambda x: x.away_mode_action == TEXT_CLOSE,
        turn_off_fn=lambda x: x.set_away_mode_action(TEXT_NO_CHANGE),
        turn_on_fn=lambda x: x.set_away_mode_action(TEXT_CLOSE),
    ),
    WiserSwitchEntityDescription(
        key="smartplug_away_action",
        name="Away Mode Turns Off",
        device_collection="devices.smartplugs",
        icon="mdi:power-socket-uk",
        legacy_type="device-switch",
        value_fn=lambda x: x.away_mode_action == TEXT_OFF,
        turn_off_fn=lambda x: x.set_away_mode_action(TEXT_NO_CHANGE),
        turn_on_fn=lambda x: x.set_away_mode_action(TEXT_OFF),
    ),
    WiserSwitchEntityDescription(
        key="smartplug_switch",
        name="Switch",
        device_collection="devices.smartplugs",
        icon="mdi:power-socket-uk",
        legacy_type="device-switch",
        value_fn=lambda x: x.is_on,
        delay=2,
        turn_off_fn=lambda x: x.turn_off(),
        turn_on_fn=lambda x: x.turn_on(),
        extra_state_attributes=[
            WiserDeviceAttribute("control_source"),
            WiserDeviceAttribute("manual_state"),
            WiserDeviceAttribute("mode"),
            WiserDeviceAttribute("name"),
            WiserDeviceAttribute("output_state", lambda x: "On" if x.is_on else "Off"),
            WiserDeviceAttribute(
                "room",
                lambda d, h: h.rooms.get_by_id(d.room_id).name
                if d.room_id != 0
                else "Unassigned",
            ),
            WiserDeviceAttribute("away_mode_action"),
            WiserDeviceAttribute("scheduled_state"),
            WiserDeviceAttribute("schedule_id"),
            WiserDeviceAttribute("schedule_name", "schedule.name"),
            WiserDeviceAttribute("next_day_change", "schedule.next.day"),
            WiserDeviceAttribute("next_schedule_change", "schedule.next.time"),
            WiserDeviceAttribute("next_schedule_datetime", "schedule.next.datetime"),
            WiserDeviceAttribute("next_schedule_state", "schedule.next.setting"),
        ],
    ),
    WiserSwitchEntityDescription(
        key="window_detection",
        name="Window Detection",
        device_collection="rooms",
        icon="mdi:window-closed",
        legacy_type="room",
        value_fn=lambda x: x.window_detection_active,
        turn_off_fn=lambda x: x.set_window_detection_active(False),
        turn_on_fn=lambda x: x.set_window_detection_active(True),
    ),
    WiserSwitchEntityDescription(
        key="passive_mode",
        name="Passive Mode",
        device_collection="rooms",
        icon="mdi:thermostat-box",
        legacy_type="room",
        supported=lambda x, d: x.number_of_smartvalves > 0,
        value_fn=lambda x: x.passive_mode_enabled,
        turn_off_fn=lambda x: x.set_passive_mode(False),
        turn_on_fn=lambda x: x.set_passive_mode(True),
    ),
    WiserSwitchEntityDescription(
        key="hot_water",
        name="Hot Water",
        device="hotwater",
        icon_fn=lambda x: "mdi:fire" if x.current_state == "On" else "mdi:fire-off",
        supported=lambda dev, hub: hub.hotwater is not None,
        value_fn=lambda x: x.current_state == "On",
        turn_off_fn=lambda x: x.override_state("Off"),
        turn_on_fn=lambda x: x.override_state("On"),
    ),
    WiserSwitchEntityDescription(
        key="summer_comfort",
        name="Summer Comfort",
        device_collection="devices.shutters",
        supported=lambda dev, hub: dev.respect_summer_comfort,
        value_fn=lambda x: x.respect_summer_comfort,
        turn_off_fn=lambda x: x.set_respect_summer_comfort(False),
        turn_on_fn=lambda x: x.set_respect_summer_comfort(True),
        extra_state_attributes=[
            WiserDeviceAttribute("summer_comfort_lift"),
            WiserDeviceAttribute("summer_comfort_tilt"),
        ],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    entities = get_entities(data, WISER_SWITCHES, WiserSwitch)
    async_add_entities(entities)

    return True


class WiserSwitch(WiserBaseEntity, SwitchEntity):
    """Switch to set the status of a Wiser boolean attribute."""

    entity_description: WiserSwitchEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserSwitchEntityDescription,
        device: _WiserDevice | _WiserRoom | _WiserSystem | None = None,
    ) -> None:
        """Initialise class instance for Wiser switch."""
        super().__init__(coordinator, description, device, "switch")

    @property
    def is_on(self):
        """Return the state of the switch."""
        return bool(self._get_switch_state())

    async def async_turn_off(self, **kwargs):
        """Turn the entity off."""
        if self.entity_description.turn_off_fn is None:
            raise NotImplementedError
        if self.is_on:
            await self.entity_description.turn_off_fn(self._device)
            await self.async_force_update(delay=self.entity_description.delay)

    async def async_turn_on(self, **kwargs):
        """Turn the entity on."""
        if self.entity_description.turn_on_fn is None:
            raise NotImplementedError
        if not self.is_on:
            await self.entity_description.turn_on_fn(self._device)
            await self.async_force_update(delay=self.entity_description.delay)

    def _get_switch_state(self):
        """Get current switch state."""
        if self.entity_description.value_fn is not None:
            return self.entity_description.value_fn(self._device)
        return None
