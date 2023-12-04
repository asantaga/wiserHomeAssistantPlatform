"""Sensor Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from functools import reduce
from inspect import signature
import logging
from typing import Any

from aioWiserHeatAPI.const import TEXT_UNKNOWN
from aioWiserHeatAPI.devices import _WiserDeviceTypeEnum as DeviceType
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    PERCENTAGE,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
    ROOM,
    SIGNAL_STRENGTH_ICONS,
    VERSION,
)
from .helpers import (
    WiserDeviceAttribute,
    WiserHubAttribute,
    get_device_by_node_id,
    get_device_name,
    get_hot_water_operation_mode,
    get_identifier,
    get_unique_id,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class WiserSensorEntityDescription(SensorEntityDescription):
    """A class that describes Wiser sensor entities."""

    sensor_type: str | None = None
    function_key: str | None = None
    icon_fn: Callable[[Any], str] | None = None
    unit_fn: Callable[[Any], str] | None = None
    value_fn: Callable[[Any], float | str] | None = None
    extra_state_attributes: dict[
        str, Callable[[Any], float | str]
    ] | None = None


HUB_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="signal",
        name="Signal",
        sensor_type="device",
        function_key="system",
        icon_fn=lambda x: SIGNAL_STRENGTH_ICONS[
            x.signal.displayed_signal_strength
        ]
        if x.signal.displayed_signal_strength in SIGNAL_STRENGTH_ICONS
        else SIGNAL_STRENGTH_ICONS["NoSignal"],
        value_fn=lambda x: x.signal.displayed_signal_strength,
        extra_state_attributes={
            "vendor": MANUFACTURER,
            "product_type": WiserDeviceAttribute("product_type"),
            "model_identifier": WiserDeviceAttribute("model"),
            "firmware": WiserDeviceAttribute("firmware_version"),
            "node_id": WiserDeviceAttribute("node_id"),
            "zigbee_channel": WiserDeviceAttribute("zigbee.network_channel"),
            "wifi_strength": WiserDeviceAttribute(
                "signal.controller_reception_rssi"
            ),
            "wifi_strength_percent": WiserDeviceAttribute(
                "signal.controller_signal_strength"
            ),
            "wifi_SSID": WiserDeviceAttribute("network.ssid"),
            "wifi_IP": WiserDeviceAttribute("network.ip_address"),
            "api_version": WiserHubAttribute("version"),
            "integration_version": VERSION,
            "uptime": WiserHubAttribute("status.uptime"),
            "last_reset_reason": WiserHubAttribute("status.last_reset_reason"),
        },
    ),
    WiserSensorEntityDescription(
        key="cloud",
        name="Cloud",
        sensor_type="device",
        function_key="system",
        icon_fn=lambda x: "mdi:cloud-check"
        if x.cloud.connection_status == "Connected"
        else "mdi:cloud-alert",
        value_fn=lambda x: x.cloud.connection_status,
    ),
    WiserSensorEntityDescription(
        key="heating_operation_mode",
        name="Heating Operation Mode",
        sensor_type="device",
        function_key="system",
        value_fn=lambda x: "Away Mode" if x.is_away_mode_enabled else "Normal",
    ),
    WiserSensorEntityDescription(
        key="heating_channel_1",
        name="Heating Channel 1",
        sensor_type="device",
        function_key="heating_channels",
        icon_fn=lambda x: "mdi:radiator-disabled"
        if x.get_by_id(1).heating_relay_status == "Off"
        else "mdi:radiator",
        value_fn=lambda x: x.get_by_id(1).heating_relay_status,
        extra_state_attributes={
            "percentage_demand": lambda x: x.get_by_id(1).percentage_demand,
            "room_ids": lambda x: x.get_by_id(1).room_ids,
            "is_smartvalve_preventing_demand": lambda x: x.get_by_id(
                1
            ).is_smart_valve_preventing_demand,
        },
    ),
    WiserSensorEntityDescription(
        key="heating_channel_2",
        name="Heating Channel 2",
        sensor_type="device",
        function_key="heating_channels",
        icon_fn=lambda x: "mdi:radiator-disabled"
        if x.get_by_id(2).heating_relay_status == "Off"
        else "mdi:radiator",
        value_fn=lambda x: x.get_by_id(2).heating_relay_status,
        extra_state_attributes={
            "percentage_demand": lambda x: x.get_by_id(2).percentage_demand,
            "room_ids": lambda x: x.get_by_id(2).room_ids,
            "is_smartvalve_preventing_demand": lambda x: x.get_by_id(
                2
            ).is_smart_valve_preventing_demand,
        },
    ),
    WiserSensorEntityDescription(
        key="hot_water_operation_mode",
        name="Hot Water Operation Mode",
        sensor_type="device",
        function_key="hotwater",
        icon="mdi:water-boiler",
        value_fn=get_hot_water_operation_mode,
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
        value_fn=lambda x: 100 if x.is_heating else 0,
    ),
    WiserSensorEntityDescription(
        key="hot_water_state",
        name="Hot Water",
        sensor_type="device",
        function_key="hotwater",
        icon_fn=lambda x: "mdi:fire"
        if x.current_state == "On"
        else "mdi:fire-off",
        value_fn=lambda x: x.current_state,
        extra_state_attributes={
            "boost_end": WiserDeviceAttribute("boost_end_time"),
            "boost_time_remaining": lambda x: int(x.boost_time_remaining / 60),
            "away_mode_supressed": WiserDeviceAttribute(
                "away_mode_suppressed"
            ),
            "is_away_mode": WiserDeviceAttribute("is_away_mode"),
            "is_boosted": WiserDeviceAttribute("is_boosted"),
            "is_override": WiserDeviceAttribute("hw.is_override"),
            "schedule_id": WiserDeviceAttribute("schedule.id"),
            "schedule_name": WiserDeviceAttribute("schedule.name"),
            "next_day_change": WiserDeviceAttribute("schedule.next.day"),
            "next_schedule_change": WiserDeviceAttribute("schedule.next.time"),
            "next_schedule_datetime": WiserDeviceAttribute(
                "schedule.next.datetime"
            ),
            "next_schedule_state": WiserDeviceAttribute(
                "schedule.next.setting"
            ),
        },
    ),
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
        value_fn=lambda x: x.opentherm.operational_data.ch_flow_temperature,
    ),
    WiserSensorEntityDescription(
        key="opentherm_return_temp",
        name="Return Temperature",
        sensor_type="device",
        function_key="system",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.opentherm.operational_data.ch_return_temperature,
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
            ATTR_BATTERY_LEVEL: WiserDeviceAttribute("battery.level"),
        },
    ),
    WiserSensorEntityDescription(
        key="signal",
        name="Signal",
        sensor_type="device",
        icon_fn=lambda x: SIGNAL_STRENGTH_ICONS[
            x.signal.displayed_signal_strength
        ]
        if x.signal.displayed_signal_strength in SIGNAL_STRENGTH_ICONS
        else SIGNAL_STRENGTH_ICONS["NoSignal"],
        value_fn=lambda x: x.signal.displayed_signal_strength,
        extra_state_attributes={
            "vendor": MANUFACTURER,
            "product_type": WiserDeviceAttribute("product_type"),
            "model_identifier": WiserDeviceAttribute("model"),
            "firmware": WiserDeviceAttribute("firmware_version"),
            "node_id": WiserDeviceAttribute("node_id"),
            "zigbee_channel": WiserDeviceAttribute("zigbee.network_channel"),
            "serial_number": WiserDeviceAttribute("serial_number"),
            "hub_route": lambda x: "Repeater"
            if x.parent_node_id > 0
            else "Direct",
            "device_reception_RSSI": WiserDeviceAttribute(
                "signal.device_reception_rssi"
            ),
            "device_reception_LQI": WiserDeviceAttribute(
                "signal.device_reception_lqi"
            ),
            "device_reception_percent": WiserDeviceAttribute(
                "signal.device_signal_strength"
            ),
            "controller_reception_RSSI": WiserDeviceAttribute(
                "signal.controller_reception_rssi"
            ),
            "controller_reception_LQI": WiserDeviceAttribute(
                "signal.controller_reception_lqi"
            ),
            "controller_reception_percent": WiserDeviceAttribute(
                "signal.controller_signal_strength"
            ),
            "parent_node_id": WiserDeviceAttribute("parent_node_id"),
            "repeater": lambda d, x: get_device_by_node_id(
                d, x.parent_node_id
            ).name,
        },
    ),
)

HEATING_ACTUATOR_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="power",
        name="Current Power",
        sensor_type="device",
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfPower.WATT,
        value_fn=lambda x: x.instantaneous_power,
    ),
    WiserSensorEntityDescription(
        key="energy_delivered",
        name="Energy Delivered",
        sensor_type="device",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power,
    ),
    WiserSensorEntityDescription(
        key="floor_temp",
        name="Floor Temp",
        sensor_type="device",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.floor_temperature_sensor.measured_temperature
        if x.floor_temperature_sensor.sensor_type != "Not_Fitted"
        else x.none,
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
        value_fn=lambda x: x.instantaneous_power,
    ),
    WiserSensorEntityDescription(
        key="pte_energy_received",
        name="Energy Received",
        sensor_type="device",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.received_power,
    ),
    WiserSensorEntityDescription(
        key="pte_energy_delivered",
        name="Energy Delivered",
        sensor_type="device",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power,
    ),
    WiserSensorEntityDescription(
        key="pte_voltage",
        name="Voltage",
        sensor_type="device",
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfElectricPotential.VOLT,
        value_fn=lambda x: x.equipment.power.rms_voltage,
    ),
    WiserSensorEntityDescription(
        key="pte_current",
        name="Current",
        sensor_type="device",
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        value_fn=lambda x: x.equipment.power.rms_current,
    ),
)

SMARTVALVE_SENSORS: tuple[WiserSensorEntityDescription, ...] = (
    WiserSensorEntityDescription(
        key="smartvalve_current_temperature",
        name="Temperature",
        sensor_type="device",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature,
    ),
    WiserSensorEntityDescription(
        key="smartvalve_percentage_demand",
        name="Percentage Demand",
        sensor_type="device",
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.percentage_demand,
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
        value_fn=lambda x: x.current_temperature,
    ),
    WiserSensorEntityDescription(
        key="roomstat_current_humidity",
        name="Humidity",
        sensor_type="device",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.current_humidity,
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
        value_fn=lambda x: x.instantaneous_power,
    ),
    WiserSensorEntityDescription(
        key="smartplug_energy",
        name="Energy",
        sensor_type="device",
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        value_fn=lambda x: x.delivered_power,
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
        value_fn=lambda x: x.percentage_demand,
    ),
    WiserSensorEntityDescription(
        key="room_current_temperature",
        name="Temperature",
        sensor_type="room",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_temperature,
    ),
    WiserSensorEntityDescription(
        key="room_target_temperature",
        name="Target Temperature",
        sensor_type="room",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
        value_fn=lambda x: x.current_target_temperature,
    ),
    WiserSensorEntityDescription(
        key="room_current_humidity",
        name="Humidity",
        sensor_type="room",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
        value_fn=lambda x: x.current_humidity if x.roomstat_id else x.none,
    ),
    WiserSensorEntityDescription(
        key="room_window_state",
        name="Window State",
        sensor_type="room",
        value_fn=lambda x: x.window_state,
    ),
)

HUB_SENSOR_ENTITIES = {"HUB": HUB_SENSORS, "OPENTHERM": OPENTHERM_SENSORS}

DEVICE_SENSOR_ENTITIES = {
    "ALL_DEVICES": ALL_DEVICE_SENSORS,
    DeviceType.HeatingActuator: HEATING_ACTUATOR_SENSORS,
    DeviceType.PowerTagE: POWERTAGE_SENSORS,
    DeviceType.RoomStat: ROOMSTAT_SENSORS,
    DeviceType.SmartPlug: SMARTPLUG_SENSORS,
    DeviceType.iTRV: SMARTVALVE_SENSORS,
}

ROOM_SENSOR_ENTITIES = {"ROOMS": ROOM_SENSORS}


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


async def async_setup_entry(
    hass: HomeAssistant, config_entry, async_add_entities
):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_sensors = []

    # Add signal sensors for all devices
    _LOGGER.debug("Setting up Device sensors")

    # NEW CODE FOR CONFIGERED SENSORS

    # Hub/system sensors
    wiser_sensors.extend(
        [
            WiserSensor(
                data,
                sensor_desc,
                getattr(data.wiserhub, sensor_desc.function_key),
            )
            for device_type, sensor_descs in HUB_SENSOR_ENTITIES.items()
            for sensor_desc in sensor_descs
            if _sensor_exist(
                data.wiserhub,
                getattr(data.wiserhub, sensor_desc.function_key),
                sensor_desc,
            )
        ]
    )

    # Room sensors
    wiser_sensors.extend(
        [
            WiserSensor(data, sensor_desc, room)
            for device_type, sensor_descs in ROOM_SENSOR_ENTITIES.items()
            for sensor_desc in sensor_descs
            for room in data.wiserhub.rooms.all
            if _sensor_exist(data.wiserhub, room, sensor_desc)
            and len(room.devices) > 0
        ]
    )

    # Device sensors
    wiser_sensors.extend(
        [
            WiserSensor(data, sensor_desc, device)
            for device_type, sensor_descs in DEVICE_SENSOR_ENTITIES.items()
            for sensor_desc in sensor_descs
            for device in data.wiserhub.devices.all
            if _sensor_exist(data.wiserhub, device, sensor_desc)
            and (
                device_type == "ALL_DEVICES"
                or device.product_type == device_type.name
            )
        ]
    )

    async_add_entities(wiser_sensors, True)


class WiserSensor(CoordinatorEntity, SensorEntity):
    """Class to monitor sensors of a Wiser device."""

    entity_description: WiserSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserSensorEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        """Init wiser sensor."""
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
                if isinstance(self._device, _WiserDevice | _WiserRoom)
                else 0
            ),
        )
        self._attr_name = description.name

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
                if isinstance(self._device, _WiserDevice | _WiserRoom)
                else 0,
                self.entity_description.sensor_type,
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data,
                        self._device.id
                        if isinstance(self._device, _WiserDevice | _WiserRoom)
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
        """Return extra state attributes for sensor."""
        attrs = {}
        if self.entity_description.extra_state_attributes:
            for (
                name,
                value,
            ) in self.entity_description.extra_state_attributes.items():
                if isinstance(value, str):
                    attrs[name] = value
                elif isinstance(value, WiserHubAttribute):
                    try:
                        attrs[name] = self.getattrd(
                            self._data.wiserhub, value.path
                        )
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
        """Get current sensor state."""
        if self._device and self.entity_description.value_fn is not None:
            no_of_params = len(
                signature(self.entity_description.value_fn).parameters
            )
            if no_of_params == 2:
                return self.entity_description.value_fn(
                    self._data, self._device
                )
            return self.entity_description.value_fn(self._device)

        return None

    def getattrd(self, obj, name):
        """Same as getattr(), but allows dot notation lookup."""  # noqa: D401
        return reduce(getattr, name.split("."), obj)
