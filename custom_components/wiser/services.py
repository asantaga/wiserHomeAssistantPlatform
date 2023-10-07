# Initialise global services
import os
import aiofiles
import voluptuous as vol
import logging
from .const import (
    ATTR_FILENAME,
    ATTR_HUB,
    ATTR_OPENTHERM_ENDPOINT,
    ATTR_OPENTHERM_PARAM,
    ATTR_OPENTHERM_PARAM_VALUE,
    ATTR_SCHEDULE,
    ATTR_SCHEDULE_ID,
    ATTR_SCHEDULE_NAME,
    ATTR_TIME_PERIOD,
    ATTR_TO_ENTITY_ID,
    DATA,
    DEFAULT_BOOST_TEMP_TIME,
    DOMAIN,
    WISER_SERVICES,
)
from .coordinator import WiserHubRESTError
from .helpers import get_config_entry_id_by_name, get_instance_count, is_wiser_config_id
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_MODE,
)
from homeassistant.core import HomeAssistant, callback, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)


async def async_setup_services(hass: HomeAssistant, data):
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

    SET_SCHEDULE_FROM_DATA_SCHEMA = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
            vol.Required(ATTR_SCHEDULE): cv.template,
        }
    )

    COPY_SCHEDULE_SCHEMA = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): cv.entity_id,
            vol.Required(ATTR_TO_ENTITY_ID): cv.entity_ids,
        }
    )

    ASSIGN_SCHEDULE_SCHEMA = vol.Schema(
        {
            vol.Optional(ATTR_ENTITY_ID): cv.entity_id,
            vol.Optional(ATTR_SCHEDULE_ID): vol.Coerce(int),
            vol.Optional(ATTR_SCHEDULE_NAME): vol.Coerce(str),
            vol.Required(ATTR_TO_ENTITY_ID): cv.entity_ids,
        }
    )

    SET_DEVICE_MODE_SCHEMA = vol.Schema(
        {
            vol.Required(ATTR_ENTITY_ID): cv.entity_ids,
            vol.Required(ATTR_MODE): vol.Coerce(str),
        }
    )

    BOOST_HOTWATER_SCHEMA = vol.Schema(
        {
            vol.Optional(ATTR_TIME_PERIOD, default=DEFAULT_BOOST_TEMP_TIME): vol.Coerce(
                int
            ),
            vol.Optional(ATTR_HUB, default=""): vol.Coerce(str),
        }
    )

    SEND_OPENTHERM_COMMAND_SCHEMA = vol.Schema(
        {
            vol.Optional(ATTR_OPENTHERM_ENDPOINT, default=""): vol.Coerce(str),
            vol.Required(ATTR_OPENTHERM_PARAM): vol.Coerce(str),
            vol.Required(ATTR_OPENTHERM_PARAM_VALUE): vol.Coerce(str),
            vol.Optional(ATTR_HUB, default=""): vol.Coerce(str),
        }
    )

    def get_entity_from_entity_id(entity: str):
        """Get wiser entity from entity_id"""
        domain = entity.split(".", 1)[0]
        entity_comp = hass.data.get("entity_components", {}).get(domain)
        if entity_comp:
            return entity_comp.get_entity(entity)
        return None

    @callback
    async def get_schedule(service_call):
        """Handle the service call."""
        entity_ids = service_call.data[ATTR_ENTITY_ID]
        for entity_id in entity_ids:
            filename = (
                service_call.data[ATTR_FILENAME]
                if service_call.data[ATTR_FILENAME] != ""
                else (
                    hass.config.config_dir
                    + "/schedules/schedule_"
                    + entity_id.split(".", 1)[1]
                    + ".yaml"
                )
            )
            entity = get_entity_from_entity_id(entity_id)
            if entity:
                if hasattr(entity, "get_schedule"):
                    # Remove leading slash on config if exists
                    filename = str(filename).replace("/config", "config")
                    # Check if dir exists, if not create it.
                    file_dir = os.path.dirname(filename)
                    if not os.path.exists(file_dir):
                        await aiofiles.os.makedirs(file_dir, exist_ok=True)
                    fn = getattr(entity, "get_schedule")
                    await fn(filename)
                else:
                    _LOGGER.error(
                        f"Cannot save schedule from entity {entity_id}.  Please see wiki for entities to choose"
                    )
            else:
                _LOGGER.error(
                    f"Invalid entity. {entity_id} does not exist in this integration"
                )

    @callback
    async def set_schedule(service_call):
        """Handle the service call."""
        entity_ids = service_call.data[ATTR_ENTITY_ID]
        for entity_id in entity_ids:
            filename = service_call.data[ATTR_FILENAME]
            entity = get_entity_from_entity_id(entity_id)
            if entity:
                if hasattr(entity, "set_schedule"):
                    fn = getattr(entity, "set_schedule")
                    await fn(filename)
                else:
                    _LOGGER.error(
                        f"Cannot set schedule for entity {entity_id}.  Please see wiki for entities to choose"
                    )
            else:
                _LOGGER.error(
                    f"Invalid entity. {entity_id} does not exist in this integration"
                )

    @callback
    async def set_schedule_from_data(service_call: ServiceCall):
        """Handle the service call."""
        schedule = service_call.data[ATTR_SCHEDULE]
        schedule.hass = hass

        entity_ids = service_call.data[ATTR_ENTITY_ID]
        for entity_id in entity_ids:
            entity = get_entity_from_entity_id(entity_id)
            if entity:
                if hasattr(entity, "set_schedule_from_data"):
                    fn = getattr(entity, "set_schedule_from_data")
                    await fn(schedule.async_render(parse_result=False))
                else:
                    _LOGGER.error(
                        f"Cannot set schedule for entity {entity_id}.  Please see wiki for entities to choose"
                    )
            else:
                _LOGGER.error(
                    f"Invalid entity. {entity_id} does not exist in this integration"
                )

    @callback
    async def copy_schedule(service_call):
        """Handle the service call"""
        entity_id = service_call.data[ATTR_ENTITY_ID]
        to_entity_ids = service_call.data[ATTR_TO_ENTITY_ID]
        for to_entity_id in to_entity_ids:
            from_entity = get_entity_from_entity_id(entity_id)
            to_entity = get_entity_from_entity_id(to_entity_id)

            if from_entity and to_entity:
                # Check from entity is a schedule entity
                if hasattr(from_entity, "copy_schedule"):
                    fn = getattr(from_entity, "copy_schedule")
                    await fn(to_entity)
                else:
                    _LOGGER.error(
                        f"Cannot copy schedule from entity {from_entity.name}.  Please see wiki for entities to choose"
                    )
            else:
                from_entity_id_text = entity_id if not from_entity else ""
                to_entity_id_text = to_entity_id if not to_entity else ""
                and_text = " and " if not from_entity and not to_entity else ""
                _LOGGER.error(
                    f"Invalid entity - {from_entity_id_text}{and_text}{to_entity_id_text} does not exist in this integration"  # noqa=E501
                )
            return False

    @callback
    async def assign_schedule(service_call):
        """Handle the service call"""
        entity_id = service_call.data.get(ATTR_ENTITY_ID)
        schedule_id = service_call.data.get(ATTR_SCHEDULE_ID)
        schedule_name = service_call.data.get(ATTR_SCHEDULE_NAME)
        to_entity_ids = service_call.data[ATTR_TO_ENTITY_ID]

        if entity_id:
            # Assign schedule from this entity to another
            for to_entity_id in to_entity_ids:
                from_entity = get_entity_from_entity_id(entity_id)
                to_entity = get_entity_from_entity_id(to_entity_id)

                if from_entity and to_entity:
                    if hasattr(from_entity, "assign_schedule_to_another_entity"):
                        fn = getattr(from_entity, "assign_schedule_to_another_entity")
                        await fn(to_entity)
                    else:
                        _LOGGER.error(
                            f"Cannot assign schedule from entity {from_entity.name}. Please see wiki for entities to choose"  # noqa=E501
                        )
                else:
                    from_entity_id_text = entity_id if not from_entity else ""
                    to_entity_id_text = to_entity_id if not to_entity else ""
                    and_text = " and " if not from_entity and not to_entity else ""
                    _LOGGER.error(
                        f"Invalid entity - {from_entity_id_text}{and_text}{to_entity_id_text} does not exist in this integration"  # noqa=E501
                    )
        elif schedule_id:
            # Assign scheduel with id to this entity
            for to_entity_id in to_entity_ids:
                to_entity = get_entity_from_entity_id(to_entity_id)
                if to_entity:
                    if hasattr(to_entity, "assign_schedule_by_id_or_name"):
                        fn = getattr(to_entity, "assign_schedule_by_id_or_name")
                        await fn(schedule_id, None)
                    else:
                        _LOGGER.error(
                            f"Cannot assign schedule to entity {to_entity.name}. Please see wiki for entities to choose"
                        )
        elif schedule_name:
            # Assign schedule with name to this entity
            for to_entity_id in to_entity_ids:
                to_entity = get_entity_from_entity_id(to_entity_id)
                if to_entity:
                    if hasattr(to_entity, "assign_schedule_by_id_or_name"):
                        fn = getattr(to_entity, "assign_schedule_by_id_or_name")
                        await fn(None, schedule_name)
                    else:
                        _LOGGER.error(
                            f"Cannot assign schedule to entity {to_entity.name}. Please see wiki for entities to choose"
                        )
        else:
            # Create default schedule and assign to entity
            for to_entity_id in to_entity_ids:
                entity = get_entity_from_entity_id(to_entity_id)
                if hasattr(entity, "create_schedule"):
                    fn = getattr(entity, "create_schedule")
                    await fn()
                else:
                    _LOGGER.error(
                        f"Cannot assign schedule to entity {to_entity.name}.  Please see wiki for entities to choose"
                    )

    @callback
    async def set_device_mode(service_call):
        """Handle the service call."""
        entity_ids = service_call.data[ATTR_ENTITY_ID]
        mode = service_call.data[ATTR_MODE]
        for entity_id in entity_ids:
            entity = get_entity_from_entity_id(entity_id)
            if entity:
                if hasattr(entity, "async_set_mode"):
                    if mode.lower() in [option.lower() for option in entity.options]:
                        fn = getattr(entity, "async_set_mode")
                        await fn(mode)
                    else:
                        _LOGGER.error(
                            f"{mode} is not a valid mode for this device.  Options are {entity.options}"
                        )
                else:
                    _LOGGER.error(
                        f"Cannot set mode for entity {entity_id}.  Please see wiki for entities to choose"
                    )
            else:
                _LOGGER.error(
                    f"Invalid entity. {entity_id} does not exist in this integration"
                )

    @callback
    async def async_boost_hotwater(service_call):
        time_period = service_call.data[ATTR_TIME_PERIOD]
        hub = service_call.data[ATTR_HUB]
        instance = data

        if get_instance_count(hass) > 1:
            if not hub:
                raise HomeAssistantError("Please specify a hub config entry id or name")
            else:
                # Find hub from config_entry_id or hub name
                if is_wiser_config_id(hass, hub):
                    instance = hass.data[DOMAIN][hub][DATA]
                else:
                    # Find hub by name
                    config_entry_id = get_config_entry_id_by_name(hass, hub)
                    if config_entry_id:
                        instance = hass.data[DOMAIN][config_entry_id][DATA]

        # If hub has hotwater functionality, call boost
        if instance.wiserhub.hotwater:
            if time_period > 0:
                _LOGGER.info(f"Boosting Hot Water for {time_period}m")
                await instance.wiserhub.hotwater.boost(time_period)
            else:
                _LOGGER.info("Cancelling Hot Water boost")
                await instance.wiserhub.hotwater.cancel_overrides()
            await data.async_refresh()
        else:
            raise HomeAssistantError("This hub does not have hotwater functionality")

    @callback
    async def async_set_opentherm_parameter(service_call):
        endpoint = service_call.data[ATTR_OPENTHERM_ENDPOINT]
        param = service_call.data[ATTR_OPENTHERM_PARAM]
        value = service_call.data[ATTR_OPENTHERM_PARAM_VALUE]
        hub = service_call.data[ATTR_HUB]
        instance = data

        if get_instance_count(hass) > 1:
            if not hub:
                raise HomeAssistantError("Please specify a hub config entry id or name")
            else:
                # Find hub from config_entry_id or hub name
                if is_wiser_config_id(hass, hub):
                    instance = hass.data[DOMAIN][hub][DATA]
                else:
                    # Find hub by name
                    config_entry_id = get_config_entry_id_by_name(hass, hub)
                    if config_entry_id:
                        instance = hass.data[DOMAIN][config_entry_id][DATA]

        # If hub has opentherm
        if instance.wiserhub.system.opentherm:
            command = {param: value}
            try:
                await instance.wiserhub.system.opentherm.set_opentherm_parameter(
                    endpoint, command
                )
            except WiserHubRESTError:
                raise HomeAssistantError(
                    "Error setting parameter.  Invalid parameter/endpoint or maybe a parameter that cannot be set"
                )
            await data.async_refresh()

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
        WISER_SERVICES["SERVICE_SET_SCHEDULE_FROM_DATA"],
        set_schedule_from_data,
        schema=SET_SCHEDULE_FROM_DATA_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_COPY_SCHEDULE"],
        copy_schedule,
        schema=COPY_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_ASSIGN_SCHEDULE"],
        assign_schedule,
        schema=ASSIGN_SCHEDULE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_SET_DEVICE_MODE"],
        set_device_mode,
        schema=SET_DEVICE_MODE_SCHEMA,
    )

    if data.wiserhub.hotwater:
        hass.services.async_register(
            DOMAIN,
            WISER_SERVICES["SERVICE_BOOST_HOTWATER"],
            async_boost_hotwater,
            schema=BOOST_HOTWATER_SCHEMA,
        )

    hass.services.async_register(
        DOMAIN,
        WISER_SERVICES["SERVICE_SEND_OPENTHERM_COMMAND"],
        async_set_opentherm_parameter,
        schema=SEND_OPENTHERM_COMMAND_SCHEMA,
    )
