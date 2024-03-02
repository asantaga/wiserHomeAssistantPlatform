"""Binary Sensor Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from aioWiserHeatAPI.const import TEXT_UNKNOWN
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, LEGACY_NAMES
from .entity import WiserBaseEntity
from .helpers import WiserDeviceAttribute, getattrd

_LOGGER = logging.getLogger(__name__)


@dataclass
class WiserBinarySensorEntityDescription(BinarySensorEntityDescription):
    """A class that describes Wiser binary sensor entities."""

    name_fn: Callable[[Any], str] | None = None
    device: str | None = None
    device_collection: list | None = None
    available_fn: Callable[[Any], bool] | None = None
    icon_fn: Callable[[Any], str] | None = None
    unit_fn: Callable[[Any], str] | None = None
    value_fn: Callable[[Any], float | str] | None = None
    legacy_name_fn: Callable[[Any], str] | None = None
    legacy_type: str = None
    extra_state_attributes: dict[str, Callable[[Any], float | str]] | None = None


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
        extra_state_attributes={
            "percentage_demand": lambda x: x.percentage_demand,
            "room_ids": lambda x: x.room_ids,
            "is_smartvalve_preventing_demand": lambda x: x.is_smart_valve_preventing_demand,
        },
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
        icon_fn=lambda x: "mdi:fire" if x.current_state == "On" else "mdi:fire-off",
        value_fn=lambda x: x.current_state == "On",
        extra_state_attributes={
            "boost_end": WiserDeviceAttribute("boost_end_time"),
            "boost_time_remaining": lambda x: int(x.boost_time_remaining / 60),
            "away_mode_supressed": WiserDeviceAttribute("away_mode_suppressed"),
            "is_away_mode": WiserDeviceAttribute("is_away_mode"),
            "is_boosted": WiserDeviceAttribute("is_boosted"),
            "is_override": WiserDeviceAttribute("hw.is_override"),
            "schedule_id": WiserDeviceAttribute("schedule.id"),
            "schedule_name": WiserDeviceAttribute("schedule.name"),
            "next_day_change": WiserDeviceAttribute("schedule.next.day"),
            "next_schedule_change": WiserDeviceAttribute("schedule.next.time"),
            "next_schedule_datetime": WiserDeviceAttribute("schedule.next.datetime"),
            "next_schedule_state": WiserDeviceAttribute("schedule.next.setting"),
        },
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


def _attr_exist(device, entity_desc: WiserBinarySensorEntityDescription) -> bool:
    """Check if an attribute exists for device."""
    try:
        r = entity_desc.value_fn(device)
        if r is not None:
            return True
        return False
    except AttributeError:
        return False


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_sensors = []

    for sensor_desc in WISER_BINARY_SENSORS:
        # get device or device collection
        if sensor_desc.device_collection and getattrd(
            data.wiserhub, sensor_desc.device_collection
        ):
            for device in getattrd(data.wiserhub, sensor_desc.device_collection).all:
                if _attr_exist(device, sensor_desc):
                    _LOGGER.info("Adding %s", device.name)
                    wiser_sensors.append(
                        WiserSensor(
                            data,
                            sensor_desc,
                            device,
                        )
                    )
        elif sensor_desc.device and getattrd(data.wiserhub, sensor_desc.device):
            device = getattrd(data.wiserhub, sensor_desc.device)
            if _attr_exist(device, sensor_desc):
                wiser_sensors.append(
                    WiserSensor(
                        data,
                        sensor_desc,
                        device,
                    )
                )

    async_add_entities(wiser_sensors)

    return True


class WiserSensor(WiserBaseEntity, BinarySensorEntity):
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
