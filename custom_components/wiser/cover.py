"""
Cover Platform Device for Wiser.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""

from homeassistant.components.cover import (
    SUPPORT_OPEN,
    SUPPORT_CLOSE,
    SUPPORT_SET_POSITION,
    SUPPORT_STOP,
    ATTR_POSITION,
    CoverEntity
)

from homeassistant.helpers.dispatcher import async_dispatcher_connect

from .schedules import WiserScheduleEntity

from .const import (
    DATA,
    DOMAIN,
    MANUFACTURER,
)
from .helpers import get_device_name, get_identifier

import logging

#TODO: Set this based on model of hub
MANUFACTURER='Schneider Electric'

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS =  SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_SET_POSITION | SUPPORT_STOP


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser shutter device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]

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
        self._device_id = shutter_id
        self._device = self._data.wiserhub.devices.shutters.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} init")

    async def async_force_update(self):
        _LOGGER.debug(f"{self._device.name} requested hub update")
        await self._data.async_update(no_throttle=True)

    async def async_update(self):
        """Async update method."""
        self._device = self._data.wiserhub.devices.shutters.get_by_id(self._device_id)
        self._schedule = self._device.schedule
      
    @property
    def supported_features(self):
        """Flag supported features."""
        return SUPPORT_FLAGS

    #TODO: What is this for?
    @property
    def scheduled_position(self):
        """Return scheduled position from data."""
        return self._device.scheduled_lift

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._device_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
                "manufacturer": MANUFACTURER,
                "model": self._data.wiserhub.devices.get_by_id(self._device_id).model,
                "serial_number" : self._data.wiserhub.devices.get_by_id(self._device_id).serial_number,
                "product_type": self._device.product_type,
                "product_identifier": self._device.product_identifier,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @property
    def icon(self):
        """Return icon to show if shutter is closed or Open."""
        return "mdi:window-shutter" if self.is_closed else "mdi:window-shutter-open"

    @property
    def name(self):
        """Return Name of device"""
        return f"{get_device_name(self._data, self._device_id)} Control"   

    @property
    def should_poll(self):
        """We don't want polling so return false."""
        return True

    @property
    def current_cover_position(self):
        """Return current position from data."""
        return self._device.current_lift
        
    @property
    def is_closed(self):
        return self._device.is_closed

    @property
    def is_opening(self):
        return self._device.is_opening

    @property
    def is_closing(self):
        return self._device.is_closing

    @property
    def unique_id(self):
        """Return unique Id."""
        return f"{self._data.wiserhub.system.name}-Wisershutter-{self._device_id}-{self.name}"

    @property
    def extra_state_attributes(self):
        """Return state attributes."""
        # Generic attributes
        attrs = super().state_attributes
        # Shutter Identification
        attrs["name"] = self._device.name
        attrs["model"] = self._device.model
        attrs["product_type"] = self._device.product_type
        attrs["product_identifier"] = self._device.product_identifier
        attrs["product_model"] = self._device.product_model
        attrs["serial_number"] = self._device.serial_number
        attrs["firmware"] = self._device.firmware_version

        # Room
        if  self._data.wiserhub.rooms.get_by_id(self._device.room_id) is not None:
            attrs["room"] = self._data.wiserhub.rooms.get_by_id(self._device.room_id).name
        else:
            attrs["room"] = "Unassigned"     
        
        # Settings
        attrs["shutter_id"] = self._device_id
        attrs["away_mode_action"] = self._device.away_mode_action   
        attrs["mode"] = self._device.mode
        attrs["lift_open_time"] = self._device.drive_config.open_time
        attrs["lift_close_time"] = self._device.drive_config.close_time
        
        # Command state
        attrs["control_source"] = self._device.control_source
        
        # Status
        attrs["is_open"] = self._device.is_open
        attrs["is_closed"] = self._device.is_closed
        if self._device.is_open :
            attrs["current_state"] = "Open"
        elif  self._device.is_closed :
            attrs["current_state"] ="Closed"
        elif (self._device.is_open == False and self._device.is_closed == False):
            attrs["current_state"] = "Middle" 
        attrs["lift_movement"] = self._device.lift_movement
        
        # Positions
        attrs["current_lift"] = self._device.current_lift
        attrs["manual_lift"] = self._device.manual_lift
        attrs["target_lift"] = self._device.target_lift
        attrs["scheduled_lift"] = self._device.scheduled_lift
        
        # Schedule
        attrs["schedule_id"] = self._device.schedule_id        
        if self._device.schedule:
            attrs["schedule_name"] = self._device.schedule.name
            attrs["next_day_change"] = str(self._device.schedule.next.day)
            attrs["next_schedule_change"] = str(self._device.schedule.next.time)
            attrs["next_schedule_state"] = self._device.schedule.next.setting    
            
        return attrs

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        position = kwargs[ATTR_POSITION]
        await self.hass.async_add_executor_job(
            setattr, self._device, "current_lift", position
        )
        await self.async_force_update()

    async def async_close_cover(self, **kwargs):
        """Close shutter"""
        await self.hass.async_add_executor_job(
            self._device.close
        )              
        await self.async_force_update()

    async def async_open_cover(self, **kwargs):
        """Close shutter"""
        await self.hass.async_add_executor_job(
            self._device.open
        )
                
        await self.async_force_update()

    async def async_stop_cover(self, **kwargs):
        """Stop shutter"""       
        await self.hass.async_add_executor_job(
            self._device.stop
        )
        await self.async_force_update()

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
