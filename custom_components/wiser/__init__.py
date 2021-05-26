"""
Drayton Wiser Compoment for Wiser System.

Includes Climate and Sensor Devices

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelo.santagata@gmail.com
"""
import asyncio
from datetime import timedelta
from functools import partial
import json

import requests.exceptions
import voluptuous as vol
from wiserHeatingAPI.wiserHub import (
    TEMP_MAXIMUM,
    TEMP_MINIMUM,
    WiserHubTimeoutException,
    wiserHub,
    WiserRESTException,
)

from homeassistant.const import (
    ATTR_ENTITY_ID,
    CONF_HOST,
    CONF_MINIMUM,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import ruamel_yaml as yaml, Throttle

from .const import (
    CONF_SETPOINT_MODE,
    DEFAULT_SETPOINT_MODE,
    _LOGGER,
    CONF_BOOST_TEMP,
    CONF_BOOST_TEMP_TIME,
    DATA,
    DEFAULT_BOOST_TEMP,
    DEFAULT_BOOST_TEMP_TIME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    HUBNAME,
    MANUFACTURER,
    UPDATE_LISTENER,
    UPDATE_TRACK,
    WISER_PLATFORMS,
    WISER_SERVICES,
)
from .util import convert_from_wiser_schedule, convert_to_wiser_schedule

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=60)

ATTR_FILENAME = "filename"
ATTR_COPYTO_ENTITY_ID = "to_entity_id"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.All(
            cv.ensure_list,
            [
                {
                    vol.Required(CONF_HOST): cv.string,
                    vol.Required(CONF_PASSWORD): cv.string,
                    vol.Optional(
                        CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
                    ): vol.All(vol.Coerce(int)),
                    vol.Optional(CONF_MINIMUM, default=TEMP_MINIMUM): vol.All(
                        vol.Coerce(int)
                    ),
                    vol.Optional(CONF_BOOST_TEMP, default=DEFAULT_BOOST_TEMP): vol.All(
                        vol.Coerce(int)
                    ),
                    vol.Optional(
                        CONF_BOOST_TEMP_TIME, default=DEFAULT_BOOST_TEMP_TIME
                    ): vol.All(vol.Coerce(int)),
                }
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
)

GET_SET_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
    }
)

COPY_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_id,
        vol.Required(ATTR_COPYTO_ENTITY_ID): cv.entity_id,
    }
)


async def async_setup(hass, config):
    """Set up of the Wiser Hub component."""
    return True


