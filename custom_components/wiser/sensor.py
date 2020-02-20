"""
Sensor Platform Device for Wiser System


https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
import asyncio
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    ATTR_BATTERY_LEVEL,
    CONF_ENTITY_NAMESPACE,
    STATE_UNKNOWN,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.icon import icon_for_battery_level

from .const import _LOGGER, BATTERY_FULL, DOMAIN, SIGNAL_STRENGTH_ICONS


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Setup the sensor platform."""
    data = hass.data[DOMAIN]  # Get Handler
    wiser_devices = []

    # Add device sensors
    for device in data.wiserhub.getDevices():
        wiser_devices.append(
            WiserDeviceSensor(data, device.get("id"), device.get("ProductType"))
        )

    # Add cloud status sensor
    wiser_devices.append(WiserSystemCloudSensor(data, sensorType="Cloud Sensor"))
    # Add operation sensor
    wiser_devices.append(
        WiserSystemOperationModeSensor(data, sensorType="Operation Mode")
    )
    # Add heating circuit sensor
    wiser_devices.append(WiserSystemCircuitState(data, sensorType="HEATING"))
    # Dont display Hotwater if hotwater not supported
    # https://github.com/asantaga/wiserHomeAssistantPlatform/issues/8
    if data.wiserhub.getHotwater() is not None:
        wiser_devices.append(WiserSystemCircuitState(data, sensorType="HOTWATER"))

    async_add_entities(wiser_devices, True)


class WiserSensor(Entity):
    """Definition of a Wiser sensor"""

    def __init__(self, data, device_id=0, sensorType=""):
        """Initialize the sensor."""
        self.data = data
        self.deviceId = device_id
        self.sensor_type = sensorType
        self._state = None

    async def async_update(self):
        _LOGGER.debug("{} device update requested".format(self.device_name))
        await self.data.async_update()

    @property
    def name(self):
        """Return the name of the sensor"""
        return self.device_name

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("{} device state requested".format(self.name))
        return self._state


class WiserDeviceSensor(WiserSensor):
    """Definition of Wiser Device Sensor"""

    def __init__(self, data, device_id=0, sensorType=""):
        super().__init__(data, device_id, sensorType)
        self.device_name = self.get_device_name()
        _LOGGER.info("{} device init".format(self.device_name))

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._state = self.data.wiserhub.getDevice(self.deviceId).get(
            "DisplayedSignalStrength"
        )

    def get_device_name(self):
        """Return the name of the Device"""
        product_type = str(
            self.data.wiserhub.getDevice(self.deviceId).get("ProductType") or ""
        )

        if product_type == "Controller":
            return "Wiser Heathub"  # Only ever one of these
        elif product_type == "iTRV":
            # Multiple ones get automagically number _n by HA
            return (
                "Wiser "
                + product_type
                + "-"
                + self.data.wiserhub.getDeviceRoom(self.deviceId)["roomName"]
            )
        elif product_type == "RoomStat":
            # Usually only one per room
            return (
                "Wiser "
                + product_type
                + "-"
                + self.data.wiserhub.getDeviceRoom(self.deviceId)["roomName"]
            )
        else:
            return (
                "Wiser "
                + product_type
                + "-"
                + str(
                    self.data.wiserhub.getDevice(self.deviceId).get("SerialNumber")
                    or ""
                )
            )

    @property
    def icon(self):
        """Return icon for signal strength"""
        try:
            return SIGNAL_STRENGTH_ICONS[
                self.data.wiserhub.getDevice(self.deviceId).get(
                    "DisplayedSignalStrength"
                )
            ]
        except KeyError as ex:
            # Handle anything else as no signal
            return SIGNAL_STRENGTH_ICONS["NoSignal"]

    @property
    def device_state_attributes(self):
        _LOGGER.debug(
            "State attributes for {} {}".format(self.deviceId, self.sensor_type)
        )
        attrs = {}
        device_data = self.data.wiserhub.getDevice(self.deviceId)

        """ Generic attributes """
        attrs["vendor"] = "Drayton Wiser"
        attrs["product_type"] = device_data.get("ProductType")
        attrs["model_identifier"] = device_data.get("ModelIdentifier")
        attrs["device_lock_enabled"] = device_data.get("DeviceLockEnabled")
        attrs["displayed_signal_strength"] = device_data.get("DisplayedSignalStrength")
        attrs["firmware"] = device_data.get("ActiveFirmwareVersion")
        attrs["serial_number"] = device_data.get("SerialNumber")

        """ if controller then add the zigbee data to the controller info """
        if device_data.get("ProductType")=="Controller":
            attrs["zigbee_channel"] = self.data.wiserhub.getHubData().get("Zigbee").get("NetworkChannel")



        """ Network Data"""
        attrs["node_id"] = device_data.get("NodeId")
        attrs["displayed_signal_strength"] = device_data.get("DisplayedSignalStrength")

        if self.sensor_type in ["RoomStat", "iTRV"]:
            attrs["parent_node_id"] = device_data.get("ParentNodeId")
            """ hub route"""
            if device_data.get("ParentNodeId")==0:

                attrs["hub_route"] = "direct"
            else:
                attrs["hub_route"] = "repeater"


        if device_data.get("ReceptionOfDevice") is not None:
            attrs["device_reception_RSSI"] = device_data.get("ReceptionOfDevice").get(
                "Rssi"
            )
            attrs["device_reception_LQI"] = device_data.get("ReceptionOfDevice").get(
                "Lqi"
            )

        if device_data.get("ReceptionOfController") is not None:
            attrs["controller_reception_RSSI"] = device_data.get(
                "ReceptionOfController"
            ).get("Rssi")
            attrs["device_reception_LQI"] = device_data.get(
                "ReceptionOfController"
            ).get("Lqi")

        """ Battery Data """
        if self.sensor_type in ["RoomStat", "iTRV", "SmartPlug"] and device_data.get(
            "BatteryVoltage"
        ):
            attrs["battery_voltage"] = device_data.get("BatteryVoltage")
            attrs["battery_percent"] = int(
                device_data.get("BatteryVoltage") / BATTERY_FULL * 100
            )
            attrs["battery_level"] = device_data.get("BatteryLevel")
            attrs["serial_number"] = device_data.get("SerialNumber")

        """ Other """
        if self.sensor_type == "RoomStat":
            attrs["humidity"] = self.data.wiserhub.getRoomStatData(self.deviceId).get(
                "MeasuredHumidity"
            )


        return attrs


