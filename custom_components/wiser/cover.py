"""
Cover Platform Device for Wiser.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
from functools import partial

import voluptuous as vol



from homeassistant.components.cover import (
    SUPPORT_OPEN,
    SUPPORT_CLOSE,
    SUPPORT_SET_POSITION,
    SUPPORT_STOP,
    STATE_CLOSED,
    STATE_OPEN,
    STATE_CLOSING,
    STATE_OPENING,
    ATTR_CURRENT_POSITION,
    ATTR_POSITION,
    CoverEntity
)
from homeassistant.const import ATTR_ENTITY_ID, ATTR_TEMPERATURE, TEMP_CELSIUS
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt

from wiserHeatAPIv2.wiserhub import (
    TEMP_MINIMUM,
    TEMP_MAXIMUM
)
from .schedules import WiserScheduleEntity

from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
    ROOM,
    WISER_SERVICES
)
from .helpers import get_device_name, get_identifier, get_room_name, get_unique_id

import logging


MANUFACTURER='Schneider Electric'

_LOGGER = logging.getLogger(__name__)

ATTR_COPYTO_ENTITY_ID = "to_entity_id"
ATTR_FILENAME = "filename"
ATTR_TIME_PERIOD = "time_period"
ATTR_TEMPERATURE_DELTA = "temperature_delta"

STATUS_AWAY = "Away Mode"
STATUS_AWAY_BOOST = "Away Boost"

SHUTTER_MODE_ON= "Manual"
SHUTTER_MODE_AUTO= "Auto"

WISER_PRESET_TO_HASS = {
    "FromAwayMode": STATUS_AWAY,
    "FromManualMode": None,
    "FromSchedule": None,
}

SHUTTER_MODE_WISER_TO_HASS = {
        "Auto": SHUTTER_MODE_AUTO,
        "Manual": SHUTTER_MODE_ON,
        
}


SHUTTER_MODE_HASS_TO_WISER = {
    SHUTTER_MODE_AUTO: "Auto",
    SHUTTER_MODE_ON: "Manual",
}  
SUPPORT_FLAGS =  SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION | SUPPORT_STOP
#| STATE_CLOSED | STATE_OPEN | STATE_CLOSING | STATE_OPENING,




async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser shutter device."""

    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler

    wiser_shutters = []
    if data.wiserhub.devices.shutters:
        _LOGGER.debug("Setting up shutter entities")
        for shutter in data.wiserhub.devices.shutters.all :
            if shutter.product_type=="Shutter":
                wiser_shutters.append ( 
                    WiserShutter(data, shutter.id ) 
                )
        async_add_entities(wiser_shutters, True)       

 


