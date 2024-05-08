"""Binary Sensor Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN
from .entity import WiserBaseEntity, WiserBaseEntityDescription, WiserDeviceAttribute
from .helpers import get_entities

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class WiserBinarySensorEntityDescription(
    BinarySensorEntityDescription, WiserBaseEntityDescription
):
    """A class that describes Wiser binary sensor entities."""

    unit_fn: Callable[[Any], str] | None = None


WISER_BINARY_SENSORS: tuple[WiserBinarySensorEntityDescription, ...] = (
    # System sensors
    WiserBinarySensorEntityDescription(
        key="heating_channel_status",
        name_fn=lambda x: f"Heating Channel {x.id}",
        device_collection="heating_channels",
        icon_fn=lambda x: "mdi:radiator-disabled"
        if x.heating_relay_status == "Off"
        else "mdi:radiator",
        value_fn=lambda x: x.heating_relay_status == "On",
        extra_state_attributes=[
            WiserDeviceAttribute("percentage_demand"),
            WiserDeviceAttribute("room_ids"),
            WiserDeviceAttribute("is_smartvalve_preventing_demand"),
        ],
    ),
    # Room Sensors
    WiserBinarySensorEntityDescription(
        key="room_is_heating",
        name="Heating",
        device_collection="rooms",
        icon="mdi:fire",
        value_fn=lambda x: x.is_heating,
    ),
    WiserBinarySensorEntityDescription(
        key="window_state",
        name="Window State",
        device_collection="rooms",
        device_class=BinarySensorDeviceClass.WINDOW,
        value_fn=lambda x: x.is_heating,
    ),
    # Hot Water
    WiserBinarySensorEntityDescription(
        key="hot_water_state",
        name="Hot Water",
        device="hotwater",
        supported=lambda device, hub: hub.hotwater is not None,
        icon_fn=lambda x: "mdi:fire" if x.current_state == "On" else "mdi:fire-off",
        value_fn=lambda x: x.current_state == "On",
        extra_state_attributes=[
            WiserDeviceAttribute("boost_end", "boost_end_time"),
            WiserDeviceAttribute(
                "boost_time_remaining", lambda x: int(x.boost_time_remaining / 60)
            ),
            WiserDeviceAttribute("away_mode_supressed"),
            WiserDeviceAttribute("is_away_mode"),
            WiserDeviceAttribute("is_boosted"),
            WiserDeviceAttribute("is_override"),
            WiserDeviceAttribute("schedule_id", "schedule.id"),
            WiserDeviceAttribute("schedule_name", "schedule.name"),
            WiserDeviceAttribute("next_day_change", "schedule.next.day"),
            WiserDeviceAttribute("next_schedule_change", "schedule.next.time"),
            WiserDeviceAttribute("next_schedule_datetime", "schedule.next.datetime"),
            WiserDeviceAttribute("next_schedule_state", "schedule.next.setting"),
        ],
    ),
    # Smoke Alarms
    WiserBinarySensorEntityDescription(
        key="smoke_alarm",
        name="Smoke Alarm",
        device_collection="devices.smokealarms",
        device_class=BinarySensorDeviceClass.SMOKE,
        value_fn=lambda x: x.smoke_alarm,
    ),
    WiserBinarySensorEntityDescription(
        key="heat_alarm",
        name="Heat Alarm",
        device_collection="devices.smokealarms",
        device_class=BinarySensorDeviceClass.HEAT,
        value_fn=lambda x: x.heat_alarm,
    ),
    WiserBinarySensorEntityDescription(
        key="tamper_alarm",
        name="Tamper Alarm",
        device_collection="devices.smokealarms",
        device_class=BinarySensorDeviceClass.TAMPER,
        value_fn=lambda x: x.tamper_alarm,
    ),
    WiserBinarySensorEntityDescription(
        key="fault_warning",
        name="Fault",
        device_collection="devices.smokealarms",
        device_class=BinarySensorDeviceClass.PROBLEM,
        value_fn=lambda x: x.fault_warning,
    ),
    WiserBinarySensorEntityDescription(
        key="remote_alarm",
        name="Remote Alarm",
        device_collection="devices.smokealarms",
        value_fn=lambda x: x.remote_alarm,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    entities = get_entities(data, WISER_BINARY_SENSORS, WiserBinarySensor)
    async_add_entities(entities)

    return True


class WiserBinarySensor(WiserBaseEntity, BinarySensorEntity):
    """Class to monitor sensors of a Wiser device."""

    entity_description: WiserBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserBinarySensorEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        """Init wiser sensor."""
        super().__init__(coordinator, description, device, "sensor")

    @property
    def is_on(self) -> float | int | str | None:
        """Return the state of the sensor."""
        return self.entity_description.value_fn(self._device)
