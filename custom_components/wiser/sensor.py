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
    ATTR_VOLTAGE,
    CONF_ENTITY_NAMESPACE,
    DEVICE_CLASS_BATTERY,
    STATE_UNKNOWN,
)
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.icon import icon_for_battery_level

from .const import (
    _LOGGER,
    BATTERY_FULL,
    DOMAIN,
    MIN_BATTERY_LEVEL,
    SIGNAL_STRENGTH_ICONS,
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup the sensor platform."""
    data = hass.data[DOMAIN]  # Get Handler
    wiser_devices = []

    # Add device sensors, only if there are some
    if data.wiserhub.getDevices() is not None:
        for device in data.wiserhub.getDevices():
            wiser_devices.append(
                WiserDeviceSensor(data, device.get("id"), device.get("ProductType"))
            )

            # Add battery sensors
            # Add based on device type due to battery values sometimes not showing
            # until sometime after a hub restart
            if device.get("ProductType") in ["iTRV", "RoomStat"]:
                wiser_devices.append(
                    WiserBatterySensor(data, device.get("id"), sensorType="Battery")
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

    def __init__(self, config_entry, device_id=0, sensorType=""):
        """Initialize the sensor."""
        self.data = config_entry
        self._deviceId = device_id
        self._sensor_type = sensorType
        self._state = None

    async def async_update(self):
        _LOGGER.debug("{} device update requested".format(self._device_name))
        await self.data.async_update()

    @property
    def name(self):
        """Return the name of the sensor"""
        return self._device_name

    @property
    def state(self):
        """Return the state of the sensor."""
        _LOGGER.debug("{} device state requested".format(self.name))
        return self._state

    @property
    def unique_id(self):
        return "{}-{}".format(self._sensor_type, self._deviceId)


class WiserBatterySensor(WiserSensor):
    """Definition of a battery sensor for wiser iTRVs and RoomStats"""

    def __init__(self, data, device_id=0, sensorType=""):
        super().__init__(data, device_id, sensorType)
        self._device_name = self.get_device_name()
        # Set default state to unknown to show this value if battery info
        # cannot be read.
        self._state = "Unknown"
        self._battery_voltage = 0
        self._battery_level = None
        _LOGGER.info("{} device init".format(self._device_name))

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()

        device = self.data.wiserhub.getDevice(self._deviceId)

        # Set battery info
        self._battery_level = device.get("BatteryLevel")
        self._battery_voltage = device.get("BatteryVoltage")
        if self._battery_voltage and self._battery_voltage > 0:
            self._state = int(
                (
                    (self._battery_voltage - MIN_BATTERY_LEVEL)
                    / (BATTERY_FULL - MIN_BATTERY_LEVEL)
                )
                * 100
            )

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return DEVICE_CLASS_BATTERY

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity."""
        return "%"

    @property
    def device_state_attributes(self):
        """Return the state attributes of the battery."""
        attrs = {}
        if self._battery_voltage and self._battery_voltage > 0:
            attrs["battery_voltage"] = str(self._battery_voltage / 10) + "v"
            attrs[ATTR_BATTERY_LEVEL] = (
                self.data.wiserhub.getDevice(self._deviceId).get("BatteryLevel") or None
            )
        return attrs

    def get_device_name(self):
        """Return the name of the Device"""
        product_type = str(
            self.data.wiserhub.getDevice(self._deviceId).get("ProductType") or ""
        )

        # Only iTRVs and RoomStats have batteries
        if product_type == "iTRV":
            # Multiple ones get automagically number _n by HA
            return (
                "Wiser "
                + product_type
                + "-"
                + self.data.wiserhub.getDeviceRoom(self._deviceId)["roomName"]
                + " Battery Level"
            )
        elif product_type == "RoomStat":
            # Usually only one per room
            return (
                "Wiser "
                + product_type
                + "-"
                + self.data.wiserhub.getDeviceRoom(self._deviceId)["roomName"]
                + " Battery Level"
            )
        else:
            return (
                "Wiser "
                + product_type
                + "-"
                + str(
                    self.data.wiserhub.getDevice(self._deviceId).get("SerialNumber")
                    or "" + " Battery Level"
                )
            )

    @property
    def device_info(self):
        """Return device specific attributes."""
        product_type = self.data.wiserhub.getDevice(self._deviceId).get("ProductType")
        return {"identifiers": {(DOMAIN, "{}-{}".format(product_type, self._deviceId))}}


class WiserDeviceSensor(WiserSensor):
    """Definition of Wiser Device Sensor"""

    def __init__(self, data, device_id=0, sensorType=""):
        super().__init__(data, device_id, sensorType)
        self._device_name = self.get_device_name()
        _LOGGER.info("{} device init".format(self._device_name))

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._state = self.data.wiserhub.getDevice(self._deviceId).get(
            "DisplayedSignalStrength"
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        identifier = None

        if (
            self.data.wiserhub.getDevice(self._deviceId).get("ProductType")
            == "Controller"
        ):
            return {"identifiers": {(DOMAIN, self.data.unique_id)}}
        elif (
            self.data.wiserhub.getDevice(self._deviceId).get("ProductType")
            == "SmartPlug"
        ):
            # combine sensor for smartplug with smartplug device
            identifier = "{}-{}".format(
                self.data.wiserhub.getSmartPlug(self._deviceId)["Name"], self._deviceId
            )

            return {"identifiers": {(DOMAIN, identifier)}}
        else:
            return {
                "name": self.name,
                "identifiers": {(DOMAIN, self.unique_id)},
                "manufacturer": "Drayton Wiser",
                "model": self.data.wiserhub.getDevice(self._deviceId).get(
                    "ProductType"
                ),
            }

    def get_device_name(self):
        """Return the name of the Device"""
        product_type = str(
            self.data.wiserhub.getDevice(self._deviceId).get("ProductType") or ""
        )

        if product_type == "Controller":
            return "Wiser Heathub"  # Only ever one of these
        elif product_type == "iTRV":
            # Multiple ones get automagically number _n by HA
            return (
                "Wiser "
                + product_type
                + "-"
                + self.data.wiserhub.getDeviceRoom(self._deviceId)["roomName"]
            )
        elif product_type == "RoomStat":
            # Usually only one per room
            return (
                "Wiser "
                + product_type
                + "-"
                + self.data.wiserhub.getDeviceRoom(self._deviceId)["roomName"]
            )
        elif product_type == "SmartPlug":
            return self.data.wiserhub.getSmartPlug(self._deviceId)["Name"]
        else:
            return (
                "Wiser "
                + product_type
                + "-"
                + str(
                    self.data.wiserhub.getDevice(self._deviceId).get("SerialNumber")
                    or ""
                )
            )

    @property
    def icon(self):
        """Return icon for signal strength"""
        try:
            return SIGNAL_STRENGTH_ICONS[
                self.data.wiserhub.getDevice(self._deviceId).get(
                    "DisplayedSignalStrength"
                )
            ]
        except KeyError:
            # Handle anything else as no signal
            return SIGNAL_STRENGTH_ICONS["NoSignal"]

    @property
    def device_state_attributes(self):
        _LOGGER.debug(
            "State attributes for {} {}".format(self._deviceId, self._sensor_type)
        )
        attrs = {}
        device_data = self.data.wiserhub.getDevice(self._deviceId)

        """ Generic attributes """
        attrs["vendor"] = "Drayton Wiser"
        attrs["product_type"] = device_data.get("ProductType")
        attrs["model_identifier"] = device_data.get("ModelIdentifier")
        attrs["device_lock_enabled"] = device_data.get("DeviceLockEnabled")
        attrs["displayed_signal_strength"] = device_data.get("DisplayedSignalStrength")
        attrs["firmware"] = device_data.get("ActiveFirmwareVersion")
        attrs["serial_number"] = device_data.get("SerialNumber")

        """ if controller then add the zigbee data to the controller info """
        if device_data.get("ProductType") == "Controller":
            attrs["zigbee_channel"] = (
                self.data.wiserhub.getHubData().get("Zigbee").get("NetworkChannel")
            )

        """ Network Data"""
        attrs["node_id"] = device_data.get("NodeId")
        attrs["displayed_signal_strength"] = device_data.get("DisplayedSignalStrength")

        if self._sensor_type in ["RoomStat", "iTRV"]:
            attrs["parent_node_id"] = device_data.get("ParentNodeId")
            """ hub route"""
            if device_data.get("ParentNodeId") == 0:

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

        """ Other """
        if self._sensor_type == "RoomStat":
            attrs["humidity"] = self.data.wiserhub.getRoomStatData(self._deviceId).get(
                "MeasuredHumidity"
            )

        return attrs


class WiserSystemCircuitState(WiserSensor):
    """Definition of a Hotwater/Heating circuit state sensor"""

    def __init__(self, data, device_id=0, sensorType=""):
        super().__init__(data, device_id, sensorType)
        self._device_name = self.get_device_name()
        _LOGGER.info("{} device init".format(self._device_name))

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        if self._sensor_type == "HEATING":
            self._state = self.data.wiserhub.getHeatingRelayStatus()
        else:
            self._state = self.data.wiserhub.getHotwaterRelayStatus()

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "identifiers": {(DOMAIN, self.data.unique_id)},
        }

    def get_device_name(self):
        """Return the name of the Device """
        if self._sensor_type == "HEATING":
            return "Wiser Heating"
        else:
            return "Wiser Hot Water"

    @property
    def icon(self):
        if self._sensor_type == "HEATING":
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
        if self._sensor_type == "HEATING":
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
        self._device_name = self.get_device_name()
        _LOGGER.info("{} device init".format(self._device_name))

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._state = self.data.wiserhub.getSystem().get("CloudConnectionStatus")

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "identifiers": {(DOMAIN, self.data.unique_id)},
        }

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
        self._device_name = self.get_device_name()
        self._override_type = self.data.wiserhub.getSystem().get("OverrideType")
        self._away_temperature = self.data.wiserhub.getSystem().get(
            "AwayModeSetPointLimit"
        )
        _LOGGER.info("{} device init".format(self._device_name))

    async def async_update(self):
        """Fetch new state data for the sensor."""
        await super().async_update()
        self._override_type = self.data.wiserhub.getSystem().get("OverrideType")
        self._away_temperature = self.data.wiserhub.getSystem().get(
            "AwayModeSetPointLimit"
        )
        self._state = self.mode()

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "identifiers": {(DOMAIN, self.data.unique_id)},
        }

    def mode(self):
        if self._override_type and self._override_type == "Away":
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
        if self._away_temperature:
            try:
                attrs["AwayModeTemperature"] = round(self._away_temperature / 10.0, 1)
            except Exception:
                _LOGGER.debug(
                    "Exception" + " : Unexpected value for awayTemperature",
                    self._away_temperature,
                )
        return attrs
