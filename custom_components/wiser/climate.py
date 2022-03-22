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
    SUPPORT_TARGET_TEMPERATURE
)

from homeassistant.components.climate import ClimateEntity
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt

from wiserHeatAPIv2.wiserhub import (
    TEMP_MINIMUM,
    TEMP_MAXIMUM
)

from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
    ROOM,
    SETPOINT_MODE_BOOST,
    SETPOINT_MODE_BOOST_AUTO,
    WISER_BOOST_PRESETS,
    WISER_SERVICES
)
from .helpers import get_device_name, get_identifier
from .schedules import WiserScheduleEntity

import logging
_LOGGER = logging.getLogger(__name__)

ATTR_COPYTO_ENTITY_ID = "to_entity_id"
ATTR_FILENAME = "filename"
ATTR_TIME_PERIOD = "time_period"
ATTR_TEMPERATURE_DELTA = "temperature_delta"

STATUS_AWAY = "Away Mode"
STATUS_AWAY_BOOST = "Away Boost"
STATUS_AWAY_OVERRIDE = "Away Override"
STATUS_BOOST = "Boost"
STATUS_COMFORT = "Comfort"
STATUS_ECO = "EcoIQ"
STATUS_OVERRIDE = "Override"

WISER_PRESET_TO_HASS = {
    "FromAwayMode": STATUS_AWAY,
    "FromManualMode": None,
    "FromBoost": STATUS_BOOST,
    "FromManualOverrideDuringAway": STATUS_AWAY_OVERRIDE,
    "FromBoostDuringAway": STATUS_AWAY_BOOST,
    "FromManualOverride": STATUS_OVERRIDE,
    "FromEcoIQ": STATUS_ECO,
    "FromSchedule": None,
    "FromComfortMode": STATUS_COMFORT,
}

WISER_PRESETS = {
    "Advance Schedule": 0,
    "Cancel Overrides": 0
}
WISER_PRESETS.update(WISER_BOOST_PRESETS)

HVAC_MODE_WISER_TO_HASS = {
        "Auto": HVAC_MODE_AUTO,
        "Manual": HVAC_MODE_HEAT,
        "Off": HVAC_MODE_OFF,
}

HVAC_MODE_HASS_TO_WISER = {
    HVAC_MODE_AUTO: "Auto",
    HVAC_MODE_HEAT: "Manual",
    HVAC_MODE_OFF: "Off",
}

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    if data.wiserhub.rooms:
        _LOGGER.debug("Setting up Room climate entities")
        wiser_rooms = [
            WiserRoom(hass, data, room.id) for room in data.wiserhub.rooms.all if len(room.devices) > 0
        ]
        async_add_entities(wiser_rooms, True)


        # Setup services
        platform = entity_platform.async_get_current_platform()

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_BOOST_HEATING"],
            {
                vol.Required(ATTR_TIME_PERIOD, default=data.boost_time): vol.Coerce(int),
                vol.Any(
                    vol.Optional(ATTR_TEMPERATURE_DELTA, default=0),
                    vol.Optional(ATTR_TEMPERATURE, default=0),
                ): vol.Coerce(float)
            },
            "async_boost_heating"
        )

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_GET_HEATING_SCHEDULE"],
            {
                vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
            },
            "async_get_schedule"
        )

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_SET_HEATING_SCHEDULE"],
            {
                vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
            },
            "async_set_schedule"
        )

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_COPY_HEATING_SCHEDULE"],
            {
                vol.Required(ATTR_COPYTO_ENTITY_ID): cv.entity_id,
            },
            "async_copy_schedule"
        )


