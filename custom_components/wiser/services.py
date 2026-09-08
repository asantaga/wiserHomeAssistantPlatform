# Initialise global services
import asyncio
import os
import aiofiles
import voluptuous as vol
import logging
from aioWiserHeatAPI.exceptions import (
    WiserHubAuthenticationError,
    WiserHubConnectionError,
    WiserHubResponseError,
)
from .const import (
    ATTR_FILENAME,
    ATTR_HUB,
    ATTR_OPENTHERM_ENDPOINT,
    ATTR_OPENTHERM_PARAM,
    ATTR_OPENTHERM_PARAM_VALUE,
    ATTR_OPENTHERM_TEMPERATURE,
    ATTR_OPENTHERM_REQUEST_ID,
    ATTR_SCHEDULE,
    ATTR_SCHEDULE_ID,
    ATTR_SCHEDULE_NAME,
    ATTR_TIME_PERIOD,
    ATTR_TO_ENTITY_ID,
    DATA,
    DEFAULT_BOOST_TEMP_TIME,
    DOMAIN,
    EVENT_OPENTHERM_COMMAND_FAILED,
    WISER_SERVICES,
)
from .coordinator import WiserHubRESTError
from .helpers import get_config_entry_id_by_name, get_instance_count, is_wiser_config_id
from .opentherm import (
    async_set_parameter,
    opentherm_parameter_feedback,
    opentherm_parameter_matches,
    parse_parameter_value,
)
from homeassistant.const import (
    ATTR_ENTITY_ID,
    ATTR_MODE,
)
from homeassistant.core import HomeAssistant, callback, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

