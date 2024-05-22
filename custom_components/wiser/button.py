"""Wiser Button Entities."""

from collections.abc import Callable
from dataclasses import dataclass
from inspect import signature
import logging
from typing import Any

from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, LEGACY_NAMES
from .entity import WiserBaseEntity, WiserBaseEntityDescription
from .helpers import get_entities

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class WiserButtonEntityDescription(ButtonEntityDescription, WiserBaseEntityDescription):
    """A class that describes Wiser button entities."""

    press_fn: Callable[[Any], float | str] | None = None


WISER_BUTTONS: tuple[WiserButtonEntityDescription, ...] = (
    WiserButtonEntityDescription(
        key="boost_all_heating",
        name="Boost All Heating",
        device="system",
        icon="mdi:fire",
        press_fn=lambda x, d: x.boost_all_rooms(d.boost_time, d.boost_temp),
    ),
    WiserButtonEntityDescription(
        key="advance_heating_schedule",
        name="Advance Schedule",
        device_collection="rooms",
        icon="mdi:calendar-arrow-right",
        press_fn=lambda x: x.schedule_advance(),
    ),
    WiserButtonEntityDescription(
        key="cancel_overrides",
        name="Cancel Overrides",
        device_collection="rooms",
        icon="mdi:close-circle",
        press_fn=lambda x: x.cancel_overrides(),
    ),
    WiserButtonEntityDescription(
        key="cancel_heating_overrides",
        name="Cancel All Heating Overrides",
        device="system",
        icon="mdi:water-plus",
        press_fn=lambda x: x.cancel_all_overrides(),
    ),
    WiserButtonEntityDescription(
        key="boost_hot_water",
        name="Boost Hot Water",
        device="hotwater",
        icon="mdi:water-plus",
        supported=lambda dev, hub: hub.hotwater is not None,
        press_fn=lambda x, d: x.boost(d.hw_boost_time),
    ),
    WiserButtonEntityDescription(
        key="cancel_hot_water_overrides",
        name="Cancel Hotwater Overrides",
        device="hotwater",
        icon="mdi:water-plus",
        supported=lambda dev, hub: hub.hotwater is not None,
        press_fn=lambda x: x.cancel_overrides(),
    ),
    WiserButtonEntityDescription(
        key="toggle_hot_water",
        name="Toggle Hot Water",
        device="hotwater",
        icon="mdi:water-boiler",
        supported=lambda dev, hub: hub.hotwater is not None,
        press_fn=lambda x: x.override_state("Off" if x.is_heating else "On"),
    ),
    # Moment buttons
    WiserButtonEntityDescription(
        key="moment",
        name_fn=lambda x: f"Moment {x.name}",
        device_collection="moments",
        icon="mdi:home-thermometer",
        supported=lambda dev, hub: hub.moments is not None,
        press_fn=lambda x: x.activate(),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    entities = get_entities(data, WISER_BUTTONS, WiserButton)
    async_add_entities(entities)

    return True


class WiserButton(WiserBaseEntity, ButtonEntity):
    """Class for button entities."""

    entity_description: WiserButtonEntityDescription
    _attr_has_entity_name = not LEGACY_NAMES

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserButtonEntityDescription,
        device: _WiserDevice | _WiserRoom | None = None,
    ) -> None:
        """Initialise class instance for Wiser switch."""
        super().__init__(coordinator, description, device, "button")

    async def async_press(self):
        """Press buton action."""
        if self.entity_description.press_fn is None:
            raise NotImplementedError
        no_of_params = len(signature(self.entity_description.press_fn).parameters)
        if no_of_params == 2:
            r = self.entity_description.press_fn(self._device, self._data)
        else:
            r = self.entity_description.press_fn(self._device)
        await r
        await self.async_force_update(delay=self.entity_description.delay)
