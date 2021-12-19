"""
Sensor Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
from datetime import datetime
import logging
from homeassistant.components.sensor import SensorDeviceClass, SensorStateClass
from homeassistant.const import ATTR_BATTERY_LEVEL, DEVICE_CLASS_BATTERY, DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS, DEVICE_CLASS_POWER_FACTOR, PERCENTAGE
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity
from homeassistant.helpers import config_validation as cv, entity_platform, service
import voluptuous as vol

from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
    SIGNAL_STRENGTH_ICONS,
)
from .helpers import get_device_name, get_room_name, get_unique_id, get_identifier

_LOGGER = logging.getLogger(__name__)

CONF_HUB_ID = "wiser_hub_id"
SERVICE_REMOVE_ORPHANED_ENTRIES = "remove_orphaned_entries"
SELECT_HUB_SCHEMA = vol.All(vol.Schema({vol.Optional(CONF_HUB_ID): str}))



async def async_setup_entry(hass, config_entry, async_add_entities):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_sensors = []

    hub_devices = data.wiserhub.devices.all

    # Add signal sensors for all devices
    _LOGGER.debug("Setting up Device sensors")
    if data.wiserhub.devices:
        for device in data.wiserhub.devices.all:
            wiser_sensors.append(
                WiserDeviceSignalSensor(data, device.id, device.product_type)
            )
            if hasattr(device, "battery"):
                wiser_sensors.append(
                        WiserBatterySensor(data, device.id, sensor_type = "Battery")
                )
    
    # Add cloud status sensor
    _LOGGER.debug("Setting up Cloud sensor")
    wiser_sensors.append(WiserSystemCloudSensor(data, sensor_type = "Cloud"))

    # Add operation sensor
    _LOGGER.debug("Setting up Heating Operation Mode sensor")
    wiser_sensors.append(
        WiserSystemOperationModeSensor(data, sensor_type = "Heating Operation Mode")
    )

    # Add heating circuit sensor
    if data.wiserhub.heating_channels:
        _LOGGER.debug("Setting up Heating Circuit sensors")
        for heating_channel in data.wiserhub.heating_channels.all:
                wiser_sensors.append(
                    WiserSystemCircuitState(data, heating_channel.id, sensor_type = "Heating")
                )
    
    # Add hot water sensors if supported on hub
    if data.wiserhub.hotwater:
        _LOGGER.debug("Setting up Hot Water sensors")
        wiser_sensors.extend([
            WiserSystemCircuitState(data, sensor_type = "Hot Water"),
            WiserSystemHotWaterPreset(data, sensor_type= "Hot Water Operation Mode")

        ])


    # Add LTS sensors - for room temp and target temp
    if data.enable_lts_sensors:
        _LOGGER.debug("Setting up LTS sensors")
        for temp_device in data.wiserhub.rooms.all:
            wiser_sensors.extend([
                WiserLTSTempSensor(data, temp_device.id, sensor_type = "current_temp"),
                WiserLTSTempSensor(data, temp_device.id, sensor_type = "current_target_temp"),
                WiserLTSDemandSensor(data, temp_device.id, "room")
            ])

        # Add heating channels demand
        for channel in data.wiserhub.heating_channels.all:
            wiser_sensors.append(
                WiserLTSDemandSensor(data, channel.id, "heating")
            )
        
        #Add hotwater demand
        if data.wiserhub.hotwater:
            wiser_sensors.append(
                WiserLTSDemandSensor(data, 0, "hotwater")
            )

    async_add_entities(wiser_sensors, True)


class WiserSensor(Entity):
    """Definition of a Wiser sensor."""

    def __init__(self, config_entry, device_id=0, sensor_type=""):
        """Initialize the sensor."""
        self._attr_device_class = SensorDeviceClass.POWER_FACTOR
        self._data = config_entry
        self._device = None
        self._device_id = device_id
        self._device_name = None
        self._sensor_type = sensor_type
        self._state = None
        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initalise")

    async def async_update(self):
        """Async Update."""
        _LOGGER.debug(f"{self._device_name} device update requested")

    @property
    def name(self):
        """Return the name of the sensor."""
        return get_device_name(self._data, 0, self._sensor_type)

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("%s device state requested", self.name)
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
                "model": self._data.wiserhub.system.model,
                "sw_version": self._data.wiserhub.system.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    async def async_added_to_hass(self):
        """Subscribe for update from the hub."""

        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._data.wiserhub.system.name}-HubUpdateMessage", async_update_state
            )
        )


class WiserBatterySensor(WiserSensor):
    """Definition of a battery sensor for wiser iTRVs and RoomStats."""

    def __init__(self, data, device_id=0, sensor_type=""):
        """Initialise the battery sensor."""
        self._attr_device_class = SensorDeviceClass.BATTERY
        super().__init__(data, device_id, sensor_type)
        self._state = "Unknown"
        self._battery_voltage = 0
        self._battery_level = None
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._state = self._device.battery.percent

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return SensorDeviceClass.BATTERY

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return "%"

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
                "model": self._device.model,
                "sw_version": self._device.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }


class WiserDeviceSignalSensor(WiserSensor):
    """Definition of Wiser Device Sensor."""

    def __init__(self, data, device_id=0, sensor_type=""):
        """Initialise the device sensor."""
        super().__init__(data, device_id, sensor_type)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._device = self._data.wiserhub.devices.get_by_id(self._device_id)
        self._state = self._device.signal.displayed_signal_strength

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"{get_device_name(self._data, self._device_id)} Signal"
    
    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._device_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
                "manufacturer": MANUFACTURER,
                "model": self._device.model,
                "sw_version": self._device.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def icon(self):
        """Return icon for signal strength."""
        try:
            return SIGNAL_STRENGTH_ICONS[
                self._data.wiserhub.devices.get_by_id(self._device_id).signal.displayed_signal_strength
            ]
        except KeyError:
            # Handle anything else as no signal
            return SIGNAL_STRENGTH_ICONS["NoSignal"]

    @property
    def extra_state_attributes(self):
        """Return device state attributes."""
        attrs = {}
        device_data = self._data.wiserhub.devices.get_by_id(self._device_id)

        # Generic attributes
        attrs["vendor"] = MANUFACTURER
        attrs["product_type"] = self._device.product_type
        attrs["model_identifier"] = self._device.model
        attrs["displayed_signal_strength"] = self._device.signal.displayed_signal_strength
        attrs["firmware"] = self._device.firmware_version
        attrs["serial_number"] = self._device.serial_number

        # if controller then add the zigbee data to the controller info
        attrs["zigbee_channel"] = (
            self._data.wiserhub.system.zigbee.network_channel
        )
        attrs["last_updated"] = datetime.now()

        # Network Data
        attrs["node_id"] = self._device.node_id
        attrs["displayed_signal_strength"] = self._device.signal.displayed_signal_strength

        if self._sensor_type in ["RoomStat", "iTRV"]:
            attrs["parent_node_id"] = self._device.parent_node_id
            # hub route
            if self._device.parent_node_id == 0:
                attrs["hub_route"] = "direct"
            else:
                attrs["hub_route"] = "repeater"
                attrs["repeater"] = self._data.wiserhub.devices.get_by_node_id(device_data.parent_node_id).name


        if self._device.signal.device_reception_rssi is not None:
            attrs["device_reception_RSSI"] = self._device.signal.device_reception_rssi
            attrs["device_reception_LQI"] = self._device.signal.device_reception_lqi

        if self._device.signal.controller_reception_rssi is not None:
            attrs["controller_reception_RSSI"] = self._device.signal.controller_reception_rssi
            attrs["device_reception_LQI"] = self._device.signal.controller_reception_lqi

        # Other
        if self._sensor_type == "RoomStat":
            attrs["humidity"] = self._data.wiserhub.devices.roomstats.get_by_id(self._device_id).current_humidity
            attrs["temperature"] = self._data.wiserhub.devices.roomstats.get_by_id(self._device_id).current_temperature
        return attrs


class WiserSystemHotWaterPreset(WiserSensor):
    """Hotwater preset sensor"""
    def __init__(self, data, device_id=0, sensor_type=""):
        """Initialise the CircuitState Sensor."""
        super().__init__(data, device_id, sensor_type)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._device = self._data.wiserhub.hotwater
        mode = "Manual" if self._device.mode != "Auto" else "Auto"
        state = ""
        if self._device.is_boosted:
            state = f"Boost {int(self._device.boost_time_remaining/60)}m"
        elif self._device.is_override:
            state = f"Override"
        elif self._device.is_away_mode:
            state = f"Away Mode"

        self._state = f"{mode}{' - ' + state if state else ''}"

    @property
    def icon(self):
        """Return icon."""
        return "mdi:water-boiler"


class WiserSystemCircuitState(WiserSensor):
    """Definition of a Hotwater/Heating circuit state sensor."""

    def __init__(self, data, device_id=0, sensor_type=""):
        """Initialise the CircuitState Sensor."""
        super().__init__(data, device_id, sensor_type)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        if self._sensor_type == "Heating":
            self._device = self._data.wiserhub.heating_channels.get_by_id(self._device_id)
            self._state = self._device.heating_relay_status
        else:
            self._device = self._data.wiserhub.hotwater
            self._state = self._device.current_state

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
            heating_channel = self._data.wiserhub.heating_channels.get_by_id(self._device_id)
            attrs[f"percentage_demand_{heating_channel.name}"] = heating_channel.percentage_demand
            attrs[f"room_ids_{heating_channel.name}"] = heating_channel.room_ids
            attrs[f"is_smartvalve_preventing_demand_{heating_channel.name}"] = heating_channel.is_smart_valve_preventing_demand
        else:
            hw = self._data.wiserhub.hotwater
            # If boosted show boost end time
            if hw.is_boosted:
                attrs["boost_end"] = hw.boost_end_time
            attrs["boost_time_remaining"] = int(hw.boost_time_remaining/60)
            attrs["away_mode_supressed"] = hw.away_mode_suppressed
            attrs["next_schedule_change"] = str(hw.schedule.next.time)
            attrs["next_schedule_state"] = hw.schedule.next.setting
            attrs["is_away_mode"] = hw.is_away_mode
            attrs["is_boosted"] = hw.is_boosted
            attrs["is_override"] = hw.is_override
        return attrs


class WiserSystemCloudSensor(WiserSensor):
    """Sensor to display the status of the Wiser Cloud."""

    def __init__(self, data, device_id=0, sensor_type=""):
        """Initialise the cloud sensor."""
        super().__init__(data, device_id, sensor_type)

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._state = self._data.wiserhub.system.cloud.connection_status
    
    @property
    def icon(self):
        """Return icon."""
        if self._state == "Connected":
            return "mdi:cloud-check"
        return "mdi:cloud-alert"


class WiserSystemOperationModeSensor(WiserSensor):
    """Sensor for the Wiser Operation Mode (Away/Normal etc)."""

    def __init__(self, data, device_id=0, sensor_type=""):
        """Initialise the operation mode sensor."""

        super().__init__(data, device_id, sensor_type)
        self._away_temperature = self._data.wiserhub.system.away_mode_target_temperature

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._away_temperature = self._data.wiserhub.system.away_mode_target_temperature
        self._state = self.mode

    @property
    def mode(self):
        """Return mode."""
        return "Away Mode" if self._data.wiserhub.system.is_away_mode_enabled else "Normal"

    @property
    def icon(self):
        """Return icon."""
        return "mdi:check" if self.mode == "Normal" else "mdi:alert"

    @property
    def extra_state_attributes(self):
        """Return the device state attributes."""
        attrs = {"away_mode_temperature": self._away_temperature}
        return attrs


class WiserLTSTempSensor(WiserSensor):
    """Sensor for long term stats for room temp and target temp"""

    def __init__(self, data, id, sensor_type=""):
        """Initialise the operation mode sensor."""
        self._lts_sensor_type = sensor_type
        if sensor_type == "current_temp":
            super().__init__(data, id, f"LTS Temperature {data.wiserhub.rooms.get_by_id(id).name}")
        else:
            super().__init__(data, id, f"LTS Target Temperature {data.wiserhub.rooms.get_by_id(id).name}")
    
    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        if self._lts_sensor_type == "current_temp":
            self._state = self._data.wiserhub.rooms.get_by_id(self._device_id).current_temperature
        else:
            self._state = self._data.wiserhub.rooms.get_by_id(self._device_id).current_target_temperature

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._device_id,"room"),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id,"room"))},
                "manufacturer": MANUFACTURER,
                "model": "Room",
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
    def unit_of_measurement(self):
        return TEMP_CELSIUS

    @property
    def entity_category(self):
        return 'diagnostic'


class WiserLTSDemandSensor(WiserSensor):
    """Sensor for long term stats for room temp and target temp"""

    def __init__(self, data, id, sensor_type=""):
        """Initialise the operation mode sensor."""
        self._lts_sensor_type = sensor_type
        if self._lts_sensor_type == "heating":
            super().__init__(data, id, f"LTS Heating Demand Channel {id}")
        elif self._lts_sensor_type == "hotwater":
            super().__init__(data, id, f"LTS Hot Water Demand")
        else:
            # Assume room demand
            super().__init__(data, id, f"LTS Heating Demand {data.wiserhub.rooms.get_by_id(id).name}")
    
    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        if self._lts_sensor_type == "heating":
            self._state = self._data.wiserhub.heating_channels.get_by_id(self._device_id).percentage_demand
        elif self._lts_sensor_type == "hotwater":
            self._state = 100 if self._data.wiserhub.hotwater.is_heating else 0
        else:
            # Assume room demand
            self._state = self._data.wiserhub.rooms.get_by_id(self._device_id).percentage_demand

    @property
    def device_info(self):
        """Return device specific attributes."""
        if self._lts_sensor_type in ["heating", "hotwater"]:
            return super().device_info
        else:
            return {
                    "name": get_device_name(self._data, self._device_id,"room"),
                    "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id,"room"))},
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
    def unit_of_measurement(self):
        return PERCENTAGE

    @property
    def entity_category(self):
        return 'diagnostic'
