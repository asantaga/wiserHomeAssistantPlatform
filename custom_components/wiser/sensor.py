"""
Sensor Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
from collections.abc import Mapping, Callable
from dataclasses import dataclass
from datetime import datetime
from functools import reduce
from inspect import signature
import logging
from typing import Any

from aioWiserHeatAPI.const import TEXT_UNKNOWN

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    STATE_UNAVAILABLE,
    UnitOfTemperature,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    PERCENTAGE,
    UnitOfPower,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from aioWiserHeatAPI.wiserhub import TEMP_OFF
from aioWiserHeatAPI.devices import _WiserDeviceTypeEnum as DeviceType
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
    SIGNAL_STRENGTH_ICONS,
    VERSION,
)
from .helpers import WiserDeviceAttribute, WiserHubAttribute, get_device_by_node_id, get_device_name, get_hot_water_operation_mode, get_unique_id, get_identifier

_LOGGER = logging.getLogger(__name__)

@dataclass
class WiserSensorEntityDescription(SensorEntityDescription):
    """A class that describes Wiser sensor entities."""

    sensor_type: str | None = None
    function_key: str | None = None
    icon_fn: Callable[[Any], str] | None = None
    unit_fn: Callable[[Any], str] | None = None
    value_fn: Callable[[Any], float | str] | None = None
    extra_state_attributes: dict[str, Callable[[Any], float | str]] | None = None


HUB_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="signal",
        name="Signal",
        sensor_type="device",
        function_key = "system",
        icon_fn=lambda x: SIGNAL_STRENGTH_ICONS[x.signal.displayed_signal_strength] if x.signal.displayed_signal_strength in SIGNAL_STRENGTH_ICONS else SIGNAL_STRENGTH_ICONS["NoSignal"],
        value_fn=lambda x: x.signal.displayed_signal_strength,
        extra_state_attributes={
            "vendor": MANUFACTURER,
            "product_type": WiserDeviceAttribute("product_type"),
            "model_identifier": WiserDeviceAttribute("model"),
            "firmware": WiserDeviceAttribute("firmware_version"),
            "node_id": WiserDeviceAttribute("node_id"),
            "zigbee_channel": WiserDeviceAttribute("zigbee.network_channel"),
            "wifi_strength": WiserDeviceAttribute("signal.controller_reception_rssi"),
            "wifi_strength_percent": WiserDeviceAttribute("signal.controller_signal_strength"),
            "wifi_SSID": WiserDeviceAttribute("network.ssid"),
            "wifi_IP": WiserDeviceAttribute("network.ip_address"),
            "api_version": WiserHubAttribute("version"),
            "integration_version": VERSION,
            "uptime": WiserHubAttribute("status.uptime"),
            "last_reset_reason": WiserHubAttribute("status.last_reset_reason")
        }
    ),
    WiserSensorEntityDescription(
        key="cloud",
        name="Cloud",
        sensor_type="device",
        function_key = "system",
        icon_fn=lambda x: "mdi:cloud-check" if x.cloud.connection_status == "Connected" else "mdi:cloud-alert",
        value_fn=lambda x: x.cloud.connection_status
    ),
    WiserSensorEntityDescription(
        key="heating_operation_mode",
        name="Heating Operation Mode",
        sensor_type="device",
        function_key = "system",
        value_fn=lambda x: "Away Mode" if x.is_away_mode_enabled else "Normal"
    ),
    WiserSensorEntityDescription(
        key="heating_channel_1",
        name="Heating Channel 1",
        sensor_type="device",
        function_key = "heating_channels",
        icon_fn=lambda x: "mdi:radiator-disabled" if x.get_by_id(1).heating_relay_status == "Off" else "mdi:radiator",
        value_fn=lambda x: x.get_by_id(1).heating_relay_status,
        extra_state_attributes={
            "percentage_demand": lambda x: x.get_by_id(1).percentage_demand,
            "room_ids": lambda x: x.get_by_id(1).room_ids,
            "is_smartvalve_preventing_demand": lambda x: x.get_by_id(1).is_smart_valve_preventing_demand
        }
    ),
    WiserSensorEntityDescription(
        key="heating_channel_2",
        name="Heating Channel 2",
        sensor_type="device",
        function_key = "heating_channels",
        icon_fn=lambda x: "mdi:radiator-disabled" if x.get_by_id(2).heating_relay_status == "Off" else "mdi:radiator",
        value_fn=lambda x: x.get_by_id(2).heating_relay_status,
        extra_state_attributes={
            "percentage_demand": lambda x: x.get_by_id(2).percentage_demand,
            "room_ids": lambda x: x.get_by_id(2).room_ids,
            "is_smartvalve_preventing_demand": lambda x: x.get_by_id(2).is_smart_valve_preventing_demand
        }
    ),
    WiserSensorEntityDescription(
        key="hot_water_operation_mode",
        name="Hot Water Operation Mode",
        sensor_type="device",
        function_key="hotwater",
        icon="mdi:water-boiler",
        value_fn=get_hot_water_operation_mode
    ),
    WiserSensorEntityDescription(
        key="hot_water_demand",
        name="Hot Water Demand",
        sensor_type="device",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        function_key="hotwater",
        icon="mdi:water-boiler",
        value_fn=lambda x: 100 if x.is_heating else 0
    ),
    WiserSensorEntityDescription(
        key="hot_water_state",
        name="Hot Water",
        sensor_type="device",
        function_key="hotwater",
        icon_fn=lambda x: "mdi:fire" if x.current_state == "On" else "mdi:fire-off",
        value_fn=lambda x: x.current_state,
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
            "next_schedule_state": WiserDeviceAttribute("schedule.next.setting")
        }
    )
)

OPENTHERM_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="opentherm_flow_temp",
        name="Flow Temperature",
        sensor_type="device",
        function_key="system",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.opentherm.operational_data.ch_flow_temperature
    ),
    WiserSensorEntityDescription(
        key="opentherm_return_temp",
        name="Return Temperature",
        sensor_type="device",
        function_key="system",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.opentherm.operational_data.ch_return_temperature
    ),
)

ALL_DEVICE_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="battery",
        name="Battery",
        sensor_type="device",
        device_class=SensorDeviceClass.BATTERY,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.battery.percent,
        extra_state_attributes={
            "battery_voltage": WiserDeviceAttribute("battery.voltage"),
            ATTR_BATTERY_LEVEL: WiserDeviceAttribute("battery.level")
        }
    ),
    WiserSensorEntityDescription(
        key="signal",
        name="Signal",
        sensor_type="device",
        icon_fn=lambda x: SIGNAL_STRENGTH_ICONS[x.signal.displayed_signal_strength] if x.signal.displayed_signal_strength in SIGNAL_STRENGTH_ICONS else SIGNAL_STRENGTH_ICONS["NoSignal"],
        value_fn=lambda x: x.signal.displayed_signal_strength,
        extra_state_attributes={
            "vendor": MANUFACTURER,
            "product_type": WiserDeviceAttribute("product_type"),
            "model_identifier": WiserDeviceAttribute("model"),
            "firmware": WiserDeviceAttribute("firmware_version"),
            "node_id": WiserDeviceAttribute("node_id"),
            "zigbee_channel": WiserDeviceAttribute("zigbee.network_channel"),
            "serial_number": WiserDeviceAttribute("serial_number"),
            "hub_route": lambda x: "Repeater" if x.parent_node_id > 0 else "Direct",
            "device_reception_RSSI": WiserDeviceAttribute("signal.device_reception_rssi"),
            "device_reception_LQI": WiserDeviceAttribute("signal.device_reception_lqi"),
            "device_reception_percent": WiserDeviceAttribute("signal.device_signal_strength"),
            "controller_reception_RSSI": WiserDeviceAttribute("signal.controller_reception_rssi"),
            "controller_reception_LQI": WiserDeviceAttribute("signal.controller_reception_lqi"),
            "controller_reception_percent": WiserDeviceAttribute("signal.controller_signal_strength"),
            "parent_node_id": WiserDeviceAttribute("parent_node_id"),
            "repeater": lambda d, x: get_device_by_node_id(d, x.parent_node_id).name
        }
    )
)

HEATING_ACTUATOR_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="power",
        name="Current Power",
        sensor_type="device",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda x: x.instantaneous_power
    ),
    WiserSensorEntityDescription(
        key="energy_delivered",
        name="Energy Delivered",
        sensor_type="device",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power
    ),
    WiserSensorEntityDescription(
        key="floor_temp",
        name="Floor Temp",
        sensor_type="device",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.floor_temperature_sensor.measured_temperature if x.floor_temperature_sensor.sensor_type != "Not_Fitted" else x.none
    ),

)

POWERTAGE_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="pte_power",
        name="Current Power",
        sensor_type="device",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda x: x.instantaneous_power
    ),
    WiserSensorEntityDescription(
        key="pte_energy_received",
        name="Energy Received",
        sensor_type="device",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.received_power
    ),
    WiserSensorEntityDescription(
        key="pte_energy_delivered",
        name="Energy Delivered",
        sensor_type="device",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power
    ),
    WiserSensorEntityDescription(
        key="pte_voltage",
        name="Voltage",
        sensor_type="device",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn=lambda x: x.equipment.power.rms_voltage
    ),
    WiserSensorEntityDescription(
        key="pte_current",
        name="Current",
        sensor_type="device",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value_fn=lambda x: x.equipment.power.rms_current
    )
)

SMARTVALVE_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="smartvalve_current_temperature",
        name="Temperature",
        sensor_type="device",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature
    ),
    WiserSensorEntityDescription(
        key="smartvalve_percentage_demand",
        name="Percentage Demand",
        sensor_type="device",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.percentage_demand
    ),
)

ROOMSTAT_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="roomstat_current_temperature",
        name="Temperature",
        sensor_type="device",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature
    ),
    WiserSensorEntityDescription(
        key="roomstat_current_humidity",
        name="Humidity",
        sensor_type="device",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.current_humidity
    ),
)

SMARTPLUG_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="smartplug_power",
        name="Power",
        sensor_type="device",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda x: x.instantaneous_power
    ),
    WiserSensorEntityDescription(
        key="smartplug_energy",
        name="Energy",
        sensor_type="device",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power
    ),
)

ROOM_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="room_heating_demand",
        name="Heating Demand",
        sensor_type="room",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.percentage_demand
    ),
    WiserSensorEntityDescription(
        key="room_current_temperature",
        name="Temperature",
        sensor_type="room",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature
    ),
    WiserSensorEntityDescription(
        key="room_target_temperature",
        name="Target Temperature",
        sensor_type="room",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_target_temperature
    ),
    WiserSensorEntityDescription(
        key="room_current_humidity",
        name="Humidity",
        sensor_type="room",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.current_humidity if x.roomstat_id else x.none
    ),
    WiserSensorEntityDescription(
        key="room_window_state",
        name="Window State",
        sensor_type="room",
        value_fn=lambda x: x.window_state
    ),
)

HUB_SENSOR_ENTITIES = {
    "HUB": HUB_SENSORS,
    "OPENTHERM": OPENTHERM_SENSORS
}

DEVICE_SENSOR_ENTITIES = {
    "ALL_DEVICES": ALL_DEVICE_SENSORS,
    DeviceType.HeatingActuator: HEATING_ACTUATOR_SENSORS,
    DeviceType.PowerTagE: POWERTAGE_SENSORS,
    DeviceType.RoomStat: ROOMSTAT_SENSORS,
    DeviceType.SmartPlug: SMARTPLUG_SENSORS,
    DeviceType.iTRV: SMARTVALVE_SENSORS,
}

ROOM_SENSOR_ENTITIES = {
    "ROOMS": ROOM_SENSORS
}


def _sensor_exist(
    data: dict, device: _WiserDevice, sensor_desc: WiserSensorEntityDescription
) -> bool:
    """Check if a sensor exist for device."""
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

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_sensors = []

    # Add signal sensors for all devices
    _LOGGER.debug("Setting up Device sensors")

    # NEW CODE FOR CONFIGERED SENSORS

    wiser_hub_sensors = [
        WiserSensor2(data, sensor_desc, getattr(data.wiserhub, sensor_desc.function_key))
        for device_type, sensor_descs in HUB_SENSOR_ENTITIES.items()
        for sensor_desc in sensor_descs
        if _sensor_exist(data.wiserhub, getattr(data.wiserhub, sensor_desc.function_key), sensor_desc)
    ]

    wiser_room_sensors = [
        WiserSensor2(data, sensor_desc, room )
        for device_type, sensor_descs in ROOM_SENSOR_ENTITIES.items()
        for sensor_desc in sensor_descs
        for room in data.wiserhub.rooms.all
        if _sensor_exist(data.wiserhub, room, sensor_desc)
    ]

    wiser_device_sensors = [
        WiserSensor2(data, sensor_desc, device )
        for device_type, sensor_descs in DEVICE_SENSOR_ENTITIES.items()
        for sensor_desc in sensor_descs
        for device in data.wiserhub.devices.all
        if _sensor_exist(data.wiserhub, device, sensor_desc) and (device_type == "ALL_DEVICES" or device.product_type == device_type.name)
    ]

    # Add hub wifi signal sensor
    #wiser_sensors.append(WiserDeviceSignalSensor(data, 0, "Controller"))
    #if data.wiserhub.devices:
        #for device in data.wiserhub.devices.all:
            # wiser_sensors.append(
            #    WiserDeviceSignalSensor(data, device.id, device.product_type)
            #)
            #if hasattr(device, "battery"):
            #    wiser_sensors.append(
            #        WiserBatterySensor(data, device.id, sensor_type="Battery")
            #    )

    # Add cloud status sensor
    #_LOGGER.debug("Setting up Cloud sensor")
    #wiser_sensors.append(WiserSystemCloudSensor(data, sensor_type="Cloud"))

    # Add operation sensor
    #_LOGGER.debug("Setting up Heating Operation Mode sensor")
    #wiser_sensors.append(
    #    WiserSystemOperationModeSensor(data, sensor_type="Heating Operation Mode")
    #)

    # Add heating circuit sensor
    #if data.wiserhub.heating_channels:
    #    _LOGGER.debug("Setting up Heating Circuit sensors")
    #    for heating_channel in data.wiserhub.heating_channels.all:
    #        wiser_sensors.append(
    #            WiserSystemCircuitState(data, heating_channel.id, sensor_type="Heating")
    #        )

    # Add hot water sensors if supported on hub
    #if data.wiserhub.hotwater:
    #    _LOGGER.debug("Setting up Hot Water sensors")
    #    wiser_sensors.extend(
    #        [
    #            WiserSystemCircuitState(data, sensor_type="Hot Water"),
                #WiserSystemHotWaterPreset(data, sensor_type="Hot Water Operation Mode"),
    #        ]
    #    )

    # Add power sensors for smartplugs
    #if data.wiserhub.devices.smartplugs:
    #    _LOGGER.debug("Setting up Smart Plug power sensors")
    #    for smartplug in data.wiserhub.devices.smartplugs.all:
    #        wiser_sensors.extend(
    #            [
    #                WiserSmartplugPower(data, smartplug.id, sensor_type="Power"),
    #                WiserSmartplugPower(data, smartplug.id, sensor_type="Total Power"),
    #            ]
    #        )

    # Add power sensors for PTE (v2Hub)
    """
    if data.wiserhub.devices.power_tags:
        for power_tag in data.wiserhub.devices.power_tags.all:
            wiser_sensors.extend(
                [
                    WiserLTSPowerSensor(data, power_tag.id, sensor_type="Power", name="Power"),
                    WiserLTSPowerSensor(data, power_tag.id, sensor_type="Energy", name="Energy Delivered"),
                    WiserLTSPowerSensor(data, power_tag.id, sensor_type="EnergyReceived", name="Energy Received"),
                    WiserCurrentVoltageSensor(data, power_tag.id, sensor_type="Voltage"),
                    WiserCurrentVoltageSensor(data, power_tag.id, sensor_type="Current")
                ]
            )
    """

    # Add LTS sensors - for room temp and target temp
    #_LOGGER.debug("Setting up LTS sensors")
    #for room in data.wiserhub.rooms.all:
    #    if room.devices:
    #        wiser_sensors.extend(
    #            [
    #                WiserLTSTempSensor(data, room.id, sensor_type="current_temp"),
    #
    #                 WiserLTSTempSensor(
    #                    data, room.id, sensor_type="current_target_temp"
    #                ),
    #                WiserLTSDemandSensor(data, room.id, "room"),
    #            ]
    #        )

    #        if room.roomstat_id:
    #            wiser_sensors.append(WiserLTSHumiditySensor(data, room.roomstat_id))

    # Add LTS sensors - for room Power and Energy for heating actuators
    #if data.wiserhub.devices.heating_actuators:
    #    _LOGGER.debug("Setting up Heating Actuator LTS sensors")
    #    for heating_actuator in data.wiserhub.devices.heating_actuators.all:
            #wiser_sensors.extend(
            #    [
            #        WiserLTSPowerSensor(data, heating_actuator.id, sensor_type="Power"),
            #        WiserLTSPowerSensor(
            #            data, heating_actuator.id, sensor_type="Energy"
            #        ),
            #    ]
            #)
            #if (
            #    heating_actuator.floor_temperature_sensor
            #    and heating_actuator.floor_temperature_sensor.sensor_type
            #    != "Not_Fitted"
            #):
            #    _LOGGER.debug(f"Adding floor temp sensor for id {heating_actuator.id}")
            #    wiser_sensors.append(
            #        WiserLTSTempSensor(
            #            data, heating_actuator.id, sensor_type="floor_current_temp"
            #        )
            #    )

    # Add heating channels demand
    #for channel in data.wiserhub.heating_channels.all:
    #    _LOGGER.debug("Setting up Heating Demand LTS sensors")
    #    wiser_sensors.append(WiserLTSDemandSensor(data, channel.id, "heating"))

        # Add hotwater demand
        #if data.wiserhub.hotwater:
            #_LOGGER.debug("Setting up HW sensorr")
            #wiser_sensors.append(WiserLTSDemandSensor(data, 0, "hotwater"))

        # Add opentherm flow & return temps
        #if data.wiserhub.system.opentherm.connection_status == "Connected":
        #    _LOGGER.debug("Setting up Opentherm sensors")
        #    wiser_sensors.extend(
        #        [
        #            WiserLTSOpenthermSensor(data, 0, sensor_type="opentherm_flow_temp"),
        #            WiserLTSOpenthermSensor(
        #                data, 0, sensor_type="opentherm_return_temp"
        #            ),
        #        ]
        #    )

    wiser_sensors.extend(wiser_hub_sensors)
    wiser_sensors.extend(wiser_room_sensors)
    wiser_sensors.extend(wiser_device_sensors)

    async_add_entities(wiser_sensors, True)

class WiserSensor2(CoordinatorEntity, SensorEntity):
    """Class to monitor sensors of a Wiser device"""

    entity_description: WiserSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserSensorEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        super().__init__(coordinator)
        self._data = coordinator
        self._device = device
        self.entity_description = description
        self._attr_unique_id = get_unique_id(self._data, "sensor", description.key, (device.id if isinstance(self._device, _WiserDevice) or isinstance(self._device, _WiserRoom) else 0))
        self._attr_name = description.name

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if isinstance(self._device, _WiserDevice):
            self._device = self._data.wiserhub.devices.get_by_id(self._device.id)
        elif isinstance(self._device, _WiserRoom):
            self._device = self._data.wiserhub.rooms.get_by_id(self._device.id)
        elif self.entity_description.function_key:
            self._device = getattr(self._data.wiserhub, self.entity_description.function_key)
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device.id if isinstance(self._device, _WiserDevice) or isinstance(self._device, _WiserRoom) else 0, self.entity_description.sensor_type),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._device.id if isinstance(self._device, _WiserDevice) or isinstance(self._device, _WiserRoom) else 0, self.entity_description.sensor_type))},
            "manufacturer": MANUFACTURER,
            "model": self._device.product_type if isinstance(self._device, _WiserDevice) else self._data.wiserhub.system.product_type,
            "sw_version": self._device.firmware_version if isinstance(self._device, _WiserDevice) else self._data.wiserhub.system.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def native_value(self) -> float | int | str | None:
        """Return the state of the sensor."""
        return self._get_sensor_state()

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor, if any."""
        if self.entity_description.unit_of_measurement:
            return self.entity_description.unit_of_measurement

        if self._device and self.entity_description.unit_fn is not None:
            return self.entity_description.unit_fn(self._device)
        return super().native_unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self._device and self.entity_description.icon_fn is not None:
            return self.entity_description.icon_fn(self._device)
        return self.entity_description.icon

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        attrs = {}
        if self.entity_description.extra_state_attributes:
            for name, value in self.entity_description.extra_state_attributes.items():
                if isinstance(value, str):
                    attrs[name] = value
                elif isinstance(value, WiserHubAttribute):
                    try:
                        attrs[name] = self.getattrd(self._data.wiserhub, value.path)
                    except AttributeError:
                        continue
                elif isinstance(value, WiserDeviceAttribute):
                    try:
                        attrs[name] = self.getattrd(self._device, value.path)
                    except AttributeError:
                        continue
                elif isinstance(value, Callable):
                    # Get number of params
                    no_of_params = len(signature(value).parameters)
                    try:
                        if no_of_params == 2:
                            attrs[name] = value(self._data, self._device)
                        else:
                            attrs[name] = value(self._device)
                    except AttributeError:
                        continue
        return attrs

    def _get_sensor_state(self):
        """Get current sensor state"""
        if self._device and self.entity_description.value_fn is not None:
            no_of_params = len(signature(self.entity_description.value_fn).parameters)
            if no_of_params == 2:
                    return self.entity_description.value_fn(self._data, self._device)
            return self.entity_description.value_fn(self._device)

        return None

    def getattrd(self, obj, name):
        """Same as getattr(), but allows dot notation lookup"""
        try:
            return reduce(getattr, name.split("."), obj)
        except AttributeError:
            raise


