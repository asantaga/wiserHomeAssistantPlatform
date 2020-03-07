"""
Drayton Wiser Compoment for Wiser System

Includes Climate and Sensor Devices

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelo.santagata@gmail.com
"""
import asyncio
import json

# import time
from datetime import timedelta
import voluptuous as vol
from wiserHeatingAPI.wiserHub import (
    wiserHub, 
    TEMP_MINIMUM, 
    TEMP_MAXIMUM,
    WiserHubTimeoutException,
    WiserHubAuthenticationException,
    WiserRESTException
)

from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import (
    CONF_HOST,
    CONF_MINIMUM,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.util import Throttle

from .const import (
    _LOGGER,
    CONF_BOOST_TEMP,
    CONF_BOOST_TEMP_TIME,
    DATA_WISER_CONFIG,
    DEFAULT_BOOST_TEMP,
    DEFAULT_BOOST_TEMP_TIME,
    DOMAIN,
    HUBNAME,
    MANUFACTURER,
    NOTIFICATION_ID,
    NOTIFICATION_TITLE,
    VERSION,
    WISER_PLATFORMS,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

PLATFORM_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_SCAN_INTERVAL, default=0): cv.time_period,
        vol.Optional(CONF_MINIMUM, default=TEMP_MINIMUM): vol.All(vol.Coerce(int)),
        vol.Optional(CONF_BOOST_TEMP, default=2): vol.All(vol.Coerce(int)),
        vol.Optional(CONF_BOOST_TEMP_TIME, default=30): vol.All(vol.Coerce(int)),
    }
)

async def async_setup(hass, config):
    """
    Wiser uses config flow for configuration.
    But, a "wiser:" entry in configuration.yaml will trigger an import flow
    if a config entry doesn't already exist. If it exists, the import
    flow will attempt to import it and create a config entry, to assist users
    migrating from the old wiser component. Otherwise, the user will have to
    continue setting up the integration via the config flow.
    """
    hass.data[DATA_WISER_CONFIG] = config.get(DOMAIN, {})

    if not hass.config_entries.async_entries(DOMAIN) and hass.data[DATA_WISER_CONFIG]:
        # No config entry exists and configuration.yaml config exists, trigger the import flow.
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN, context={"source": SOURCE_IMPORT}, data = hass.data[DATA_WISER_CONFIG]
            )
        )

    return True


