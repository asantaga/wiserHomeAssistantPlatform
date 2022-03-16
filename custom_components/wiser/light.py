
"""Support for Wiser lights vis Wiser Hub"""
import logging

from functools import partial

import voluptuous as vol

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    SUPPORT_BRIGHTNESS,
    LightEntity,
)
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, entity_platform

from .const import DATA, DOMAIN, MANUFACTURER, WISER_SERVICES
from .helpers import get_device_name, get_identifier, get_unique_id
from .schedules import WiserScheduleEntity

MANUFACTURER='Schneider Electric'

_LOGGER = logging.getLogger(__name__)

ATTR_COPYTO_ENTITY_ID = "to_entity_id"
ATTR_FILENAME = "filename"
ATTR_TIME_PERIOD = "time_period"
ATTR_TEMPERATURE_DELTA = "temperature_delta"

STATUS_AWAY = "Away Mode"
STATUS_AWAY_BOOST = "Away Boost"

STATUS_AWAY = "Away Mode"
STATUS_OVERRIDE = "Override"

LIGHT_MODE_ON= "Manual"
LIGHT_MODE_AUTO= "Auto"

LIGHT_MODE_WISER_TO_HASS = {
        "Auto": LIGHT_MODE_AUTO,
        "Manual": LIGHT_MODE_ON,
        
}


LIGHT_MODE_HASS_TO_WISER = {
    LIGHT_MODE_AUTO: "Auto",
    LIGHT_MODE_ON: "Manual",
}  

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    wiser_lights = []
    if data.wiserhub.devices.lights:
        _LOGGER.debug("Setting up light entities")
        for light in data.wiserhub.devices.lights.all:
            if light.is_dimmable:
                wiser_lights.append(
                    WiserDimmerLight(data, light.id)
                )
        async_add_entities(wiser_lights, True)


