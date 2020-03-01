"""
Climate Platform Device for Wiser Rooms

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
import asyncio
import logging
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.climate import ClimateDevice
from homeassistant.core import callback

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
from homeassistant.util import ruamel_yaml as yaml

from .const import _LOGGER, DOMAIN

from .util import convert_to_wiser_schedule, convert_from_wiser_schedule


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

SERVICE_BOOST_HEATING = "boost_heating"
SERVICE_GET_SCHEDULE = "get_schedule"
SERVICE_SET_SCHEDULE = "set_schedule"
SERVICE_COPY_SCHEDULE = "copy_schedule"

WISER_PRESET_TO_HASS = {
    "fromawaymode": PRESET_AWAY,
    "frommanualmode": None,
    "fromboost": PRESET_BOOST,
    "frommanualoverrideduringaway": PRESET_AWAY_OVERRIDE,
    "fromboostduringaway": PRESET_AWAY_BOOST,
    "frommanualoverride": PRESET_OVERRIDE,
    "fromecoiq": None,
    "fromschedule": None,
    "fromcomfortmode": None,
}

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE


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


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser climate device"""
    data = hass.data[DOMAIN]

    wiser_rooms = [
        WiserRoom(hass, data, room.get("id")) for room in data.wiserhub.getRooms()
    ]
    async_add_entities(wiser_rooms, True)

    @callback
    def heating_boost(service):
        """Handle the service call."""
        entity_id = service.data[ATTR_ENTITY_ID]
        boost_time = service.data[ATTR_TIME_PERIOD]
        boost_temp = service.data[ATTR_TEMPERATURE]
        boost_temp_delta = service.data[ATTR_TEMPERATURE_DELTA]

        for room in wiser_rooms:
            _LOGGER.debug("*****BOOST for {}".format(room.entity_id))
            if room.entity_id == entity_id:
                if boost_temp_delta > 0:
                    boost_temp = ((room.current_temperature)) + boost_temp_delta
                _LOGGER.debug(
                    "Boost service called for {} to set to {}C for {} mins.".format(
                        room.name, boost_temp, boost_time
                    )
                )

                hass.async_create_task(
                    room.set_room_mode(room.room_id, "boost", boost_temp, boost_time)
                )
                room.schedule_update_ha_state(True)
                break

    @callback
    def get_schedule(service):
        """Handle the service call"""
        entity_id = service.data[ATTR_ENTITY_ID]
        filename = (
            service.data[ATTR_FILENAME]
            if service.data[ATTR_FILENAME] != ""
            else ("schedule_" + entity_id + ".yaml")
        )

        for room in wiser_rooms:
            if room.entity_id == entity_id:
                scheduleData = room.schedule
                _LOGGER.debug("Sched Service Data = {}".format(scheduleData))
                if scheduleData != None:
                    scheduleData = convert_from_wiser_schedule(scheduleData, room.name)
                    yaml.save_yaml(filename, scheduleData)
                else:
                    raise Exception("No schedule data returned")
                break

    @callback
    def set_schedule(service):
        """Handle the service call"""
        entity_id = service.data[ATTR_ENTITY_ID]
        filename = service.data[ATTR_FILENAME]
        # Get schedule data
        scheduleData = yaml.load_yaml(filename)
        # Set schedule
        for room in wiser_rooms:
            if room.entity_id == entity_id:
                hass.async_create_task(
                    room.set_room_schedule(room.room_id, scheduleData)
                )
                room.schedule_update_ha_state(True)
                break

    @callback
    def copy_schedule(service):
        """Handle the service call"""
        entity_id = service.data[ATTR_ENTITY_ID]
        to_entity_id = service.data[ATTR_COPYTO_ENTITY_ID]

        for room in wiser_rooms:
            if room.entity_id == entity_id:
                for to_room in wiser_rooms:
                    if to_room.entity_id == to_entity_id:
                        hass.async_create_task(
                            room.copy_room_schedule(room.room_id, to_room.room_id)
                        )
                        room.schedule_update_ha_state(True)
                        break

    hass.services.async_register(
        DOMAIN, SERVICE_BOOST_HEATING, heating_boost, schema=BOOST_HEATING_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN, SERVICE_GET_SCHEDULE, get_schedule, schema=GET_SET_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN, SERVICE_SET_SCHEDULE, set_schedule, schema=GET_SET_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN, SERVICE_COPY_SCHEDULE, copy_schedule, schema=COPY_SCHEDULE_SCHEMA,
    )