class WiserSystemCircuitState(WiserSensor):
    """Definition of a Hotwater/Heating circuit state sensor"""

    def __init__(self, data, device_id=0, sensorType=""):
        super().__init__(data, device_id, sensorType)
        self.device_name = self.get_device_name()
        _LOGGER.info("{} device init".format(self.device_name))

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        if self.sensor_type == "HEATING":
            self._state = self.data.wiserhub.getHeatingRelayStatus()
        else:
            self._state = self.data.wiserhub.getHotwaterRelayStatus()

    def get_device_name(self):
        """Return the name of the Device """
        if self.sensor_type == "HEATING":
            return "Wiser Heating"
        else:
            return "Wiser Hot Water"

    @property
    def icon(self):
        if self.sensor_type == "HEATING":
            if self._state == "Off":
                return "mdi:radiator-disabled"
            else:
                return "mdi:radiator"
        else:
            # Hot water circuit
            if self._state == "Off":
                return "mdi:water-off"
            else:
                return "mdi:water"

    @property
    def device_state_attributes(self):
        """ returns additional info"""
        attrs = {}
        if self.sensor_type == "HEATING":
            heating_channels = self.data.wiserhub.getHeatingChannels()
            for heatingChannel in heating_channels:
                channel_name = heatingChannel.get("Name")
                channel_pct_dmd = heatingChannel.get("PercentageDemand")
                channel_room_ids = heatingChannel.get("RoomIds")
                attr_name = "percentage_demand_{}".format(channel_name)
                attrs[attr_name] = channel_pct_dmd
                attr_name_2 = "room_ids_{}".format(channel_name)
                attrs[attr_name_2] = channel_room_ids
        return attrs


class WiserSystemCloudSensor(WiserSensor):
    """Sensor to display the status of the Wiser Cloud"""

    def __init__(self, data, device_id=0, sensorType=""):
        super().__init__(data, device_id, sensorType)
        self.device_name = self.get_device_name()
        _LOGGER.info("{} device init".format(self.device_name))

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._state = self.data.wiserhub.getSystem().get("CloudConnectionStatus")

    def get_device_name(self):
        """Return the name of the Device """
        return "Wiser Cloud Status"

    @property
    def icon(self):
        if self._state == "Connected":
            return "mdi:cloud-check"
        else:
            return "mdi:cloud-alert"


class WiserSystemOperationModeSensor(WiserSensor):
    """Sensor for the Wiser Operation Mode (Away/Normal etc)"""

    def __init__(self, data, device_id=0, sensorType=""):
        super().__init__(data, device_id, sensorType)
        self.device_name = self.get_device_name()
        self.override_type = self.data.wiserhub.getSystem().get("OverrideType")
        self.away_temperature = self.data.wiserhub.getSystem().get(
            "AwayModeSetPointLimit"
        )
        _LOGGER.info("{} device init".format(self.device_name))

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self.override_type = self.data.wiserhub.getSystem().get("OverrideType")
        self.away_temperature = self.data.wiserhub.getSystem().get(
            "AwayModeSetPointLimit"
        )
        self._state = self.mode()

    def mode(self):
        if self.override_type and self.override_type == "Away":
            return "Away"
        else:
            return "Normal"

    def get_device_name(self):
        """Return the name of the Device """
        return "Wiser Operation Mode"

    @property
    def icon(self):
        if self.mode() == "Normal":
            return "mdi:check"
        else:
            return "mdi:alert"

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {"AwayModeTemperature": -1.0}
        if self.away_temperature:
            try:
                attrs["AwayModeTemperature"] = round(self.away_temperature / 10.0, 1)
            except Exception as ex:
                _LOGGER.debug(
                    "Exception" + " : Unexpected value for awayTemperature",
                    self.away_temperature,
                )
        return attrs
