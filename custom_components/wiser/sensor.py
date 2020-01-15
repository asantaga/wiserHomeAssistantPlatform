"""
Sensor Platform Device for Wiser System


https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""

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

_LOGGER = logging.getLogger(__name__)
DOMAIN = "wiser"
BATTERY_FULL = 31


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    handler = hass.data[DOMAIN]  # Get Handler
    hub_data = handler.get_hub_data()
    handler.update()
    wiser_devices = []
    # Process  general devices
    for device in handler.get_hub_data().getDevices():
        wiser_devices.append(
            WiserDevice(device.get("id"), handler, device.get("ProductType"))
        )

    wiser_devices.append(WiserSystemCircuitState(handler, "HEATING"))
    # Dont display Hotwater if hotwater not supported
    # https://github.com/asantaga/wiserHomeAssistantPlatform/issues/8
    if hub_data.getHotwater() is not None:
        wiser_devices.append(WiserSystemCircuitState(handler, "HOTWATER"))
    wiser_devices.append(WiserSystemCloudSensor(handler))
    wiser_devices.append(WiserSystemOperationModeSensor(handler))
    add_devices(wiser_devices)


""" 
Definition of Wiser Device
"""


class WiserDevice(Entity):
    def __init__(self, device_id, handler, sensor_type):

        """Initialize the sensor."""
        _LOGGER.info("Wiser Device Init")
        self.handler = handler
        self.deviceId = device_id
        self.sensorType = sensor_type

    def update(self):
        _LOGGER.debug("**********************************")
        _LOGGER.debug("Wiser Device Update requested")
        _LOGGER.debug("**********************************")
        self.handler.update()

    @property
    def icon(self):
        icon_list = {
            "Poor": "mdi:wifi-strength-1",
            "Medium": "mdi:wifi-strength-2",
            "Good": "mdi:wifi-strength-3",
            "VeryGood": "mdi:wifi-strength-4",
        }
        try:
            return icon_list[
                self.handler.get_hub_data()
                .getDevice(self.deviceId)
                .get("DisplayedSignalStrength")
            ]
        except KeyError as ex:
            # Handle anything else as no signal
            return "mdi:wifi-strength-alert-outline"

    @property
    def name(self):
        # Return the name of the Device
        product_type = str(
            self.handler.get_hub_data()
            .getDevice(self.deviceId)
            .get("ProductType")
            or ""
        )
        if product_type == "Controller":
            return "Wiser Heathub"  # Only ever one of these
        elif product_type == "iTRV":
            # Multiple ones get automagically number _n by HA
            return (
                "Wiser "
                + product_type
                + "-"
                + self.handler.get_hub_data().getDeviceRoom(self.deviceId)[
                    "roomName"
                ]
            )

        elif product_type == "RoomStat":
            # Usually only one per room
            return (
                "Wiser "
                + product_type
                + "-"
                + self.handler.get_hub_data().getDeviceRoom(self.deviceId)[
                    "roomName"
                ]
            )
        else:
            return (
                "Wiser "
                + product_type
                + "-"
                + str(
                    self.handler.get_hub_data()
                    .getDevice(self.deviceId)
                    .get("SerialNumber")
                    or ""
                )
            )

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    # Assumption 31 = 100% battery

    @property
    def battery_level(self):
        return (
            self.handler.get_hub_data()
            .getDevice(self.deviceId)
            .get("BatteryVoltage")
            / BATTERY_FULL
            * 100
        )

    @property
    def device_state_attributes(self):
        _LOGGER.debug(
            "State attributes for {} {}".format(self.deviceId, self.sensorType)
        )

        attrs = {}
        device_data = self.handler.get_hub_data().getDevice(self.deviceId)
        # Generic attributes
        attrs["vendor"] = "Drayton Wiser"
        attrs["product_type"] = device_data.get("ProductType")
        attrs["model_identifier"] = device_data.get("ModelIdentifier")
        attrs["device_lock_enabled"] = device_data.get("DeviceLockEnabled")
        attrs["displayed_signal_strength"] = device_data.get(
            "DisplayedSignalStrength"
        )
        attrs["firmware"] = device_data.get("ActiveFirmwareVersion")

        if device_data.get("ReceptionOfDevice") is not None:
            attrs["device_reception_RSSI"] = device_data.get(
                "ReceptionOfDevice"
            ).get("Rssi")
            attrs["device_reception_LQI"] = device_data.get(
                "ReceptionOfDevice"
            ).get("Lqi")

        if device_data.get("ReceptionOfController") is not None:
            attrs["controller_reception_RSSI"] = device_data.get(
                "ReceptionOfController"
            ).get("Rssi")
            attrs["device_reception_LQI"] = device_data.get(
                "ReceptionOfController"
            ).get("Lqi")

        if self.sensorType in ["RoomStat", "iTRV", "SmartPlug"]:
            attrs["battery_voltage"] = device_data.get("BatteryVoltage")
            attrs["battery_level"] = device_data.get("BatteryLevel")
            attrs["serial_number"] = device_data.get("SerialNumber")

        if self.sensorType == "RoomStat":
            attrs["humidity"] = (
                self.handler.get_hub_data()
                .getRoomStatData(self.deviceId)
                .get("MeasuredHumidity")
            )
        return attrs

    @property
    def state(self):
        _LOGGER.debug("**********************************")
        _LOGGER.debug(
            "Wiser Device state requested deviceId : %s", self.deviceId
        )
        _LOGGER.debug("**********************************")
        return (
            self.handler.get_hub_data()
            .getDevice(self.deviceId)
            .get("DisplayedSignalStrength")
        )


""" 
Specific Sensor to display the status of heating or water circuit
"""


class WiserSystemCircuitState(Entity):
    """ circuitType is HEATING HOTWATER """

    def __init__(self, handler, circuit_type):

        """Initialize the sensor."""
        _LOGGER.info("Wiser Circuit Sensor Init")
        self.handler = handler
        self.circuitType = circuit_type

    def update(self):
        _LOGGER.debug("********************************************")
        _LOGGER.debug("Wiser Cloud Circut status Update requested")
        _LOGGER.debug("*******************************************")
        self.handler.update()

    @property
    def icon(self):
        if self.circuitType == "HEATING":
            if self.state == "Off":
                return "mdi:radiator-disabled"
            else:
                return "mdi:radiator"
        else:
            # HOT WATER
            if self.state == "Off":
                return "mdi:water-off"
            else:
                return "mdi:water"

    @property
    def name(self):
        """Return the name of the Device """
        if self.circuitType == "HEATING":
            return "Wiser Heating"
        else:
            return "Wiser Hot Water"

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def device_state_attributes(self):
        """ returns additional info"""
        attrs = {}
        if self.circuitType == "HEATING":
            heating_channels = self.handler.get_hub_data().getHeatingChannels()
            for heatingChannel in heating_channels:
                channel_name = heatingChannel.get("Name")
                channel_pct_dmd = heatingChannel.get("PercentageDemand")
                channel_room_ids = heatingChannel.get("RoomIds")
                attr_name = "percentage_demand_{}".format(channel_name)
                attrs[attr_name] = channel_pct_dmd
                attr_name_2 = "room_ids_{}".format(channel_name)
                attrs[attr_name_2] = channel_room_ids
        return attrs

    @property
    def state(self):
        _LOGGER.debug("**********************************")
        _LOGGER.debug("Wiser Cloud Circut STATE requested")
        _LOGGER.debug("**********************************")
        if self.circuitType == "HEATING":
            return self.handler.get_hub_data().getHeatingRelayStatus()
        else:
            return self.handler.get_hub_data().getHotwaterRelayStatus()


"""
Sensor to display the status of the Wiser Cloud
"""


class WiserSystemCloudSensor(Entity):
    def __init__(self, handler):

        """Initialize the sensor."""
        _LOGGER.info("Wiser Cloud Sensor Init")
        self.handler = handler
        self.cloudStatus = (
            self.handler.get_hub_data().getSystem().get("CloudConnectionStatus")
        )

    def update(self):
        _LOGGER.debug("Wiser Cloud Sensor Update requested")
        self.handler.update()
        self.cloudStatus = (
            self.handler.get_hub_data().getSystem().get("CloudConnectionStatus")
        )

    @property
    def icon(self):
        if self.cloudStatus == "Connected":
            return "mdi:cloud-check"
        else:
            return "mdi:cloud-alert"

    @property
    def name(self):
        """Return the name of the Device """
        return "Wiser Cloud Status"

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def state(self):
        _LOGGER.debug("*************************************")
        _LOGGER.debug("Wiser Cloud  status Update requested")
        _LOGGER.debug("*************************************")
        return self.cloudStatus


"""
Sensor to display the status of the Wiser Operation Mode (Away/Normal etc)
"""


class WiserSystemOperationModeSensor(Entity):
    def __init__(self, handler):

        """Initialize the sensor."""
        _LOGGER.info("Wiser Operation  Mode Sensor Init")
        self.handler = handler
        self.override_type = (
            self.handler.get_hub_data().getSystem().get("OverrideType")
        )
        self.away_temperature = (
            self.handler.get_hub_data().getSystem().get("AwayModeSetPointLimit")
        )

    def update(self):
        _LOGGER.debug("Wiser Operation Mode Sensor Update requested")
        self.handler.update()
        self.override_type = (
            self.handler.get_hub_data().getSystem().get("OverrideType")
        )
        self.away_temperature = (
            self.handler.get_hub_data().getSystem().get("AwayModeSetPointLimit")
        )

    def mode(self):
        if self.override_type and self.override_type == "Away":
            return "Away"
        else:
            return "Normal"

    @property
    def icon(self):
        if self.mode() == "Normal":
            return "mdi:check"
        else:
            return "mdi:alert"

    @property
    def name(self):
        """Return the name of the Device """
        return "Wiser Operation Mode"

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def state(self):
        return self.mode()

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        attrs = {"AwayModeTemperature": -1.0}
        if self.away_temperature:
            try:
                attrs["AwayModeTemperature"] = int(self.away_temperature) / 10.0
            except Exception as ex:
                _LOGGER.debug(
                    "Exception" + " : Unexpected value for awayTemperature",
                    self.away_temperature,
                )
        return attrs
