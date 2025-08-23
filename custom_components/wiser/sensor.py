"""
Sensor Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""

from datetime import datetime
import logging

from aioWiserHeatAPI.const import TEXT_UNKNOWN

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
    SensorEntity,
)
from homeassistant.const import (
    ATTR_BATTERY_LEVEL,
    LIGHT_LUX,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
    UnitOfTemperature,
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    PERCENTAGE,
    UnitOfPower,
    UnitOfEnergy,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from aioWiserHeatAPI.wiserhub import TEMP_OFF

from .const import (
    DATA,
    DOMAIN,
    HOT_WATER,
    MANUFACTURER,
    MANUFACTURER_SCHNEIDER,
    SIGNAL_STRENGTH_ICONS,
    VERSION,
)
from .helpers import get_device_name, get_unique_id, get_identifier, get_room_name, get_equipment_name, get_equipment_identifier

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_sensors = []

    # Add signal sensors for all devices
    _LOGGER.debug("Setting up Device sensors")

    # Add hub wifi signal sensor
    wiser_sensors.append(WiserDeviceSignalSensor(data, 0, "Controller"))
    if data.wiserhub.devices:
        for device in data.wiserhub.devices.all:
            wiser_sensors.append(
                WiserDeviceSignalSensor(data, device.id, device.product_type)
            )
            if hasattr(device, "battery"):
                wiser_sensors.append(
                    WiserBatterySensor(data, device.id, sensor_type="Battery")
                )

            # Add threshold temp sensors
            if hasattr(device, "threshold_sensors"):
                for threshold_sensor in getattr(device, "threshold_sensors"):
                    if threshold_sensor.quantity == "Temperature":
                        wiser_sensors.append(
                            WiserThresholdTempSensor(
                                data, device.id, "threshold_temp", threshold_sensor.id
                            )
                        )
                    elif threshold_sensor.quantity == "Humidity":
                        wiser_sensors.append(
                            WiserThresholdHumiditySensor(
                                data,
                                device.id,
                                "threshold_humidity",
                                threshold_sensor.id,
                            )
                        )
                    elif threshold_sensor.quantity == "LightLevel":
                        wiser_sensors.append(
                            WiserThresholdLightLevelSensor(
                                data,
                                device.id,
                                "threshold_lightlevel",
                                threshold_sensor.id,
                            )
                        )

    # Add cloud status sensor
    _LOGGER.debug("Setting up Cloud sensor")
    wiser_sensors.append(WiserSystemCloudSensor(data, sensor_type="Cloud"))

    # Add pairing status sensor LGO
    _LOGGER.debug("Setting up pairing sensor")
    wiser_sensors.append(WiserSystemPairingSensor(data, sensor_type="Pairing Status"))

    # Add operation sensor
    _LOGGER.debug("Setting up Heating Operation Mode sensor")
    wiser_sensors.append(
        WiserSystemOperationModeSensor(data, sensor_type="Heating Operation Mode")
    )

    # Add heating circuit sensor
    if data.wiserhub.heating_channels:
        _LOGGER.debug("Setting up Heating Circuit sensors")
        for heating_channel in data.wiserhub.heating_channels.all:
            wiser_sensors.append(
                WiserSystemCircuitState(data, heating_channel.id, sensor_type="Heating")
            )

    # Add hot water sensors if supported on hub
    if data.wiserhub.hotwater:
        _LOGGER.debug("Setting up Hot Water sensors")
        wiser_sensors.extend(
            [
                WiserSystemCircuitState(data, sensor_type="Hot Water"),
                WiserSystemHotWaterPreset(data, sensor_type="Hot Water Operation Mode"),
            ]
        )

    # Add power sensors for smartplugs
    if data.wiserhub.devices.smartplugs:
        _LOGGER.debug("Setting up Smart Plug power sensors")
        for smartplug in data.wiserhub.devices.smartplugs.all:
        # Add a sensor equipment for smartplugs 
        # Hub V2 features   
            if smartplug.equipment_id > 0:
                wiser_sensors.extend(
                [
                    WiserLTSPowerSensor(data, smartplug.id, sensor_type="Power", name="Equipment Power"),
                    WiserLTSPowerSensor(data, smartplug.id, sensor_type="Energy", name="Equipment Energy Delivered"),
                    WiserLTSPowerSensor(data, smartplug.id, sensor_type="Energy", name="Equipment Total Energy"),
                    WiserCurrentVoltageSensor(data, smartplug.id, sensor_type="Current"),
                    # to preserve the backward compatility
                    WiserSmartplugPower(data, smartplug.id, sensor_type="Power"),
                    WiserSmartplugPower(data, smartplug.id, sensor_type="Total Power"),                    
                     
                ]
                )
            else:
        # Hub V1 features
                wiser_sensors.extend(
                [
                    WiserSmartplugPower(data, smartplug.id, sensor_type="Power"),
                    WiserSmartplugPower(data, smartplug.id, sensor_type="Total Power"),                    
                ]
                )

    # Add power sensors for PTE (v2Hub)
    if data.wiserhub.devices.power_tags:
        _LOGGER.debug("Setting up Power Tag power sensors")
        for power_tag in data.wiserhub.devices.power_tags.all:
            wiser_sensors.extend(
                [
                    WiserLTSPowerSensor(
                        data, power_tag.id, sensor_type="Power", name="Power"
                    ),
                    WiserLTSPowerSensor(
                        data,
                        power_tag.id,
                        sensor_type="Energy",
                        name="Energy Delivered",
                    ),
                    WiserLTSPowerSensor(
                        data,
                        power_tag.id,
                        sensor_type="EnergyReceived",
                        name="Energy Received",
                    ),
                    WiserCurrentVoltageSensor(
                        data, power_tag.id, sensor_type="Voltage"
                    ),
                    WiserCurrentVoltageSensor(
                        data, power_tag.id, sensor_type="Current"
                    ),
                    WiserLTSPowerSensor(
                        data,
                        power_tag.id,
                        sensor_type="Energy",
                        name="Total Energy"),
                ]        
            )

    # Add LTS sensors - for room temp and target temp
    _LOGGER.debug("Setting up LTS sensors")
    for room in data.wiserhub.rooms.all:
        if room.devices:
            wiser_sensors.extend(
                [
                    WiserLTSTempSensor(data, room.id, sensor_type="current_temp"),
                    WiserLTSTempSensor(
                        data, room.id, sensor_type="current_target_temp"
                    ),
                    WiserLTSDemandSensor(data, room.id, "room"),
                ]
            )

            if room.roomstat_id:
                wiser_sensors.append(WiserLTSHumiditySensor(data, room.roomstat_id))

    # Add temp sensors for smoke alarms
    _LOGGER.debug("Setting up smoke alarms sensors")
    wiser_sensors.extend(
        WiserLTSTempSensor(
            data,
            device.id,
            sensor_type="smokealarm_temp",
        )
        for device in data.wiserhub.devices.smokealarms.all
    )

    # Add LTS sensors - for room Power and Energy for heating actuators
    if data.wiserhub.devices.heating_actuators:
        _LOGGER.debug("Setting up Heating Actuator LTS sensors")
        for heating_actuator in data.wiserhub.devices.heating_actuators.all:
        # Add a sensor equipment for heating actuators
        # Hub V2 features
            if heating_actuator.equipment_id > 0:
                wiser_sensors.extend(
                [
                    WiserLTSPowerSensor(data, heating_actuator.id, sensor_type="Power", name="Equipment Power"),
                    WiserLTSPowerSensor(data, heating_actuator.id, sensor_type="Energy", name="Equipment Energy Delivered"),
                    WiserLTSPowerSensor(data, heating_actuator.id, sensor_type="Energy", name="Equipment Total Energy"),
                    # to preserve the backward compatility
                    WiserLTSPowerSensor(data, heating_actuator.id, sensor_type="Power"),
                    WiserLTSPowerSensor(data, heating_actuator.id, sensor_type="Energy"),
                ]
            )
            else:
        # Hub V1 features        
                wiser_sensors.extend(
                [
                    WiserLTSPowerSensor(data, heating_actuator.id, sensor_type="Power"),
                    WiserLTSPowerSensor(
                        data, heating_actuator.id, sensor_type="Energy"
                    ),
                ]
            )  
        # Add a sensor floor temperature                             

            if (
                heating_actuator.floor_temperature_sensor
                and heating_actuator.floor_temperature_sensor.sensor_type
                != "Not_Fitted"
            ):
                _LOGGER.debug(f"Adding floor temp sensor for id {heating_actuator.id}")
                wiser_sensors.append(
                    WiserLTSTempSensor(
                        data, heating_actuator.id, sensor_type="floor_current_temp"
                    )
                )

        # Add heating channels demand
        for channel in data.wiserhub.heating_channels.all:
            _LOGGER.debug("Setting up Heating Demand LTS sensors")
            wiser_sensors.append(WiserLTSDemandSensor(data, channel.id, "heating"))

        # Add hotwater demand
        if data.wiserhub.hotwater:
            _LOGGER.debug("Setting up HW sensorr")
            wiser_sensors.append(WiserLTSDemandSensor(data, 0, "hotwater"))

        # Add opentherm flow & return temps
        if (
            data.wiserhub.system.opentherm.connection_status == "Connected"
            and data.wiserhub.system.opentherm.enabled
        ):
            _LOGGER.debug("Setting up Opentherm sensors")
            wiser_sensors.extend(
                [
                    WiserLTSOpenthermSensor(data, 0, sensor_type="opentherm_flow_temp"),
                    WiserLTSOpenthermSensor(data, 0, sensor_type="opentherm_return_temp"),
                ]
            )

        # Add LTS Weather sensors
        if data.wiserhub.system.weather.temperature is not None:
            _LOGGER.debug("Setting up Weather sensors")
            wiser_sensors.extend(
                [
                    WiserLTSWeatherSensor(data, 0,sensor_type="temperature"),
                #    WiserLTSWeatherSensor(data, 0,  sensor_type="next_day_2pm_temperature"),   
                ]
            )
       
        # Add Equipment sensors
        if data.wiserhub.equipments:
            _LOGGER.debug(f"Wiserhub Equipment Collection NB {data.wiserhub.equipments.count} ")
            for equipment in data.wiserhub.equipments.all:
                if equipment.name :
                    wiser_sensors.append( WiserEquipmentSensor(data, equipment.id,equipment.name) )                           
                
    async_add_entities(wiser_sensors, True)


class WiserSensor(CoordinatorEntity, SensorEntity):
    """Definition of a Wiser sensor."""

    def __init__(
        self, coordinator, device_id=0, sensor_type="", ancillary_sensor_id: int = 0
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._device = None
        self._device_id = device_id
        self._ancillary_sensor_id = ancillary_sensor_id
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
        self._state = self._get_battery_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._state = self._get_battery_state()
        self.async_write_ha_state()

    def _get_battery_state(self) -> int | str:
        # TODO: Move this into api
        if self._device.battery.percent:
            return self._device.battery.percent
        if self._device.battery.voltage is None:
            # This device does not provide battery voltage.  Calc % from level text
            levels = {"normal": 100, "twothirds": 66, "onethird": 33, "low": 10}
            return levels.get(self._device.battery.level.lower(), 0)
        return 0

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return self._device.battery.level != TEXT_UNKNOWN

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return SensorDeviceClass.BATTERY

    @property
    def state_class(self):
        return SensorStateClass.MEASUREMENT

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
        self._state = self._device.signal.displayed_signal_strength

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
        attrs["displayed_signal_strength"] = (
            self._device.signal.displayed_signal_strength
        )
        attrs["uuid"] = self._device.uuid
        attrs["type"] = self._device.type_comm

        # For non controller device
        if self._device_id != 0:
            attrs["product_model"] = self._device.product_model
            attrs["product_identifier"] = self._device.product_identifier
            attrs["serial_number"] = self._device.serial_number
            attrs["hub_route"] = "direct"

            if self._device.signal.device_reception_rssi is not None:
                attrs["device_reception_RSSI"] = (
                    self._device.signal.device_reception_rssi
                )
                attrs["device_reception_LQI"] = self._device.signal.device_reception_lqi
                attrs["device_reception_percent"] = (
                    self._device.signal.device_signal_strength
                )

            if self._device.signal.controller_reception_rssi is not None:
                attrs["controller_reception_RSSI"] = (
                    self._device.signal.controller_reception_rssi
                )
                attrs["controller_reception_LQI"] = (
                    self._device.signal.controller_reception_lqi
                )
                attrs["controller_reception_percent"] = (
                    self._device.signal.controller_signal_strength
                )

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
            attrs["wifi_strength_percent"] = (
                self._device.signal.controller_signal_strength
            )
            attrs["wifi_SSID"] = self._device.network.ssid
            attrs["wifi_IP"] = self._device.network.ip_address

            # Show integration and api version info
            attrs["api_version"] = self._data.wiserhub.version
            attrs["integration_version"] = VERSION

            # Show status info if exists
            if self._data.wiserhub.status:
                attrs["uptime"] = self._data.wiserhub.status.uptime
                attrs["last_reset_reason"] = (
                    self._data.wiserhub.status.last_reset_reason
                )

            attrs["hardware_generation"] = self._data.hub_version

            # Hub V2 features

            # summer comfort
            if self._data.hub_version == 2:
                attrs["seasonal_comfort_enabled"] = self._device.seasonal_comfort_enabled
                attrs["summer_comfort_enabled"] = self._device.summer_comfort_enabled
                attrs["indoor_discomfort_temperature"] = (
                    self._device.indoor_discomfort_temperature
                )
                attrs["outdoor_discomfort_temperature"] = (
                    self._device.outdoor_discomfort_temperature
                )
                attrs["summer_comfort_available"] = (
                    self._device.summer_comfort_available
                )
                attrs["summer_discomfort_prevention"] = (
                    self._device.summer_discomfort_prevention
                )
                attrs["pcm_version"] = self._device.pcm_version
                attrs["pcm_status"] = self._device.pcm_status
                attrs["pcm_device_limit_reached"] = (
                    self._device.pcm_device_limit_reached
                )
                attrs["can_activate_pcm"] = self._device.can_activate_pcm

                attrs["weather_temperature"] = self._data.wiserhub.system.weather.temperature
                attrs["next_day_2pm_temperature"] = self._data.wiserhub.system.weather.next_day_2pm_temperature


        # Other
        device = self._data.wiserhub.devices.get_by_id(self._device_id)

        if device and device.id != 0:
            attrs["device_id"] = device.id

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

        if self._sensor_type == "SmokeAlarmDevice":
            attrs["led_brightness"] = self._device.led_brightness
            attrs["alarm_sound_mode"] = self._device.alarm_sound_mode
            attrs["alarm_sound_level"] = self._device.alarm_sound_level
            attrs["life_time"] = self._device.life_time
            attrs["hush_duration"] = self._device.hush_duration

            attrs["device_type_id"] = self._device.device_type_id
            attrs["id"] = self._device.id
            attrs["smokealarm_id"] = self._device.id
            attrs["report_count"] = self._device.report_count

        if self._sensor_type == "WindowDoorSensor":
            attrs["name"] = self._device.name
            attrs["active"] = self._device.active
            attrs["type"] = self._device.type
            attrs["sensorstatus"] = self._device.sensorstatus
            attrs["enable_notification"] = self._device.enable_notification
            attrs["interacts_with_room_climate"] = (
                self._device.interacts_with_room_climate
            )
            attrs["device_type_id"] = self._device.device_type_id
            attrs["id"] = self._device.id

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
            state = f"Boost {int(self._device.boost_time_remaining / 60)}m"
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

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(
                self._data, self._data.wiserhub.hotwater.id, "Hot Water"
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data, self._data.wiserhub.hotwater.id, "hot_water"
                    ),
                )
            },
            "manufacturer": MANUFACTURER,
            "model": HOT_WATER.title(),
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


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
            self._state = (
                self._device.heating_relay_status
                if self._device.heating_relay_status != TEXT_UNKNOWN
                else self._device.demand_on_off_output
            )
        else:
            self._device = self._data.wiserhub.hotwater
            self._state = self._device.current_state
        self.async_write_ha_state()

    @property
    def name(self):
        """Return name of sensor."""
        if (
            self._sensor_type == "Heating"
            and len(self._data.wiserhub.heating_channels.all) > 1
        ):
            return get_device_name(
                self._data, 0, self._sensor_type + " Channel " + str(self._device_id)
            )
        return get_device_name(self._data, 0, self._sensor_type)

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
            attrs[f"percentage_demand_{heating_channel.name}"] = (
                heating_channel.percentage_demand
            )
            attrs[f"room_ids_{heating_channel.name}"] = heating_channel.room_ids
            attrs[f"is_smartvalve_preventing_demand_{heating_channel.name}"] = (
                heating_channel.is_smart_valve_preventing_demand
            )
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

    @property
    def device_info(self):
        """Return device specific attributes."""
        if self._sensor_type == "Heating":
            return super().device_info
        return {
            "name": get_device_name(
                self._data, self._data.wiserhub.hotwater.id, "Hot Water"
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data, self._data.wiserhub.hotwater.id, "hot_water"
                    ),
                )
            },
            "manufacturer": MANUFACTURER,
            "model": HOT_WATER.title(),
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


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

#add LGO 
class WiserSystemPairingSensor(WiserSensor):
    """Sensor to display the pairing status of the Wiser Hub."""

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._state = self._data.wiserhub.system.pairing_status
        self.async_write_ha_state()

    @property
    def icon(self):
        """Return icon."""
        if self._state == "Paired":
            return "mdi:cloud-check"
        return "mdi:cloud-alert"

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attrs = {}
        attrs["latitude"] = self._data.wiserhub.system.geo_position.latitude
        attrs["longitude"] = self._data.wiserhub.system.geo_position.longitude
        return attrs
   
# end add LGO

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
        self.async_write_ha_state()

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
            if self._device.delivered_power is not None:
                self._state = round(self._device.delivered_power / 1000, 2)
                self._last_delivered_power = round(
                    self._device.delivered_power / 1000, 2
                )

            else:
                self._state = self._last_delivered_power or STATE_UNKNOWN
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

    def __init__(
        self, data, device_id, sensor_type="", ancillary_sensor_id: int = 0
    ) -> None:
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
        elif sensor_type == "smokealarm_temp":
            device = data.wiserhub.devices.get_by_id(device_id)
            if device.room_id and (
                room := data.wiserhub.rooms.get_by_id(device.room_id)
            ):
                name = f"{room.name} {device.name}  Temperature"
            else:
                name = f"{device.name} {device_id} Temperature"
            super().__init__(
                data,
                device_id,
                name,
            )
        elif sensor_type == "threshold_temp":
            super().__init__(data, device_id, "Temperature", ancillary_sensor_id)
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
        elif self._lts_sensor_type == "smokealarm_temp":
            self._state = self._data.wiserhub.devices.get_by_id(
                self._device_id
            ).current_temperature
        elif self._lts_sensor_type == "threshold_temp":
            for th_sensor in self._data.wiserhub.devices.get_by_id(
                self._device_id
            ).threshold_sensors:
                if th_sensor.id == self._ancillary_sensor_id:
                    self._state = th_sensor.current_value
        else:
            if (
                self._data.wiserhub.rooms.get_by_id(self._device_id).mode == "Off"
                or self._data.wiserhub.rooms.get_by_id(
                    self._device_id
                ).current_target_temperature
                == TEMP_OFF
            ):
                self._state = STATE_UNAVAILABLE
            else:
                self._state = self._data.wiserhub.rooms.get_by_id(
                    self._device_id
                ).current_target_temperature
        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device specific attributes."""
        if self._lts_sensor_type in [
            "floor_current_temp",
            "smokealarm_temp",
            "threshold_temp",
        ]:
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
            self._state = self._data.wiserhub.system.opentherm.operational_data.ch_flow_temperature
        elif self._lts_sensor_type == "opentherm_return_temp":
            self._state = self._data.wiserhub.system.opentherm.operational_data.ch_return_temperature
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
            attrs["ch_flow_active_lower_setpoint"] = (
                opentherm.ch_flow_active_lower_setpoint
            )
            attrs["ch_flow_active_upper_setpoint"] = (
                opentherm.ch_flow_active_upper_setpoint
            )
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
            attrs["relative_modulation_level"] = (
                operational_data.relative_modulation_level
            )
            attrs["hw_temperature"] = operational_data.hw_temperature
            attrs["hw_flow_rate"] = operational_data.hw_flow_rate
            attrs["slave_status"] = operational_data.slave_status

            boiler_params = opentherm.boiler_parameters
            attrs["boiler_ch_max_setpoint_read_write"] = (
                boiler_params.ch_max_setpoint_read_write
            )
            attrs["boiler_ch_max_setpoint_transfer_enable"] = (
                boiler_params.ch_max_setpoint_transfer_enable
            )
            attrs["boiler_ch_setpoint"] = boiler_params.ch_setpoint
            attrs["boiler_ch_setpoint_lower_bound"] = (
                boiler_params.ch_setpoint_lower_bound
            )
            attrs["boiler_ch_setpoint_upper_bound"] = (
                boiler_params.ch_setpoint_upper_bound
            )
            attrs["boiler_hw_setpoint_read_write"] = (
                boiler_params.hw_setpoint_read_write
            )
            attrs["boiler_hw_setpoint_transfer_enable"] = (
                boiler_params.hw_setpoint_transfer_enable
            )
            attrs["boiler_hw_setpoint"] = boiler_params.hw_setpoint
            attrs["boiler_hw_setpoint_lower_bound"] = (
                boiler_params.hw_setpoint_lower_bound
            )
            attrs["boiler_hw_setpoint_upper_bound"] = (
                boiler_params.hw_setpoint_upper_bound
            )
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

    def __init__(
        self, data, device_id, sensor_type="", ancillary_sensor_id: int = 0
    ) -> None:
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

        # Set humidity to unavailable if no value
        if self._state == 0:
            self._state = STATE_UNAVAILABLE

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
        if self._lts_sensor_type == "heating":
            return super().device_info
        if self._lts_sensor_type == "hotwater":
            return {
                "name": get_device_name(
                    self._data, self._data.wiserhub.hotwater.id, "Hot Water"
                ),
                "identifiers": {
                    (
                        DOMAIN,
                        get_identifier(
                            self._data, self._data.wiserhub.hotwater.id, "hot_water"
                        ),
                    )
                },
                "manufacturer": MANUFACTURER,
                "model": HOT_WATER.title(),
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

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


class WiserLTSPowerSensor(WiserSensor):
    """Sensor for long term stats for heating actuators power and energy"""

    def __init__(self, data, device_id, sensor_type="", name="") -> None:
        """Initialise the operation mode sensor."""
        self._device_id = device_id
        self._lts_sensor_type = sensor_type
        self._device = data.wiserhub.devices.get_by_id(device_id)
        self._sensor_name = name
        if self._device.room_id == 0:
            device_name = self._device.product_type + " " + str(self._device.id)
        else:
            device_name = data.wiserhub.rooms.get_by_id(self._device.room_id).name

        if name:
            super().__init__(data, device_id, f"{name.title()} ")
        elif sensor_type == "Power":
            super().__init__(
                data,
                device_id,
                f"LTS Power {device_name}",
            )
        else:
            super().__init__(
                data,
                device_id,
                f"LTS Energy {device_name}",
            )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if self._lts_sensor_type == "Power":
            if (
                self._data.wiserhub.devices.get_by_id(
                    self._device_id
                ).instantaneous_power
                is not None
            ):
                self._state = self._data.wiserhub.devices.get_by_id(
                    self._device_id
                ).instantaneous_power
            else:
                self._state = STATE_UNKNOWN
        elif self._lts_sensor_type == "Energy":
            if (
                self._data.wiserhub.devices.get_by_id(self._device_id).delivered_power
                is not None
            ):
                self._state = round(
                    self._data.wiserhub.devices.get_by_id(
                        self._device_id
                    ).delivered_power
                    / 1000,
                    2,
                )
            else:
                self._state = STATE_UNKNOWN
        elif self._lts_sensor_type == "EnergyReceived":
            if (
                self._data.wiserhub.devices.get_by_id(self._device_id).received_power
                is not None
            ):
                self._state = round(
                    self._data.wiserhub.devices.get_by_id(
                        self._device_id
                    ).received_power
                    / 1000,
                    2,
                )
            else:
                self._state = STATE_UNKNOWN
        self.async_write_ha_state()

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._sensor_name:
            return f"{get_device_name(self._data, self._device_id)} {self._sensor_name}"
        else:
            return get_device_name(self._data, 0, self._sensor_type)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(
                self._data,
                self._device_id,
                "device",
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data,
                        self._device_id,
                        "device",
                    ),
                )
            },
            "manufacturer": MANUFACTURER,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def icon(self):
        """Return icon for sensor"""
        if self._lts_sensor_type == "Power":
            return (
                "mdi:home-lightning-bolt"
                # if self._data.wiserhub.devices.get_by_id(
                #    self._device_id
                # ).instantaneous_power
                # > 0
                # else "mdi:home-lightning-bolt-outline"
            )
        if self._lts_sensor_type == "Energy":
            return "mdi:home-lightning-bolt"
        return "mdi:home-lightning-bolt-outline"

    @property
    def device_class(self):
        if self._lts_sensor_type == "Power":
            return SensorDeviceClass.POWER
        else:
            return SensorDeviceClass.ENERGY

    @property
    def state_class(self):
        if self._lts_sensor_type == "Power":
            return SensorStateClass.MEASUREMENT
        else:
            return SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self) -> float:
        """Return the state of the entity."""
        return self._state

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit this state is expressed in."""
        if self._lts_sensor_type == "Power":
            return UnitOfPower.WATT
        else:
            return UnitOfEnergy.KILO_WATT_HOUR


class WiserThresholdSensor(WiserSensor):
    """Sensor for threshold devices."""

    def __init__(
        self, data, device_id, sensor_type="", ancillary_sensor_id: int = 0
    ) -> None:
        super().__init__(data, device_id, sensor_type, ancillary_sensor_id)
        self._device = data.wiserhub.devices.get_by_id(device_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self.async_write_ha_state()

    @property
    def state(self) -> float:
        """Return the state of the entity."""
        for th_sensor in self._data.wiserhub.devices.get_by_id(
            self._device_id
        ).threshold_sensors:
            if th_sensor.id == self._ancillary_sensor_id:
                return th_sensor.current_value
        return TEXT_UNKNOWN

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
    # added by LGO
    @property
    def extra_state_attributes(self):
        """Return device threshold extra attributes."""
        attrs = {} 

        for th_sensor in self._data.wiserhub.devices.get_by_id(
            self._device_id
        ).threshold_sensors:
            if th_sensor.id == self._ancillary_sensor_id:
                attrs["uuid"] = th_sensor.UUID
                attrs["quantity"] = th_sensor.quantity
                attrs["current_level"] = th_sensor.current_level
                attrs["high_threshold"] = th_sensor.high_threshold
                attrs["medium_level"] = th_sensor.medium_threshold
                attrs["low_level"] = th_sensor.low_threshold
                attrs["interacts_with_room_climate"] = th_sensor.interacts_with_room_climate
    
        return attrs

class WiserThresholdLightLevelSensor(WiserThresholdSensor):
    """Sensor for light level of threshold devices."""

    @property
    def device_class(self):
        """Return sensor device class."""
        return SensorDeviceClass.ILLUMINANCE

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_device_name(self._data, self._device_id)} Light Level"

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit this state is expressed in."""
        return LIGHT_LUX