async def async_setup_entry(hass, config_entry):
    """Set up Wiser from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    data = WiserHubHandle(
        hass,
        config_entry,
    )

    # Services callback functions
    @callback
    def get_schedule(service):
        """Handle the service call."""
        entity_id = service.data[ATTR_ENTITY_ID]
        filename = (
            service.data[ATTR_FILENAME]
            if service.data[ATTR_FILENAME] != ""
            else ("schedule_" + entity_id + ".yaml")
        )

        _LOGGER.debug("Getting schedule for %s", entity_id)
        if entity_id in data.schedules:
            _LOGGER.debug("Schedule Id is %s", data.schedules[entity_id])
            hass.async_create_task(
                    data.get_schedule(entity_id, data.schedules[entity_id], filename)
                )
        else:
            _LOGGER.error("No schedule exists for %s", entity_id)

    @callback
    def set_schedule(service):
        """Handle the service call."""
        entity_id = service.data[ATTR_ENTITY_ID]
        filename = service.data[ATTR_FILENAME]
        schedule_data = None

        # Set schedule data
        _LOGGER.debug("Setting schedule for %s from file %s", entity_id, filename)
        if entity_id in data.schedules:
            try:
                _LOGGER.debug("Loading schedule file - %s", filename)
                schedule_data = yaml.load_yaml(filename)
            except Exception as ex:
                _LOGGER.error("Error loading schedule file %s. Error is %s", filename, str(ex))
            # Set schedule
            if schedule_data is not None:
                hass.async_create_task(
                    data.set_schedule(entity_id, data.schedules[entity_id], schedule_data)
                )
            else:
                _LOGGER.error("Error loading schedule data from file")
        else:
            _LOGGER.error("No schedule exists for %s", entity_id)

    @callback
    def copy_schedule(service):
        """Handle the service call."""
        entity_id = service.data[ATTR_ENTITY_ID]
        to_entity_id = service.data[ATTR_COPYTO_ENTITY_ID]

        # Check from and to are valid schedule entities
        _LOGGER.debug("Copying schedule from %s to %s", entity_id, to_entity_id)
        if entity_id in data.schedules and to_entity_id in data.schedules:
            hass.async_create_task(
                data.copy_schedule(entity_id, data.schedules[entity_id], to_entity_id, data.schedules[to_entity_id])
            )
        else:
            if entity_id not in data.schedules:
                _LOGGER.error("You cannot copy the schedule from %s. This entity has no schedule", entity_id)
            if to_entity_id not in data.schedules:
                _LOGGER.error("You cannot copy the schedule to %s. This entity has no schedule", entity_id)

    try:
        await hass.async_add_executor_job(data.connect)
    except (
        WiserHubTimeoutException,
        requests.exceptions.ConnectionError,
        requests.exceptions.ChunkedEncodingError,
        requests.exceptions.InvalidHeader,
        requests.exceptions.ProxyError
    ):
        _LOGGER.error("Connection error trying to connect to wiser hub")
        raise ConfigEntryNotReady
    except KeyError:
        _LOGGER.error("Failed to login to wiser hub")
        return False
    except RuntimeError as exc:
        _LOGGER.error("Failed to setup wiser hub: %s", exc)
        return ConfigEntryNotReady
    except requests.exceptions.HTTPError as ex:
        if ex.response.status_code > 400 and ex.response.status_code < 500:
            _LOGGER.error("Failed to login to wiser hub: %s", ex)
            return False
        raise ConfigEntryNotReady

    # Do first update
    await hass.async_add_executor_job(data.update)

    # Poll for updates in the background
    update_track = async_track_time_interval(
        hass,
        lambda now: data.update(),
        timedelta(
            seconds=config_entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
        ),
    )

    update_listener = config_entry.add_update_listener(_async_update_listener)

    hass.data[DOMAIN][config_entry.entry_id] = {
        DATA: data,
        UPDATE_TRACK: update_track,
        UPDATE_LISTENER: update_listener,
    }

    for platform in WISER_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    _LOGGER.info("Wiser Component Setup Completed")
    await data.async_update_device_registry()

    # Register services
    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_GET_SCHEDULE"],
        get_schedule,
        schema=GET_SET_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_SET_SCHEDULE"],
        set_schedule,
        schema=GET_SET_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_COPY_SCHEDULE"],
        copy_schedule,
        schema=COPY_SCHEDULE_SCHEMA,
    )

    return True


async def _async_update_listener(hass, config_entry):
    """Handle options update."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_unload_entry(hass, config_entry):
    """
    Unload a config entry.

    :param hass:
    :param config_entry:
    :return:
    """
    # Deregister services
    _LOGGER.debug("Unregister Wiser Services")
    for service in WISER_SERVICES:
        hass.services.async_remove(DOMAIN, WISER_SERVICES[service])

    _LOGGER.debug("Unloading Wiser Component")
    # Unload a config entry
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(config_entry, platform)
                for platform in WISER_PLATFORMS
            ]
        )
    )

    hass.data[DOMAIN][config_entry.entry_id][UPDATE_TRACK]()
    hass.data[DOMAIN][config_entry.entry_id][UPDATE_LISTENER]()

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


