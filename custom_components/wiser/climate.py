"""
Climate Platform Device for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
from functools import partial

import voluptuous as vol

from homeassistant.components.climate.const import (
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_AUTO,
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_PRESET_MODE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import callback
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt

from .const import (
    _LOGGER,
    CONF_BOOST_TEMP,
    CONF_BOOST_TEMP_TIME,
    DATA,
    DOMAIN,
    MANUFACTURER,
    ROOM,
    WISER_SERVICES,
)

try:
    from homeassistant.components.climate import ClimateEntity
except ImportError:
    from homeassistant.components.climate import ClimateDevice as ClimateEntity


ATTR_TIME_PERIOD = "time_period"
ATTR_TEMPERATURE_DELTA = "temperature_delta"

PRESET_AWAY = "Away Mode"
PRESET_AWAY_BOOST = "Away Boost"
PRESET_AWAY_OVERRIDE = "Away Override"
PRESET_BOOST = "boost"
PRESET_BOOST30 = "Boost 30m"
PRESET_BOOST60 = "Boost 1h"
PRESET_BOOST120 = "Boost 2h"
PRESET_BOOST180 = "Boost 3h"
PRESET_BOOST_CANCEL = "Cancel Boost"
PRESET_OVERRIDE = "Override"

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

HASS_HVAC_TO_WISER = {
    HVAC_MODE_AUTO: "auto",
    HVAC_MODE_HEAT: "manual",
    HVAC_MODE_OFF: "manual",
}

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

BOOST_HEATING_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Optional(ATTR_TIME_PERIOD, default=0): vol.Coerce(int),
        vol.Optional(ATTR_TEMPERATURE, default=0): vol.Coerce(float),
        vol.Optional(ATTR_TEMPERATURE_DELTA, default=0): vol.Coerce(float),
    }
)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    if (data.wiserhub.getRooms()) is not None:
        wiser_rooms = [
            WiserRoom(hass, data, room.get("id")) for room in data.wiserhub.getRooms()
        ]
    else:
        wiser_rooms = None
    async_add_entities(wiser_rooms, True)

    @callback
    def heating_boost(service):
        """Handle the service call."""
        entity_id = service.data[ATTR_ENTITY_ID]
        boost_time = service.data[ATTR_TIME_PERIOD]
        boost_temp = service.data[ATTR_TEMPERATURE]
        boost_temp_delta = service.data[ATTR_TEMPERATURE_DELTA]

        # Set to config values if not set
        if boost_time == 0:
            boost_time = config_entry.options[CONF_BOOST_TEMP_TIME]

        if boost_temp == 0 and boost_temp_delta == 0:
            boost_temp_delta = config_entry.options[CONF_BOOST_TEMP]

        # Find correct room to boost
        for room in wiser_rooms:
            _LOGGER.debug("BOOST for %s", room.entity_id)
            if room.entity_id == entity_id:
                if boost_temp_delta > 0:
                    boost_temp = (room.current_temperature) + boost_temp_delta
                _LOGGER.info(
                    "Boost service called for %s to set to %sC for %s mins.",
                    room.name,
                    boost_temp,
                    boost_time,
                )

                hass.async_create_task(
                    room.set_room_mode(room.room_id, "boost", boost_temp, boost_time)
                )
                room.schedule_update_ha_state(True)
                break

    

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_BOOST_HEATING"],
        heating_boost,
        schema=BOOST_HEATING_SCHEMA,
    )


class WiserRoom(ClimateEntity):
    """WiserRoom ClientEntity Object."""

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
            "Wiser Room Initialisation for %s",
            self.data.wiserhub.getRoom(self.room_id).get("Name"),
        )

    async def async_update(self):
        """Async update method."""
        _LOGGER.debug("WiserRoom Update requested for %s", self.name)
        if self._force_update:
            await self.data.async_update(no_throttle=True)
            self._force_update = False
        self.schedule = self.data.wiserhub.getRoomSchedule(self.room_id)
        # Testing for adding schedule ids to hub controller entity
        self.data.schedules[str(self.entity_id)] = self.data.wiserhub.getRoom(self.room_id).get("ScheduleId")

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def should_poll(self):
        """We don't want polling so return false."""
        return False

    @property
    def state(self):
        """Return stategit s."""
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
        """Return Name of device."""
        return "Wiser " + self.data.wiserhub.getRoom(self.room_id).get("Name")

    @property
    def temperature_unit(self):
        """Return temp units."""
        return TEMP_CELSIUS

    @property
    def min_temp(self):
        """Return min temp from data."""
        return self.data.minimum_temp

    @property
    def max_temp(self):
        """Return max temp from data."""
        return self.data.maximum_temp

    @property
    def current_temperature(self):
        """Return current temp from data."""
        raw = self.data.wiserhub.getRoom(self.room_id).get("CalculatedTemperature")
        if raw == -32768: # Reported temperature if there are no thermostats available
            return None
        return raw / 10

    @property
    def icon(self):
        """Return icon to show if radiator is heating, not heating or set to off."""
        if self.data.wiserhub.getRoom(self.room_id).get("ControlOutputState") == "On":
            return "mdi:radiator"
        if self.data.wiserhub.getRoom(self.room_id).get("CurrentSetPoint") == -200:
            return "mdi:radiator-off"
        return "mdi:radiator-disabled"

    @property
    def unique_id(self):
        """Return unique Id."""
        return f"WiserRoom-{self.room_id}"

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": self.name,
            "identifiers": {(DOMAIN, self.unique_id)},
            "manufacturer": MANUFACTURER,
            "model": ROOM.title(),
        }

    @property
    def hvac_action(self):
        """Return hvac action from data."""
        if self.data.wiserhub.getRoom(self.room_id).get("ControlOutputState") == "On":
            return CURRENT_HVAC_HEAT
        return CURRENT_HVAC_IDLE

    @property
    def hvac_mode(self):
        """Return set hvac mode."""
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
        _LOGGER.info(
            "Setting Device Operation %s for roomId %s", hvac_mode, self.room_id,
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
        """Set preset mode."""
        # Added fix for old firmware where capitalisation of name is different
        wiser_preset = self.data.wiserhub.getRoom(self.room_id).get(
            "SetpointOrigin",
            self.data.wiserhub.getRoom(self.room_id).get("SetPointOrigin", "NA"),
        )
        mode = self.data.wiserhub.getRoom(self.room_id).get("Mode")

        if (
            mode.lower() == HVAC_MODE_AUTO
            and wiser_preset.lower() == "frommanualoverride"
        ):
            preset = PRESET_OVERRIDE
        else:
            try:
                preset = WISER_PRESET_TO_HASS[wiser_preset.lower()]
            except KeyError:
                preset = None
        return preset

    async def async_set_preset_mode(self, preset_mode):
        """Async call to set preset mode ."""
        boost_time = self.data.boost_time
        boost_temp = self.data.boost_temp

        _LOGGER.debug(
            "*******Setting Preset Mode %s for roomId %s", preset_mode, self.room_id,
        )
        # Convert HA preset to required api presets

        # Cancel boost mode
        if preset_mode.lower() == PRESET_BOOST_CANCEL.lower():
# Change based on https://github.com/halfofabanana/wiserHomeAssistantPlatform/commit/463095bd9c4837107f6c8cf6fdb9084f9d68d883
# Return to corect setpoint after override cancellation
            if self.hvac_mode == HVAC_MODE_HEAT:
                preset_mode = "auto_to_manual"
            else:
                preset_mode = HASS_HVAC_TO_WISER[self.hvac_mode]   


        # Deal with boost time variations
        if preset_mode.lower() == PRESET_BOOST30.lower():
            boost_time = 30
        if preset_mode.lower() == PRESET_BOOST60.lower():
            boost_time = 60
        if preset_mode.lower() == PRESET_BOOST120.lower():
            boost_time = 120
        if preset_mode.lower() == PRESET_BOOST180.lower():
            boost_time = 180

        # Set boost mode
        if preset_mode[:5].lower() == PRESET_BOOST.lower():
            preset_mode = PRESET_BOOST

            # Set boost temp to current + boost_temp
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
        """Return target temp."""
        current_set_point = self.data.wiserhub.getRoom(self.room_id).get(
            "DisplayedSetPoint"
        )

        if current_set_point == -200:
            return None

        return current_set_point / 10

    @property
    def state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes

        # If boosted show boost end time
        #if self.data.wiserhub.getRoom(self.room_id).get("OverrideTimeoutUnixTime", 0) > 0:
        boost_end = self.data.wiserhub.getRoom(self.room_id).get("OverrideTimeoutUnixTime", 0)

        attrs["boost_end"] = dt.utc_from_timestamp(boost_end)

        if boost_end > 0:
            boost_remaining = dt.utc_from_timestamp(
                self.data.wiserhub.getRoom(self.room_id).get("OverrideTimeoutUnixTime", 0)
                ) - dt.utc_from_timestamp(self.data.wiserhub.getSystem().get("UnixTime", 0))
            attrs["boost_remaining"] = int(boost_remaining.total_seconds()/60)
        else:
            attrs["boost_remaining"] = 0
        

            
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

        _LOGGER.info("Setting temperature for %s to %s", self.name, target_temperature)

        await self.hass.async_add_executor_job(
            partial(
                self.data.wiserhub.setRoomTemperature, self.room_id, target_temperature,
            )
        )
        self._force_update = True
        await self.async_update_ha_state(True)

        return True

    async def set_room_mode(self, room_id, mode, boost_temp=None, boost_time=None):
        """Set to default values if not passed in."""
        boost_temp = self.data.boost_temp if boost_temp is None else boost_temp
        boost_time = self.data.boost_time if boost_time is None else boost_time
        _LOGGER.debug("Setting Room Mode to %s for roomId %s", mode, self.room_id)
        await self.hass.async_add_executor_job(
            partial(
                self.data.wiserhub.setRoomMode, room_id, mode, boost_temp, boost_time,
            )
        )
        self._force_update = True
        await self.async_update_ha_state(True)
        return True

    async def async_added_to_hass(self):
        """Subscribe for update from the hub."""

        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, "WiserHubUpdateMessage", async_update_state
            )
        )