class WiserRoom(ClimateEntity, WiserScheduleEntity):
    """WiserRoom ClientEntity Object."""

    def __init__(self, hass, data, room_id):
        """Initialize the sensor."""
        self._hass = hass
        self._data = data
        self._room_id = room_id
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._hvac_modes_list = [modes for modes in HVAC_MODE_HASS_TO_WISER.keys()]
        self._is_heating = self._room.is_heating
        self._schedule = self._room.schedule

        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} init")

    async def async_force_update(self):
        _LOGGER.debug(f"{self._room.name} requested hub update")
        await self._data.async_update(no_throttle=True)

    async def async_update(self):
        """Async update method."""
        self._room = self._data.wiserhub.rooms.get_by_id(self._room_id)
        self._schedule = self._room.schedule

        # Vars to support change fired events
        self._is_heating = self._room.is_heating
        await self.async_fire_events()

        if not self._room.is_boosted:
            self._boosted_time = 0

    @property
    def current_temperature(self):
        """Return current temp from data."""
        return self._room.current_temperature

    @property
    def current_humidity(self):
        """Return current temp from data."""
        return self._room.current_humidity

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._room_id,"room"),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._room_id,"room"))},
                "manufacturer": MANUFACTURER,
                "model": ROOM.title(),
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def icon(self):
        """Return icon to show if radiator is heating, not heating or set to off."""
        if self._room.mode == "Off":
            return "mdi:radiator-off"
        elif self._room.is_heating:
            return "mdi:radiator"
        else:
            return "mdi:radiator-disabled"

    @property
    def hvac_action(self):
        """Return hvac action from data."""
        return CURRENT_HVAC_HEAT if self._room.is_heating else CURRENT_HVAC_IDLE

    @property
    def hvac_modes(self):
        """Return the list of available operation modes."""
        return self._hvac_modes_list

    def set_hvac_mode(self, hvac_mode):
        """Set new operation mode."""
        _LOGGER.debug(
            f"Setting HVAC mode to {hvac_mode} for {self._room.name}"
        )
        try:
            self._room.mode = HVAC_MODE_HASS_TO_WISER[hvac_mode]
        except KeyError:
            _LOGGER.error(f"Invalid HVAC mode.  Options are {self.hvac_modes}")
        self.hass.async_create_task(
            self.async_force_update()
        )
        return True

    @property
    def max_temp(self):
        """Return max temp from data."""
        return TEMP_MAXIMUM

    @property
    def min_temp(self):
        """Return min temp from data."""
        return TEMP_MINIMUM

    @property
    def name(self):
        """Return Name of device."""
        return get_device_name(self._data, self._room_id, "room")

    @property
    def preset_mode(self):
        """Get current preset mode."""
        try:
            if WISER_PRESET_TO_HASS[self._room.target_temperature_origin] == STATUS_BOOST:
                if int(self._room.boost_time_remaining/60) != 0:
                    return f"{STATUS_BOOST} {int(self._room.boost_time_remaining/60)}m"
                else:
                    return STATUS_BOOST
            else:
                return WISER_PRESET_TO_HASS[self._room.target_temperature_origin]
        except KeyError:
            return None
    
    @property
    def preset_modes(self):
        """Return the list of available preset modes."""
        return list(WISER_PRESETS.keys())

    async def async_set_preset_mode(self, preset_mode):
        """Async call to set preset mode ."""
        _LOGGER.debug(
                f"Setting Preset Mode {preset_mode} for {self._room.name}"
            )
        try:
            if preset_mode == "Advance Schedule":
                await self.hass.async_add_executor_job(
                    self._room.schedule_advance
                )
            elif WISER_PRESETS[preset_mode] == 0:
                await self.hass.async_add_executor_job(
                    self._room.cancel_overrides
                )
            else:
                boost_time = WISER_PRESETS[preset_mode]
                boost_temp = self._data.boost_temp
                await self.hass.async_add_executor_job(
                    self._room.boost, boost_temp, boost_time
                )
        except KeyError:
            _LOGGER.error(f"Invalid preset mode.  Options are {self.preset_modes}")
        
        await self.async_force_update()
        return True

    @property
    def should_poll(self):
        """We don't want polling so return false."""
        return False

    @property
    def state(self):
        """Return state"""
        return HVAC_MODE_WISER_TO_HASS[self._room.mode]

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes

        # If boosted show boost end time
        if self._room.is_boosted:
            attrs["boost_end"] = self._room.boost_end_time

        attrs["boost_time_remaining"] = int(self._room.boost_time_remaining/60)
        attrs["percentage_demand"] = self._room.percentage_demand
        attrs["control_output_state"] = "On" if self._room.is_heating else "Off"
        attrs["heating_rate"] = self._room.heating_rate
        attrs["window_state"] = self._room.window_state
        attrs["window_detection_active"] = self._room.window_detection_active
        attrs["away_mode_supressed"] = self._room.away_mode_suppressed
        # Room can have no schedule
        if self._room.schedule:
            attrs["current_schedule_temp"] = self._room.schedule.current_setting
            attrs["next_schedule_change"] = str(self._room.schedule.next.time)
            attrs["next_schedule_temp"] = self._room.schedule.next.setting
        attrs["is_boosted"] = self._room.is_boosted
        attrs["is_override"] = self._room.is_override
        attrs["is_heating"] = self._room.is_heating
        return attrs

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS
    
    @property
    def target_temperature(self):
        """Return target temp."""
        if self._room.mode == "Off":
            return None
        return self._room.current_target_temperature

    async def async_set_temperature(self, **kwargs):
        """Set new target temperatures."""
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        
        if target_temperature is None:
            return False

        if (self._data.setpoint_mode == SETPOINT_MODE_BOOST 
            or (self._data.setpoint_mode == SETPOINT_MODE_BOOST_AUTO and self.state == HVAC_MODE_AUTO)
        ):
            _LOGGER.info(f"Setting temperature for {self.name} to {target_temperature} using boost")
            await self.hass.async_add_executor_job(
                self._room.set_target_temperature_for_duration, target_temperature, self._data.boost_time
            )
        else:
            _LOGGER.info(f"Setting temperature for {self.name} to {target_temperature}")
            await self.hass.async_add_executor_job(
                self._room.set_target_temperature, target_temperature
            )
        await self.async_force_update()
        return True

    @property
    def temperature_unit(self):
        """Return temp units."""
        return TEMP_CELSIUS

    @property
    def unique_id(self):
        """Return unique Id."""
        return f"{self._data.wiserhub.system.name}-WiserRoom-{self._room_id}-{self.name}"


    async def async_fire_events(self):
        # Fire event if is_heating status changed
        if self._is_heating != self._room.is_heating:
            self._hass.bus.fire("wiser_room_heating_status_changed", {
                "entity_id": self.entity_id,
                "is_heating": self._room.is_heating,
                "is_boosted": self._room.is_boosted,
                "scheduled_temperature": self._room.scheduled_target_temperature,
                "target_temperature": self._room.current_target_temperature, 
                "current_temperature": self._room.current_temperature
                }
            )

    @callback
    async def async_boost_heating(self, time_period: int, temperature_delta = 0, temperature = 0) -> None:
        """Boost heating for room"""
        # If neither temperature_delta or temperature set then use config boost temp. Issue #216
        if temperature_delta == 0 and temperature == 0:
            temperature_delta = self._data.boost_temp

        if temperature_delta > 0:
            _LOGGER.info(f"Boosting heating for {self._room.name} by {temperature_delta}C for {time_period}m ")
            await self.hass.async_add_executor_job(
                self._room.boost, temperature_delta, time_period
            )
        if temperature > 0 and temperature_delta == 0:
            _LOGGER.info(f"Boosting heating for {self._room.name} to {temperature}C for {time_period}m ")
            await self.hass.async_add_executor_job(
                self._room.set_target_temperature_for_duration, temperature, time_period
            )
        await self.async_force_update()

    @callback
    async def async_get_schedule(self, filename: str) -> None:
        _LOGGER.warning(f"The Save Heating Schedule to File service is deprecated and will be removed in a future release.  Please use the Save Schedule to File service instead")
        try:
            _LOGGER.info(f"Saving {self._room.name} schedule to file {filename}")
            await self.hass.async_add_executor_job(
                self._room.schedule.save_schedule_to_yaml_file, filename
            )
        except:
            _LOGGER.error(f"Saving {self._room.name} schedule to file {filename}")

    @callback
    async def async_set_schedule(self, filename: str) -> None:
        _LOGGER.warning(f"The Set Heating Schedule from File service is deprecated and will be removed in a future release.  Please use the Set Schedule from File service instead")
        try:
            _LOGGER.info(f"Setting {self._room.name} schedule from file {filename}")
            await self.hass.async_add_executor_job(
                self._room.schedule.set_schedule_from_yaml_file, filename
            )
            await self.async_force_update()
        except:
            _LOGGER.error(f"Error setting {self._room.name} schedule from file {filename}")

    @callback
    async def async_copy_schedule(self, to_entity_id)-> None:
        _LOGGER.warning(f"The Copy Heating Schedule service is deprecated and will be removed in a future release.  Please use the Copy Schedule service instead")
        to_room_name = to_entity_id.replace("climate.wiser_","").replace("_"," ")
        try:
            # Add Check that to_entity is of same type as from_entity
            _LOGGER.info(f"Copying schedule from {self._room.name} to {to_room_name.title()}")
            await self.hass.async_add_executor_job(
                    self._room.schedule.copy_schedule, self._data.wiserhub.rooms.get_by_name(to_room_name).schedule.id
                )
            await self.async_force_update()
        except:
            _LOGGER.error(f"Error copying schedule from {self._room.name} to {to_room_name}")

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
