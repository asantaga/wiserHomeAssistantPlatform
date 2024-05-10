"""Number Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom
from aioWiserHeatAPI.wiserhub import TEMP_MAXIMUM, TEMP_MINIMUM

from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, LEGACY_NAMES
from .entity import WiserBaseEntity, WiserBaseEntityDescription
from .helpers import get_entities

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class WiserNumberEntityDescription(NumberEntityDescription, WiserBaseEntityDescription):
    """A class that describes Wiser number entities."""

    min_value: Callable[[Any], int | float] | None = None
    max_value: Callable[[Any], int | float] | None = None
    step: int | float | None = 1
    set_fn: Callable[[Any], str] | None = None


WISER_NUMBERS: tuple[WiserNumberEntityDescription, ...] = (
    WiserNumberEntityDescription(
        key="away_mode_target_temperature",
        name="Away Mode Target Temperature",
        device="system",
        icon="mdi:thermometer-low",
        min_value=TEMP_MINIMUM,
        max_value=TEMP_MAXIMUM,
        step=0.5,
        set_fn=lambda x, t: x.set_away_mode_target_temperature(t),
        value_fn=lambda x: x.away_mode_target_temperature,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    WiserNumberEntityDescription(
        key="floor_temp_offset",
        name="Floor Temp Offset",
        device_collection="devices.heating_actuators",
        icon="mdi:thermometer-low",
        min_value=-9,
        max_value=9,
        step=1,
        supported=lambda dev, hub: hasattr(dev.floor_temperature_sensor, "sensor_type")
        and dev.floor_temperature_sensor.sensor_type != "Not_Fitted",
        set_fn=lambda x, t: x.floor_temperature_sensor.set_temperature_offset(t),
        value_fn=lambda x: x.floor_temperature_sensor.temperature_offset,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    WiserNumberEntityDescription(
        key="indoor_discomfort_temperature",
        name="Indoor Discomfort Temperature",
        device="system",
        icon="mdi:home-thermometer",
        min_value=20,
        max_value=32,
        step=0.5,
        supported=lambda dev, hub: hub.system.hardware_generation == 2,
        set_fn=lambda x, t: x.set_outdoor_discomfort_temperature(t),
        value_fn=lambda x: x.outdoor_discomfort_temperature,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    WiserNumberEntityDescription(
        key="outdoor_discomfort_temperature",
        name="Outdoor Discomfort Temperature",
        device="system",
        icon="mdi:home-thermometer",
        min_value=20,
        max_value=30,
        step=0.5,
        supported=lambda dev, hub: hub.system.hardware_generation == 2,
        set_fn=lambda x, t: x.set_indoor_discomfort_temperature(t),
        value_fn=lambda x: x.indoor_discomfort_temperature,
        unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    entities = get_entities(data, WISER_NUMBERS, WiserNumber)
    async_add_entities(entities)

    return True


class WiserNumber(WiserBaseEntity, NumberEntity):
    """Class to provide select entities for Wiser device control."""

    entity_description: WiserNumberEntityDescription
    _attr_has_entity_name = not LEGACY_NAMES

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserNumberEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        """Init wiser sensor."""
        super().__init__(coordinator, description, device, "number")

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        return self.entity_description.min_value

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return self.entity_description.max_value

    @property
    def native_step(self) -> float:
        """Return the step value."""
        return self.entity_description.step

    @property
    def mode(self) -> NumberMode:
        """Return the mode of the entity."""
        return NumberMode.AUTO

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor, if any."""
        if self.entity_description.unit_of_measurement:
            return self.entity_description.unit_of_measurement

        if self._device and self.entity_description.unit_fn is not None:
            return self.entity_description.unit_fn(self._device)
        return super().native_unit_of_measurement

    @property
    def native_value(self):
        """Return device value."""
        return self.entity_description.value_fn(self._device)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        _LOGGER.debug("Setting %s to %sC", self.name, value)
        await self.entity_description.set_fn(self._device, value)
        await self.async_force_update()
