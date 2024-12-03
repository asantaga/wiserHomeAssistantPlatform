"""Wiser Data Update Coordinator."""

import asyncio
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
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SCAN_INTERVAL,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_AUTOMATIONS_HW_AUTO_MODE,
    CONF_AUTOMATIONS_HW_BOOST_MODE,
    CONF_AUTOMATIONS_HW_CLIMATE,
    CONF_AUTOMATIONS_HW_HEAT_MODE,
    CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID,
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
    DEFAULT_HW_AUTO_MODE,
    DEFAULT_HW_BOOST_MODE,
    DEFAULT_HW_HEAT_MODE,
    DEFAULT_PASSIVE_TEMP_INCREMENT,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_SETPOINT_MODE,
    DOMAIN,
    MIN_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class WiserSettings:
    """Class to hold settings."""

    minimum_temp: float
    maximum_temp: float
    boost_temp: float
    boost_time: int
    hw_boost_time: int
    setpoint_mode: str
    enable_moments: bool
    enable_lts_sensors: bool
    enable_hw_climate: bool
    previous_target_temp_option: str
    hw_auto_mode: str
    hw_heat_mode: str
    hw_sensor_entity_id: str
    hw_target_temperature: float


@dataclass
class WiserData:
    """Class to hold Wiser data."""

    # settings: WiserSettings = field(init=False, default_factory=dict)
    data: dict


class WiserUpdateCoordinator(DataUpdateCoordinator):
    """Wiser hub data update coordinator."""

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

        # Passive Mode Automation option params
        self.enable_automations_passive_mode = config_entry.options.get(
            CONF_AUTOMATIONS_PASSIVE, {}
        ).get(CONF_AUTOMATIONS_PASSIVE, False)

        self.passive_temperature_increment = config_entry.options.get(
            CONF_AUTOMATIONS_PASSIVE, {}
        ).get(CONF_AUTOMATIONS_PASSIVE_TEMP_INCREMENT, DEFAULT_PASSIVE_TEMP_INCREMENT)

        # HW Climate Automation
        self.hw_sensor_entity_id = config_entry.options.get(
            CONF_AUTOMATIONS_HW_CLIMATE, {}
        ).get(CONF_AUTOMATIONS_HW_SENSOR_ENTITY_ID)
        self.enable_hw_climate = config_entry.options.get(
            CONF_AUTOMATIONS_HW_CLIMATE, {}
        ).get(CONF_AUTOMATIONS_HW_CLIMATE, False)
        self.hw_auto_mode = config_entry.options.get(
            CONF_AUTOMATIONS_HW_CLIMATE, {}
        ).get(CONF_AUTOMATIONS_HW_AUTO_MODE, DEFAULT_HW_AUTO_MODE)
        self.hw_heat_mode = config_entry.options.get(
            CONF_AUTOMATIONS_HW_CLIMATE, {}
        ).get(CONF_AUTOMATIONS_HW_HEAT_MODE, DEFAULT_HW_HEAT_MODE)
        self.hw_boost_mode = config_entry.options.get(
            CONF_AUTOMATIONS_HW_CLIMATE, {}
        ).get(CONF_AUTOMATIONS_HW_BOOST_MODE, DEFAULT_HW_BOOST_MODE)

        self.wiserhub = WiserAPI(
            host=config_entry.data[CONF_HOST],
            port=config_entry.data.get(CONF_PORT, 80),
            secret=str(config_entry.data[CONF_PASSWORD]).strip(),
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

        self.wiserhub.api_parameters.boost_temp_delta = self.boost_temp

        # HW climate mode
        self.wiserhub.api_parameters.hw_climate_mode = self.enable_hw_climate

    async def async_update_data(self) -> WiserData:
        """Update data from hub."""
        try:
            self.last_update_status = "Failed"
            await self.wiserhub.read_hub_data()
            self.hub_version = self.wiserhub.system.hardware_generation
            self.last_update_time = datetime.now()
            self.last_update_status = "Success"

            _LOGGER.info("Hub update completed for %s", self.wiserhub.system.name)

            # Send event to websockets to notify hub update
            async_dispatcher_send(
                self.hass, "wiser_update_received", self.wiserhub.system.name
            )
        except (
            WiserHubConnectionError,
            WiserHubAuthenticationError,
            WiserHubRESTError,
        ) as ex:
            _LOGGER.warning(
                "Error fetching wiser (%s) data. %s",
                f"{DOMAIN}-{self.config_entry.data.get(CONF_NAME)}",
                ex,
            )
        except asyncio.CancelledError:
            _LOGGER.warning("Asyncio task cancelled during hub update!")
        except Exception as ex:  # pylint: disable=broad-except  # noqa: BLE001
            _LOGGER.error(
                "Unknown error fetching wiser (%s) data. %s.  Please report this error to the integration owner",
                f"{DOMAIN}-{self.config_entry.data.get(CONF_NAME)}",
                ex,
            )
        else:
            return True
