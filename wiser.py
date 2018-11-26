"""
Drayton Wiser Compoment for Wiser System

Includes Climate and Sensor Devices

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelo.santagata@gmail.com
"""

import logging
import time
import requests
from socket import timeout
from threading import Lock
import json
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import load_platform
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_SCAN_INTERVAL
from .wiserAPI import wiserHub

# TODO : Once the core library is added to PyPi will modify this
#REQUIREMENTS = ['package name'']

_LOGGER = logging.getLogger(__name__)
NOTIFICATION_ID = 'wiser_notification'
NOTIFICATION_TITLE = 'Wiser Component Setup'

DOMAIN = 'wiser'
DATA_KEY = 'wiser'

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=300): cv.time_period,
})


def setup(hass, config):
    hubHost=config[DOMAIN][0][CONF_HOST]
    password=config[DOMAIN][0][CONF_PASSWORD]
    scan_interval=    config[DOMAIN][0][CONF_SCAN_INTERVAL].total_seconds()
    _LOGGER.error("Wiser Component setup with HubIp =  {}".format(hubHost))
    hass.data[DATA_KEY] = WiserHubHandle(hubHost, password, scan_interval)

    _LOGGER.info("Wiser Component Setup Completed")

    load_platform(hass, 'climate', DOMAIN, {}, config)
    load_platform(hass, 'sensor', DOMAIN, {}, config)
    return True

"""
Single parent class to coordindate the rest calls to teh Heathub
"""
class WiserHubHandle:
    

    def __init__(self, ip, secret, scan_interval):
        self.scan_interval = scan_interval
        self.ip = ip
        self.secret = secret
        self.scan_interval
        self.wiserHub=wiserHub.wiserHub(self.ip,self.secret)
        self.mutex = Lock()
        self._updatets = time.time()
       

    def getHubData(self):
    
        return self.wiserHub

    def update(self):
        _LOGGER.error("Component Wiser : Update Requested")
        with self.mutex:
            if (time.time() - self._updatets) >= self.scan_interval:
                _LOGGER.debug("Updating Wiser Data Set")
                try:
                    self.wiserHub.refreshData()
                except timeout as timeoutex:
                    _LOGGER.error("Wiser Component : Timed out whilst connecting to {}, with error {}".format(self.ip,str(timeoutex)))
                    hass.components.persistent_notification.create("Error: {}<br /> You will need to restart Home Assistant after fixing.".format(ex), title=NOTIFICATION_TITLE, notification_id=NOTIFICATION_ID)
                    return False
                except json.decoder.JSONDecodeError as JSONex:
                    _LOGGER.error("Wiser Component : Data not JSON when getting Data from hub, did you enter the right URL? error {}".format(str(timeoutex)))
                    hass.components.persistent_notification.create("Error: {}<br /> You will need to restart Home Assistant after fixing.".format(ex), title=NOTIFICATION_TITLE, notification_id=NOTIFICATION_ID)   
                    return False
                self._updatets = time.time()
                return True
            else:
                _LOGGER.debug("Component Wiser : Skipping update (data already gotten within scan interval)")