class WiserShutter(CoverEntity, WiserScheduleEntity):
    """Wisershutter ClientEntity Object."""

    def __init__(self, data, shutter_id):
        """Initialize the sensor."""
        self._data = data
        self._shutter_id = shutter_id
        self._shutter = self._data.wiserhub.devices.shutters.get_by_id(self._shutter_id)
        self._name = self._shutter.name
        self._schedule = self._shutter.schedule
        self._shutter_modes_list = [modes for modes in SHUTTER_MODE_HASS_TO_WISER.keys()]

        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} init")

    async def async_force_update(self):
        _LOGGER.debug(f"{self._shutter.name} requested hub update")
        await self._data.async_update(no_throttle=True)

    async def async_update(self):
        """Async update method."""
        self._shutter = self._data.wiserhub.devices.shutters.get_by_id(self._shutter_id)
        self._schedule = self._shutter.schedule
      
    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_FLAGS

    @property
    def scheduled_position(self):
        """Return scheduled position from data."""
        return self._shutter.scheduled_lift


    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._shutter_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._shutter_id))},
                "manufacturer": MANUFACTURER,
                #"model": self._shutter.product_model,
                "model": self._data.wiserhub.devices.get_by_id(self._shutter_id).model,
                "serial_number" : self._data.wiserhub.devices.get_by_id(self._shutter_id).serial_number,
                "product_type": self._shutter.product_type,
                "product_identifier": self._shutter.product_identifier,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def icon(self):
        """Return icon to show if shutter is closed or Open."""
        
        return "mdi:window-shutter" if self.is_closed else "mdi:window-shutter-open"
        

    @property
    def shutter_modes(self):
        """Return the list of available operation modes."""
        return self._shutter_modes_list

    @property
    def away_action_mode(self):
        """Return the list of available operation modes."""
        return self._away_action_mode
    
    def set_away_action_mode(self):
        """Return the list of available operation modes."""
        self._away_action_mode = "NoChange" 
       

    @property
    def name(self):
     #   Return Name of device.
        return f"{get_device_name(self._data, self._shutter_id)} Control"   
        """ {self._name}"""

    @property
    def should_poll(self):
        """We don't want polling so return false."""
        return True

    @property
    def is_open(self):
        return True if self._shutter.is_open else 'OFF'
        
    @property
    def is_closed(self):
        return True if self._shutter.is_closed else 'OFF'  

    @property
    def current_state(self):
        if self._shutter.is_open :
            return "Open"
        elif  self._shutter.is_closed :
            return "Closed"
        elif (self._shutter.is_open == False and self._shutter.is_closed == False):
            return "Middle"
        
         
    @property
    def shutter_unit(self):
        """Return percent units."""
        return "%"

    @property
    def unique_id(self):
        """Return unique Id."""
        return f"{self._data.wiserhub.system.name}-Wisershutter-{self._shutter_id}-{self.name}"

    @property
    def schedule_id(self):
        """Return schedule Id."""
        return self._shutter.schedule_id

    @property
    def product_model(self):
        """Return schedule Id."""
        return self._shutter.product_model
                
   
    @property
    def target_scheduled_lift(self):
        """Return target lift."""
        return self._shutter.target_scheduled_lift

    @property
    def lift_open_time(self):
        """Return target lift."""
        return self._shutter.drive_config.get("LiftOpenTime")

    
    @property
    def current_cover_position(self):
        """Return current position from data."""
        return self._shutter.current_lift


    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs[ATTR_POSITION]
        self._shutter.current_lift = position



    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes
        # Shutter Identification
        attrs["name"] = self._shutter.name
        attrs["model"] = self._shutter.model
        attrs["product_type"] = self._shutter.product_type
        attrs["product_identifier"] = self._shutter.product_identifier
        attrs["product_model"] = self._shutter.product_model
        attrs["serial_number"] = self._shutter.serial_number
        attrs["firmware"] = self._shutter.firmware_version
        # Room
        if  self._data.wiserhub.rooms.get_by_id(self._shutter.room_id) is not None:
            attrs["room"] = self._data.wiserhub.rooms.get_by_id(self._shutter.room_id).name
        else:
            attrs["room"] = "Unassigned"     
        # Settings
        attrs["shutter_id"] = self._shutter_id
        attrs["away_mode_action"] = self._shutter.away_mode_action   
        attrs["mode"] = self._shutter.mode
        attrs["lift_open_time"] = self._shutter.drive_config.open_time
        attrs["lift_close_time"] = self._shutter.drive_config.close_time
        # Command state
        attrs["control_source"] = self._shutter.control_source
        # Status
        attrs["is_open"] = self._shutter.is_open
        attrs["is_closed"] = self._shutter.is_closed
        if self._shutter.is_open :
            attrs["current_state"] = "Open"
        elif  self._shutter.is_closed :
            attrs["current_state"] ="Closed"
        elif (self._shutter.is_open == False and self._shutter.is_closed == False):
            attrs["current_state"] = "Middle" 
        attrs["lift_movement"] = self._shutter.lift_movement
        # Positions
        attrs["current_lift"] = self._shutter.current_lift
        attrs["manual_lift"] = self._shutter.manual_lift
        attrs["target_lift"] = self._shutter.target_lift
        attrs["scheduled_lift"] = self._shutter.scheduled_lift
        # Schedule
        attrs["schedule_id"] = self._shutter.schedule_id        
        if self._shutter.schedule:
            attrs["next_day_change"] = str(self._shutter.schedule.next.day)
            attrs["next_schedule_change"] = str(self._shutter.schedule.next.time)
            attrs["next_schedule_state"] = self._shutter.schedule.next.setting    
            
            
        return attrs

 


    # added by LGO44 tested OK 2022 02 25

    async def async_close_cover(self, **kwargs):
        """Close shutter"""
        await self.hass.async_add_executor_job(
            self._shutter.close
        )              
        await self.async_force_update()
        return True

    async def async_open_cover(self, **kwargs):
        """Close shutter"""
        await self.hass.async_add_executor_job(
            self._shutter.open
        )
                
        await self.async_force_update()
        return True

    async def async_stop_cover(self, **kwargs):
        """Stop shutter"""       
        await self.hass.async_add_executor_job(
            self._shutter.stop
        )
                
        await self.async_force_update()
        return True

    @property
    def current_cover_position(self):
        """Return current position from data."""
        return self._shutter.current_lift

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs[ATTR_POSITION]
        self._shutter.current_lift = position


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