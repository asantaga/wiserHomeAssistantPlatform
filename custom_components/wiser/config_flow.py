"""
Config Flow for Wiser Rooms.

https://github.com/asantaga/wiserHomeAssistantPlatform
@msp1974

"""
from typing import Any
import voluptuous as vol
from aioWiserHeatAPI.wiserhub import WiserAPI
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aioWiserHeatAPI.exceptions import (
    WiserHubConnectionError,
    WiserHubAuthenticationError,
    WiserHubRESTError,
)

from homeassistant import config_entries, exceptions
from homeassistant.components import zeroconf
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    selector,
    EntitySelector,
    EntitySelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_AUTOMATIONS_PASSIVE,
    CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT,
    CONF_HEATING_BOOST_TEMP,
    CONF_HEATING_BOOST_TIME,
    CONF_RESTORE_MANUAL_TEMP_OPTION,
    CONF_SETPOINT_MODE,
    CONF_HW_BOOST_TIME,
    CONF_HOSTNAME,
    CONF_HW_AUTO_MODE,
    CONF_HW_CLIMATE,
    CONF_HW_HEAT_MODE,
    CONF_HW_SENSOR_ENTITY_ID,
    CONF_HW_TARGET_TEMP,
    CUSTOM_DATA_STORE,
    DEFAULT_BOOST_TEMP,
    DEFAULT_BOOST_TEMP_TIME,
    DEFAULT_PASSIVE_TEMP_INCREMENT,
    DEFAULT_HW_AUTO_MODE,
    DEFAULT_HW_HEAT_MODE,
    DEFAULT_HW_TARGET_TEMP,
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    WISER_HW_AUTO_MODES,
    WISER_HW_HEAT_MODES,
    WISER_RESTORE_TEMP_DEFAULT_OPTIONS,
    WISER_SETPOINT_MODES,
)

