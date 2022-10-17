from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field

from homeassistant.config_entries import ConfigEntry

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from homeassistant.const import (
    CONF_HOST,
    CONF_MINIMUM,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
)

from aioWiserHeatAPI.wiserhub import (
    TEMP_MINIMUM,
    TEMP_MAXIMUM,
    WiserAPI,
    WiserHubConnectionError,
    WiserHubAuthenticationError,
    WiserHubRESTError,
)

from .const import (
    CONF_MOMENTS,
    CONF_RESTORE_MANUAL_TEMP_OPTION,
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
    WISER_CARD_FILENAMES,
    UPDATE_LISTENER,
    UPDATE_TRACK,
    URL_BASE,
    WISER_PLATFORMS,
    WISER_SERVICES,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class WiserSettings:
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
    # settings: WiserSettings = field(init=False, default_factory=dict)
    data: dict


class WiserUpdateCoordinator(DataUpdateCoordinator):

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
        """Initialize data update coordinator."""

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN} ({config_entry.unique_id})",
            update_interval=timedelta(seconds=30),
        )

        self.wiserhub = WiserAPI(
            host=config_entry.data[CONF_HOST],
            secret=config_entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        )
        self._name = config_entry.data[CONF_NAME]
        self.last_update_time = datetime.now()
        self.last_update_status = ""
        self.minimum_temp = TEMP_MINIMUM
        self.maximum_temp = TEMP_MAXIMUM
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
        self.enable_moments = config_entry.options.get(CONF_MOMENTS, False)
        self.enable_lts_sensors = config_entry.options.get(CONF_LTS_SENSORS, False)
        self.previous_target_temp_option = config_entry.options.get(
            CONF_RESTORE_MANUAL_TEMP_OPTION, "Schedule"
        )

    async def _async_update_data(self) -> WiserData:
        if await self.wiserhub.read_hub_data():
            self.last_update_time = datetime.now()
            self.last_update_status = "Success"
            return True
        else:
            self.last_update_status = "Failed"
            return False
