"""
Drayton Wiser Compoment for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
msparker@sky.com
"""
import asyncio
from datetime import timedelta, datetime
import logging
import voluptuous as vol
from wiserHeatAPIv2.wiserhub import (
    TEMP_MINIMUM,
    TEMP_MAXIMUM,
    WiserAPI,
    WiserHubConnectionError,
    WiserHubAuthenticationError,
    WiserHubRESTError,
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
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    entity_registry as er,
)
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC
from homeassistant.helpers.entity_registry import (
    async_entries_for_device,
)
from homeassistant.helpers.dispatcher import dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import Throttle

from .const import (
    CONF_MOMENTS,
    CONF_SETPOINT_MODE,
    DEFAULT_SETPOINT_MODE,
    CONF_HEATING_BOOST_TEMP,
    CONF_HEATING_BOOST_TIME,
    CONF_HW_BOOST_TIME,
    CONF_LTS_SENSORS,
    DATA,
    DEFAULT_BOOST_TEMP,
    DEFAULT_BOOST_TEMP_TIME,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    MANUFACTURER,
    UPDATE_LISTENER,
    UPDATE_TRACK,
    WISER_PLATFORMS,
    WISER_SERVICES
)

from .helpers import get_device_name, get_identifier

_LOGGER = logging.getLogger(__name__)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

ATTR_FILENAME = "filename"
ATTR_COPYTO_ENTITY_ID = "to_entity_id"
CONF_HUB_ID = "wiser_hub_id"
CONF_ENDPOINT = "wiser_hub_endpoint"
SERVICE_REMOVE_ORPHANED_ENTRIES = "remove_orphaned_entries"
SERVICE_OUTPUT_HUB_JSON = "output_hub_json"

GET_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
    }
)

SET_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_FILENAME): vol.Coerce(str),
    }
)

COPY_SCHEDULE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
        vol.Required(ATTR_COPYTO_ENTITY_ID): cv.entity_id,
    }
)

