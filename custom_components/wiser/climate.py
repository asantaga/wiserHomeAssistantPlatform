"""
Climate Platform Device for Wiser Rooms

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
import logging
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.climate import ClimateDevice

# from homeassistant.components.climate.const import (STATE_AUTO,
#                                                    SUPPORT_OPERATION_MODE,
#                                                    SUPPORT_TARGET_TEMPERATURE,
#                                                    HVAC_MODE_HEAT_COOL)
#
from homeassistant.components.climate.const import (
    HVAC_MODE_AUTO,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_PRESET_MODE,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_BATTERY_LEVEL,
    ATTR_TEMPERATURE,
    TEMP_CELSIUS,
)
from homeassistant.helpers.entity import Entity
from homeassistant.util.ruamel_yaml import load_yaml, save_yaml

_LOGGER = logging.getLogger(__name__)
DOMAIN = "wiser"

ATTR_TIME_PERIOD = "time_period"
ATTR_TEMPERATURE_DELTA = "temperature_delta"
ATTR_FILENAME = "filename"
ATTR_COPYTO_ENTITY_ID = "to_entity_id"

PRESET_BOOST = "boost"
PRESET_BOOST30 = "Boost 30m"
PRESET_BOOST60 = "Boost 1h"
PRESET_BOOST120 = "Boost 2h"
PRESET_BOOST180 = "Boost 3h"
PRESET_BOOST_CANCEL = "Cancel Boost"
PRESET_OVERRIDE = "Override"
PRESET_AWAY = "Away Mode"
PRESET_AWAY_BOOST = "Away Boost"
PRESET_AWAY_OVERRIDE = "Away Override"

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

SERVICE_BOOST_HEATING = "boost_heating"
SERVICE_GET_SCHEDULE = "get_schedule"
SERVICE_SET_SCHEDULE = "set_schedule"
SERVICE_COPY_SCHEDULE = "copy_schedule"

BOOST_HEATING_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Optional(ATTR_TIME_PERIOD, default=60): vol.Coerce(int),
        vol.Optional(ATTR_TEMPERATURE, default="23.0"): vol.Coerce(float),
        vol.Optional(ATTR_TEMPERATURE_DELTA, default="0"): vol.Coerce(float),
    }
)

GET_SET_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
    }
)

COPY_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_COPYTO_ENTITY_ID): cv.entity_id,
    }
)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    handler = hass.data[DOMAIN]  # Get Handler

    handler.update()
    wiser_rooms = []

    """ Get Rooms """
    for room in handler.get_hub_data().getRooms():
        """    https://github.com/asantaga/wiserHomeAssistantPlatform/issues/10 """
        if room.get("RoomStatId") != None or room.get("SmartValveIds") != None:
            wiser_rooms.append(WiserRoom(room.get("id"), handler))
    add_devices(wiser_rooms)

    def heating_boost(service):
        """Handle the service call."""
        entity_id = service.data[ATTR_ENTITY_ID]

        if entity_id:
            target_devices = [
                device
                for device in wiser_rooms
                if device.entity_id in entity_id
            ]
        else:
            _LOGGER.error("Cannot boost entity id entered")
            return

        boost_time = service.data[ATTR_TIME_PERIOD]
        boost_temp = service.data[ATTR_TEMPERATURE]
        boost_temp_delta = service.data[ATTR_TEMPERATURE_DELTA]

        for target_device in target_devices:
            if boost_temp_delta > 0:
                boost_temp = (
                    handler.get_hub_data()
                    .getRoom(target_device.roomId)
                    .get("CalculatedTemperature")
                    / 10
                ) + boost_temp_delta

            _LOGGER.debug(
                "Boost service called for {} to set to {}C for {} mins.".format(
                    target_device.name, boost_temp, boost_time
                )
            )

            handler.set_room_mode(
                target_device.roomId, "boost", boost_temp, boost_time
            )
            target_device.async_schedule_update_ha_state(True)
        
    def get_schedule(service):
        """Handle the service call"""
        entity_id = service.data[ATTR_ENTITY_ID]
        if entity_id:
            target_devices = [
                device for device in wiser_rooms if device.entity_id in entity_id
            ]
        else:
            _LOGGER.error("Cannot get schedule from this entity")
            return
        filename = service.data[ATTR_FILENAME] if service.data[ATTR_FILENAME] != "" else ("schedule_" + entity_id + ".yaml")
        #Get schedule data
        for target_device in target_devices:
            scheduleData = handler.get_room_schedule(target_device.roomId)
        if scheduleData != None:
            #Write to file
            save_yaml(filename, scheduleData)
            return
            
    def set_schedule(service):
        """Handle the service call"""
        entity_id = service.data[ATTR_ENTITY_ID]
        if entity_id:
            target_devices = [
                device for device in wiser_rooms if device.entity_id in entity_id
            ]
        else:
            _LOGGER.error("Cannot set schedule of this entity")
            return
        filename = service.data[ATTR_FILENAME]
        #Get schedule data
        scheduleData = load_yaml(filename)
        #Set schedule
        for target_device in target_devices:
            handler.set_room_schedule(target_device.roomId, scheduleData)
        return
            
    def copy_schedule(service):
        """Handle the service call"""
        entity_id = service.data[ATTR_ENTITY_ID]
        to_entity_id = service.data[ATTR_COPYTO_ENTITY_ID]
        
        if entity_id:
            target_devices = [
                device for device in wiser_rooms if device.entity_id in entity_id
            ]
        else:
            _LOGGER.error("Cannot copy schedule of this entity")
            return
        
        if to_entity_id:
            target_copyto_devices = [
                device for device in wiser_rooms if device.entity_id in to_entity_id
            ]
        else:
            _LOGGER.error("Cannot copy schedule to this entity")
            return
        
        for target_device in target_devices:
            handler.copy_room_schedule(target_device.roomId, target_copyto_devices[0].roomId)
        return

    hass.services.register(
        DOMAIN,
        SERVICE_BOOST_HEATING,
        heating_boost,
        schema=BOOST_HEATING_SCHEMA,
    )
                
    hass.services.register(
        DOMAIN,
        SERVICE_GET_SCHEDULE,
        get_schedule,
        schema=GET_SET_SCHEDULE_SCHEMA,
    )
                
    hass.services.register(
        DOMAIN,
        SERVICE_SET_SCHEDULE,
        set_schedule,
        schema=GET_SET_SCHEDULE_SCHEMA,
    )
                
    hass.services.register(
        DOMAIN,
        SERVICE_COPY_SCHEDULE,
        copy_schedule,
        schema=COPY_SCHEDULE_SCHEMA,
    )