class WiserSensor(CoordinatorEntity, SensorEntity):
    """Definition of a Wiser sensor."""

    def __init__(self, coordinator, device_id=0, sensor_type="") -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._device = None
        self._device_id = device_id
        self._device_name = None
        self._sensor_type = sensor_type
        self._state = None
        self._room = self._data.wiserhub.rooms.get_by_device_id(self._device_id)
        _LOGGER.debug(
            f"{self._data.wiserhub.system.name} {self.name} {'in room ' + self._room.name if self._room else ''} initalise"  # noqa: E501
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} device update requested")

    @property
    def name(self):
        """Return the name of the sensor."""
        return get_device_name(self._data, 0, self._sensor_type)

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
        return self._state

    @property
    def native_value(self):
        """Return the native value of this entity"""
        return self._state

    @property
    def unique_id(self):
        """Return uniqueid."""
        return get_unique_id(self._data, "sensor", self._sensor_type, self._device_id)

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


class WiserBatterySensor(WiserSensor):
    """Definition of a battery sensor for wiser iTRVs and RoomStats."""

    def __init__(self, data, device_id=0, sensor_type="") -> None:
        """Initialise the battery sensor."""
        super().__init__(data, device_id, sensor_type)
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._state = self._device.battery.percent

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._state = self._device.battery.percent
        self.async_write_ha_state()

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._device.battery.voltage is not None

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return SensorDeviceClass.BATTERY

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return PERCENTAGE

    @property
    def extra_state_attributes(self):
        """Return the state attributes of the battery."""
        attrs = {}
        attrs["battery_voltage"] = self._device.battery.voltage
        attrs[ATTR_BATTERY_LEVEL] = self._device.battery.level
        return attrs

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_device_name(self._data, self._device_id)} {self._sensor_type}"

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