class WiserHubHandle:
    """Main Wiser class handling all data."""

    def __init__(self, hass, config_entry):
        """Initialise the base class."""
        self._hass = hass
        self._config_entry = config_entry
        self._name = config_entry.data[CONF_NAME]
        self.host = config_entry.data[CONF_HOST]
        self.secret = config_entry.data[CONF_PASSWORD]
        self.wiserhub = None
        self.schedules = {}
        self.minimum_temp = TEMP_MINIMUM
        self.maximum_temp = TEMP_MAXIMUM
        self.boost_temp = config_entry.options.get(CONF_BOOST_TEMP, DEFAULT_BOOST_TEMP)
        self.boost_time = config_entry.options.get(
            CONF_BOOST_TEMP_TIME, DEFAULT_BOOST_TEMP_TIME
        )
        self.setpoint_mode = config_entry.options.get(CONF_SETPOINT_MODE, DEFAULT_SETPOINT_MODE)

    def connect(self):
        """Connect to Wiser Hub."""
        self.wiserhub = wiserHub(self.host, self.secret)
        self._hass.async_create_task(self.async_update())
        return True

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Call Wiser Hub async update."""
        self._hass.async_create_task(self.async_update())

    async def async_update(self, no_throttle: bool = False):
        """Update from Wiser Hub."""
        try:
            result = await self._hass.async_add_executor_job(self.wiserhub.refreshData)
            if result is not None:
                _LOGGER.info("**Wiser Hub data updated**")
                # Send update notice to all components to update
                dispatcher_send(self._hass, "WiserHubUpdateMessage")
                return True

            _LOGGER.error("Unable to update from wiser hub")
            return False
        except json.decoder.JSONDecodeError as ex:
            _LOGGER.error(
                "Data not in JSON format when getting data from the Wiser hub. Error is %s",
                str(ex),
            )
            return False
        except WiserHubTimeoutException as ex:
            _LOGGER.error("Unable to update from Wiser hub due to timeout error")
            _LOGGER.debug("Error is %s", str(ex))
            return False
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.error("Unable to update from Wiser hub due to unknown error")
            _LOGGER.debug("Error is %s", str(ex))
            return False

        _LOGGER.error(self.schedules)

    @property
    def unique_id(self):
        """Return a unique name, otherwise config flow does not work right."""
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
            sw_version=self.wiserhub.getDevice(0).get("ActiveFirmwareVersion"),
        )

    async def set_away_mode(self, away, away_temperature):
        """Set Away mode, with temp."""
        mode = "AWAY" if away else "HOME"
        if self.wiserhub is None:
            self.wiserhub = await self._hass.async_add_executor_job(self.connect)
        _LOGGER.debug("Setting away mode to %s with temp %s.", mode, away_temperature)
        try:
            await self._hass.async_add_executor_job(
                partial(self.wiserhub.setHomeAwayMode, mode, away_temperature)
            )
            await self.async_update(no_throttle=True)
        except BaseException as ex:  # pylint: disable=broad-except
            _LOGGER.debug("Error setting away mode! %s", str(ex))

    async def set_system_switch(self, switch, mode):
        """Set the a system switch , stored in config files."""
        if self.wiserhub is None:
            self.wiserhub = await self._hass.async_add_executor_job(self.connect)
        _LOGGER.debug("Setting %s system switch to %s.", switch, mode)
        try:
            await self._hass.async_add_executor_job(
                partial(self.wiserhub.setSystemSwitch, switch, mode)
            )
            await self.async_update(no_throttle=True)
        except BaseException as ex:  # pylint: disable=broad-except
            _LOGGER.debug("Error setting %s system switch! %s", switch, str(ex))

    async def set_smartplug_mode(self, plug_id, plug_mode):
        """
        Set the mode of the smart plug.

        :param plug_id:
        :param mode: Can be manual or auto
        :return:
        """
        if self.wiserhub is None:
            self.wiserhub = await self._hass.async_add_executor_job(self.connect)

        if plug_mode.lower() in ["auto", "manual"]:
            _LOGGER.info("Setting SmartPlug %s mode to %s ", plug_id, plug_mode)

            try:
                await self._hass.async_add_executor_job(
                    partial(self.wiserhub.setSmartPlugMode, plug_id, plug_mode)
                )
                # Add small delay to allow hub to update status before refreshing
                await asyncio.sleep(0.5)
                await self.async_update(no_throttle=True)

            except BaseException as ex:  # pylint: disable=broad-except
                _LOGGER.debug(
                    "Error setting SmartPlug %s mode to %s, error %s",
                    plug_id,
                    plug_mode,
                    str(ex),
                )
        else:
            _LOGGER.error(
                "Plug mode can only be auto or manual. Mode was %s", plug_mode
            )

    async def set_smart_plug_state(self, plug_id, state):
        """
        Set the state of the smart plug.

        :param plug_id:
        :param state: Can be On or Off
        :return:
        """
        if self.wiserhub is None:
            self.wiserhub = await self._hass.async_add_executor_job(self.connect)
        _LOGGER.info("Setting SmartPlug %s to %s ", plug_id, state)

        try:
            await self._hass.async_add_executor_job(
                partial(self.wiserhub.setSmartPlugState, plug_id, state)
            )
            # Add small delay to allow hub to update status before refreshing
            await asyncio.sleep(0.5)
            await self.async_update(no_throttle=True)

        except BaseException as ex:  # pylint: disable=broad-except
            _LOGGER.debug(
                "Error setting SmartPlug %s to %s, error %s",
                plug_id,
                state,
                str(ex),
            )

    async def set_hotwater_mode(self, hotwater_mode):
        """Set the hotwater mode."""
        if self.wiserhub is None:
            self.wiserhub = await self._hass.async_add_executor_job(self.connect)
        _LOGGER.info("Setting Hotwater to %s ", hotwater_mode)
        # Add small delay to allow hub to update status before refreshing
        await asyncio.sleep(0.5)
        await self.async_update(no_throttle=True)

        try:
            await self._hass.async_add_executor_job(
                partial(self.wiserhub.setHotwaterMode, hotwater_mode)
            )
        except BaseException as ex:  # pylint: disable=broad-except
            _LOGGER.debug(
                "Error setting Hotwater Mode to  %s, error %s",
                hotwater_mode,
                str(ex),
            )

    async def get_schedule(self, entity_id, schedule_id, filename):
        """Get wiser device schedule."""
        schedule_data = self.wiserhub.getSchedule(self.schedules[entity_id])
        if schedule_data is not None:
            for r in (("climate.",""),("switch.",""),("sensor.",""),("_"," ")):
                entity_id = entity_id.replace(*r)

            schedule_data = convert_from_wiser_schedule(
                schedule_data, entity_id.title()
            )
            try:
                yaml.save_yaml(filename, schedule_data)
            except Exception as ex:  # pylint: disable=broad-except
                _LOGGER.error("Error saving schedule file. Error is %s", str(ex))
            _LOGGER.debug("Saved schedule for %s to file %s", entity_id, filename)
        else:
            _LOGGER.error("No schedule data returned for %s", entity_id)
    
    async def set_schedule(self, entity_id, schedule_id, schedule_data):
        """Set wiser device schedule."""
        if schedule_data is not None:
            schedule_data = convert_to_wiser_schedule(schedule_data)
            try:
                await self._hass.async_add_executor_job(
                    partial(self.wiserhub.setSchedule, schedule_id, schedule_data)
                )
                _LOGGER.debug("Set schedule for %s", entity_id)
                await self.async_update(no_throttle=True)
                return True
            except WiserRESTException:
                _LOGGER.error("Error setting schedule for %s.  Please check your schedule file.", entity_id)
        return False

    async def copy_schedule(self, entity_id, schedule_id, to_entity_id, to_schedule_id):
        """Copy schedule from one device to another."""
        try:
            await self._hass.async_add_executor_job(
                partial(self.wiserhub.copySchedule, schedule_id, to_schedule_id)
            )
            _LOGGER.debug(
                "Copied schedule from %s to %s",
                entity_id,
                to_entity_id,
            )
            await self.async_update(no_throttle=True)
            return True
        except WiserRESTException:
                _LOGGER.error("Error copying schedule %s to %s.", entity_id, to_entity_id)
        return False