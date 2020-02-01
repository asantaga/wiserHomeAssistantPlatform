"""
Drayton Wiser Compoment for Wiser System

Includes Climate and Sensor Devices

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelo.santagata@gmail.com
"""
import asyncio
import json
#import time
from datetime import datetime, timedelta

from wiserHeatingAPI.wiserHub import wiserHub, TEMP_MINIMUM, TEMP_MAXIMUM
import voluptuous as vol

from homeassistant.const import (
    CONF_HOST,
    CONF_MINIMUM,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.util import Throttle

from .const import (
    _LOGGER,
    CONF_BOOST_TEMP,
    CONF_BOOST_TEMP_TIME,
    DOMAIN,
    NOTIFICATION_ID,
    NOTIFICATION_TITLE,
    VERSION,
    WISER_PLATFORMS
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=0): cv.time_period,
    vol.Optional(CONF_MINIMUM, default=TEMP_MINIMUM): vol.All(vol.Coerce(int)),
    vol.Optional(CONF_BOOST_TEMP, default=2): vol.All(vol.Coerce(int)),
    vol.Optional(CONF_BOOST_TEMP_TIME, default=30): vol.All(vol.Coerce(int))
})

async def async_setup(hass, config):
    
    host = config[DOMAIN][0][CONF_HOST]
    secret = config[DOMAIN][0][CONF_PASSWORD]
    scan_interval = config[DOMAIN][0][CONF_SCAN_INTERVAL]
    
    if scan_interval > timedelta(0):
        MIN_TIME_BETWEEN_UPDATES = scan_interval
    
    _LOGGER.info("Wiser setup with Hub IP =  {} and scan interval of {}".format(host,MIN_TIME_BETWEEN_UPDATES))

    data = WiserHubHandle(hass, config, host, secret)
    await data.async_update()
    
    if data.wiserhub.getDevices is None:
        _LOGGER.error("No Wiser devices found to set up")
        return False
    
    hass.data[DOMAIN] = data
    
    for component in WISER_PLATFORMS:
        hass.async_create_task(
            async_load_platform(
                hass, component, DOMAIN, {}, config
            )
        )

    _LOGGER.info("Wiser Component Setup Completed")
    return True


class WiserHubHandle:
    def __init__(self, hass, config, ip, secret):
        self._hass = hass
        self._config = config
        self.ip = ip
        self.secret = secret
        self.wiserhub = wiserHub(self.ip, self.secret)
        self.minimum_temp = TEMP_MINIMUM
        self.maximum_temp = TEMP_MAXIMUM
        self.boost_temp = self._config[DOMAIN][0][CONF_BOOST_TEMP]
        self.boost_time = self._config[DOMAIN][0][CONF_BOOST_TEMP_TIME]

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        _LOGGER.info("**Update of Wiser Hub data requested**")
        try:
            result = await self._hass.async_add_executor_job(self.wiserhub.refreshData)
            _LOGGER.info("**Wiser Hub data updated**")
        except json.decoder.JSONDecodeError as JSONex:
            _LOGGER.error(
                "Data not JSON when getting Data from hub, " +
                "did you enter the right URL? error {}".
                format(str(JSONex)))
            hass.components.persistent_notification.create(
                "Error: {}" +
                "<br /> You will need to restart Home Assistant " +
                " after fixing.".format(ex), title=NOTIFICATION_TITLE,
                notification_id=NOTIFICATION_ID)

    async def set_away_mode(self, away, away_temperature):
        mode = 'AWAY' if away else 'HOME'
        if self.wiserhub is None:
            self.wiserhub = wiserHub(self.ip, self.secret)
        _LOGGER.debug("Setting away mode to {} with temp {}.".format(mode, away_temperature))
        try:
            self.wiserhub.setHomeAwayMode(mode, away_temperature)
            await self.async_update(no_throttle = True)
        except BaseException as e:
            _LOGGER.debug("Error setting away mode! {}".format(str(e)))
            
    async def set_system_switch(self, switch, mode):
        if self.wiserhub is None:
            self.wiserhub = wiserHub(self.ip, self.secret)
        _LOGGER.debug("Setting {} system switch to {}.".format(switch, "on" if mode else "off"))
        try:
            self.wiserhub.setSystemSwitch(switch, mode)
            await self.async_update(no_throttle = True)
        except BaseException as e:
            _LOGGER.debug("Error setting {} system switch! {}".format(switch, str(e)))