async def async_setup_entry(hass, config_entry):

    """Set up the Wiser component."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    _LOGGER.info(
        "Wiser setup with Hub IP =  {} and scan interval of {}".format(
            config_entry.data[CONF_HOST], MIN_TIME_BETWEEN_UPDATES
        )
    )

    data = WiserHubHandle(hass, config_entry, config_entry.data[CONF_HOST], config_entry.data[CONF_PASSWORD])

    @callback
    def retryWiserHubSetup():
        hass.async_create_task(wiserHubSetup())
    
    async def wiserHubSetup():
        _LOGGER.info("Initiating WiserHub connection")
        try:
            if await data.async_update(no_throttle=True):
                if data.wiserhub.getDevices is None:
                    _LOGGER.error("No Wiser devices found to set up")
                    return False
            
                hass.data[DOMAIN] = data
            
                for component in WISER_PLATFORMS:
                    hass.async_create_task(
                         hass.config_entries.async_forward_entry_setup(config_entry, component))
            
                _LOGGER.info("Wiser Component Setup Completed")
                return True
            else:
                await scheduleWiserHubSetup()
                return True
        except (asyncio.TimeoutError):
            await scheduleWiserHubSetup()
            return True
        except WiserHubTimeoutException:
            await scheduleWiserHubSetup()
            return True
    
    async def scheduleWiserHubSetup(interval = 30):
        _LOGGER.error(
            "Unable to connect to the Wiser Hub, retrying in {} seconds".format(interval)
        )
        hass.loop.call_later(interval, retryWiserHubSetup)
        return
        
    hass.async_create_task(wiserHubSetup())
    await data.async_update_device_registry()
    return True
    
async def async_unload_entry(hass, config_entry):
    """Unload a config entry."""
    for component in WISER_PLATFORMS:
        hass.async_create_task(
             hass.config_entries.async_forward_entry_unload(config_entry, component))
        

class WiserHubHandle:
    def __init__(self, hass, config_entry, ip, secret):
        self._hass = hass
        self._config_entry = config_entry
        self._name = config_entry.data[CONF_NAME]
        self.ip = ip
        self.secret = secret
        self.wiserhub = wiserHub(self.ip, self.secret)
        self.minimum_temp = TEMP_MINIMUM
        self.maximum_temp = TEMP_MAXIMUM
        self.boost_temp = config_entry.data[CONF_BOOST_TEMP] or DEFAULT_BOOST_TEMP
        self.boost_time = config_entry.data[CONF_BOOST_TEMP_TIME] or DEFAULT_BOOST_TEMP_TIME

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
        _LOGGER.info("**Update of Wiser Hub data requested**")
        try:
            result = await self._hass.async_add_executor_job(self.wiserhub.refreshData)
            if result is not None:
                _LOGGER.info("**Wiser Hub data updated**")
                return True
            else:
                _LOGGER.info("**Unable to update from wiser hub**")
                return False
        except json.decoder.JSONDecodeError as JSONex:
            _LOGGER.error(
                "Data not JSON when getting Data from hub, "
                + "did you enter the right URL? error {}".format(str(JSONex))
            )
            self.hass.components.persistent_notification.create(
                "Error: {}"
                + "<br /> You will need to restart Home Assistant "
                + " after fixing.".format(JSONex),
                title=NOTIFICATION_TITLE,
                notification_id=NOTIFICATION_ID,
            )
            return False
        except WiserHubTimeoutException:
            pass
            
    @property
    def unique_id(self):
        return self._name
            
    async def async_update_device_registry(self):
        """Update device registry."""
        device_registry = await self._hass.helpers.device_registry.async_get_registry()
        device_registry.async_get_or_create(
            config_entry_id=self._config_entry.entry_id,
            connections={(CONNECTION_NETWORK_MAC, self.wiserhub.getMACAddress())},
            identifiers={(DOMAIN, self.unique_id)},
            manufacturer=MANUFACTURER,
            name=HUBNAME,
            model=self.wiserhub.getDevice(0).get("ProductType"),
            sw_version=self.wiserhub.getDevice(0).get("ActiveFirmwareVersion")
        )

    async def set_away_mode(self, away, away_temperature):
        mode = "AWAY" if away else "HOME"
        if self.wiserhub is None:
            self.wiserhub = wiserHub(self.ip, self.secret)
        _LOGGER.debug(
            "Setting away mode to {} with temp {}.".format(mode, away_temperature)
        )
        try:
            self.wiserhub.setHomeAwayMode(mode, away_temperature)
            await self.async_update(no_throttle=True)
        except BaseException as e:
            _LOGGER.debug("Error setting away mode! {}".format(str(e)))

    async def set_system_switch(self, switch, mode):
        if self.wiserhub is None:
            self.wiserhub = wiserHub(self.ip, self.secret)
        _LOGGER.debug(
            "Setting {} system switch to {}.".format(switch, mode)
        )
        try:
            self.wiserhub.setSystemSwitch(switch, mode)
            await self.async_update(no_throttle=True)
        except BaseException as e:
            _LOGGER.debug("Error setting {} system switch! {}".format(switch, str(e)))


    async def set_smart_plug_state(self, plug_id, state):
        """
        Set the state of the smart plug,
        :param plug_id:
        :param state: Can be On or Off
        :return:
        """
        if self.wiserhub is None:
            self.wiserhub = wiserHub(self.ip, self.secret)
        _LOGGER.info(
            "Setting SmartPlug {} to {} ".format(plug_id, state))

        try:
            self.wiserhub.setSmartPlugState(plug_id,state)
            # Add small delay to allow hub to update status before refreshing
            await asyncio.sleep(0.5)
            await self.async_update(no_throttle=True)

        except BaseException as e:
            _LOGGER.debug("Error setting SmartPlug {} to {}, error {}".format(plug_id, state, str(e)))

    async def set_hotwater_mode(self, hotwater_mode):
        """

        """
        if self.wiserhub is None:
            self.wiserhub = wiserHub(self.ip, self.secret)
        _LOGGER.info(
            "Setting Hotwater to {} ".format(hotwater_mode))
        # Add small delay to allow hub to update status before refreshing
        await asyncio.sleep(0.5)
        await self.async_update(no_throttle=True)

        try:
            self.wiserhub.setHotwaterMode(hotwater_mode)


        except BaseException as e:
            _LOGGER.debug(
                "Error setting Hotwater Mode to  {}, error {}".format(hotwater_mode,
                                                                    str(e)))