"""Number Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""
from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from aioWiserHeatAPI.const import TEXT_UNKNOWN
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom
from aioWiserHeatAPI.wiserhub import TEMP_MAXIMUM, TEMP_MINIMUM

from config.custom_components.wiser.entity import WiserBaseEntity
from homeassistant.components.number import (
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, LEGACY_NAMES
from .helpers import getattrd

_LOGGER = logging.getLogger(__name__)


@dataclass
class WiserNumberEntityDescription(NumberEntityDescription):
    """A class that describes Wiser sensor entities."""

    name_fn: Callable[[Any], str] | None = None
    device: str | None = None
    device_collection: list | None = None
    available_fn: Callable[[Any], bool] | None = None
    icon_fn: Callable[[Any], str] | None = None
    min_value: Callable[[Any], int | float] | None = None
    max_value: Callable[[Any], int | float] | None = None
    step: int | float | None = 1
    set_fn: Callable[[Any], str] | None = None
    value_fn: Callable[[Any], int | float] | None = None
    legacy_name_fn: Callable[[Any], str] | None = None
    legacy_type: str = None
    extra_state_attributes: dict[str, Callable[[Any], float | str]] | None = None


WISER_NUMBERS: tuple[WiserNumberEntityDescription, ...] = (
    WiserNumberEntityDescription(
        key="away_mode_target_temperature",
        name="Away Mode Target Temperature",
        device="system",
        min_value=TEMP_MINIMUM,
        max_value=TEMP_MAXIMUM,
        step=0.5,
        set_fn=lambda x, t: x.set_away_mode_target_temperature(t),
        value_fn=lambda x: x.away_mode_target_temperature,
    ),
    WiserNumberEntityDescription(
        key="floor_temp_offset",
        name="Floor Temp Offset",
        device_collection="devices.heating_actuators",
        min_value=-9,
        max_value=9,
        step=1,
        available_fn=lambda x: x.floor_temperature_sensor.sensor_type != "Not_Fitted",
        set_fn=lambda x, t: x.floor_temperature_sensor.set_temperature_offset(t),
        value_fn=lambda x: x.floor_temperature_sensor.temperature_offset,
    ),
)


def _attr_exist(device, entity_desc: WiserNumberEntityDescription) -> bool:
    """Check if an attribute exists for device."""
    try:
        r = entity_desc.value_fn(device)
        if r is not None and r != TEXT_UNKNOWN:
            if entity_desc.available_fn:
                return entity_desc.available_fn(device)
            return True
        return False
    except AttributeError:
        return False


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    wiser_numbers = []

    for number_desc in WISER_NUMBERS:
        # get device or device collection
        if number_desc.device_collection and getattrd(
            data.wiserhub, number_desc.device_collection
        ):
            for device in getattrd(data.wiserhub, number_desc.device_collection).all:
                if _attr_exist(device, number_desc):
                    _LOGGER.info("Adding %s", device.name)
                    wiser_numbers.append(
                        WiserNumber(
                            data,
                            number_desc,
                            device,
                        )
                    )
        elif number_desc.device and getattrd(data.wiserhub, number_desc.device):
            device = getattrd(data.wiserhub, number_desc.device)
            if _attr_exist(device, number_desc):
                wiser_numbers.append(
                    WiserNumber(
                        data,
                        number_desc,
                        device,
                    )
                )

    async_add_entities(wiser_numbers)


class WiserNumber(WiserBaseEntity, NumberEntity):
    """Class to provide select entities for Wiser device control."""

    entity_description: WiserNumberEntityDescription
    _attr_has_entity_name = False if LEGACY_NAMES else True

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
    def native_value(self):
        """Return device value."""
        return self.entity_description.value_fn(self._device)

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        _LOGGER.debug("Setting %s to %sC", self.name, value)
        await self.entity_description.set_fn(self._device, value)
        await self.async_force_update()
