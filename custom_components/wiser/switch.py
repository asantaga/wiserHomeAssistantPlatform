import logging
import time
import json

from homeassistant.components.switch import SwitchDevice

_LOGGER = logging.getLogger(__name__)
DOMAIN = 'wiser'


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Add the Wiser Switch entities"""

    entities = []
    handler = hass.data[DOMAIN]  # Get Handler

    entities.append(WiserAwaySwitch(handler))

    if len(entities):
        add_devices(entities)


"""
Switch to set the status of the Wiser Operation Mode (Away/Normal)
"""


class WiserAwaySwitch(SwitchDevice):
    def __init__(self, handler):
        """Initialize the sensor."""
        _LOGGER.info('Wiser Away Mode Switch Init')
        self.ison = True
        self.handler = handler
        self.overrideType = self.handler.get_hub_data().getSystem(). \
            get('OverrideType')
        self.awayTemperature = self.handler.get_hub_data().getSystem(). \
            get('AwayModeSetPointLimit')

    def update(self):
        _LOGGER.debug('Wiser Away Mode Switch Update requested')
        self.handler.update()
        self.overrideType = self.handler.get_hub_data().getSystem(). \
            get('OverrideType')
        self.awayTemperature = self.handler.get_hub_data().getSystem(). \
            get('AwayModeSetPointLimit')

    @property
    def name(self):
        """Return the name of the Device """
        return 'Wiser Away Mode'

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def is_on(self):
        """Return true if device is on."""
        return self.overrideType and self.overrideType == "Away"

    def turn_on(self, **kwargs):
        """Turn the device on."""
        self.handler.set_away_mode(True, self.awayTemperature)
        return True

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self.handler.set_away_mode(False, self.awayTemperature)
        return True