class WiserDeviceSignalSensor(WiserSensor):
    """Definition of Wiser Device Sensor."""

    def __init__(self, data, device_id=0, sensor_type="") -> None:
        """Initialise the device sensor."""
        super().__init__(data, device_id, sensor_type)
        if self._device_id == 0:
            self._device = self._data.wiserhub.system
        else:
            self._device = self._data.wiserhub.devices.get_by_id(self._device_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if self._device_id == 0:
            self._device = self._data.wiserhub.system
        else:
            self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._state = self._device.signal.displayed_signal_strength
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        await super().async_update()

    @property
    def native_unit_of_measurement(self):
        """Return the native uom"""
        return None

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._device_id == 0:
            return f"{get_device_name(self._data, self._device_id, 'HeatHub')} Signal"
        return f"{get_device_name(self._data, self._device_id)} Signal"

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
    def icon(self):
        """Return icon for signal strength."""
        try:
            return SIGNAL_STRENGTH_ICONS[self._device.signal.displayed_signal_strength]
        except KeyError:
            # Handle anything else as no signal
            return SIGNAL_STRENGTH_ICONS["NoSignal"]

    @property
    def extra_state_attributes(self):
        """Return device state attributes."""
        attrs = {}

        # Generic attributes
        attrs["vendor"] = MANUFACTURER
        attrs["product_type"] = self._device.product_type
        attrs["model_identifier"] = self._device.model
        attrs["firmware"] = self._device.firmware_version

        # Zigbee Data
        attrs["node_id"] = self._device.node_id
        attrs["zigbee_channel"] = self._data.wiserhub.system.zigbee.network_channel
        attrs[
            "displayed_signal_strength"
        ] = self._device.signal.displayed_signal_strength

        # For non controller device
        if self._device_id != 0:
            attrs["serial_number"] = self._device.serial_number
            attrs["hub_route"] = "direct"

            if self._device.signal.device_reception_rssi is not None:
                attrs[
                    "device_reception_RSSI"
                ] = self._device.signal.device_reception_rssi
                attrs["device_reception_LQI"] = self._device.signal.device_reception_lqi
                attrs[
                    "device_reception_percent"
                ] = self._device.signal.device_signal_strength

            if self._device.signal.controller_reception_rssi is not None:
                attrs[
                    "controller_reception_RSSI"
                ] = self._device.signal.controller_reception_rssi
                attrs[
                    "controller_reception_LQI"
                ] = self._device.signal.controller_reception_lqi
                attrs[
                    "controller_reception_percent"
                ] = self._device.signal.controller_signal_strength

            if self._device.parent_node_id > 0:
                attrs["parent_node_id"] = self._device.parent_node_id
                attrs["hub_route"] = "repeater"
                attrs["repeater"] = (
                    get_device_name(
                        self._data,
                        self._data.wiserhub.devices.get_by_node_id(
                            self._device.parent_node_id
                        ).id,
                    )
                    if self._data.wiserhub.devices.get_by_node_id(
                        self._device.parent_node_id
                    )
                    else "Unknown"
                )
        else:
            # Show Wifi info
            attrs["wifi_strength"] = self._device.signal.controller_reception_rssi
            attrs[
                "wifi_strength_percent"
            ] = self._device.signal.controller_signal_strength
            attrs["wifi_SSID"] = self._device.network.ssid
            attrs["wifi_IP"] = self._device.network.ip_address

            # Show integration and api version info
            attrs["api_version"] = self._data.wiserhub.version
            attrs["integration_version"] = VERSION

            # Show status info if exists
            if self._data.wiserhub.status:
                attrs["uptime"] = self._data.wiserhub.status.uptime
                attrs["last_reset_reason"] = self._data.wiserhub.status.last_reset_reason

        # Other
        if self._sensor_type == "RoomStat":
            attrs["humidity"] = self._data.wiserhub.devices.roomstats.get_by_id(
                self._device_id
            ).current_humidity

        if self._sensor_type in [
            "iTRV",
            "RoomStat",
            "HeatingActuator",
            "UnderFloorHeating",
        ]:
            attrs["temperature"] = self._data.wiserhub.devices.get_by_id(
                self._device_id
            ).current_temperature

        if self._sensor_type == "HeatingActuator":
            attrs["target_temperature"] = self._data.wiserhub.devices.get_by_id(
                self._device_id
            ).current_target_temperature
            attrs["output_type"] = self._data.wiserhub.devices.get_by_id(
                self._device_id
            ).output_type

        return attrs


class WiserSystemHotWaterPreset(WiserSensor):
    """Hotwater preset sensor"""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.hotwater
        mode = "Manual" if self._device.mode != "Auto" else "Auto"
        state = ""
        if self._device.is_boosted:
            state = f"Boost {int(self._device.boost_time_remaining/60)}m"
        elif self._device.is_override:
            state = "Override"
        elif self._device.is_away_mode:
            state = "Away Mode"

        self._state = f"{mode}{' - ' + state if state else ''}"
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        await super().async_update()

    @property
    def icon(self):
        """Return icon."""
        return "mdi:water-boiler"

class WiserSystemCircuitState(WiserSensor):
    """Definition of a Hotwater/Heating circuit state sensor."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if self._sensor_type == "Heating":
            self._device = self._data.wiserhub.heating_channels.get_by_id(
                self._device_id
            )
            self._state = self._device.heating_relay_status
        else:
            self._device = self._data.wiserhub.hotwater
            self._state = self._device.current_state
        self.async_write_ha_state()

    @property
    def icon(self):
        """Return icon."""
        if self._sensor_type == "Heating":
            if self._state == "Off":
                return "mdi:radiator-disabled"
            return "mdi:radiator"

        # Hot water circuit
        if self._state == "Off":
            return "mdi:fire-off"
        return "mdi:fire"

    @property
    def extra_state_attributes(self):
        """Return additional info."""
        attrs = {}
        if self._sensor_type == "Heating":
            heating_channel = self._data.wiserhub.heating_channels.get_by_id(
                self._device_id
            )
            attrs[
                f"percentage_demand_{heating_channel.name}"
            ] = heating_channel.percentage_demand
            attrs[f"room_ids_{heating_channel.name}"] = heating_channel.room_ids
            attrs[
                f"is_smartvalve_preventing_demand_{heating_channel.name}"
            ] = heating_channel.is_smart_valve_preventing_demand
            if self._data.wiserhub.system.opentherm.connection_status == "Connected":
                opentherm = self._data.wiserhub.system.opentherm.operational_data
                attrs["ch_flow_temperature"] = opentherm.ch_flow_temperature
                attrs["ch_pressure_bar"] = opentherm.ch_pressure_bar
                attrs["ch_return_temperature"] = opentherm.ch_return_temperature
                attrs["relative_modulation_level"] = opentherm.relative_modulation_level
                attrs["hw_temperature"] = opentherm.hw_temperature
        else:
            hw = self._data.wiserhub.hotwater
            # If boosted show boost end time
            if hw.is_boosted:
                attrs["boost_end"] = hw.boost_end_time
            attrs["boost_time_remaining"] = int(hw.boost_time_remaining / 60)
            attrs["away_mode_supressed"] = hw.away_mode_suppressed
            attrs["is_away_mode"] = hw.is_away_mode
            attrs["is_boosted"] = hw.is_boosted
            attrs["is_override"] = hw.is_override

            if hw.schedule:
                attrs["schedule_id"] = hw.schedule.id
                attrs["schedule_name"] = hw.schedule.name
                attrs["next_day_change"] = str(hw.schedule.next.day)
                attrs["next_schedule_change"] = str(hw.schedule.next.time)
                attrs["next_schedule_datetime"] = str(hw.schedule.next.datetime)
                attrs["next_schedule_state"] = hw.schedule.next.setting
        return attrs


class WiserSystemCloudSensor(WiserSensor):
    """Sensor to display the status of the Wiser Cloud."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._state = self._data.wiserhub.system.cloud.connection_status
        self.async_write_ha_state()

    @property
    def icon(self):
        """Return icon."""
        if self._state == "Connected":
            return "mdi:cloud-check"
        return "mdi:cloud-alert"


class WiserSystemOperationModeSensor(WiserSensor):
    """Sensor for the Wiser Operation Mode (Away/Normal etc)."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._state = self.mode
        self.async_write_ha_state()

    @property
    def mode(self):
        """Return mode."""
        return (
            "Away Mode" if self._data.wiserhub.system.is_away_mode_enabled else "Normal"
        )

    @property
    def icon(self):
        """Return icon."""
        return "mdi:check" if self.mode == "Normal" else "mdi:alert"

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}
        attrs["last_updated"] = self._data.last_update_time
        attrs["minutes_since_last_update"] = int(
            (datetime.now() - self._data.last_update_time).total_seconds() / 60
        )
        attrs["last_update_status"] = self._data.last_update_status
        return attrs


class WiserCurrentVoltageSensor(WiserSensor):
    """Sensor for voltage of equipment devices"""
    def __init__(self, data, device_id, sensor_type="") -> None:
        super().__init__(data, device_id, sensor_type)
        self._device = data.wiserhub.devices.get_by_id(device_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)

    @property
    def device_class(self):
        """Return sensor device class"""
        if self._sensor_type == "voltage":
            return SensorDeviceClass.VOLTAGE
        if self._sensor_type == "current":
            return SensorDeviceClass.CURRENT

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_device_name(self._data, self._device_id)} {self._sensor_type}"

    @property
    def icon(self):
        """Return icon."""
        return "mdi:lightning-bolt-circle"

    @property
    def state(self) -> float:
        """Return the state of the entity."""
        if self._sensor_type == "Voltage":
            return self._device.equipment.power.rms_voltage
        if self._sensor_type == "Current":
            return self._device.equipment.power.rms_current

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit this state is expressed in."""
        if self._sensor_type == "Voltage":
            return UnitOfElectricPotential.VOLT
        if self._sensor_type == "Current":
            return UnitOfElectricCurrent.AMPERE

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


class WiserSmartplugPower(WiserSensor):
    """Sensor for the power of a Wiser SmartPlug."""

    def __init__(self, data, device_id, sensor_type="") -> None:
        """Initialise the operation mode sensor."""
        super().__init__(data, device_id, sensor_type)
        self._device = data.wiserhub.devices.smartplugs.get_by_id(device_id)
        self._last_delivered_power = 0

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.smartplugs.get_by_id(self._device_id)
        if self._sensor_type == "Power":
            self._state = self._device.instantaneous_power
        else:
            # Fix for api/hub returning 0 value in some situations causing issues with energy
            # monitoring showing high usage
            # Issue 223
            if self._device.delivered_power > -1:
                self._state = round(self._device.delivered_power / 1000, 2)
                self._last_delivered_power = round(
                    self._device.delivered_power / 1000, 2
                )

            else:
                self._state = self._last_delivered_power
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_device_name(self._data, self._device_id)} {self._sensor_type}"

    @property
    def icon(self):
        """Return icon."""
        return "mdi:lightning-bolt-circle"

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
    def device_class(self):
        if self._sensor_type == "Power":
            return SensorDeviceClass.POWER
        return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        if self._sensor_type == "Power":
            return SensorStateClass.MEASUREMENT
        return SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float:
        """Return the state of the entity."""
        return self._state

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit this state is expressed in."""
        if self._sensor_type == "Power":
            return UnitOfPower.WATT
        return UnitOfEnergy.KILO_WATT_HOUR


class WiserLTSTempSensor(WiserSensor):
    """Sensor for long term stats for room temp and target temp"""

    def __init__(self, data, device_id, sensor_type="") -> None:
        """Initialise the operation mode sensor."""
        self._lts_sensor_type = sensor_type
        if sensor_type == "current_temp":
            super().__init__(
                data,
                device_id,
                f"LTS Temperature {data.wiserhub.rooms.get_by_id(device_id).name}",
            )
        elif sensor_type == "floor_current_temp":
            sensor_name = (
                data.wiserhub.rooms.get_by_id(
                    data.wiserhub.devices.get_by_id(device_id).room_id
                ).name
                if data.wiserhub.devices.get_by_id(device_id).room_id
                else data.wiserhub.devices.get_by_id(device_id).name
            )
            super().__init__(
                data,
                device_id,
                f"LTS Floor Temperature {sensor_name}",
            )
        else:
            super().__init__(
                data,
                device_id,
                f"LTS Target Temperature {data.wiserhub.rooms.get_by_id(device_id).name}",
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if self._lts_sensor_type == "current_temp":
            self._state = self._data.wiserhub.rooms.get_by_id(
                self._device_id
            ).current_temperature
        elif self._lts_sensor_type == "floor_current_temp":
            self._state = self._data.wiserhub.devices.get_by_id(
                self._device_id
            ).floor_temperature_sensor.measured_temperature
        else:
            if (
                self._data.wiserhub.rooms.get_by_id(self._device_id).mode == "Off"
                or self._data.wiserhub.rooms.get_by_id(
                    self._device_id
                ).current_target_temperature
                == TEMP_OFF
            ):
                self._state = "Off"
            else:
                self._state = self._data.wiserhub.rooms.get_by_id(
                    self._device_id
                ).current_target_temperature
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device specific attributes."""
        if self._lts_sensor_type == "floor_current_temp":
            return {
                "name": get_device_name(self._data, self._device_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }
        return {
            "name": get_device_name(self._data, self._device_id, "room"),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(self._data, self._device_id, "room"),
                )
            },
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def icon(self):
        """Return icon for sensor"""
        if self._lts_sensor_type == "hotwater":
            return "mdi:water-boiler"
        if self._lts_sensor_type == "current_temp":
            return "mdi:home-thermometer"
        return "mdi:home-thermometer-outline"

    @property
    def device_class(self):
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the entity."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        if self._state == "Off":
            return None
        return UnitOfTemperature.CELSIUS


