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
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_SCAN_INTERVAL,CONF_MINIMUM


# TODO : Once the core library is added to PyPi will modify this
#REQUIREMENTS = ['package name'']

_LOGGER = logging.getLogger(__name__)
NOTIFICATION_ID = 'wiser_notification'
NOTIFICATION_TITLE = 'Wiser Component Setup'
CONF_BOOST_TEMP_DEFAULT ="20"
CONF_BOOST_TEMP="boost_temp"
CONF_BOOST_TEMP_TIME="boost_temp_time"

DOMAIN = 'wiser'
DATA_KEY = 'wiser'

PLATFORM_SCHEMA = vol.Schema({
    vol.Required(CONF_HOST): cv.string,
    vol.Optional(CONF_PASSWORD): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=300): cv.time_period,
    vol.Optional(CONF_MINIMUM, default=-5): vol.All(vol.Coerce(int)),
    vol.Optional(CONF_BOOST_TEMP, default=20): vol.All(vol.Coerce(int)),
    vol.Optional(CONF_BOOST_TEMP_TIME, default=30): vol.All(vol.Coerce(int))
})


def setup(hass, config):
    hubHost= config[DOMAIN][0][CONF_HOST]
    password= config[DOMAIN][0][CONF_PASSWORD]
    scan_interval= config[DOMAIN][0][CONF_SCAN_INTERVAL].total_seconds()
    minimum_temp= config[DOMAIN][0][CONF_MINIMUM]
    boost_temp= config[DOMAIN][0][CONF_BOOST_TEMP]
    boost_temp_time= config[DOMAIN][0][CONF_BOOST_TEMP_TIME]

    _LOGGER.info("Wiser setup with HubIp =  {}".format(hubHost))
    hass.data[DATA_KEY] = WiserHubHandle(hubHost, password, scan_interval,minimum_temp,boost_temp,boost_temp_time)

    _LOGGER.info("Wiser Component Setup Completed")

    load_platform(hass, 'climate', DOMAIN, {}, config)
    load_platform(hass, 'sensor', DOMAIN, {}, config)
    return True

"""
Single parent class to coordindate the rest calls to teh Heathub
"""
class WiserHubHandle:
    

    def __init__(self, ip, secret, scan_interval,minimum_temp,boost_temp,boost_temp_time):
        self.scan_interval = scan_interval
        self.ip = ip
        self.secret = secret
        self.wiserHubInstance=None
        self.mutex = Lock()
        self.minimum_temp=minimum_temp
        self._updatets = time.time()
        self.boost_temp=boost_temp
        self.boost_temp_time=boost_temp_time

        _LOGGER.info("min temp = {}".format(self.minimum_temp))

    def getHubData(self):
        from .wiserAPI import wiserHub
        if (self.wiserHubInstance==None):
            self.wiserHubInstance=wiserHub.wiserHub(self.ip,self.secret)
        return self.wiserHubInstance

    def getMinimumTemp(self):
        return self.minimum_temp

    def update(self):
        _LOGGER.info("Update Requested")
        from .wiserAPI import wiserHub
        if (self.wiserHubInstance==None):
            self.wiserHubInstance=wiserHub.wiserHub(self.ip,self.secret)
        with self.mutex:
            if (time.time() - self._updatets) >= self.scan_interval:
                _LOGGER.debug("*********************************************************************")
                _LOGGER.info("Scan Interval exceeeded, updating Wiser DataSet from hub")
                _LOGGER.debug("*********************************************************************")
                try:
                    self.wiserHubInstance.refreshData()
                except timeout as timeoutex:
                    _LOGGER.error("Timed out whilst connecting to {}, with error {}".format(self.ip,str(timeoutex)))
                    hass.components.persistent_notification.create("Error: {}<br /> You will need to restart Home Assistant after fixing.".format(ex), title=NOTIFICATION_TITLE, notification_id=NOTIFICATION_ID)
                    return False
                except json.decoder.JSONDecodeError as JSONex:
                    _LOGGER.error("Data not JSON when getting Data from hub, did you enter the right URL? error {}".format(str(timeoutex)))
                    hass.components.persistent_notification.create("Error: {}<br /> You will need to restart Home Assistant after fixing.".format(ex), title=NOTIFICATION_TITLE, notification_id=NOTIFICATION_ID)   
                    return False
                self._updatets = time.time()
                return True
            else:
                _LOGGER.info("Skipping update (data already gotten within scan interval)")

    def setRoomTemperature(self, roomId, target_temperature):
        _LOGGER.info("set {} to {}".format(roomId, target_temperature))
        from .wiserAPI import wiserHub
        if (self.wiserHubInstance==None):
            self.wiserHubInstance=wiserHub.wiserHub(self.ip,self.secret)
        with self.mutex:
            self.wiserHubInstance.setRoomTemperature(roomId, target_temperature)
            return True
        return False
    
    def setRoomMode(self,roomId,mode):
        from .wiserAPI import wiserHub
        if (self.wiserHubInstance==None):
            self.wiserHubInstance=wiserHub.wiserHub(self.ip,self.secret)
        with self.mutex:
            self.wiserHubInstance.setRoomMode(roomId,mode,self.boost_temp,self.boost_temp_time)
            return True
        return False