class WiserThresholdTempSensor(WiserThresholdSensor):
    """Sensor for temp of threshold devices."""

    @property
    def device_class(self):
        """Return sensor device class."""
        return SensorDeviceClass.TEMPERATURE

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_device_name(self._data, self._device_id)} Temperature"

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit this state is expressed in."""
        return UnitOfTemperature.CELSIUS


class WiserThresholdHumiditySensor(WiserThresholdSensor):
    """Sensor for humidity level of threshold devices."""

    @property
    def device_class(self):
        """Return sensor device class."""
        return SensorDeviceClass.HUMIDITY

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_device_name(self._data, self._device_id)} Humidity"

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit this state is expressed in."""
        return PERCENTAGE


class WiserLTSWeatherSensor(WiserSensor):
    """Sensor for long term stats for weather temperature and Next days 2PM temperature"""

    def __init__(self, data, device_id, sensor_type="") -> None:
        """Initialise the operation mode sensor."""
        self._lts_sensor_type = sensor_type
        if sensor_type == "temperature":
            super().__init__(data, device_id, "LTS Weather Temperature")
        elif sensor_type == "next_day_2pm_temperature":
            super().__init__(data, device_id, "LTS Weather Next Day 2PM Temperature")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if self._lts_sensor_type == "temperature":
            self._state = self._data.wiserhub.system.weather.temperature
        elif self._lts_sensor_type == "next_day_2pm_temperature":
            self._state = self._data.wiserhub.system.weather.next_day_2pm_temperature
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
        if self._lts_sensor_type == "weather":
            weather = self._data.wiserhub.system.weather
            attrs["next_day_2PM_temperature"] = (
                self._data.wiserhub.system.weather.next_day_2pm_temperature
            )

        return attrs

    @property
    def icon(self):
        """Return icon for sensor"""
        return "mdi:thermometer-water"

    @property
    def device_class(self):
        return SensorDeviceClass.TEMPERATURE

    @property
    def native_value(self):
        """Return the state of the entity."""
        return self._state

    @property
    def native_unit_of_measurement(self):
        if self._state == "Off":
            return None
        return UnitOfTemperature.CELSIUS

