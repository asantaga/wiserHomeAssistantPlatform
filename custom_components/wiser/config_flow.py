"""
Config Flow for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
@msp1974

"""
import requests.exceptions
from typing import Any
import voluptuous as vol
from wiserHeatAPIv2.wiserhub import WiserAPI
from wiserHeatAPIv2.exceptions import (
    WiserHubConnectionError,
    WiserHubAuthenticationError,
    WiserHubRESTError,
)

from homeassistant import config_entries, exceptions
from homeassistant.components import zeroconf
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_HEATING_BOOST_TEMP,
    CONF_HEATING_BOOST_TIME,
    CONF_LTS_SENSORS,
    CONF_MOMENTS,
    CONF_SETPOINT_MODE,
    CONF_HW_BOOST_TIME,
    DEFAULT_BOOST_TEMP,
    DEFAULT_BOOST_TEMP_TIME,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SETPOINT_MODE,
    DOMAIN,
    SETPOINT_MODE_BOOST,
    SETPOINT_MODE_BOOST_AUTO
)

import logging
_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_HOST): str, vol.Required(CONF_PASSWORD): str}
)


async def validate_input(hass, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    wiser = await hass.async_add_executor_job(
        WiserAPI, data[CONF_HOST], data[CONF_PASSWORD],
    )
    wiser_id = wiser.system.name
    return {"title": wiser_id, "unique_id": get_unique_id(wiser_id)}


def get_unique_id(wiser_id: str):
    return str(f"{DOMAIN}-{wiser_id}")


@config_entries.HANDLERS.register(DOMAIN)
class WiserFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """
    WiserFlowHandler configuration method.

    The schema version of the entries that it creates
    Home Assistant will call your migrate method if the version changes
    (this is not implemented yet)
    """

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the wiser flow."""
        self.discovery_info = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Return flow options."""
        return WiserOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """
        Handle a Wiser Heat Hub config flow start.

        Manage device specific parameters.
        """
        errors = {}
        if user_input is not None:
            try:
                validated = await validate_input(self.hass, user_input)
            except WiserHubAuthenticationError:
                errors["base"] = "auth_failure"
            except (WiserHubConnectionError, requests.exceptions.ConnectionError):
                errors["base"] = "timeout_error"
            except (WiserHubRESTError, RuntimeError, Exception):
                errors["base"] = "unknown"

            if "base" not in errors:
                await self.async_set_unique_id(validated["unique_id"])
                self._abort_if_unique_id_configured()

                # Add hub name to config
                user_input[CONF_NAME] = validated["title"]
                return self.async_create_entry(
                    title=validated["title"], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.discovery_info or DATA_SCHEMA,
            errors=errors,
        )
    

    async def async_step_zeroconf(self, discovery_info: zeroconf.ZeroconfServiceInfo) -> FlowResult:
        """Handle zeroconf discovery."""
        if not discovery_info.name.startswith("WiserHeat"):
            return self.async_abort(reason="not_wiser_hub")

        host = discovery_info.host
        zctype = discovery_info.type
        name = discovery_info.name.replace(f".{zctype}", "")

        await self.async_set_unique_id(get_unique_id(name))
        self._abort_if_unique_id_configured()

        self.context.update({"title_placeholders": {"name": name}})

        self.discovery_info.update(
            {
                CONF_HOST: host,
                CONF_NAME: name,
            }
        )
        return await self.async_step_zeroconf_confirm()
    

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] = None
    ) -> FlowResult:
        """Handle a confirmation flow initiated by zeroconf."""
        errors = {}
        if user_input is not None:
            user_input[CONF_HOST] = self.discovery_info[CONF_HOST]
            try:
                validated = await validate_input(self.hass, user_input)
            except WiserHubAuthenticationError:
                _LOGGER.warning("Authentication failure connecting to Wiser Hub")
                errors["base"] = "auth_failure"
            except (WiserHubConnectionError, requests.exceptions.ConnectionError):
                _LOGGER.warning("Connection timout error connecting to Wiser Hub")
                errors["base"] = "timeout_error_discovery"
            except (WiserHubRESTError, RuntimeError, Exception):
                _LOGGER.exception("Unknown error connecting to Wiser Hub")
                errors["base"] = "unknown"

            if "base" not in errors:
                # Add hub name to config
                user_input[CONF_NAME] = validated["title"]
                return self.async_create_entry(
                    title=validated["title"], data=user_input
                )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"name": self.discovery_info[CONF_NAME]},
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )


class WiserOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for wiser hub."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        data_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_HEATING_BOOST_TEMP,
                    default=self.config_entry.options.get(
                        CONF_HEATING_BOOST_TEMP, DEFAULT_BOOST_TEMP
                    ),
                ): int,
                vol.Optional(
                    CONF_HEATING_BOOST_TIME,
                    default=self.config_entry.options.get(
                        CONF_HEATING_BOOST_TIME, DEFAULT_BOOST_TEMP_TIME
                    ),
                ): int,
                vol.Optional(
                    CONF_HW_BOOST_TIME,
                    default=self.config_entry.options.get(
                        CONF_HW_BOOST_TIME, DEFAULT_BOOST_TEMP_TIME
                    ),
                ): int,
                vol.Optional(
                    CONF_SCAN_INTERVAL,
                    default=self.config_entry.options.get(
                        CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                    ),
                ): int,
                vol.Optional(
                    CONF_MOMENTS,
                    default=self.config_entry.options.get(
                        CONF_MOMENTS, False
                    ),
                ): bool,
                vol.Optional(
                    CONF_LTS_SENSORS,
                    default=self.config_entry.options.get(
                        CONF_LTS_SENSORS, False
                    ),
                ): bool,
                vol.Optional(
                    CONF_SETPOINT_MODE,
                    default=self.config_entry.options.get(
                        CONF_SETPOINT_MODE, DEFAULT_SETPOINT_MODE
                    ),
                ): vol.In([DEFAULT_SETPOINT_MODE, SETPOINT_MODE_BOOST,  SETPOINT_MODE_BOOST_AUTO]),
            }
        )
        return self.async_show_form(step_id="init", data_schema=data_schema)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class UnknownError(exceptions.HomeAssistantError):
    """Error to indicate there is an unknown error."""