SELECT_HUB_SCHEMA = vol.All(vol.Schema({vol.Required(CONF_HUB_ID): str}))

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
                    vol.Optional(CONF_HEATING_BOOST_TEMP, default=DEFAULT_BOOST_TEMP): vol.All(
                        vol.Coerce(int)
                    ),
                    vol.Optional(
                        CONF_HEATING_BOOST_TIME, default=DEFAULT_BOOST_TEMP_TIME
                    ): vol.All(vol.Coerce(int)),
                }
            ],
        )
    },
    extra=vol.ALLOW_EXTRA,
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

    try:
        await hass.async_add_executor_job(data.connect)
    except (WiserHubConnectionError, WiserHubRESTError) as ex:
        _LOGGER.error(ex)
        raise ConfigEntryNotReady("Unable to connect to the Wiser Hub")
    except WiserHubAuthenticationError as ex:
        _LOGGER.error(ex)
        return False
    except Exception as ex:  # pylint: disable=broad-except
        _LOGGER.error(f"An unknown error occurred trying to update from Wiser hub {config_entry.data[CONF_HOST]}")
        _LOGGER.debug(f"Error is {str(ex)}")
        raise ConfigEntryNotReady("Unknown error connecting to the Wiser Hub")

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


    # Setup platforms
    for platform in WISER_PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(config_entry, platform)
        )

    # Initialise global services
    def get_entity_from_entity_id(entity_id: str):
        """Get wiser entity from entity_id"""
        domain = entity_id.split(".", 1)[0]
        entity_comp = hass.data.get("entity_components", {}).get(domain)
        if entity_comp:
            return entity_comp.get_entity(entity_id)
        return None

    @callback
    def get_schedule(service_call):
        """Handle the service call."""
        entity_ids = service_call.data[ATTR_ENTITY_ID]
        for entity_id in entity_ids:
            filename = (
                service_call.data[ATTR_FILENAME]
                if service_call.data[ATTR_FILENAME] != ""
                else (hass.config.config_dir + "/schedules/schedule_" + entity_id.split(".", 1)[1] + ".yaml")
            )
            entity = get_entity_from_entity_id(entity_id)
            if hasattr(entity, "get_schedule"):
                getattr(entity, "get_schedule")(filename)
            else:
                _LOGGER.error(f"Cannot save schedule from entity {entity_id}.  Please see integration instructions for entities to choose")

    @callback
    def set_schedule(service_call):
        """Handle the service call."""
        entity_ids = service_call.data[ATTR_ENTITY_ID]
        for entity_id in entity_ids:
            filename = service_call.data[ATTR_FILENAME]
            entity = get_entity_from_entity_id(entity_id)
            if hasattr(entity, "set_schedule"):
                getattr(entity, "set_schedule")(filename)
            else:
                _LOGGER.error(f"Cannot set schedule for entity {entity_id}.  Please see integration instructions for entities to choose")

    @callback
    def copy_schedule(service_call):
        """Handle the service call"""
        entity_ids = service_call.data[ATTR_ENTITY_ID]
        to_entity_id = service_call.data[ATTR_COPYTO_ENTITY_ID]

        if len(entity_ids) == 1:
            from_entity = get_entity_from_entity_id(entity_ids[0])
            to_entity = get_entity_from_entity_id(to_entity_id)

            #TODO: Validate they are on same hub - be able to copy across hubs?
            if from_entity._data.wiserhub.system.name == to_entity._data.wiserhub.system.name:
                if hasattr(to_entity, "_schedule") and to_entity._schedule:
                    if hasattr(from_entity, "copy_schedule"):
                        getattr(from_entity, "copy_schedule")(to_entity._schedule.id, to_entity._schedule.name)
                    else:
                        _LOGGER.error(f"Cannot copy schedule from entity {from_entity.name}.  Please see integration instructions for entities to choose")
                else:
                    _LOGGER.error(f"Cannot copy schedule to entity {to_entity_id}.  Please see integration instructions for entities to choose")
            else:
                _LOGGER.error("You cannot copy schedules across different Wiser Hubs.  Download form one and upload to the other instead")
        else:
            _LOGGER.error(f"Cannot copy schedule from multiple entities. Please select only one")



    @callback
    def remove_orphaned_entries_service(service):
        for entry_id in hass.data[DOMAIN]:
            hass.async_create_task(
                data.async_remove_orphaned_entries(entry_id, service.data[CONF_HUB_ID])
            )

    @callback
    def output_hub_json(service):
        for entry_id in hass.data[DOMAIN]:
            hass.async_create_task(
                data.async_output_hub_json(entry_id, service.data[CONF_HUB_ID])
            )

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_GET_SCHEDULE"],
        get_schedule,
        schema=GET_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_SET_SCHEDULE"],
        set_schedule,
        schema=SET_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_COPY_SCHEDULE"],
        copy_schedule,
        schema=COPY_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_REMOVE_ORPHANED_ENTRIES,
        remove_orphaned_entries_service,
        schema=SELECT_HUB_SCHEMA,
    )

    hass.services.async_register (
        DOMAIN,
        SERVICE_OUTPUT_HUB_JSON,
        output_hub_json,
        schema=SELECT_HUB_SCHEMA
    )

    # Add hub as device
    await data.async_update_device_registry()

    _LOGGER.info("Wiser Component Setup Completed")

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
    hass.services.async_remove(DOMAIN, SERVICE_REMOVE_ORPHANED_ENTRIES)
    hass.services.async_remove(DOMAIN, WISER_SERVICES["SERVICE_GET_SCHEDULE"])
    hass.services.async_remove(DOMAIN, WISER_SERVICES["SERVICE_SET_SCHEDULE"])
    hass.services.async_remove(DOMAIN, WISER_SERVICES["SERVICE_COPY_SCHEDULE"])

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
        self.last_update_time = datetime.now()
        self.last_update_status = ""
        self.minimum_temp = TEMP_MINIMUM
        self.maximum_temp = TEMP_MAXIMUM
        self.boost_temp = config_entry.options.get(CONF_HEATING_BOOST_TEMP, DEFAULT_BOOST_TEMP)
        self.boost_time = config_entry.options.get(
            CONF_HEATING_BOOST_TIME, DEFAULT_BOOST_TEMP_TIME
        )
        self.hw_boost_time = config_entry.options.get(
            CONF_HW_BOOST_TIME, DEFAULT_BOOST_TEMP_TIME
        )
        self.setpoint_mode = config_entry.options.get(CONF_SETPOINT_MODE, DEFAULT_SETPOINT_MODE)
        self.enable_moments = config_entry.options.get(CONF_MOMENTS, False)
        self.enable_lts_sensors = config_entry.options.get(CONF_LTS_SENSORS, False)

    def connect(self):
        """Connect to Wiser Hub."""
        self.wiserhub = WiserAPI(self.host, self.secret)
        return True

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Call Wiser Hub async update."""
        self._hass.async_create_task(self.async_update())

    async def async_update(self, no_throttle: bool = False):
        """Update from Wiser Hub."""
        try:
            result = await self._hass.async_add_executor_job(self.wiserhub.read_hub_data)
            if result:
                _LOGGER.debug(f"Wiser Hub data updated - {self.wiserhub.system.name}")
                # Send update notice to all components to update
                self.last_update_time = datetime.now()
                self.last_update_status = "Success"
                dispatcher_send(self._hass, f"{self.wiserhub.system.name}-HubUpdateMessage")
                return True

            _LOGGER.error(f"Unable to update from Wiser hub - {self.wiserhub.system.name}")

        except (WiserHubConnectionError, WiserHubAuthenticationError, WiserHubRESTError) as ex:
            _LOGGER.error(ex)
        except Exception as ex:  # pylint: disable=broad-except
            _LOGGER.error(f"An unknown error occurred trying to update from Wiser hub {self.wiserhub.system.name}")
            _LOGGER.debug(f"Error is {str(ex)}")
        
        self.last_update_status = "Failed"
        dispatcher_send(self._hass, f"{self.wiserhub.system.name}-HubUpdateFailedMessage")
        return False



    @property
    def unique_id(self):
        """Return a unique name, otherwise config flow does not work right."""
        return self.wiserhub.system.name

    async def async_update_device_registry(self):
        """Update device registry."""
        device_registry = dr.async_get(self._hass)
        device_registry.async_get_or_create(
            config_entry_id=self._config_entry.entry_id,
            connections={(CONNECTION_NETWORK_MAC, self.wiserhub.system.network.mac_address)},
            identifiers={(DOMAIN, get_identifier(self, 0))},
            manufacturer=MANUFACTURER,
            name=get_device_name(self, 0),
            model=self.wiserhub.system.model,
            sw_version=self.wiserhub.system.firmware_version,
        )

    @callback
    async def async_remove_orphaned_entries(self, entry_id, wiser_hub_id: str):
        """Remove orphaned Wiser entries from device registry"""
        api = self._hass.data[DOMAIN][entry_id]["data"]

        if api.wiserhub.system.name == wiser_hub_id:
            _LOGGER.info(f"Removing orphaned devices for {wiser_hub_id}")

            device_registry = dr.async_get(self._hass)
            entity_registry = er.async_get(self._hass)

            devices_to_be_removed = []

            #Get list of all devices for integration
            all_devices = [
                entry
                for entry in device_registry.devices.values()
                if entry_id in entry.config_entries
            ]

            # Don't remove the Gateway host entry
            wiser_hub = device_registry.async_get_device(
                connections={(CONNECTION_NETWORK_MAC, api.wiserhub.system.network.mac_address)},
                identifiers={(DOMAIN, api.unique_id)},
            )
            devices_to_be_removed = [ device.id for device in all_devices if device.id != wiser_hub.id ]

            # Remove devices that don't belong to any entity
            for device_id in devices_to_be_removed:
                if (
                    len(
                        async_entries_for_device(
                            entity_registry, device_id, include_disabled_entities=True
                        )
                    )
                    == 0
                ):
                    _LOGGER.info(f"Removed {device_id}")
                    device_registry.async_remove_device(device_id)

    @callback
    async def async_output_hub_json(self, entry_id, wiser_hub_id: str):
        """Output hub jsondata from endpoint"""
        api = self._hass.data[DOMAIN][entry_id]["data"]
        wiserhub = api.wiserhub

        if wiserhub.system.name == wiser_hub_id:
            _LOGGER.info(f"Outputing json data from {wiser_hub_id}")
            for endpoint in ['domain','network','schedules']:
                if await self._hass.async_add_executor_job(
                    wiserhub.output_raw_hub_data, endpoint, f"{endpoint}-{datetime.now().strftime('%Y%m%d-%H%M%S')}", self._hass.config.config_dir
                ):
                    _LOGGER.info(f"Written hub {endpoint} data to the wiser_data subdirectory in your config directory")

            