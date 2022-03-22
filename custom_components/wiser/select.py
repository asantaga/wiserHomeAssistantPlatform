import logging
from .const import (
    ATTR_TIME_PERIOD,
    DATA,
    DEFAULT_BOOST_TEMP_TIME,
    DOMAIN,
    MANUFACTURER,
    WISER_SERVICES
)
from .climate import (
    ATTR_COPYTO_ENTITY_ID,
    ATTR_FILENAME
)
from .helpers import get_device_name, get_unique_id, get_identifier
from .schedules import WiserScheduleEntity

import voluptuous as vol
from homeassistant.const import ATTR_MODE
from homeassistant.components.select import SelectEntity
from homeassistant.components.water_heater import SUPPORT_OPERATION_MODE
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv, entity_platform
from homeassistant.helpers.dispatcher import async_dispatcher_connect

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_selects = []

    if data.wiserhub.hotwater:
        _LOGGER.debug("Setting up Hot Water mode select")
        wiser_selects.extend([WiserHotWaterModeSelect(data)])

    # Add SmartPlugs (if any)
    if data.wiserhub.devices.smartplugs.count > 0:
        _LOGGER.debug("Setting up Smartplug mode select")
        for plug in data.wiserhub.devices.smartplugs.all:
            wiser_selects.extend([
                WiserSmartPlugModeSelect(data, plug.id)
            ])
    
    async_add_entities(wiser_selects)

    # Setup services
    platform = entity_platform.async_get_current_platform()

    if data.wiserhub.hotwater:
        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_SET_HOTWATER_MODE"],
            {
                vol.Required(ATTR_MODE): vol.In(data.wiserhub.hotwater.available_modes),
            },
            "async_set_mode"
        )

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_BOOST_HOTWATER"],
            {
                vol.Optional(ATTR_TIME_PERIOD, default=DEFAULT_BOOST_TEMP_TIME): vol.Coerce(int),
            },
            "async_boost"
        )

    if data.wiserhub.devices.smartplugs:
        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_SET_SMARTPLUG_MODE"],
            {
                vol.Required(ATTR_MODE): vol.In(data.wiserhub.devices.smartplugs.available_modes),
            },
            "async_set_mode"
        )

    if data.wiserhub.hotwater or data.wiserhub.devices.smartplugs:
        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_GET_ONOFF_SCHEDULE"],
            {
                vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
            },
            "async_get_schedule"
        )

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_SET_ONOFF_SCHEDULE"],
            {
                vol.Optional(ATTR_FILENAME, default=""): vol.Coerce(str),
            },
            "async_set_schedule"
        )

        platform.async_register_entity_service(
            WISER_SERVICES["SERVICE_COPY_ONOFF_SCHEDULE"],
            {
                vol.Required(ATTR_COPYTO_ENTITY_ID): cv.entity_id,
            },
            "async_copy_schedule"
        )


class WiserSelectEntity(SelectEntity):
    def __init__(self, data):
        """Initialize the sensor."""
        self._data = data
        _LOGGER.info(f"{self._data.wiserhub.system.name} {self.name} initalise")

    async def async_force_update(self):
        await self._data.async_update(no_throttle=True)

    @property
    def should_poll(self):
        """We don't want polling so return false."""
        return False

    @property
    def name(self):
        """Return Name of device."""
        return self._name

    @property
    def options(self) -> list[str]:
        return self._options

    @callback
    async def async_set_mode(self, mode):
        _LOGGER.error(f"Set mode service is not available on this entity")

    @callback
    async def async_boost(self, time_period: int):
        _LOGGER.error(f"Boost service is not available on this entity")

    @callback
    async def async_get_schedule(self, filename: str) -> None:
        _LOGGER.error(f"Get schedule service is not available on this entity")

    @callback
    async def async_set_schedule(self, filename: str) -> None:
        _LOGGER.error(f"Set schedule service is not available on this entity")

    @callback
    async def async_copy_schedule(self, to_entity_id)-> None:
        _LOGGER.error(f"Copy schedule service is not available on this entity")

    async def async_added_to_hass(self):
        """Subscribe for update from the hub."""

        async def async_update_state():
            """Update sensor state."""
            await self.async_update_ha_state(True)

        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, f"{self._data.wiserhub.system.name}-HubUpdateMessage", async_update_state
            )
        )


class WiserHotWaterModeSelect(WiserSelectEntity, WiserScheduleEntity):

    def __init__(self, data):
        """Initialize the sensor."""
        super().__init__(data)
        self._hotwater = self._data.wiserhub.hotwater
        self._options = self._hotwater.available_modes
        self._schedule = self._hotwater.schedule

    async def async_update(self):
        """Async update method."""
        self._hotwater = self._data.wiserhub.hotwater
        self._schedule = self._hotwater.schedule
    
    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, 0, 'Hot Water')} Mode"

    @property
    def current_option(self) -> str:
        return self._hotwater.mode

    def select_option(self, option: str) -> None:
        _LOGGER.debug("Setting hot water mode to {option}")
        self._hotwater.mode = option
        self._hotwater.cancel_overrides()
        self.hass.async_create_task(self.async_force_update())

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(self._data, "hotwater", "mode-select", 0)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, 0),
                "identifiers": {(DOMAIN, get_identifier(self._data, 0))},
                "manufacturer": MANUFACTURER,
                "model": self._data.wiserhub.system.product_type,
                "sw_version": self._data.wiserhub.system.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @callback
    async def async_set_mode(self, mode):
        _LOGGER.info(f"Setting Hot Water to {mode} mode")
        await self.hass.async_add_executor_job(
            self.select_option, mode
        )
        await self.async_force_update()

    @callback
    async def async_boost(self, time_period: int):
        _LOGGER.info(f"Boosting Hot Water for {time_period}m")
        await self.hass.async_add_executor_job(
            self._data.wiserhub.hotwater.boost, time_period
        )
        await self.async_force_update()

    @callback
    async def async_get_schedule(self, filename: str) -> None:
        _LOGGER.warning(f"The Save Heating Schedule to File service is deprecated and will be removed in a future release.  Please use the Save Schedule to File service instead")
        try:
            _LOGGER.info(f"Saving hot water schedule to file {filename}")
            await self.hass.async_add_executor_job(
                self._data.wiserhub.hotwater.schedule.save_schedule_to_yaml_file, filename
            )
        except Exception as ex:
            _LOGGER.error(f"Error saving hotwater schedule to file {filename}.  Error is {ex}")

    @callback
    async def async_set_schedule(self, filename: str) -> None:
        _LOGGER.warning(f"The Set Heating Schedule from File service is deprecated and will be removed in a future release.  Please use the Set Schedule from File service instead")
        try:
            _LOGGER.info(f"Setting hotwater schedule from file {filename}")
            await self.hass.async_add_executor_job(
                self._data.wiserhub.hotwater.schedule.set_schedule_from_yaml_file, filename
            )
            await self.async_force_update()
        except Exception as ex:
            _LOGGER.error(f"Error setting hotwater schedule from file {filename}.  Error is {ex}")


