"""
Climate Platform Device for Wiser Rooms


https://github.com/asantaga/wiserHomeAssistantPlatform
Angelo.santagata@gmail.com

"""
import logging

import voluptuous as vol
# Import the device class from the component that you want to support
from homeassistant.components.climate import (
    ClimateDevice, STATE_AUTO ,SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_OPERATION_MODE)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import TEMP_CELSIUS,ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
DOMAIN = "wiser"



SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    handler = hass.data[DOMAIN] # Get Handler
    hubData = handler.getHubData()
    handler.update()
    wiserRooms = []

    # Get Rooms
    for room in handler.getHubData().getRooms():
        wiserRooms.append(WiserRoom(room.get('id'),handler))
    add_devices(wiserRooms)

    

# Definition of WiserRoom
class WiserRoom(ClimateDevice):

    def __init__(self, roomId,handler):
        """Initialize the sensor."""
        _LOGGER.info('Wiser Room Initialisation')
        self._operation_list = [STATE_AUTO]
        self.handler=handler
        self.roomId=roomId

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def should_poll(self):
        return True
    @property
    def state(self):
        return self.handler.getHubData().getRoom(self.roomId).get("Mode")
    @property
    def name(self):
        return "Wiser "+self.handler.getHubData().getRoom(self.roomId).get("Name")

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        temp=self.handler.getHubData().getRoom(self.roomId).get("CalculatedTemperature")/10
        if temp<-20:
            # Sometimes we get really low temps (like -3000!), not sure why, if we do then just set it to -20 for now till i debug this.
            temp=-20

        return temp 

    @property
    def icon(self):
        return "mdi:oil-temperature"

    @property
    def current_operation(self):
        return self.handler.getHubData().getRoom(self.roomId).get("Mode")

    @property
    def target_temperature(self):
          return self.handler.getHubData().getRoom(self.roomId).get("CurrentSetPoint")/10

   
    def update(self):
        _LOGGER.info("Component Wiser Climate : Update called for room {}".format(self.roomId))
        self.handler.update()