class WiserLTSOpenthermSensor(WiserSensor):
    """Sensor for long term stats for room temp and target temp"""

    def __init__(self, data, device_id, sensor_type="") -> None:
        """Initialise the operation mode sensor."""
        self._lts_sensor_type = sensor_type
        if sensor_type == "opentherm_flow_temp":
            super().__init__(data, device_id, "LTS Boiler Flow Temperature")
        elif sensor_type == "opentherm_return_temp":
            super().__init__(data, device_id, "LTS Boiler Return Temperature")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if self._lts_sensor_type == "opentherm_flow_temp":
            self._state = (
                self._data.wiserhub.system.opentherm.operational_data.ch_flow_temperature
            )
        elif self._lts_sensor_type == "opentherm_return_temp":
            self._state = (
                self._data.wiserhub.system.opentherm.operational_data.ch_return_temperature
            )
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device_id),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(self._data, self._device_id),
                )
            },
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def extra_state_attributes(self):
        """Return additional info."""
        attrs = {}
        if self._lts_sensor_type == "opentherm_flow_temp":
            opentherm = self._data.wiserhub.system.opentherm
            attrs[
                "ch_flow_active_lower_setpoint"
            ] = opentherm.ch_flow_active_lower_setpoint
            attrs[
                "ch_flow_active_upper_setpoint"
            ] = opentherm.ch_flow_active_upper_setpoint
            attrs["ch1_flow_enabled"] = opentherm.ch1_flow_enabled
            attrs["ch1_flow_setpoint"] = opentherm.ch1_flow_setpoint
            attrs["ch2_flow_enabled"] = opentherm.ch2_flow_enabled
            attrs["ch2_flow_setpoint"] = opentherm.ch2_flow_setpoint
            attrs["connection_status"] = opentherm.connection_status
            attrs["hw_enabled"] = opentherm.hw_enabled
            attrs["hw_flow_setpoint"] = opentherm.hw_flow_setpoint
            attrs["operating_mode"] = opentherm.operating_mode
            attrs["tracked_room_id"] = opentherm.tracked_room_id
            attrs["room_setpoint"] = opentherm.room_setpoint
            attrs["room_temperature"] = opentherm.room_temperature

            operational_data = opentherm.operational_data
            attrs["ch_flow_temperature"] = operational_data.ch_flow_temperature
            attrs["ch_pressure_bar"] = operational_data.ch_pressure_bar
            attrs["ch_return_temperature"] = operational_data.ch_return_temperature
            attrs[
                "relative_modulation_level"
            ] = operational_data.relative_modulation_level
            attrs["hw_temperature"] = operational_data.hw_temperature
            attrs["hw_flow_rate"] = operational_data.hw_flow_rate
            attrs["slave_status"] = operational_data.slave_status

            boiler_params = opentherm.boiler_parameters
            attrs[
                "boiler_ch_max_setpoint_read_write"
            ] = boiler_params.ch_max_setpoint_read_write
            attrs[
                "boiler_ch_max_setpoint_transfer_enable"
            ] = boiler_params.ch_max_setpoint_transfer_enable
            attrs["boiler_ch_setpoint"] = boiler_params.ch_setpoint
            attrs[
                "boiler_ch_setpoint_lower_bound"
            ] = boiler_params.ch_setpoint_lower_bound
            attrs[
                "boiler_ch_setpoint_upper_bound"
            ] = boiler_params.ch_setpoint_upper_bound
            attrs[
                "boiler_hw_setpoint_read_write"
            ] = boiler_params.hw_setpoint_read_write
            attrs[
                "boiler_hw_setpoint_transfer_enable"
            ] = boiler_params.hw_setpoint_transfer_enable
            attrs["boiler_hw_setpoint"] = boiler_params.hw_setpoint
            attrs[
                "boiler_hw_setpoint_lower_bound"
            ] = boiler_params.hw_setpoint_lower_bound
            attrs[
                "boiler_hw_setpoint_upper_bound"
            ] = boiler_params.hw_setpoint_upper_bound
        return attrs

    @property
    def icon(self):
        """Return icon for sensor"""
        return "mdi:thermometer-water"

    @property
    def device_class(self):
        return SensorDeviceClass.TEMPERATURE

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the entity."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        if self._state == "Off":
            return None
        return UnitOfTemperature.CELSIUS