class WiserEquipmentSensor(WiserSensor):
    """Definition of Wiser Equipment Sensor."""

    def __init__(self, data, equipment_id=0, sensor_type="") -> None:
        """Initialise the device sensor."""
        self._equipment_id = equipment_id
        self._sensor_type = sensor_type
        super().__init__(data, equipment_id, sensor_type)
        if self._equipment_id == 0:
            self._equipment = self._data.wiserhub.system
        else:
            self._equipment = self._data.wiserhub.equipments.get_equip_by_id(self._equipment_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if self._equipment_id == 0:
            self._equipment = self._data.wiserhub.system
        else:
            self._equipment = self._data.wiserhub.equipments.get_equip_by_id(self._equipment_id)
        self._state = self._equipment.equipment.power.total_active_power
        self.async_write_ha_state()

    async def async_update(self) -> None:
        """Fetch new state data for the sensor."""
        await super().async_update()

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_equipment_name(self._data, self._equipment_id)} Equipment"
        
        
    @property
    def icon(self):
        """Return icon."""
        return "mdi:home-lightning-bolt"

    @property
    def state(self) -> float:
        """Return the state of the entity."""
        return self._equipment.equipment.power.total_active_power

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit this state is expressed in."""
        return UnitOfPower.WATT
        
    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._equipment.equipment.device_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._equipment.equipment.device_id))},
            "manufacturer": MANUFACTURER_SCHNEIDER,
    #            "model": self._device.product_type,
    #            "sw_version": self._device.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }
    @property
    def extra_state_attributes(self):
        """Return device state attributes."""
        attrs = {} 
        # dev = self._equipment.equipment to facilitate the grasping of objects
        dev = self._equipment.equipment
 
        # Device identification
        attrs["name"] = self._equipment.name
        attrs["device_type"] = dev.device_type
        attrs["device_application_instance_id"] = self._equipment.device_application_instance_id
       
        attrs["family"] = dev.equipment_family
        attrs["installation_type"] = dev.installation_type
        attrs["number_of_phases"] = dev.number_of_phases        
        attrs["direction"] = dev.direction

        attrs["application_instance_type"] = self._equipment.device_application_instance_type
        attrs["equipment_id"] = dev.id
        attrs["equipment_device_id"] = dev.device_id

        attrs["equipment_UUID"] = dev.uuid
        if dev.device_type not in ["PTE","PowerTagE",]:
            attrs["functional_control_mode"] = dev.functional_control_mode
        #  SmartPlug attributes
        if dev.device_type in ["SmartPlug"]:
            attrs["functional_control_mode"] = dev.functional_control_mode      
    
        attrs["current_control_mode"] = dev.current_control_mode

        # equipment capabilities
        attrs["controllable"] = dev.controllable        
        attrs["cloud_managed"] = dev.cloud_managed        
        attrs["monitored"] = dev.monitored        
        attrs["smart_compatible"] = dev.smart_compatible
        attrs["smart_supported"] = dev.smart_supported
        attrs["can_be_scheduled"] = dev.can_be_scheduled        
        attrs["onoff_green_schedule_supported"] = dev.onoff_green_schedule_supported
        attrs["onoff_cost_schedule_supported"] = dev.onoff_cost_schedule_supported        

        

        #PCM
        if dev.device_type not in ["PTE","PowerTagE",]:
            attrs["pcm_mode"] = dev.pcm_mode
            attrs["pcm_supported"] = dev.pcm_supported
            attrs["pcm_priority"] = dev.pcm_priority
        

        # Equipment status
        attrs["operating_status"] = dev.operating_status
        attrs["fault_status"] = dev.fault_status
        
        #Load  and shedding
        if dev.device_type not in ["PTE","PowerTagE",]:
            attrs["load_state_status"] = dev.load_state_status
            attrs["load_state_command_optimized"] = dev.load_state_command_optimized
            attrs["load_shedding_status"] = dev.load_shedding_status
            attrs["load_state_command_prio"] = dev.load_state_command_prio
            attrs["load_setpoint_command_prio"] = dev.load_setpoint_command_prio
        #Measures
        attrs["active_power"] = dev.power.active_power    
        attrs["total_active_power"] = dev.power.total_active_power    
        attrs["energy"] = round(
            dev.power.current_summation_delivered / 1000,
            2,
        )

        # PowerTagE and SmartPlug attributes
        if dev.device_type in ["PTE","PowerTagE","SmartPlug"]:
            attrs["energy_delivered"] = dev.power.current_summation_delivered      
            attrs["pcm_mode"] = dev.pcm_mode

        # PowerTagE attributes
        if dev.device_type in ["PTE","PowerTagE",]:
            attrs["rms_current"] = self._equipment.power.rms_current    
            attrs["rms_voltage"] = self._equipment.power.rms_voltage    
            attrs["energy_received"] = self._equipment.power.current_summation_received  

            attrs["grid_limit"] = self._equipment.grid_limit
            attrs["grid_limit_Uom"] = self._equipment.grid_limit_uom
            attrs["energy_export"] = self._equipment.energy_export
            attrs["self_consumption"] = self._equipment.self_consumption

        return attrs        