class WiserSmartPlugModeSelect(WiserSelectEntity, WiserScheduleEntity):

    def __init__(self, data, smartplug_id):
        """Initialize the sensor."""
        self._smartplug_id = smartplug_id
        super().__init__(data)
        self._smartplug = self._data.wiserhub.devices.smartplugs.get_by_id(self._smartplug_id)
        self._options = self._smartplug.available_modes
        self._schedule = self._smartplug.schedule


    async def async_update(self):
        """Async update method."""
        self._smartplug = self._data.wiserhub.devices.smartplugs.get_by_id(self._smartplug_id)
        self._schedule = self._smartplug.schedule
    
    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._smartplug_id)} Mode"

    @property
    def current_option(self) -> str:
        return self._smartplug.mode

    def select_option(self, option: str) -> None:
        if option and option in self._options:
            _LOGGER.debug("Setting smartplug mode to {option}")
            self._smartplug.mode = option
            self.hass.async_create_task(self.async_force_update())
        else:
            _LOGGER.error(f"{option} is not a valid Smart Plug mode.  Please choose from {self._options}")
    
    @property
    def unique_id(self):
        """Return unique ID for the plug."""
        return get_unique_id(self._data, self._smartplug.product_type, "mode-select", self._smartplug_id)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
                "name": get_device_name(self._data, self._smartplug_id),
                "identifiers": {(DOMAIN, get_identifier(self._data, self._smartplug_id))},
                "manufacturer": MANUFACTURER,
                "model": self._smartplug.product_type,
                "sw_version": self._smartplug.firmware_version,
                "via_device": (DOMAIN, self._data.wiserhub.system.name),
            }

    @callback
    async def async_set_mode(self, mode):
        _LOGGER.info(f"Setting {self._smartplug.name} to {mode} mode")
        await self.hass.async_add_executor_job(
            self.select_option, mode
        )
        await self.async_force_update()

    @callback
    async def async_get_schedule(self, filename: str) -> None:
        _LOGGER.warning(f"The Save Heating Schedule to File service is deprecated and will be removed in a future release.  Please use the Save Schedule to File service instead")
        try:
            if self._smartplug.schedule:
                _LOGGER.info(f"Saving {self._smartplug.name} schedule to file {filename}")
                await self.hass.async_add_executor_job(
                    self._smartplug.schedule.save_schedule_to_yaml_file, filename
                )
            else:
                _LOGGER.warning(f"{self._smartplug.name} has no schedule to save")
        except Exception as ex:
            _LOGGER.error(f"Error saving {self._smartplug.name} schedule to file {filename}.  Error is {ex}")

    @callback
    async def async_set_schedule(self, filename: str) -> None:
        _LOGGER.warning(f"The Set Heating Schedule from File service is deprecated and will be removed in a future release.  Please use the Set Schedule from File service instead")
        try:
            if self._smartplug.schedule:
                _LOGGER.info(f"Setting {self._smartplug.name} schedule from file {filename}")
                await self.hass.async_add_executor_job(
                    self._smartplug.schedule.set_schedule_from_yaml_file, filename
                )
                await self.async_force_update()
            else:
                _LOGGER.warning(f"{self._smartplug.name} has no schedule to assigned")
        except Exception as ex:
            _LOGGER.error(f"Error setting {self._smartplug.name} schedule from file {filename}.  Error is {ex}")

    @callback
    async def async_copy_schedule(self, to_entity_id)-> None:
        _LOGGER.warning(f"The Copy Heating Schedule service is deprecated and will be removed in a future release.  Please use the Copy Schedule service instead")
        to_smartplug_name = to_entity_id.replace("select.wiser_","").replace("_mode","").replace("_"," ")
        try:
            if self._smartplug.schedule:
                # Add Check that to_entity is of same type as from_entity
                _LOGGER.info(f"Copying schedule from {self._smartplug.name} to {to_smartplug_name}")
                await self.hass.async_add_executor_job(
                        self._smartplug.schedule.copy_schedule, self._data.wiserhub.devices.smartplugs.get_by_name(to_smartplug_name).schedule.id
                    )
                await self.async_force_update()
            else:
                _LOGGER.warning(f"{self._smartplug.name} has no schedule to copy")
        except Exception as ex:
            _LOGGER.error(f"Error copying schedule from {self._smartplug.name} to {to_smartplug_name}.  Error is {ex}")