import logging

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=80): int,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(hass: HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    wiserhub = WiserAPI(
        host=data[CONF_HOST],
        port=data[CONF_PORT],
        secret=data[CONF_PASSWORD],
        extra_config_file=hass.config.config_dir + CUSTOM_DATA_STORE,
        enable_automations=False,
    )

    await wiserhub.read_hub_data()
    wiser_id = wiserhub.system.name
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

    def __init__(self) -> None:
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
            except WiserHubConnectionError:
                errors["base"] = "timeout_error"
            except (
                WiserHubRESTError,
                RuntimeError,
            ) as ex:
                errors["base"] = "unknown"
                _LOGGER.debug(ex)

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

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        if not discovery_info.name.startswith("WiserHeat"):
            return self.async_abort(reason="not_wiser_hub")
        host = discovery_info.host
        port = discovery_info.port
        zctype = discovery_info.type
        name = discovery_info.name.replace(f".{zctype}", "")

        await self.async_set_unique_id(get_unique_id(name))
        self._abort_if_unique_id_configured()

        self.context.update({"title_placeholders": {"name": name}})

        self.discovery_info.update(
            {
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_HOSTNAME: discovery_info.hostname.replace(".local.", ".local"),
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
            try:
                validated = await validate_input(self.hass, user_input)
            except WiserHubAuthenticationError:
                _LOGGER.warning("Authentication failure connecting to Wiser Hub")
                errors["base"] = "auth_failure"
            except WiserHubConnectionError:
                _LOGGER.warning("Connection timout error connecting to Wiser Hub")
                errors["base"] = "timeout_error_discovery"
            except (
                WiserHubRESTError,
                RuntimeError,
            ) as ex:
                _LOGGER.error("Unknown error connecting to Wiser Hub")
                _LOGGER.debug(ex)
                errors["base"] = "unknown"

            if "base" not in errors:
                # Add hub name to config
                user_input[CONF_NAME] = validated["title"]
                return self.async_create_entry(
                    title=validated["title"], data=user_input
                )

        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={
                "name": self.discovery_info[CONF_NAME],
                "hostname": self.discovery_info[CONF_HOSTNAME],
                "ip_address": self.discovery_info[CONF_HOST],
                "port": self.discovery_info[CONF_PORT],
            },
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HOST, default=self.discovery_info[CONF_HOST]
                    ): str,
                    vol.Optional(
                        CONF_PORT, default=self.discovery_info[CONF_PORT]
                    ): int,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )


class WiserOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle a option flow for wiser hub."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_automation_params(self, user_input=None):
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(data=options)

        data_schema = {
            vol.Optional(
                CONF_AUTOMATIONS_PASSIVE,
                default=self.config_entry.options.get(CONF_AUTOMATIONS_PASSIVE, False),
            ): bool,
            vol.Optional(
                CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT,
                default=self.config_entry.options.get(
                    CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT,
                    DEFAULT_PASSIVE_TEMP_INCREMENT,
                ),
            ): selector(
                {
                    "number": {
                        "min": 0.5,
                        "max": 20,
                        "step": 0.5,
                        "unit_of_measurement": "°C",
                        "mode": "box",
                    }
                }
            ),
        }
        return self.async_show_form(
            step_id="automation_params", data_schema=vol.Schema(data_schema)
        )

    async def async_step_hw_climate_params(self, user_input=None):
        if user_input is not None:
            options = self.config_entry.options | user_input
            return self.async_create_entry(data=options)

        data_schema = {
            vol.Optional(
                CONF_HW_CLIMATE,
                default=self.config_entry.options.get(CONF_HW_CLIMATE, False),
            ): bool,
            vol.Optional(
                CONF_HW_SENSOR_ENTITY_ID,
                default=self.config_entry.options.get(CONF_HW_SENSOR_ENTITY_ID),
            ): EntitySelector(
                EntitySelectorConfig(
                    domain=["sensor", "number", "input_number"],
                    device_class="temperature",
                    multiple=False,
                )
            ),
            vol.Optional(
                CONF_HW_AUTO_MODE,
                default=self.config_entry.options.get(
                    CONF_HW_AUTO_MODE, list(WISER_HW_AUTO_MODES.values())[0]
                ),
            ): selector(
                {
                    "select": {
                        "options": list(WISER_HW_AUTO_MODES.values()),
                        "mode": SelectSelectorMode.DROPDOWN,
                    }
                }
            ),
            vol.Optional(
                CONF_HW_HEAT_MODE,
                default=self.config_entry.options.get(
                    CONF_HW_HEAT_MODE, list(WISER_HW_HEAT_MODES.values())[0]
                ),
            ): selector(
                {
                    "select": {
                        "options": list(WISER_HW_HEAT_MODES.values()),
                        "mode": SelectSelectorMode.DROPDOWN,
                    }
                }
            ),
            vol.Optional(
                CONF_HW_TARGET_TEMP,
                default=self.config_entry.options.get(
                    CONF_HW_TARGET_TEMP, DEFAULT_HW_TARGET_TEMP
                ),
            ): int,
        }

        return self.async_show_form(
            step_id="hw_climate_params", data_schema=vol.Schema(data_schema)
        )

    async def async_step_main_params(self, user_input=None):
        """Handle options flow."""
        if user_input is not None:
            if user_input[CONF_HOST]:
                data = {
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PORT: user_input[CONF_PORT],
                    CONF_PASSWORD: self.config_entry.data[CONF_PASSWORD],
                    CONF_NAME: self.config_entry.data[CONF_NAME],
                }
                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=data
                )
            options = self.config_entry.options | user_input
            options.pop(CONF_HOST)
            options.pop(CONF_PORT)
            return self.async_create_entry(data=options)

        data_schema = {
            vol.Required(CONF_HOST, default=self.config_entry.data[CONF_HOST]): str,
            vol.Optional(
                CONF_PORT, default=self.config_entry.data.get(CONF_PORT, 80)
            ): int,
            vol.Optional(
                CONF_SCAN_INTERVAL,
                default=self.config_entry.options.get(
                    CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
                ),
            ): int,
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
                CONF_SETPOINT_MODE,
                default=self.config_entry.options.get(
                    CONF_SETPOINT_MODE, list(WISER_SETPOINT_MODES.values())[0]
                ),
            ): selector(
                {
                    "select": {
                        "options": list(WISER_SETPOINT_MODES.values()),
                        "mode": SelectSelectorMode.DROPDOWN,
                    }
                }
            ),
            vol.Optional(
                CONF_RESTORE_MANUAL_TEMP_OPTION,
                default=self.config_entry.options.get(
                    CONF_RESTORE_MANUAL_TEMP_OPTION,
                    WISER_RESTORE_TEMP_DEFAULT_OPTIONS[0],
                ),
            ): selector(
                {
                    "select": {
                        "options": WISER_RESTORE_TEMP_DEFAULT_OPTIONS,
                        "mode": SelectSelectorMode.DROPDOWN,
                    }
                }
            ),
        }
        return self.async_show_form(
            step_id="main_params", data_schema=vol.Schema(data_schema)
        )

    async def async_step_init(self, user_input=None):
        """Handle options flow."""
        return self.async_show_menu(
            step_id="init",
            menu_options=["main_params", "hw_climate_params", "automation_params"],
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(exceptions.HomeAssistantError):
    """Error to indicate there is invalid auth."""


class UnknownError(exceptions.HomeAssistantError):
    """Error to indicate there is an unknown error."""
