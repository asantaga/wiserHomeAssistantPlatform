"""Sensor Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""

from collections.abc import Callable
from dataclasses import dataclass
from inspect import signature
import logging
from typing import Any

from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, MANUFACTURER, SIGNAL_STRENGTH_ICONS, VERSION
from .entity import (
    WiserAttribute,
    WiserBaseEntity,
    WiserBaseEntityDescription,
    WiserDeviceAttribute,
    WiserHubAttribute,
)
from .helpers import get_entities, get_hot_water_operation_mode

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class WiserSensorEntityDescription(SensorEntityDescription, WiserBaseEntityDescription):
    """A class that describes Wiser sensor entities."""

    unit_fn: Callable[[Any], str] | None = None


WISER_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    # System Sensors
    WiserSensorEntityDescription(
        key="signal",
        name="Signal",
        device="system",
        icon_fn=lambda x: SIGNAL_STRENGTH_ICONS[x.signal.displayed_signal_strength]
        if x.signal.displayed_signal_strength in SIGNAL_STRENGTH_ICONS
        else SIGNAL_STRENGTH_ICONS["NoSignal"],
        value_fn=lambda x: x.signal.displayed_signal_strength,
        extra_state_attributes=[
            WiserAttribute("vendor", MANUFACTURER),
            WiserDeviceAttribute("product_type"),
            WiserDeviceAttribute("model"),
            WiserDeviceAttribute("firmware", "firmware_version"),
            WiserDeviceAttribute("node_id"),
            WiserDeviceAttribute("zigbee_channel", "zigbee.network_channel"),
            WiserDeviceAttribute("wifi_strength", "signal.controller_reception_rssi"),
            WiserDeviceAttribute(
                "wifi_strength_percent", "signal.controller_signal_strength"
            ),
            WiserDeviceAttribute("wifi_SSID", "network.ssid"),
            WiserDeviceAttribute("wifi_IP", "network.ip_address"),
            WiserHubAttribute("api_version", "version"),
            WiserAttribute("integration_version", VERSION),
            WiserHubAttribute("uptime", "status.uptime"),
            WiserHubAttribute("last_reset_reason", "status.last_reset_reason"),
        ],
    ),
    WiserSensorEntityDescription(
        key="cloud",
        name="Cloud",
        device="system",
        icon_fn=lambda x: "mdi:cloud-check"
        if x.cloud.connection_status == "Connected"
        else "mdi:cloud-alert",
        value_fn=lambda x: x.cloud.connection_status,
    ),
    WiserSensorEntityDescription(
        key="heating_operation_mode",
        name="Heating Operation Mode",
        device="system",
        value_fn=lambda x: "Away Mode" if x.is_away_mode_enabled else "Normal",
    ),
    # Heating Channel Sensors
    WiserSensorEntityDescription(
        key="heating_channel_state",
        name_fn=lambda d, x: "Heating"
        if d.heating_channels.count == 1
        else f"Heating Channel {x.id}",
        legacy_name_fn=lambda d, x: "Heating"
        if d.heating_channels.count == 1
        else f"Heating Channel {x.id}",
        legacy_type="system",
        device_collection="heating_channels",
        icon_fn=lambda x: "mdi:radiator-disabled"
        if x.heating_relay_status == "Off"
        else "mdi:radiator",
        value_fn=lambda x: x.heating_relay_status,
        extra_state_attributes=[
            WiserDeviceAttribute("percentage_demand", "percentage_demand"),
            WiserDeviceAttribute("room_ids", "room_ids"),
            WiserDeviceAttribute(
                "is_smartvalve_preventing_demand", "is_smart_valve_preventing_demand"
            ),
        ],
    ),
    WiserSensorEntityDescription(
        key="heating_channel_demand",
        name_fn=lambda x: f"Heating Demand Channel {x.id}",
        legacy_name_fn=lambda x: f"LTS Heating Demand Channel {x.id}",
        legacy_type="system",
        device_collection="heating_channels",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        icon="mdi:radiator",
        value_fn=lambda x: x.percentage_demand,
    ),
    # Hot Water Sensors
    WiserSensorEntityDescription(
        key="hot_water_operation_mode",
        name="Hot Water Operation Mode",
        device="hotwater",
        icon="mdi:water-boiler",
        value_fn=get_hot_water_operation_mode,
    ),
    WiserSensorEntityDescription(
        key="hot_water_demand",
        name="Hot Water Demand",
        device="hotwater",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        icon="mdi:water-boiler",
        value_fn=lambda x: 100 if x.is_heating else 0,
    ),
    WiserSensorEntityDescription(
        key="hot_water_state",
        name="Hot Water",
        device="hotwater",
        icon_fn=lambda x: "mdi:fire" if x.current_state == "On" else "mdi:fire-off",
        value_fn=lambda x: x.current_state,
        extra_state_attributes=[
            WiserDeviceAttribute("boost_end", "boost_end_time"),
            WiserDeviceAttribute(
                "boost_time_remaining", lambda x: int(x.boost_time_remaining / 60)
            ),
            WiserDeviceAttribute("away_mode_supressed"),
            WiserDeviceAttribute("is_away_mode"),
            WiserDeviceAttribute("is_boosted"),
            WiserDeviceAttribute("is_override", "hw.is_override"),
            WiserDeviceAttribute("schedule_id", "schedule.id"),
            WiserDeviceAttribute("schedule_name", "schedule.name"),
            WiserDeviceAttribute("next_day_change", "schedule.next.day"),
            WiserDeviceAttribute("next_schedule_change", "schedule.next.time"),
            WiserDeviceAttribute("next_schedule_datetime", "schedule.next.datetime"),
            WiserDeviceAttribute("next_schedule_state", "schedule.next.setting"),
        ],
    ),
    # Opentherm Sensors
    WiserSensorEntityDescription(
        key="opentherm_flow_temp",
        name="Flow Temperature",
        device="system",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.opentherm.operational_data.ch_flow_temperature,
    ),
    WiserSensorEntityDescription(
        key="opentherm_return_temp",
        name="Return Temperature",
        device="system",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.opentherm.operational_data.ch_return_temperature,
    ),
    # All Devices Sensors
    WiserSensorEntityDescription(
        key="battery",
        name="Battery",
        device_collection="devices",
        legacy_type="device",
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        supported=lambda dev, hub: hasattr(dev, "battery"),
        value_fn=lambda x: x.battery.percent,
        extra_state_attributes=[
            WiserDeviceAttribute("battery_voltage", "battery.voltage"),
            WiserDeviceAttribute(ATTR_BATTERY_LEVEL, "battery.level"),
        ],
    ),
    WiserSensorEntityDescription(
        key="signal",
        name="Signal",
        device_collection="devices",
        legacy_type="signal",
        icon_fn=lambda x: SIGNAL_STRENGTH_ICONS[x.signal.displayed_signal_strength]
        if x.signal.displayed_signal_strength in SIGNAL_STRENGTH_ICONS
        else SIGNAL_STRENGTH_ICONS["NoSignal"],
        value_fn=lambda x: x.signal.displayed_signal_strength,
        extra_state_attributes=[
            WiserAttribute("vendor", MANUFACTURER),
            WiserDeviceAttribute("product_type"),
            WiserDeviceAttribute("model_identifier", "model"),
            WiserDeviceAttribute("firmware", "firmware_version"),
            WiserDeviceAttribute("node_id"),
            WiserHubAttribute("zigbee_channel", "system.zigbee.network_channel"),
            WiserDeviceAttribute("serial_number"),
            WiserDeviceAttribute(
                "hub_route", lambda x: "Repeater" if x.parent_node_id > 0 else "Direct"
            ),
            WiserDeviceAttribute(
                "device_reception_RSSI", "signal.device_reception_rssi"
            ),
            WiserDeviceAttribute("device_reception_LQI", "signal.device_reception_lqi"),
            WiserDeviceAttribute(
                "device_reception_percent", "signal.device_signal_strength"
            ),
            WiserDeviceAttribute(
                "controller_reception_RSSI", "signal.controller_reception_rssi"
            ),
            WiserDeviceAttribute(
                "controller_reception_LQI", "signal.controller_reception_lqi"
            ),
            WiserDeviceAttribute(
                "controller_reception_percent", "signal.controller_signal_strength"
            ),
            WiserDeviceAttribute("parent_node_id"),
            WiserHubAttribute(
                "repeater",
                lambda d, h: h.devices.get_by_node_id(d.parent_node_id).name
                if d.parent_node_id > 0
                else "None",
            ),
        ],
    ),
    WiserSensorEntityDescription(
        key="schedule",
        name="Schedule",
        device_collection="devices",
        supported=lambda dev, hub: hasattr(dev, "schedule"),
        value_fn=lambda x: x.schedule.next.datetime if x.schedule else None,
        extra_state_attributes=[
            WiserDeviceAttribute("setting", "schedule.next.setting"),
        ],
    ),
    # Heating Actuators
    WiserSensorEntityDescription(
        key="power",
        name="Current Power",
        legacy_type="device",
        legacy_name_fn=lambda d, x: f"LTS Power {d.rooms.get_by_id(x.room_id).name}"
        if x.room_id
        else f"{x.product_type} {x.id}",
        device_collection="devices.heating_actuators",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda x: x.instantaneous_power,
    ),
    WiserSensorEntityDescription(
        key="energy_delivered",
        name="Energy Delivered",
        legacy_type="device",
        device_collection="devices.heating_actuators",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power,
    ),
    WiserSensorEntityDescription(
        key="floor_temperature",
        name="Floor Temperature",
        legacy_type="device",
        device_collection="devices.heating_actuators",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.floor_temperature_sensor.measured_temperature
        if x.floor_temperature_sensor.sensor_type != "Not_Fitted"
        else x.none,
    ),
    # Power Tags
    WiserSensorEntityDescription(
        key="pte_power",
        name="Current Power",
        device_collection="devices.power_tags",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda x: x.instantaneous_power,
    ),
    WiserSensorEntityDescription(
        key="pte_energy_received",
        name="Energy Received",
        device_collection="devices.power_tags",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        value_fn=lambda x: x.received_power,
    ),
    WiserSensorEntityDescription(
        key="pte_energy_delivered",
        name="Energy Delivered",
        device_collection="devices.power_tags",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        value_fn=lambda x: x.delivered_power,
    ),
    WiserSensorEntityDescription(
        key="pte_voltage",
        name="Voltage",
        device_collection="devices.power_tags",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn=lambda x: x.equipment.power.rms_voltage,
    ),
    WiserSensorEntityDescription(
        key="pte_current",
        name="Current",
        device_collection="devices.power_tags",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value_fn=lambda x: x.equipment.power.rms_current,
    ),
    # iTRVs
    WiserSensorEntityDescription(
        key="smartvalve_current_temperature",
        name="Temperature",
        device_collection="devices.smartvalves",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature,
    ),
    WiserSensorEntityDescription(
        key="smartvalve_percentage_demand",
        name="Percentage Demand",
        device_collection="devices.smartvalves",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.percentage_demand,
    ),
    # Roomstats
    WiserSensorEntityDescription(
        key="roomstat_current_temperature",
        name="Temperature",
        device_collection="devices.roomstats",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature,
    ),
    WiserSensorEntityDescription(
        key="roomstat_current_humidity",
        name="Humidity",
        device_collection="devices.roomstats",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.current_humidity,
    ),
    # Smart Plugs
    WiserSensorEntityDescription(
        key="smartplug_power",
        name="Power",
        device_collection="devices.smartplugs",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda x: x.instantaneous_power,
    ),
    WiserSensorEntityDescription(
        key="smartplug_energy",
        name="Energy",
        device_collection="devices.smartplugs",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power,
    ),
    # Smoke Alarms
    WiserSensorEntityDescription(
        key="smokealarm_current_temperature",
        name="Temperature",
        device_collection="devices.smokealarms",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature,
    ),
    # Room Sensors
    WiserSensorEntityDescription(
        key="room_heating_demand",
        name="Heating Demand",
        legacy_name_fn=lambda x: f"LTS Heating Demand {x.name}",
        legacy_type="room",
        device_collection="rooms",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.percentage_demand,
    ),
    WiserSensorEntityDescription(
        key="room_current_temperature",
        name="Temperature",
        legacy_name_fn=lambda x: f"LTS Temperature {x.name}",
        legacy_type="room",
        device_collection="rooms",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature,
    ),
    WiserSensorEntityDescription(
        key="room_target_temperature",
        name="Target Temperature",
        legacy_name_fn=lambda x: f"LTS Target Temperature {x.name}",
        legacy_type="room",
        device_collection="rooms",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_target_temperature,
    ),
    WiserSensorEntityDescription(
        key="room_current_humidity",
        name="Humidity",
        legacy_name_fn=lambda x: f"LTS Humidity {x.name}",
        legacy_type="room",
        device_collection="rooms",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.current_humidity if x.roomstat_id else None,
    ),
    WiserSensorEntityDescription(
        key="room_schedule",
        name="Schedule",
        device_collection="rooms",
        value_fn=lambda x: "Active" if x.mode == "Auto" else "Inactive",
        extra_state_attributes=[
            WiserDeviceAttribute("schedule_id", "schedule.id"),
            WiserDeviceAttribute("schedule_name", "schedule.name"),
            WiserDeviceAttribute("scheduled_temperature", "schedule.current_setting"),
            WiserDeviceAttribute("next_change", "schedule.next.datetime"),
            WiserDeviceAttribute("next_temperature", "schedule.next.setting"),
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
    entities = get_entities(data, WISER_SENSORS, WiserSensor)
    async_add_entities(entities)

    return True


class WiserSensor(WiserBaseEntity, SensorEntity):
    """Class to monitor sensors of a Wiser device."""

    entity_description: WiserSensorEntityDescription

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserSensorEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        """Init wiser sensor."""
        super().__init__(coordinator, description, device, "sensor")

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        if self._device and self.entity_description.value_fn is not None:
            no_of_params = len(signature(self.entity_description.value_fn).parameters)
            if no_of_params == 2:
                return self.entity_description.value_fn(self._data, self._device)
            return self.entity_description.value_fn(self._device)

        return None

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor, if any."""
        if self.entity_description.unit_of_measurement:
            return self.entity_description.unit_of_measurement

        if self._device and self.entity_description.unit_fn is not None:
            return self.entity_description.unit_fn(self._device)
        return super().native_unit_of_measurement