class WiserLight(LightEntity, WiserScheduleEntity):
    """WiserLight ClientEntity Object."""

    def __init__(self, data, light_id):
        """Initialize the sensor."""
        self._data = data
        self._light_id = light_id
        self._light = self._data.wiserhub.devices.lights.get_by_id(light_id)
        self._name = self._light.name
        self._schedule = self._light.schedule
        self._light_modes_list = [modes for modes in LIGHT_MODE_HASS_TO_WISER.keys()]
        _LOGGER.info(f"{self._data.wiserhub.system.name} {self._name} init")

    async def async_force_update(self):
        _LOGGER.debug(f"{self._light.name} requested hub update")
        await self._data.async_update(no_throttle=True)


    async def async_update(self):
        """Async Update method ."""
        _LOGGER.debug(f"Wiser {self.name} Light Update requested")
        self._light = self._data.wiserhub.devices.lights.get_by_id(self._light_id)
        self._schedule = self._light.schedule

    @property
    def is_on(self):
        """Return the boolean response if the node is on."""
        return self._light.is_on

    @property
    def name(self):
        """Return the name of the Device.""" 
        return f"{get_device_name(self._data, self._light.id)} Light"

    @property
    def icon(self):
        """Return icon."""
        if self._light.mode == "Auto":
            return "mdi:lightbulb-auto" if self.is_on else "mdi:lightbulb-auto-outline"
        else:
            return "mdi:lightbulb" if self.is_on else "mdi:lightbulb-outline"


    @property
    def light_modes(self):
        """Return the list of available operation modes."""
        return self._light_modes_list
   
    def set_light_mode(self, light_mode):
        """Set new operation mode."""  
        _LOGGER.debug(
            f"Setting LIGHT mode to {light_mode} for {self._light.name}"
        )
        try:
            self._light.mode = LIGHT_MODE_HASS_TO_WISER[light_mode]
            pass
        except KeyError:
            _LOGGER.error(f"Invalid LIGHT mode.  Options are {self.light_modes}")
        self.hass.async_create_task(
            self.async_force_update()
        )
        return True

    @property
    def mode(self):
        return self._ligth.mode 

    @property
    def away_action(self):
        """Return the state for away_action."""
        return self._light.away_action
 
    @property
    def unique_id(self):
        return get_unique_id(self._data, "device", "light", self.name)

    @property
    def should_poll(self):
        """Return the polling state."""
        return False

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._light.id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._light.id))},
                "manufacturer": MANUFACTURER,
                "model": self._data.wiserhub.devices.get_by_id(self._light_id).model,
                "sw_version": self._light.firmware_version,
                "serial_number" : self._data.wiserhub.devices.get_by_id(self._light_id).serial_number,
                "product_type": self._light.product_type,
                "product_identifier": self._light.product_identifier,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        attrs = {}
        #attrs = super().state_attributes
        return attrs

    async def async_added_to_hass(self):
        """Subscribe for update from the hub."""

        async def async_update_state():
            """Update light state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._data.wiserhub.system.name}-HubUpdateMessage", async_update_state
            )
        )


class WiserDimmerLight(WiserLight):
    """A Class for an Wiser light entity."""
    def __init__(self, data, light_id):
        """Initialize the sensor."""
        super().__init__(data, light_id)

    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_BRIGHTNESS

    @property
    def brightness(self):
        """Return the brightness of this light between 0..100."""
        return round((self._light.current_percentage / 100) * 255)

    async def async_turn_on(self, **kwargs):
        """Turn light on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = int(kwargs[ATTR_BRIGHTNESS])
            await self.hass.async_add_executor_job(
                setattr, self._light, "current_percentage", round((brightness / 255) * 100)
            )
        else:
            await self.hass.async_add_executor_job(
                self._light.turn_on
            )
        await self.async_force_update()
        return True

    async def async_turn_off(self, **kwargs):
        """Turn light off."""
        await self.hass.async_add_executor_job(
            self._light.turn_off
        )
        await self.async_force_update()
        return True

    #Added by LGO44   
     
    @property
    def current_level(self):
        """Return current level from data."""
        return self._light.current_level

    @property
    def manual_level(self):
        """Return manual level from data."""
        return self._light.manual_level
 
    @property
    def output_range_maximum(self):
        """Return max level from data."""
        return self._light.output_range.maximum

    @property
    def output_range_minimum(self):
        """Return min level from data."""
        return self._light.output_range.minimum

    @property
    def target_state(self):
        """Return target state."""
        return self._light.target_state
   
    @property
    def target_percentage(self):
        """Return target percentage."""
        return self._light.target_percentage
        
    @property
    def scheduled_percentage(self):
        """Return scheduled percentage."""
        return self._light.scheduled_percentage

    @property
    def schedule_id(self):
        """Return scheduled id."""
        return self._light.schedule_id 
        
    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        attrs = super().extra_state_attributes
        # Room
        if  self._data.wiserhub.rooms.get_by_id(self._light.room_id) is not None:
            attrs["room"] = self._data.wiserhub.rooms.get_by_id(self._light.room_id).name
        else:
            attrs["room"] = "Unassigned" 
        # Identification
        attrs["name"] = self._light.name
        attrs["model"] = self._light.model
        attrs["product_type"] = self._light.product_type
        attrs["product_identifier"] = self._light.product_identifier
        #attrs["Vendor"] = MANUFACTURER
        attrs["product_model"] = self._light.product_model
        attrs["serial_number"] = self._light.serial_number
        attrs["firmware"] = self._light.firmware_version                
               
        # Settings
        attrs["is_dimmable"] = self._light.is_dimmable
        attrs["output_range_min"] = self._light.output_range.minimum
        attrs["output_range_max"] = self._light.output_range.maximum
        attrs["mode"] = self._light.mode
        attrs["away_mode_action"] = self._light.away_mode_action
 
        #Command State
        attrs["control_source"] = self._light.control_source  
        #Status 
        attrs["current_state"] = self._light.current_state    
        
        attrs["current_percentage"] = self._light.current_percentage
        attrs["current_level"] = self._light.current_level
        attrs["target_state"] = self._light.target_state
        attrs["target_percentage"] = self._light.target_percentage
        attrs["manual_level"] = self._light.manual_level
        attrs["override_level"] = self._light.override_level
        #Schedule
        attrs["scheduled_percentage"] = self._light.scheduled_percentage
        attrs["schedule_id"] = self._light.schedule_id
        if self._light.schedule:
            attrs["next_day_change"] = str(self._light.schedule.next.day)
            attrs["next_schedule_change"] = str(self._light.schedule.next.time)
            attrs["next_schedule_percentage"] = self._light.schedule.next.setting    
        return attrs
  



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