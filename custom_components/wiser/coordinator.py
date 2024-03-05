"""Data coordinator for Wiser hub."""
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from aioWiserHeatAPI.wiserhub import (
    TEMP_MAXIMUM,
    TEMP_MINIMUM,
    WiserAPI,
    WiserHubAuthenticationError,
    WiserHubConnectionError,
    WiserHubRESTError,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_AUTOMATIONS_PASSIVE,
    CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT,
    CONF_HEATING_BOOST_TEMP,
    CONF_HEATING_BOOST_TIME,
    CONF_HW_BOOST_TIME,
    CONF_RESTORE_MANUAL_TEMP_OPTION,
    CONF_SETPOINT_MODE,
    CUSTOM_DATA_STORE,
    DEFAULT_BOOST_TEMP,
    DEFAULT_BOOST_TEMP_TIME,
    DEFAULT_PASSIVE_TEMP_INCREMENT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SETPOINT_MODE,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class WiserSettings:
    """Class to hold wiser settings."""

    minimum_temp: float
    maximum_temp: float
    boost_temp: float
    boost_time: int
    hw_boost_time: int
    setpoint_mode: str
    enable_moments: bool
    enable_lts_sensors: bool
    previous_target_temp_option: str


@dataclass
class WiserData:
    """Class to hold wiser data."""

    data: dict


class WiserUpdateCoordinator(DataUpdateCoordinator):
    """Update coordinator to manage Wiser hub data."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize data update coordinator."""
        self.scan_interval = config_entry.options.get(
            CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL
        )
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            update_method=self.async_update_data,
            update_interval=timedelta(
                seconds=self.scan_interval
                if self.scan_interval > MIN_SCAN_INTERVAL
                else MIN_SCAN_INTERVAL
            ),
        )

        self.hub_version = 0
        self.last_update_time = datetime.now()
        self.last_update_status = ""
        self.minimum_temp = TEMP_MINIMUM
        self.maximum_temp = TEMP_MAXIMUM

        # Main option params
        self.boost_temp = config_entry.options.get(
            CONF_HEATING_BOOST_TEMP, DEFAULT_BOOST_TEMP
        )
        self.boost_time = config_entry.options.get(
            CONF_HEATING_BOOST_TIME, DEFAULT_BOOST_TEMP_TIME
        )
        self.hw_boost_time = config_entry.options.get(
            CONF_HW_BOOST_TIME, DEFAULT_BOOST_TEMP_TIME
        )
        self.setpoint_mode = config_entry.options.get(
            CONF_SETPOINT_MODE, DEFAULT_SETPOINT_MODE
        )
        self.previous_target_temp_option = config_entry.options.get(
            CONF_RESTORE_MANUAL_TEMP_OPTION, "Schedule"
        )

        # Automation option params
        self.enable_automations_passive_mode = config_entry.options.get(
            CONF_AUTOMATIONS_PASSIVE, False
        )

        self.passive_temperature_increment = config_entry.options.get(
            CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT, DEFAULT_PASSIVE_TEMP_INCREMENT
        )

        self.wiserhub = WiserAPI(
            host=config_entry.data[CONF_HOST],
            secret=config_entry.data[CONF_PASSWORD],
            extra_config_file=hass.config.config_dir + CUSTOM_DATA_STORE,
            enable_automations=self.enable_automations_passive_mode,
        )

        # Initialise api parameters
        self.wiserhub.api_parameters.stored_manual_target_temperature_alt_source = (
            self.previous_target_temp_option
        )
        self.wiserhub.api_parameters.passive_mode_increment = (
            self.passive_temperature_increment
        )

    async def async_update_data(self) -> WiserData:
        """Update data from the Wiser hub."""
        try:
            await self.wiserhub.read_hub_data()
            self.hub_version = self.wiserhub.system.hardware_generation
            self.last_update_time = datetime.now()
            self.last_update_status = "Success"

            _LOGGER.info("Hub update completed for %s", self.wiserhub.system.name)

            # Send event to websockets to notify hub update
            async_dispatcher_send(
                self.hass, "wiser_update_received", self.wiserhub.system.name
            )
            return True
        except (
            WiserHubConnectionError,
            WiserHubAuthenticationError,
            WiserHubRESTError,
        ) as ex:
            self.last_update_status = "Failed"
            _LOGGER.warning(ex)
        except Exception as ex:
            self.last_update_status = "Failed"
            _LOGGER.error(ex)
            raise ex