""" Definition of WiserRoom """


class WiserRoom(ClimateDevice):
    def __init__(self, hass, data, room_id):
        """Initialize the sensor."""
        self.data = data
        self.hass = hass
        self.schedule = {}
        self.room_id = room_id
        self._force_update = False
        self._hvac_modes_list = [HVAC_MODE_AUTO, HVAC_MODE_HEAT, HVAC_MODE_OFF]
        self._preset_modes_list = [
            PRESET_BOOST30,
            PRESET_BOOST60,
            PRESET_BOOST120,
            PRESET_BOOST180,
            PRESET_BOOST_CANCEL,
        ]
        _LOGGER.info(
            "Wiser Room Initialisation for {}".format(
                self.data.wiserhub.getRoom(self.room_id).get("Name")
            )
        )

    async def async_update(self):
        _LOGGER.debug("WiserRoom Update requested for {}".format(self.name))
        if self._force_update:
            await self.data.async_update(no_throttle=True)
            self._force_update = False
        else:
            await self.data.async_update()
        self.schedule = self.data.wiserhub.getRoomSchedule(self.room_id)

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def should_poll(self):
        return True

    @property
    def state(self):
        state = self.data.wiserhub.getRoom(self.room_id).get("Mode")
        current_temp = self.data.wiserhub.getRoom(self.room_id).get("DisplayedSetPoint")
        _LOGGER.info("State requested for room %s, state=%s", self.room_id, state)

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
        return "Wiser " + self.data.wiserhub.getRoom(self.room_id).get("Name")

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def min_temp(self):
        return self.data.minimum_temp

    @property
    def max_temp(self):
        return self.data.maximum_temp

    @property
    def current_temperature(self):
        temp = (
            self.data.wiserhub.getRoom(self.room_id).get("CalculatedTemperature") / 10
        )
        if temp < self.min_temp:
            """ Sometimes we get really low temps (like -3000!),
                not sure why, if we do then just set it to -20 for now till i
                debug this.
            """
            temp = self.min_temp
        return temp

    @property
    def icon(self):
        # Change icon to show if radiator is heating, not heating or set to off.
        if self.data.wiserhub.getRoom(self.room_id).get("ControlOutputState") == "On":
            return "mdi:radiator"
        else:
            if self.data.wiserhub.getRoom(self.room_id).get("CurrentSetPoint") == -200:
                return "mdi:radiator-off"
            else:
                return "mdi:radiator-disabled"
                
    @property
    def unique_id(self):
        return "WiserRoom-{}".format(self.room_id)
                
    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": "Drayton Wiser",
            "model": "Room",
        }

    @property
    def hvac_mode(self):
        state = self.data.wiserhub.getRoom(self.room_id).get("Mode")
        current_set_point = self.data.wiserhub.getRoom(self.room_id).get(
            "CurrentSetPoint"
        )
        if state.lower() == "manual":
            if current_set_point == -200:
                state = HVAC_MODE_OFF
            else:
                state = HVAC_MODE_HEAT
        if state.lower() == "auto":
            state = HVAC_MODE_AUTO
        return state

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new operation mode."""
        _LOGGER.debug(
            "Setting Device Operation {} for roomId {}".format(hvac_mode, self.room_id)
        )
        # Convert HA heat_cool to manual as required by api
        if hvac_mode == HVAC_MODE_HEAT:
            hvac_mode = "manual"
        await self.set_room_mode(self.room_id, hvac_mode)
        return True

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._hvac_modes_list

    @property
    def preset_mode(self):
        wiser_preset = self.data.wiserhub.getRoom(self.room_id).get("SetpointOrigin")
        mode = self.data.wiserhub.getRoom(self.room_id).get("Mode")

        if (
            mode.lower() == HVAC_MODE_AUTO
            and wiser_preset.lower() == "frommanualoverride"
        ):
            preset = PRESET_OVERRIDE
        else:
            try:
                preset = WISER_PRESET_TO_HASS[wiser_preset.lower()]
            except:
                preset = None
        return preset

    async def async_set_preset_mode(self, preset_mode):
        boost_time = self.data.boost_time
        boost_temp = self.data.boost_temp
        """Set new preset mode."""
        _LOGGER.debug(
            "*******Setting Preset Mode {} for roomId {}".format(
                preset_mode, self.room_id
            )
        )
        # Convert HA preset to required api presets

        """ Cancel boost mode """
        if preset_mode.lower() == PRESET_BOOST_CANCEL.lower():
            preset_mode = self.hvac_mode

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
                self.data.wiserhub.getRoom(self.room_id).get("CalculatedTemperature")
                / 10
            ) + boost_temp

        await self.set_room_mode(self.room_id, preset_mode, boost_temp, boost_time)
        return True

    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return self._preset_modes_list

    @property
    def target_temperature(self):
        target = self.data.wiserhub.getRoom(self.room_id).get("DisplayedSetPoint") / 10

        state = self.data.wiserhub.getRoom(self.room_id).get("Mode")
        current_set_point = self.data.wiserhub.getRoom(self.room_id).get(
            "DisplayedSetPoint"
        )

        if state.lower() == "manual" and current_set_point == -200:
            target = None

        return target

    """    https://github.com/asantaga/wiserHomeAssistantPlatform/issues/13 """

    @property
    def state_attributes(self):
        # Generic attributes
        attrs = super().state_attributes
        attrs["percentage_demand"] = self.data.wiserhub.getRoom(self.room_id).get(
            "PercentageDemand"
        )
        attrs["control_output_state"] = self.data.wiserhub.getRoom(self.room_id).get(
            "ControlOutputState"
        )
        attrs["heating_rate"] = self.data.wiserhub.getRoom(self.room_id).get(
            "HeatingRate"
        )
        attrs["window_state"] = self.data.wiserhub.getRoom(self.room_id).get(
            "WindowState"
        )
        attrs["window_detection_active"] = self.data.wiserhub.getRoom(self.room_id).get(
            "WindowDetectionActive"
        )
        attrs["away_mode_supressed"] = self.data.wiserhub.getRoom(self.room_id).get(
            "AwayModeSuppressed"
        )

        return attrs

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        if target_temperature is None:
            return False

        _LOGGER.debug(
            "Setting temperature for {} to {}".format(self.name, target_temperature)
        )
        self.data.wiserhub.setRoomTemperature(self.room_id, target_temperature)
        self._force_update = True

    async def set_room_mode(self, room_id, mode, boost_temp=None, boost_time=None):
        """ Set to default values if not passed in """
        boost_temp = self.data.boost_temp if boost_temp is None else boost_temp
        boost_time = self.data.boost_time if boost_time is None else boost_time
        _LOGGER.debug(
            "Setting Room Mode to {} for roomId {}".format(mode, self.room_id)
        )
        self.data.wiserhub.setRoomMode(room_id, mode, boost_temp, boost_time)
        self._force_update = True

    async def set_room_schedule(self, room_id, scheduleData):
        if scheduleData != None:
            scheduleData = convert_to_wiser_schedule(scheduleData)
            self.data.wiserhub.setRoomSchedule(room_id, scheduleData)
            _LOGGER.debug("Set room schedule for {}".format(self.name))
            self._force_update = True
            return True
        else:
            return False

    async def copy_room_schedule(self, room_id, to_room_id):
        self.data.wiserhub.copyRoomSchedule(room_id, to_room_id)
        _LOGGER.debug(
            "Copied room schedule from {} to {}".format(
                self.name, self.data.wiserhub.getRoom(to_room_id).get("Name")
            )
        )
        self._force_update = True
        return True
