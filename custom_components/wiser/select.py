"""Select Platform Device for Wiser System.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com
"""

from collections.abc import Callable
from dataclasses import dataclass
import logging
from typing import Any

from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from config.custom_components.wiser.entity import (
    WiserBaseEntity,
    WiserBaseEntityDescription,
)
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, LEGACY_NAMES
from .helpers import get_entities

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class WiserSelectEntityDescription(SelectEntityDescription, WiserBaseEntityDescription):
    """A class that describes Wiser select entities."""

    options_fn: Callable[[Any], str] | None = None
    set_fn: Callable[[Any], str] | None = None


WISER_SELECTS: tuple[WiserSelectEntityDescription, ...] = (
    WiserSelectEntityDescription(
        key="hotwater_mode",
        name="Mode",
        device="hotwater",
        options_fn=lambda x: x.available_modes,
        set_fn=lambda x, m: x.set_mode(m),
        value_fn=lambda x: x.mode,
    ),
    WiserSelectEntityDescription(
        key="smartplug_mode",
        name="Mode",
        device_collection="devices.smartplugs",
        options_fn=lambda x: x.available_modes,
        set_fn=lambda x, m: x.set_mode(m),
        value_fn=lambda x: x.mode,
    ),
    WiserSelectEntityDescription(
        key="light_mode",
        name="Mode",
        device_collection="devices.lights",
        options_fn=lambda x: x.available_modes,
        set_fn=lambda x, m: x.set_mode(m),
        value_fn=lambda x: x.mode,
    ),
    WiserSelectEntityDescription(
        key="shutter_mode",
        name="Mode",
        device_collection="devices.shutters",
        options_fn=lambda x: x.available_modes,
        set_fn=lambda x, m: x.set_mode(m),
        value_fn=lambda x: x.mode,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Add the Wiser System Switch entities."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    entities = get_entities(data, WISER_SELECTS, WiserSelect)
    async_add_entities(entities)

    return True


class WiserSelect(WiserBaseEntity, SelectEntity):
    """Class to provide select entities for Wiser device control."""

    entity_description: WiserSelectEntityDescription
    _attr_has_entity_name = not LEGACY_NAMES

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserSelectEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        """Init wiser sensor."""
        super().__init__(coordinator, description, device, "select")

    @property
    def options(self) -> list[str]:
        """Return list of available options."""
        return self.entity_description.options_fn(self._device)

    @property
    def current_option(self) -> str:
        """Return current selected option."""
        return self.entity_description.value_fn(self._device)

    async def async_select_option(self, option: str) -> None:
        """Set value based on selected option."""
        _LOGGER.debug("Setting %s to %s", self.name, option)
        if option in self.options:
            await self.async_set_mode(option)
            await self.async_force_update()
        else:
            _LOGGER.error(
                "%s is not a valid %s.  Please choose from %s",
                option,
                self.name,
                self.options,
            )

    async def async_set_mode(self, option: str) -> None:
        """Set the device mode."""
        _LOGGER.debug("Setting %s mode to %s", self.name, option)
        await self.entity_description.set_fn(self._device, option)
