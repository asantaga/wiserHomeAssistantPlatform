import logging
import asyncio
from .const import (
    DATA,
    DOMAIN,
    HOT_WATER,
    MANUFACTURER,
    MANUFACTURER_SCHNEIDER,
)

from .helpers import get_device_name, get_unique_id, get_identifier, hub_error_handler
from .schedules import WiserScheduleEntity

from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    wiser_selects = []

    if data.wiserhub.hotwater and not data.enable_hw_climate:
        _LOGGER.debug("Setting up Hot Water mode select")
        wiser_selects.extend([WiserHotWaterModeSelect(data)])

    # Add SmartPlugs (if any)
    if data.wiserhub.devices.smartplugs.count > 0:
        _LOGGER.debug("Setting up Smartplug mode select")
        for plug in data.wiserhub.devices.smartplugs.all:
            wiser_selects.extend([WiserSmartPlugModeSelect(data, plug.id)])

    if data.wiserhub.devices.lights.count > 0:
        _LOGGER.debug("Setting up Light mode select")
        for light in data.wiserhub.devices.lights.all:
            wiser_selects.extend([WiserLightModeSelect(data, light.id)])

            if light.is_dimmable:
                if light.is_led_indicator_supported:
                    wiser_selects.extend([WiserLightLedIndicatorSelect(data, light.id)])
                if light.is_power_on_behaviour_supported:
                    wiser_selects.extend(
                        [WiserLightPowerOnBehaviourSelect(data, light.id)]
                    )

    if data.wiserhub.devices.shutters.count > 0:
        _LOGGER.debug("Setting up Shutter mode select")
        for shutter in data.wiserhub.devices.shutters.all:
            wiser_selects.extend([WiserShutterModeSelect(data, shutter.id)])

    if data.wiserhub.devices.binary_sensor.count > 0:
        _LOGGER.debug("Setting up binary sensors enable notification select")
        for binary_sensor in data.wiserhub.devices.binary_sensor.all:
            wiser_selects.extend([WiserWindowNotificationEnableSelect(data, binary_sensor.id)])
            if binary_sensor.type in ["Window", "Door"]:
                wiser_selects.extend([WiserWindowTypeSelect(data, binary_sensor.id)])

    # Add PTCs
    if data.wiserhub.devices.power_tags_c.count > 0:
        for ptc in data.wiserhub.devices.power_tags_c.all:
            wiser_selects.extend([WiserPowerTagCModeSelect(data, ptc.id)])

    async_add_entities(wiser_selects)


class WiserSelectEntity(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initalise")

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} updating")

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._device_id)} Mode"

    @property
    def options(self) -> list[str]:
        return self._options

    @property
    def current_option(self) -> str:
        return self._device.mode

    @hub_error_handler
    async def async_select_option(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} to {option}")
        if option in self._options:
            await self.async_set_mode(option)
            await self.async_force_update()
        else:
            _LOGGER.error(
                f"{option} is not a valid {self.name}.  Please choose from {self._options}"
            )

    async def async_set_mode(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} mode to {option}")
        await self._device.set_mode(option)

    @property
    def unique_id(self):
        """Return unique ID of device"""
        return get_unique_id(
            self._data, self._device.product_type, "mode-select", self._device_id
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
            "manufacturer": MANUFACTURER,
            "model": self._device.product_type,
            "sw_version": self._device.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


class WiserHotWaterModeSelect(WiserSelectEntity, WiserScheduleEntity):
    def __init__(self, data) -> None:
        """Initialize the sensor."""
        super().__init__(data)
        self._hotwater = self._data.wiserhub.hotwater
        self._device_id = self._hotwater.id
        self._options = self._hotwater.available_modes
        self._schedule = self._hotwater.schedule
        self._state = self._hotwater.mode

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._hotwater = self._data.wiserhub.hotwater
        self._schedule = self._hotwater.schedule
        self.async_write_ha_state()

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, 0, 'Hot Water')} Mode"

    @property
    def current_option(self) -> str:
        return self._hotwater.mode

    async def async_set_mode(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} mode to {option}")
        if self._hotwater.is_override:
            await self._hotwater.cancel_overrides()
        await self._hotwater.set_mode(option)

    @property
    def unique_id(self):
        """Return unique Id."""
        return get_unique_id(self._data, "hotwater", "mode-select", 0)

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(
                self._data, self._data.wiserhub.hotwater.id, "Hot Water"
            ),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(
                        self._data, self._data.wiserhub.hotwater.id, "hot_water"
                    ),
                )
            },
            "manufacturer": MANUFACTURER,
            "model": HOT_WATER.title(),
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }


class WiserSmartPlugModeSelect(WiserSelectEntity, WiserScheduleEntity):
    def __init__(self, data, smartplug_id) -> None:
        """Initialize the sensor."""
        self._device_id = smartplug_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.smartplugs.get_by_id(self._device_id)
        self._options = self._device.available_modes
        self._schedule = self._device.schedule

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.smartplugs.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self.async_write_ha_state()


class WiserPowerTagCModeSelect(WiserSelectEntity, WiserScheduleEntity):
    def __init__(self, data, powertag_c_id) -> None:
        """Initialize the sensor."""
        self._device_id = powertag_c_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.power_tags_c.get_by_id(
            self._device_id
        )
        self._options = self._device.available_modes
        self._schedule = self._device.schedule

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.power_tags_c.get_by_id(
            self._device_id
        )
        self._schedule = self._device.schedule
        self.async_write_ha_state()


class WiserLightModeSelect(WiserSelectEntity, WiserScheduleEntity):
    def __init__(self, data, light_id) -> None:
        """Initialize the sensor."""
        self._device_id = light_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._options = self._device.available_modes
        self._schedule = self._device.schedule

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self.async_write_ha_state()