""" Definition of WiserRoom """


class WiserRoom(ClimateDevice):
    def __init__(self, room_id, handler):
        """Initialize the sensor."""
        _LOGGER.info("Wiser Room Initialisation")
        self.handler = handler
        self.roomId = room_id
        self._hvac_modes_list = [HVAC_MODE_AUTO, HVAC_MODE_HEAT, HVAC_MODE_OFF]
        self._preset_modes_list = [
            PRESET_BOOST30,
            PRESET_BOOST60,
            PRESET_BOOST120,
            PRESET_BOOST180,
            PRESET_BOOST_CANCEL,
        ]

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def should_poll(self):
        return True

    @property
    def state(self):
        state = self.handler.get_hub_data().getRoom(self.roomId).get("Mode")
        current_temp = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("CurrentSetPoint")
        )
        _LOGGER.info(
            "State requested for room %s, state=%s", self.roomId, state
        )

        if state.lower() == "manual":
            if current_temp == -200:
                state = HVAC_MODE_OFF
            else:
                state = HVAC_MODE_HEAT
        else:
            state = HVAC_MODE_AUTO
        return state

    @property
    def name(self):
        return "Wiser " + self.handler.get_hub_data().getRoom(self.roomId).get(
            "Name"
        )

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def min_temp(self):
        return self.handler.minimum_temp

    @property
    def max_temp(self):
        return self.handler.maximum_temp

    @property
    def current_temperature(self):
        temp = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("CalculatedTemperature")
            / 10
        )
        if temp < self.handler.get_minimum_temp():
            """ Sometimes we get really low temps (like -3000!),
                not sure why, if we do then just set it to -20 for now till i
                debug this.
            """
            temp = self.handler.get_minimum_temp()
        return temp

    @property
    def icon(self):
        # Change icon to show if radiator is heating, not heating or set to off.
        if (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("ControlOutputState")
            == "On"
        ):
            return "mdi:radiator"
        else:
            if (
                self.handler.get_hub_data()
                .getRoom(self.roomId)
                .get("CurrentSetPoint")
                == -200
            ):
                return "mdi:radiator-off"
            else:
                return "mdi:radiator-disabled"

    @property
    def hvac_mode(self):
        state = self.handler.get_hub_data().getRoom(self.roomId).get("Mode")
        current_set_point = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("CurrentSetPoint")
        )
        if state.lower() == "manual":
            if current_set_point == -200:
                state = HVAC_MODE_OFF
            else:
                state = HVAC_MODE_HEAT
        if state.lower() == "auto":
            state = HVAC_MODE_AUTO
        return state

    def set_hvac_mode(self, hvac_mode):
        """Set new operation mode."""
        _LOGGER.debug(
            "*******Setting Device Operation {} for roomId {}".format(
                hvac_mode, self.roomId
            )
        )
        # Convert HA heat_cool to manual as required by api
        if hvac_mode == HVAC_MODE_HEAT:
            hvac_mode = "manual"
        self.handler.set_room_mode(self.roomId, hvac_mode)

        return True

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._hvac_modes_list

    @property
    def preset_mode(self):
        wiser_preset = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("SetpointOrigin")
        )
        mode = self.handler.get_hub_data().getRoom(self.roomId).get("Mode")

        if (
            mode.lower() == HVAC_MODE_AUTO
            and wiser_preset.lower() == "frommanualoverride"
        ):
            preset = PRESET_OVERRIDE
        else:
            if wiser_preset.lower() == "fromboost":
                preset = PRESET_BOOST
            elif wiser_preset.lower() == "fromawaymode":
                preset = PRESET_AWAY
            elif wiser_preset.lower() == "frommanualoverrideduringaway":
                preset = PRESET_AWAY_OVERRIDE
            elif wiser_preset.lower() == "fromboostduringaway":
                preset = PRESET_AWAY_BOOST
            else:
                preset = None
        return preset

    def set_preset_mode(self, preset_mode):
        boost_time = self.handler.boost_time
        boost_temp = self.handler.boost_temp
        """Set new preset mode."""
        _LOGGER.debug(
            "*******Setting Preset Mode {} for roomId {}".format(
                preset_mode, self.roomId
            )
        )
        # Convert HA preset to required api presets

        """ Cancel boost mode """
        if preset_mode.lower() == PRESET_BOOST_CANCEL.lower():
            preset_mode = (
                self.handler.get_hub_data().getRoom(self.roomId).get("Mode")
            )

        """ Deal with boost time variations """
        if preset_mode.lower() == PRESET_BOOST30.lower():
            boost_time = 30
        if preset_mode.lower() == PRESET_BOOST60.lower():
            boost_time = 60
        if preset_mode.lower() == PRESET_BOOST120.lower():
            boost_time = 120
        if preset_mode.lower() == PRESET_BOOST180.lower():
            boost_time = 180

        """ Set boost mode """
        if preset_mode[:5].lower() == PRESET_BOOST.lower():
            preset_mode = PRESET_BOOST

            """ Set boost temp to current + boost_temp """
            boost_temp = (
                self.handler.get_hub_data()
                .getRoom(self.roomId)
                .get("CalculatedTemperature")
                / 10
            ) + boost_temp

        self.handler.set_room_mode(
            self.roomId, preset_mode, boost_temp, boost_time
        )

        return True

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return self._preset_modes_list

    @property
    def target_temperature(self):
        target = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("CurrentSetPoint")
            / 10
        )

        state = self.handler.get_hub_data().getRoom(self.roomId).get("Mode")
        current_set_point = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("CurrentSetPoint")
        )

        if state.lower() == "manual" and current_set_point == -200:
            target = None

        return target

    def update(self):
        _LOGGER.debug("*******************************************")
        _LOGGER.debug("WiserRoom Update requested for {}".format(self.name))
        _LOGGER.debug("*******************************************")
        self.handler.update()

    """    https://github.com/asantaga/wiserHomeAssistantPlatform/issues/13 """

    @property
    def state_attributes(self):
        # Generic attributes
        attrs = super().state_attributes
        attrs["percentage_demand"] = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("PercentageDemand")
        )
        attrs["control_output_state"] = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("ControlOutputState")
        )
        attrs["heating_rate"] = (
            self.handler.get_hub_data().getRoom(self.roomId).get("HeatingRate")
        )
        attrs["window_state"] = (
            self.handler.get_hub_data().getRoom(self.roomId).get("WindowState")
        )
        attrs["window_detection_active"] = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("WindowDetectionActive")
        )
        attrs["away_mode_supressed"] = (
            self.handler.get_hub_data()
            .getRoom(self.roomId)
            .get("AwayModeSuppressed")
        )

        return attrs

    """ Set temperature """

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is None:
            return False
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        _LOGGER.debug(
            "Setting Device Temperature for roomId {}, temperature {}".format(
                self.roomId, target_temperature
            )
        )
        _LOGGER.debug("Value of wiserhub {}".format(self.handler))

        self.handler.set_room_temperature(self.roomId, target_temperature)

