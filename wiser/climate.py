"""
Climate Platform Device for Wiser Rooms

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""
import logging
import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.components.climate import ClimateDevice
from homeassistant.components.climate.const import (STATE_AUTO,
                                                    SUPPORT_OPERATION_MODE,
                                                    SUPPORT_TARGET_TEMPERATURE)
from homeassistant.const import (ATTR_BATTERY_LEVEL, ATTR_TEMPERATURE,
                                 TEMP_CELSIUS)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)
DOMAIN = 'wiser'

STATE_MANUAL = 'manual'
STATE_BOOST = 'Boost'

SUPPORT_FLAGS = SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    handler = hass.data[DOMAIN]  # Get Handler

    handler.update()
    wiser_rooms = []

    """ Get Rooms """
    for room in handler.get_hub_data().getRooms():
        wiser_rooms.append(WiserRoom(room.get('id'), handler))
    add_devices(wiser_rooms)


""" Definition of WiserRoom """


class WiserRoom(ClimateDevice):

    def __init__(self, room_id, handler):
        """Initialize the sensor."""
        _LOGGER.info("Wiser Room Initialisation")
        self.handler = handler
        self.roomId = room_id
        self._operation_list = [STATE_AUTO, STATE_MANUAL, STATE_BOOST]

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def should_poll(self):
        return True

    @property
    def state(self):
        _LOGGER.info('State requested for room %s', self.roomId)
        return self.handler.get_hub_data().getRoom(self.roomId).get('Mode')

    @property
    def name(self):
        return "Wiser " + self.handler.get_hub_data().getRoom(self.roomId). \
            get('Name')

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def current_temperature(self):
        temp = self.handler.get_hub_data().getRoom(self.roomId). \
                   get('CalculatedTemperature') / 10
        if temp < self.handler.get_minimum_temp():
            """ Sometimes we get really low temps (like -3000!),
                not sure why, if we do then just set it to -20 for now till i
                debug this.
            """
            temp = self.handler.get_minimum_temp()
        return temp

    @property
    def icon(self):
        return "mdi:oil-temperature"

    @property
    def current_operation(self):
        return self.handler.get_hub_data().getRoom(self.roomId).get('Mode')

    @property
    def target_temperature(self):
        return self.handler.get_hub_data().getRoom(self.roomId). \
                   get('CurrentSetPoint') / 10

    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return self._operation_list

    def update(self):
        _LOGGER.debug("*******************************************")
        _LOGGER.debug("WiserRoom Update requested")
        _LOGGER.debug("*******************************************")
        self.handler.update()

    """    https://github.com/asantaga/wiserHomeAssistantPlatform/issues/13 """

    @property
    def state_attributes(self):
        # Generic attributes
        attrs = super().state_attributes
        attrs['percentage_demand'] = self.handler.get_hub_data(). \
            getRoom(self.roomId).get('PercentageDemand')
        attrs['heating_rate'] = self.handler.get_hub_data(). \
            getRoom(self.roomId).get('HeatingRate')
        attrs['window_state'] = self.handler.get_hub_data(). \
            getRoom(self.roomId).get('WindowState')
        attrs['window_detection_active'] = self.handler.get_hub_data(). \
            getRoom(self.roomId).get('WindowDetectionActive')
        attrs['away_mode_supressed'] = self.handler.get_hub_data(). \
            getRoom(self.roomId).get('AwayModeSuppressed')
        return attrs

    """ Set temperature """

    def set_temperature(self, **kwargs):
        """Set new target temperatures."""
        if kwargs.get(ATTR_TEMPERATURE) is None:
            return False
        target_temperature = kwargs.get(ATTR_TEMPERATURE)
        _LOGGER.debug(
            "Setting Device Temperature for roomId {}, temperature {}".
                format(self.roomId, target_temperature))
        _LOGGER.debug("Value of wiserhub {}".format(self.handler))
        self.handler.set_room_temperature(self.roomId, target_temperature)

    def set_operation_mode(self, operation_mode):
        """Set new operation mode."""
        _LOGGER.debug("*******Setting Device Operation {} for roomId {}".
                      format(operation_mode, self.roomId))
        self.handler.set_room_mode(self.roomId, operation_mode)
        return True