class WiserShutterModeSelect(WiserSelectEntity, WiserScheduleEntity):
    def __init__(self, data, shutter_id) -> None:
        """Initialize the sensor."""
        self._device_id = shutter_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.shutters.get_by_id(self._device_id)
        self._options = self._device.available_modes
        self._schedule = self._device.schedule

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.shutters.get_by_id(self._device_id)
        self._schedule = self._device.schedule
        self.async_write_ha_state()


class WiserLightPowerOnBehaviourSelect(WiserSelectEntity):
    def __init__(self, data, light_id) -> None:
        """Initialize the sensor."""
        self._device_id = light_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._options = self._device.available_power_on_behaviour

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._options = self._device.available_power_on_behaviour
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return unique ID of device."""
        return get_unique_id(
            self._data,
            self._device.product_type,
            "power_on_behaviour_select",
            self._device_id,
        )

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._device_id)} Power On Behaviour"

    @property
    def current_option(self) -> str:
        return self._device.power_on_behaviour

    @hub_error_handler
    async def async_select_option(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} to {option}")
        if option in self._options:
            await self._device.set_power_on_behaviour(option)
            await self.async_force_update()
        else:
            _LOGGER.error(
                f"{option} is not a valid {self.name}.  Please choose from {self._options}"
            )


class WiserLightLedIndicatorSelect(WiserSelectEntity):
    def __init__(self, data, light_id) -> None:
        """Initialize the sensor."""
        self._device_id = light_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._options = self._device.available_led_indicator

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.lights.get_by_id(self._device_id)
        self._options = self._device.available_led_indicator
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return unique ID of device."""
        return get_unique_id(
            self._data,
            self._device.product_type,
            "led-indicator",
            self._device_id,
        )

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._device_id)} Led Indicator"

    @property
    def current_option(self) -> str:
        return self._device.led_indicator

    @hub_error_handler
    async def async_select_option(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} to {option}")
        if option in self._options:
            await self.async_set_led_indicator(option)
            await self.async_force_update()
        else:
            _LOGGER.error(
                f"{option} is not a valid {self.name}.  Please choose from {self._options}"
            )

class WiserNotificationSelectEntity(CoordinatorEntity, SelectEntity):
    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        _LOGGER.debug(f"{self._data.wiserhub.system.name} {self.name} initalise")

    async def async_force_update(self, delay: int = 0):
        _LOGGER.debug(f"Hub update initiated by {self.name}")
        if delay:
            asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug(f"{self.name} updating")

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._device_id)} Enable Notification"

    @property
    def options(self) -> list[str]:
        return self._options

    @property
    def current_option(self) -> str:
        return self._device.enable_notification

    @hub_error_handler
    async def async_select_option(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} to {option}")
        if option in self._options:
            await self.async_set_enable_notification(option)
            await self.async_force_update()
        else:
            _LOGGER.error(
                f"{option} is not a valid {self.name}.  Please choose from {self._options}"
            )

    async def async_set_mode(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} mode to {option}")
        await self._device.set_enable_notification(option)

    @property
    def unique_id(self):
        """Return unique ID of device"""
        return get_unique_id(
            self._data, self._device.product_type, "enable_notification_select", self._device_id
        )

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_device_name(self._data, self._device_id),
            "identifiers": {(DOMAIN, get_identifier(self._data, self._device_id))},
            "manufacturer": MANUFACTURER_SCHNEIDER,
            "model": self._device.product_type,
            "sw_version": self._device.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

class WiserWindowNotificationEnableSelect(WiserNotificationSelectEntity, WiserScheduleEntity):
    def __init__(self, data, binary_sensor_id) -> None:
        """Initialize the sensor."""
        self._device_id = binary_sensor_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.binary_sensor.get_by_id(self._device_id)
        self._options = self._device.available_enable_notification

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.binary_sensor.get_by_id(self._device_id)
        self.async_write_ha_state()

    @property
    def current_option(self) -> str:
        return self._device.enable_notification
    
    @hub_error_handler
    async def async_select_option(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} enable notification {option}")
        if option in self._options:
            await self._device.set_enable_notification(option)
            await self.async_force_update()
        else:
            _LOGGER.error(
                f"{option} is not a valid {self.name}.  Please choose from {self._options}"
            )

    async def async_set_enable_notification(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} enable_notification {option}")
        await self._device.set_enable_notification(option)

class WiserWindowTypeSelect(WiserSelectEntity):
    def __init__(self, data, binary_sensor_id) -> None:
        """Initialize the sensor."""
        self._device_id = binary_sensor_id
        super().__init__(data)
        self._device = self._data.wiserhub.devices.binary_sensor.get_by_id(self._device_id)
        self._options = self._device.available_type

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        self._device = self._data.wiserhub.devices.binary_sensor.get_by_id(self._device_id)
        self._options = self._device.available_type
        self.async_write_ha_state()

    @property
    def unique_id(self):
        """Return unique ID of device."""
        return get_unique_id(
            self._data,
            self._device.product_type,
            "type",
            self._device_id,
        )

    @property
    def name(self):
        """Return Name of device."""
        return f"{get_device_name(self._data, self._device_id)} Type"

    @property
    def current_option(self) -> str:
        return self._device.type

    @hub_error_handler
    async def async_select_option(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} to {option}")
        if option in self._options:
            await self.async_set_type(option)
            await self.async_force_update()
        else:
            _LOGGER.error(
                f"{option} is not a valid {self.name}.  Please choose from {self._options}"
            )

    async def async_set_type(self, option: str) -> None:
        _LOGGER.debug(f"Setting {self.name} type {option}")
        await self._device.set_type(option)