class WiserLTSHumiditySensor(WiserSensor):
    """Sensor for long term stats for room temp and target temp"""

    def __init__(self, data, device_id) -> None:
        """Initialise the LTS Humidity."""
        super().__init__(
            data,
            device_id,
            f"LTS Humidity {data.wiserhub.rooms.get_by_id(data.wiserhub.devices.get_by_id(device_id).room_id).name}",
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._state = self._data.wiserhub.devices.get_by_id(
            self._device_id
        ).current_humidity
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(
                self._data,
                self._data.wiserhub.devices.get_by_id(self._device_id).room_id,
                "room",
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data,
                        self._data.wiserhub.devices.get_by_id(self._device_id).room_id,
                        "room",
                    ),
                )
            },
            "manufacturer": MANUFACTURER,
            "model": "Room",
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def icon(self):
        """Return icon for sensor"""
        return "mdi:water-percent"

    @property
    def device_class(self):
        return SensorDeviceClass.HUMIDITY

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the entity."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        return "%"


class WiserLTSDemandSensor(WiserSensor):
    """Sensor for long term stats for room temp and target temp"""

    def __init__(self, data, device_id, sensor_type="") -> None:
        """Initialise the operation mode sensor."""
        self._lts_sensor_type = sensor_type
        if self._lts_sensor_type == "heating":
            super().__init__(data, device_id, f"LTS Heating Demand Channel {device_id}")
        elif self._lts_sensor_type == "hotwater":
            super().__init__(data, device_id, "LTS Hot Water Demand")
        else:
            # Assume room demand
            super().__init__(
                data,
                device_id,
                f"LTS Heating Demand {data.wiserhub.rooms.get_by_id(device_id).name}",
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if self._lts_sensor_type == "heating":
            self._state = self._data.wiserhub.heating_channels.get_by_id(
                self._device_id
            ).percentage_demand
        elif self._lts_sensor_type == "hotwater":
            self._state = 100 if self._data.wiserhub.hotwater.is_heating else 0
        else:
            # Assume room demand
            self._state = self._data.wiserhub.rooms.get_by_id(
                self._device_id
            ).percentage_demand
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device specific attributes."""
        if self._lts_sensor_type in ["heating", "hotwater"]:
            return super().device_info
        else:
            return {
                "name": get_device_name(self._data, self._device_id, "room"),
                "identifiers": {
                    (DOMAIN, get_identifier(self._data, self._device_id, "room"))
                },
                "manufacturer": MANUFACTURER,
                "model": "Room",
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def icon(self):
        """Return icon for sensor"""
        if self._lts_sensor_type == "hotwater":
            return "mdi:water-boiler"
        return "mdi:radiator"

    @property
    def device_class(self):
        return SensorDeviceClass.POWER_FACTOR

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

    @property
    def native_value(self):
        """Return the state of the entity."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        return PERCENTAGE


