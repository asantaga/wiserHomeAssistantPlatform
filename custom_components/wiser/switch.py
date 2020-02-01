import asyncio

from homeassistant.components.switch import SwitchDevice
from .const import (
    _LOGGER,
    DOMAIN,
    WISER_SWITCHES
)


async def async_setup_platform(hass, config, async_add_entities , discovery_info=None):
    """Add the Wiser Switch entities"""
    entities = []
    data = hass.data[DOMAIN]
    
    for switchType, hubKey in WISER_SWITCHES.items():
        entities.append(WiserSwitch(hass, data, switchType, hubKey))
    

    if len(entities):
        async_add_entities(entities)


"""
Switch to set the status of the Wiser Operation Mode (Away/Normal)
"""


class WiserSwitch(SwitchDevice):
    def __init__(self, hass, data, switchType, hubKey):
        """Initialize the sensor."""
        _LOGGER.info('Wiser {} Switch Init'.format(switchType))
        self.data = data
        self._force_update = False
        self.hass = hass
        self.hub_key = hubKey
        self.switch_type = switchType
        self.awayTemperature = None

    async def async_update(self):
        _LOGGER.debug('Wiser {} Switch Update requested'.format(self.switch_type))
        if self._force_update:
            await self.data.async_update(no_throttle = True)
            self._force_update = False
        else:
            await self.data.async_update()
            
        if self.switch_type == "Away Mode":
            self.awayTemperature = round(self.data.wiserhub.getSystem().get('AwayModeSetPointLimit') / 10,1)

    @property
    def name(self):
        """Return the name of the Device """
        return 'Wiser ' + self.switch_type

    @property
    def should_poll(self):
        """Return the polling state."""
        return True

    @property
    def is_on(self):
        """Return true if device is on."""
        status = self.data.wiserhub.getSystem().get(self.hub_key)
        _LOGGER.debug("{}: {}".format(self.switch_type,status))
        if self.switch_type == "Away Mode":
            return status and status.lower() == "away"
        else:
            return status

    async def async_turn_on(self, **kwargs):
        """Turn the device on."""
        if self.switch_type == "Away Mode":
            await self.data.set_away_mode(True, self.awayTemperature)
            self._force_update = True
        else:
            await self.data.set_system_switch(self.hub_key, True)
        return True

    async def async_turn_off(self, **kwargs):
        """Turn the device off."""
        if self.switch_type == "Away Mode":
            await self.data.set_away_mode(False, self.awayTemperature)
            self._force_update = True
        else:
            await self.data.set_system_switch(self.hub_key, False)
        return True
