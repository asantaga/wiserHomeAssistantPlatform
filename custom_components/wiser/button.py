"""Wiser Button Entities."""

from collections.abc import Callable
from dataclasses import dataclass
from inspect import signature
import logging
from typing import Any

from aioWiserHeatAPI.const import TEXT_UNKNOWN
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.room import _WiserRoom

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, LEGACY_NAMES
from .entity import WiserBaseEntity
from .helpers import getattrd

_LOGGER = logging.getLogger(__name__)


@dataclass
class WiserButtonEntityDescription(ButtonEntityDescription):
    """A class that describes Wiser switch entities."""

    name_fn: Callable[[Any], str] | None = None
    device: str | None = None
    device_collection: list | None = None
    delay: int | None = None
    available_fn: Callable[[Any], bool] | None = None
    icon_fn: Callable[[Any], str] | None = None
    unit_fn: Callable[[Any], str] | None = None
    press_fn: Callable[[Any], float | str] | None = None
    extra_state_attributes: dict[str, Callable[[Any], float | str]] | None = None


WISER_BUTTONS: tuple[WiserButtonEntityDescription, ...] = (
    WiserButtonEntityDescription(
        key="boost_all_heating",
        name="Boost All Heating",
        device="system",
        icon="mdi:fire",
        press_fn=lambda x, d: x.boost_all_rooms(d.boost_time, d.boost_temp),
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
        press_fn=lambda x, d: x.boost(d.hw_boost_time),
    ),
    WiserButtonEntityDescription(
        key="cancel_hot_water_overrides",
        name="Cancel Hotwater Overrides",
        device="hotwater",
        icon="mdi:water-plus",
        press_fn=lambda x: x.cancel_overrides(),
    ),
    WiserButtonEntityDescription(
        key="toggle_hot_water",
        name="Toggle Hot Water",
        device="hotwater",
        icon="mdi:water-boiler",
        press_fn=lambda x: x.override_state("Off" if x.is_heating else "On"),
    ),
    # Moment buttons
    WiserButtonEntityDescription(
        key="moment",
        name_fn=lambda x: f"Moment {x.name}",
        device_collection="moments",
        icon="mdi:water-boiler",
        press_fn=lambda x: x.override_state("Off" if x.is_heating else "On"),
    ),
)


def _attr_exist(device, entity_desc: WiserButtonEntityDescription) -> bool:
    """Check if an attribute exists for device."""
    try:
        r = entity_desc.value_fn(device)
        if r is not None and r != TEXT_UNKNOWN:
            return True
        return False
    except AttributeError:
        return False


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    wiser_sensors = []

    for button_desc in WISER_BUTTONS:
        # get device or device collection
        if button_desc.device_collection and getattrd(
            data.wiserhub, button_desc.device_collection
        ):
            for device in getattrd(data.wiserhub, button_desc.device_collection).all:
                if device:
                    _LOGGER.info("Adding %s", device.name)
                    wiser_sensors.append(
                        WiserButton(
                            data,
                            button_desc,
                            device,
                        )
                    )
        elif button_desc.device and getattrd(data.wiserhub, button_desc.device):
            device = getattrd(data.wiserhub, button_desc.device)
            if device:
                wiser_sensors.append(
                    WiserButton(
                        data,
                        button_desc,
                        device,
                    )
                )

    async_add_entities(wiser_sensors)

    return True


class WiserButton(WiserBaseEntity, ButtonEntity):
    """Class for button entities."""

    entity_description: WiserButtonEntityDescription
    _attr_has_entity_name = False if LEGACY_NAMES else True

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
            raise NotImplementedError()
        no_of_params = len(signature(self.entity_description.press_fn).parameters)
        if no_of_params == 2:
            r = self.entity_description.press_fn(self._device, self._data)
        else:
            r = self.entity_description.press_fn(self._device)
        await r
        await self.async_force_update(delay=self.entity_description.delay)
