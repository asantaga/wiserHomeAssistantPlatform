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
from aioWiserHeatAPI.pte import _WiserPowerTagEnergy
from aioWiserHeatAPI.room import _WiserRoom
from aioWiserHeatAPI.smartplug import _WiserSmartPlug

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
    WiserV2DeviceAttribute,
)
from .helpers import get_entities, get_hot_water_operation_mode, get_vendor_name

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
            WiserDeviceAttribute("hardware_generation"),
            WiserDeviceAttribute("firmware", "firmware_version"),
            WiserDeviceAttribute("node_id"),
            WiserDeviceAttribute("zigbee_channel", "zigbee.network_channel"),
            WiserV2DeviceAttribute("zigbee_uuid", "uuid"),
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
        key="heating_operation_mode",
        name="Heating Operation Mode",
        device="system",
        value_fn=lambda x: "Away Mode" if x.is_away_mode_enabled else "Normal",
        extra_state_attributes=[
            WiserDeviceAttribute("last_updated", "0")  # TODO: Resolve this issue!
        ],
    ),
    # Heating Channel Sensors
    WiserSensorEntityDescription(
        key="heating_channel_demand",
        name_fn=lambda d, h: "Heating Demand"
        if h.heating_channels.count == 1
        else f"Heating Demand Channel {d.id}",
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
    # Opentherm Sensors
    WiserSensorEntityDescription(
        key="opentherm_flow_temp",
        name="Flow Temperature",
        device="system.opentherm",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        supported=lambda dev, hub: dev.enabled is not None,
        value_fn=lambda x: x.operational_data.ch_flow_temperature,
        extra_state_attributes=[
            WiserDeviceAttribute("ch_flow_active_lower_setpoint"),
            WiserDeviceAttribute("ch_flow_active_upper_setpoint"),
            WiserDeviceAttribute("ch1_flow_enabled"),
            WiserDeviceAttribute("ch1_flow_setpoint"),
            WiserDeviceAttribute("ch2_flow_enabled"),
            WiserDeviceAttribute("ch2_flow_setpoint"),
            WiserDeviceAttribute("connection_status"),
            WiserDeviceAttribute("hw_enabled"),
            WiserDeviceAttribute("hw_flow_setpoint"),
            WiserDeviceAttribute("operating_mode"),
            WiserDeviceAttribute("tracked_room_id"),
            WiserDeviceAttribute(
                "tracked_room_name",
                lambda dev, hub: hub.rooms.get_by_id(dev.tracked_room_id).name,
            ),
            WiserDeviceAttribute("room_setpoint"),
            WiserDeviceAttribute("room_temperature"),
            # Operational Data Attributes
            WiserDeviceAttribute(
                "ch_pressure_bar",
                "operational_data.ch_pressure_bar",
            ),
            WiserDeviceAttribute(
                "ch_return_temperature",
                "operational_data.ch_return_temperature",
            ),
            WiserDeviceAttribute(
                "relative_modulation_level",
                "operational_data.relative_modulation_level",
            ),
            WiserDeviceAttribute(
                "hw_temperature",
                "operational_data.hw_temperature",
            ),
            WiserDeviceAttribute(
                "hw_flow_rate",
                "operational_data.hw_flow_rate",
            ),
            WiserDeviceAttribute(
                "slave_status",
                "operational_data.slave_status",
            ),
            # Boiler Params
            WiserDeviceAttribute(
                "boiler_ch_max_setpoint_read_write",
                "boiler_parameters.ch_max_setpoint_read_write",
            ),
            WiserDeviceAttribute(
                "boiler_ch_max_setpoint_transfer_enable",
                "boiler_parameters.ch_max_setpoint_transfer_enable",
            ),
            WiserDeviceAttribute(
                "boiler_ch_setpoint",
                "boiler_parameters.ch_setpoint",
            ),
            WiserDeviceAttribute(
                "boiler_ch_setpoint_lower_bound",
                "boiler_parameters.ch_setpoint_lower_bound",
            ),
            WiserDeviceAttribute(
                "boiler_ch_setpoint_upper_bound",
                "boiler_parameters.ch_setpoint_upper_bound",
            ),
            WiserDeviceAttribute(
                "oiler_hw_setpoint_read_write",
                "boiler_parameters.hw_setpoint_read_write",
            ),
            WiserDeviceAttribute(
                "boiler_hw_setpoint_transfer_enable",
                "boiler_parameters.hw_setpoint_transfer_enable",
            ),
            WiserDeviceAttribute(
                "boiler_hw_setpoint",
                "boiler_parameters.hw_setpoint",
            ),
            WiserDeviceAttribute(
                "boiler_hw_setpoint_lower_bound",
                "boiler_parameters.hw_setpoint_lower_bound",
            ),
            WiserDeviceAttribute(
                "boiler_hw_setpoint_upper_bound",
                "boiler_parameters.hw_setpoint_upper_bound",
            ),
        ],
    ),
    WiserSensorEntityDescription(
        key="opentherm_return_temp",
        name="Return Temperature",
        device="system.opentherm",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        supported=lambda dev, hub: dev.enabled is not None,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.operational_data.ch_return_temperature,
    ),
    # All Devices Sensors
    WiserSensorEntityDescription(
        key="battery",
        name="Battery",
        device_collection="devices",
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
        icon_fn=lambda x: SIGNAL_STRENGTH_ICONS[x.signal.displayed_signal_strength]
        if x.signal.displayed_signal_strength in SIGNAL_STRENGTH_ICONS
        else SIGNAL_STRENGTH_ICONS["NoSignal"],
        value_fn=lambda x: x.signal.displayed_signal_strength,
        extra_state_attributes=[
            WiserDeviceAttribute("vendor", get_vendor_name),
            WiserDeviceAttribute("product_type"),
            WiserDeviceAttribute("model", "model"),
            WiserDeviceAttribute("product_identifier"),
            WiserDeviceAttribute("firmware", "firmware_version"),
            WiserDeviceAttribute("node_id"),
            WiserHubAttribute("zigbee_channel", "system.zigbee.network_channel"),
            WiserV2DeviceAttribute("zigbee_uuid", "uuid"),
            WiserDeviceAttribute("serial_number"),
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
            WiserDeviceAttribute(
                "hub_route", lambda x: "Repeater" if x.parent_node_id > 0 else "Direct"
            ),
            WiserHubAttribute(
                "repeater",
                lambda d, h: h.devices.get_by_node_id(d.parent_node_id).name
                if d.parent_node_id > 0
                else "None",
            ),
            # V2 only attributes
            WiserV2DeviceAttribute("type", "type_comm"),
            WiserV2DeviceAttribute("uuid"),
            WiserV2DeviceAttribute("endpoint"),
        ],
    ),
    WiserSensorEntityDescription(
        key="schedule",
        name="Schedule",
        device_collection="devices",
        supported=lambda dev, hub: hasattr(dev, "schedule"),
        value_fn=lambda x: "Unassigned"
        if not x.schedule_id
        else "Active"
        if x.mode == "Auto"
        else "Inactive",
        extra_state_attributes=[
            WiserDeviceAttribute("schedule_id", "schedule.id"),
            WiserDeviceAttribute("schedule_name", "schedule.name"),
            WiserDeviceAttribute("scheduled_state", "schedule.current_setting"),
            WiserDeviceAttribute("next_change", "schedule.next.datetime"),
            WiserDeviceAttribute("next_temperature", "schedule.next.setting"),
        ],
    ),
    WiserSensorEntityDescription(
        key="equipment",
        name="Equipment",
        device_collection="devices",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        supported=lambda dev, hub: hasattr(dev, "equipment")
        and dev.equipment is not None,
        value_fn=lambda x: x.equipment.power.total_active_power / 1000,
        extra_state_attributes=[
            WiserDeviceAttribute("product_identifier"),
            WiserDeviceAttribute("name", "equipment.equipment_name"),
            WiserDeviceAttribute("family", "equipment.equipment_family"),
            WiserDeviceAttribute("installation_type", "equipment.installation_type"),
            WiserDeviceAttribute("equipment_id", "equipment.id"),
            WiserDeviceAttribute("equipment_device_id", "equipment.device_id"),
            WiserDeviceAttribute("equipment_UUID", "equipment.uuid"),
            WiserDeviceAttribute("number_of_phases", "equipment.number_of_phases"),
            WiserDeviceAttribute("direction", "equipment.direction"),
            WiserDeviceAttribute("operating_status", "equipment.operating_status"),
            WiserDeviceAttribute("fault_status", "equipment.fault_status"),
            WiserDeviceAttribute("active_power", "equipment.power.active_power"),
            WiserDeviceAttribute(
                "total_active_power", "equipment.power.total_active_power"
            ),
            WiserDeviceAttribute(
                "energy",
                lambda x: round(
                    x.equipment.power.current_summation_delivered / 1000,
                    2,
                ),
            ),
            # Power Tag Only Attributes
            WiserDeviceAttribute("grid_limit", device_type=_WiserPowerTagEnergy),
            WiserDeviceAttribute(
                "grid_limit_UOM", "grid_limit_uom", device_type=_WiserPowerTagEnergy
            ),
            WiserDeviceAttribute("energy_export", device_type=_WiserPowerTagEnergy),
            WiserDeviceAttribute("self_consumption", device_type=_WiserPowerTagEnergy),
            WiserDeviceAttribute(
                "rmms_current",
                "equipment.power.rms_current",
                device_type=_WiserPowerTagEnergy,
            ),
            WiserDeviceAttribute(
                "rmms_voltage",
                "equipment.power.rms_voltage",
                device_type=_WiserPowerTagEnergy,
            ),
            WiserDeviceAttribute(
                "energy_received",
                "equipment.power.current_summation_received",
                device_type=_WiserPowerTagEnergy,
            ),
            # Smartplug Only Attributes
            WiserDeviceAttribute(
                "functional_control_mode",
                "equipment.functional_control_mode",
                device_type=_WiserSmartPlug,
            ),
            # Smartplug and PowerTag only
            WiserDeviceAttribute(
                "pcm_mode",
                "equipment.pcm_mode",
                device_type=(_WiserPowerTagEnergy, _WiserSmartPlug),
            ),
        ],
    ),
    # Heating Actuators
    WiserSensorEntityDescription(
        key="power",
        name="Current Power",
        device_collection="devices.heating_actuators",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        value_fn=lambda x: x.instantaneous_power,
    ),
    WiserSensorEntityDescription(
        key="energy_delivered",
        name="Energy Delivered",
        device_collection="devices.heating_actuators",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power,
    ),
    WiserSensorEntityDescription(
        key="heating_actuator_current_temperature",
        name="Temperature",
        device_collection="devices.heating_actuators",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature,
    ),
    WiserSensorEntityDescription(
        key="floor_temperature",
        name="Floor Temperature",
        device_collection="devices.heating_actuators",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        supported=lambda dev, hub: hasattr(dev.floor_temperature_sensor, "sensor_type")
        and dev.floor_temperature_sensor.sensor_type != "Not_Fitted",
        value_fn=lambda x: x.floor_temperature_sensor.measured_temperature,
        extra_state_attributes=[
            WiserDeviceAttribute("sensor_type", "floor_temperature_sensor.sensor_type"),
            WiserDeviceAttribute("status", "floor_temperature_sensor.status"),
            WiserDeviceAttribute(
                "min_temp", "floor_temperature_sensor.minimum_temperature"
            ),
            WiserDeviceAttribute(
                "max_temp", "floor_temperature_sensor.maximum_temperature"
            ),
        ],
    ),
    # Power Tags
    WiserSensorEntityDescription(
        key="pte_power",
        name="Current Power",
        device_collection="devices.power_tags",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfPower.WATT,
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        value_fn=lambda x: x.instantaneous_power,
    ),
    WiserSensorEntityDescription(
        key="pte_energy_received",
        name="Energy Received",
        device_collection="devices.power_tags",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.received_power,
    ),
    WiserSensorEntityDescription(
        key="pte_energy_delivered",
        name="Energy Delivered",
        device_collection="devices.power_tags",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
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
        key="pte_total_energy",
        name="Net Energy",
        device_collection="devices.power_tags",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power - x.received_power,
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
        suggested_unit_of_measurement=UnitOfPower.KILO_WATT,
        value_fn=lambda x: x.instantaneous_power,
    ),
    WiserSensorEntityDescription(
        key="smartplug_energy",
        name="Energy",
        device_collection="devices.smartplugs",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        suggested_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
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
        device_collection="rooms",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.percentage_demand,
    ),
    WiserSensorEntityDescription(
        key="room_current_temperature",
        name="Temperature",
        device_collection="rooms",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature,
    ),
    WiserSensorEntityDescription(
        key="room_target_temperature",
        name="Target Temperature",
        device_collection="rooms",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_target_temperature,
    ),
    WiserSensorEntityDescription(
        key="room_current_humidity",
        name="Humidity",
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