OPENTHERM_CONFIRMATION_WINDOW = 90


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
            # ``parameter_value`` remains available for existing YAML callers.
            # The action UI uses the friendlier Celsius ``temperature`` field.
            vol.Exclusive(ATTR_OPENTHERM_PARAM_VALUE, "opentherm_value"): vol.Any(
                str, bool, int, float
            ),
            vol.Exclusive(ATTR_OPENTHERM_TEMPERATURE, "opentherm_value"): vol.Coerce(
                float
            ),
            # Optional caller token used to correlate asynchronous confirmation
            # failures without coupling Wiser to any consuming integration.
            vol.Optional(ATTR_OPENTHERM_REQUEST_ID): vol.Coerce(str),
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
                    if file_dir and not os.path.exists(file_dir):
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

        if entity_id is not None:
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
        elif schedule_id is not None:
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
        elif schedule_name is not None:
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

    async def async_set_opentherm_parameter(service_call):
        endpoint = service_call.data[ATTR_OPENTHERM_ENDPOINT]
        param = service_call.data[ATTR_OPENTHERM_PARAM]
        if ATTR_OPENTHERM_TEMPERATURE in service_call.data:
            # The Wiser API represents temperatures in tenths of a degree.
            value = round(service_call.data[ATTR_OPENTHERM_TEMPERATURE] * 10)
        elif ATTR_OPENTHERM_PARAM_VALUE in service_call.data:
            value = service_call.data[ATTR_OPENTHERM_PARAM_VALUE]
        else:
            raise HomeAssistantError("Please provide an OpenTherm temperature")
        request_id = service_call.data.get(ATTR_OPENTHERM_REQUEST_ID)
        hub = service_call.data[ATTR_HUB]
        instance = data

        if hub:
            config_entry_id = (
                hub
                if is_wiser_config_id(hass, hub)
                else get_config_entry_id_by_name(hass, hub)
            )
            if not config_entry_id:
                raise HomeAssistantError("The specified Wiser hub was not found")
            instance = hass.data[DOMAIN].get(config_entry_id, {}).get(DATA)
            if instance is None:
                raise HomeAssistantError("The specified Wiser hub is not loaded")
        elif get_instance_count(hass) > 1:
            raise HomeAssistantError("Please specify a hub config entry id or name")

        if not instance.wiserhub.system.opentherm:
            raise HomeAssistantError("This hub does not have OpenTherm functionality")
        lock = getattr(instance, "_opentherm_write_lock", None)
        if lock is None:
            lock = instance._opentherm_write_lock = asyncio.Lock()

        revision = getattr(instance, "_opentherm_write_revision", 0) + 1
        instance._opentherm_write_revision = revision
        previous_verification = getattr(
            instance, "_opentherm_verification_task", None
        )
        if previous_verification is not None:
            previous_verification.cancel()
            instance._opentherm_verification_task = None

        async def write_parameter():
            try:
                await async_set_parameter(
                    instance.wiserhub.system, endpoint, param, value
                )
            except ValueError as err:
                raise HomeAssistantError(str(err)) from err
            except (
                WiserHubRESTError,
                WiserHubConnectionError,
                WiserHubResponseError,
                WiserHubAuthenticationError,
            ) as err:
                raise HomeAssistantError(
                    f"Unable to set OpenTherm parameter {param}: {err}"
                ) from err

        async def verify_on_next_update():
            update_received = asyncio.Event()
            remove_listener = instance.async_add_listener(update_received.set)
            retry_sent = False
            retry_error = None
            deadline = (
                asyncio.get_running_loop().time() + OPENTHERM_CONFIRMATION_WINDOW
            )

            async def report_failure_if_still_mismatched():
                """Report only a mismatch that survives the full window."""
                if (
                    instance._opentherm_write_revision != revision
                    or instance.last_update_status != "Success"
                    or opentherm_parameter_matches(
                        instance.wiserhub.system, endpoint, param, value
                    )
                    is not False
                ):
                    return

                reported = opentherm_parameter_feedback(
                    instance.wiserhub.system, endpoint, param
                )
                requested = parse_parameter_value(value) / 10
                if retry_error is None:
                    _LOGGER.warning(
                        "OpenTherm parameter %s still does not match after "
                        "retry and confirmation window: requested=%s reported=%s",
                        param,
                        requested,
                        reported,
                    )
                    message = (
                        f"OpenTherm parameter {param} did not remain at "
                        f"{requested:g} °C after one retry and the "
                        f"{OPENTHERM_CONFIRMATION_WINDOW}-second confirmation "
                        f"window. Wiser reports {reported:g} °C. No further "
                        "retry will be sent."
                    )
                else:
                    _LOGGER.warning(
                        "Unable to retry OpenTherm parameter %s: %s; "
                        "requested=%s reported=%s",
                        param,
                        retry_error,
                        requested,
                        reported,
                    )
                    message = (
                        f"OpenTherm parameter {param} did not remain at "
                        f"{requested:g} °C, and its retry could not be sent: "
                        f"{retry_error}. Wiser reports {reported:g} °C. No "
                        "further retry will be sent."
                    )
                event_data = {
                    "request_id": request_id,
                    "endpoint": endpoint,
                    "parameter": param,
                    "requested": requested,
                    "reported": reported,
                }
                if retry_error is not None:
                    event_data["error"] = str(retry_error)
                hass.bus.async_fire(
                    EVENT_OPENTHERM_COMMAND_FAILED,
                    event_data,
                    context=service_call.context,
                )
                await hass.services.async_call(
                    "persistent_notification",
                    "create",
                    {
                        "title": "Wiser OpenTherm command",
                        "message": message,
                        "notification_id": (
                            f"wiser_opentherm_{instance.wiserhub.system.name}_{param}"
                        ),
                    },
                    blocking=False,
                )

            try:
                while True:
                    remaining = deadline - asyncio.get_running_loop().time()
                    timed_out = remaining <= 0
                    if remaining <= 0:
                        _LOGGER.debug(
                            "OpenTherm confirmation window expired for parameter %s",
                            param,
                        )
                    else:
                        try:
                            await asyncio.wait_for(update_received.wait(), remaining)
                        except asyncio.TimeoutError:
                            timed_out = True
                            _LOGGER.debug(
                                "OpenTherm confirmation window expired for parameter %s",
                                param,
                            )

                    if not timed_out:
                        update_received.clear()
                    if instance._opentherm_write_revision != revision:
                        return
                    if instance.last_update_status != "Success":
                        if timed_out:
                            return
                        continue

                    matches = opentherm_parameter_matches(
                        instance.wiserhub.system, endpoint, param, value
                    )
                    if matches is None:
                        return
                    if matches:
                        if retry_sent or timed_out:
                            return
                        continue

                    if retry_sent:
                        # A slow hub may still apply the retry. Keep observing
                        # until the deadline instead of warning on this update.
                        if timed_out:
                            await report_failure_if_still_mismatched()
                            return
                        continue

                    async with lock:
                        if instance._opentherm_write_revision != revision:
                            return
                        _LOGGER.warning(
                            "OpenTherm parameter %s did not match after writing; "
                            "retrying once",
                            param,
                        )
                        retry_sent = True
                        try:
                            await write_parameter()
                        except HomeAssistantError as err:
                            # This verifier runs after the service call has
                            # returned, so surface a failed retry through the
                            # same event and notification as a rejected value.
                            # Keep watching until the original deadline in case
                            # the first write was merely slow to settle.
                            retry_error = err
                            continue
                        # Give the retry its own complete confirmation window.
                        # Time spent confirming the original write must not
                        # shorten the period in which the retry may settle.
                        deadline = (
                            asyncio.get_running_loop().time()
                            + OPENTHERM_CONFIRMATION_WINDOW
                        )
                        # Do not let the refresh initiated by the retry count as
                        # independent confirmation that the boiler rejected it.
                        remove_listener()
                        await instance.async_refresh()
                        update_received = asyncio.Event()
                        remove_listener = instance.async_add_listener(
                            update_received.set
                        )
            finally:
                remove_listener()
                if (
                    getattr(instance, "_opentherm_verification_task", None)
                    is asyncio.current_task()
                ):
                    instance._opentherm_verification_task = None

        # Keep each initial write atomic per hub. A later command increments
        # the revision and cancels this command's pending confirmation.
        async with lock:
            await write_parameter()
            await instance.async_refresh()

            matches = opentherm_parameter_matches(
                instance.wiserhub.system, endpoint, param, value
            )
            if matches is not None:
                instance._opentherm_verification_task = hass.async_create_task(
                    verify_on_next_update(),
                    f"Wiser OpenTherm confirmation: {param}",
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
