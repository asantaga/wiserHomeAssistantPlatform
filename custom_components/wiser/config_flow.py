import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PASSWORD
from homeassistant.core import HomeAssistantError
from .const import (
    _LOGGER,
    DATA_WISER_CONFIG,
    DOMAIN,
    CONF_BOOST_TEMP,
    CONF_BOOST_TEMP_TIME,
    DEFAULT_BOOST_TEMP,
    DEFAULT_BOOST_TEMP_TIME,
)
from wiserHeatingAPI.wiserHub import (
    wiserHub,
    WiserHubAuthenticationException,
    WiserHubTimeoutException,
    WiserHubDataNull,
    WiserRESTException,
)


@config_entries.HANDLERS.register(DOMAIN)
class WiserFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    # (this is not implemented yet)
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    def __init__(self):
        """Initialize the wiser flow."""
        self.device_config = {}
        self.discovery_schema = {}
        self.import_schema = {}
        self._ip = None
        self._secret = None
        self._name = None

    async def _test_connection(self, ip, secret):
        self.wiserhub = wiserHub(ip, secret)
        try:
            return await self.hass.async_add_executor_job(self.wiserhub.getWiserHubName)
        except:
            raise

    def _get_entry(self):
        return self.async_create_entry(
            title=self._title, data={"Host": self._host, "Name": self._name},
        )

    async def _create_entry(self):
        """
        Create entry for device.
        Generate a name to be used as a prefix for device entities.
        """
        self.device_config[CONF_NAME] = self._name
        title = self._name
        return self.async_create_entry(title=title, data=self.device_config)

    async def async_step_user(self, user_input=None):
        """
        Handle a Wiser Heat Hub config flow start.
        Manage device specific parameters.
        """
        errors = {}

        if user_input is not None:
            try:
                device = await self._test_connection(
                    ip=user_input[CONF_HOST], secret=user_input[CONF_PASSWORD]
                )

                self._name = device
                await self.async_set_unique_id(self._name)

                self._abort_if_unique_id_configured(
                    updates={
                        CONF_NAME: self._name,
                        CONF_HOST: user_input[CONF_HOST],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                        CONF_BOOST_TEMP: user_input[CONF_BOOST_TEMP],
                        CONF_BOOST_TEMP_TIME: user_input[CONF_BOOST_TEMP_TIME],
                    }
                )

                # set device config values
                self.device_config = {
                    CONF_NAME: self._name,
                    CONF_HOST: user_input[CONF_HOST],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_BOOST_TEMP: user_input[CONF_BOOST_TEMP],
                    CONF_BOOST_TEMP_TIME: user_input[CONF_BOOST_TEMP_TIME],
                }

                return await self._create_entry()

            except WiserHubAuthenticationException:
                return self.async_abort(reason="auth_failure")
            except WiserHubTimeoutException:
                return self.async_abort(reason="timeout_error")
            except (WiserRESTException, WiserHubDataNull):
                return self.async_abort(reason="not_successful")

        data = self.discovery_schema or {
            vol.Required(CONF_HOST): str,
            vol.Required(CONF_PASSWORD): str,
            vol.Required(CONF_BOOST_TEMP, default=DEFAULT_BOOST_TEMP): int,
            vol.Required(CONF_BOOST_TEMP_TIME, default=DEFAULT_BOOST_TEMP_TIME): int,
        }

        return self.async_show_form(
            step_id="user",
            description_placeholders=self.device_config,
            data_schema=vol.Schema(data),
            errors=errors,
        )

    async def async_step_zeroconf(self, discovery_info):
        # Check that it is a Wiser Hub
        if not discovery_info.get("name") or not discovery_info["name"].startswith(
            "WiserHeat"
        ):
            return self.async_abort(reason="not_wiser_device")

        self._host = discovery_info[CONF_HOST].rstrip(".")
        self._type = discovery_info["type"]
        self._name = discovery_info["name"].replace("." + self._type, "")
        self._title = self._name
        self._manufacturer = "Wiser"

        await self.async_set_unique_id(self._name)

        # If already configured then abort config
        self._abort_if_unique_id_configured(
            updates={CONF_HOST: self._host, CONF_NAME: self._name,}
        )

        # replace placeholder with hub mDNS name
        self.context["title_placeholders"] = {
            CONF_NAME: self._name,
        }

        self.discovery_schema = {
            vol.Required(CONF_HOST, default=self._host): str,
            vol.Required(CONF_PASSWORD,): str,
            vol.Required(CONF_BOOST_TEMP, default=DEFAULT_BOOST_TEMP): int,
            vol.Required(CONF_BOOST_TEMP_TIME, default=DEFAULT_BOOST_TEMP_TIME): int,
        }

        return await self.async_step_user()

    async def async_step_import(self, import_data):
        """
        Import wiser config from configuration.yaml.
        Triggered by async_setup only if a config entry doesn't already exist.
        We will attempt to validate the credentials
        and create an entry if valid. Otherwise, we will delegate to the user
        step so that the user can continue the config flow.
        """
        user_input = {}
        try:
            user_input = {
                CONF_HOST: import_data[0][CONF_HOST],
                CONF_PASSWORD: import_data[0][CONF_PASSWORD],
                CONF_BOOST_TEMP: import_data[0][CONF_BOOST_TEMP] or DEFAULT_BOOST_TEMP,
                CONF_BOOST_TEMP_TIME: import_data[0][CONF_BOOST_TEMP_TIME]
                or DEFAULT_BOOST_TEMP_TIME,
            }
        except (HomeAssistantError, KeyError):
            _LOGGER.debug(
                "No valid wiser configuration found for import, delegating to user step"
            )
            return await self.async_step_user(user_input=user_input)

        try:
            device = await self._test_connection(
                ip=user_input.get(CONF_HOST), secret=user_input.get(CONF_PASSWORD)
            )

            self._name = device
            await self.async_set_unique_id(self._name)

            self._abort_if_unique_id_configured(
                updates={
                    CONF_NAME: self._name,
                    CONF_HOST: user_input.get(CONF_HOST),
                    CONF_PASSWORD: user_input.get(CONF_PASSWORD),
                    CONF_BOOST_TEMP: user_input.get(CONF_BOOST_TEMP),
                    CONF_BOOST_TEMP_TIME: user_input.get(CONF_BOOST_TEMP_TIME),
                }
            )

            # set device config values
            self.device_config = user_input

            return await self._create_entry()
        except:
            _LOGGER.debug(
                "Error connecting to Wiser Hub using configuration found for import, delegating to user step"
            )
            return await self.async_step_user(user_input=user_input)
