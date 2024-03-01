"""Select Platform Device for Wiser System.

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

from config.custom_components.wiser.entity import WiserBaseEntity
from homeassistant.components.select import SelectEntity, SelectEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, LEGACY_NAMES
from .helpers import getattrd

_LOGGER = logging.getLogger(__name__)


@dataclass
class WiserSelectEntityDescription(SelectEntityDescription):
    """A class that describes Wiser sensor entities."""

    name_fn: Callable[[Any], str] | None = None
    device: str | None = None
    device_collection: list | None = None
    available_fn: Callable[[Any], bool] | None = None
    icon_fn: Callable[[Any], str] | None = None
    options_fn: Callable[[Any], str] | None = None
    set_fn: Callable[[Any], str] | None = None
    value_fn: Callable[[Any], float | str] | None = None
    extra_state_attributes: dict[str, Callable[[Any], float | str]] | None = None


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


def _attr_exist(device, switch_desc: WiserSelectEntityDescription) -> bool:
    """Check if an attribute exists for device."""
    try:
        r = switch_desc.value_fn(device)
        if r is not None and r != TEXT_UNKNOWN:
            return True
        return False
    except AttributeError:
        return False


async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    """Set up Wiser climate device."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]
    wiser_selects = []

    for select_desc in WISER_SELECTS:
        # get device or device collection
        if select_desc.device_collection and getattrd(
            data.wiserhub, select_desc.device_collection
        ):
            for device in getattrd(data.wiserhub, select_desc.device_collection).all:
                if _attr_exist(device, select_desc):
                    _LOGGER.info("Adding %s", device.name)
                    wiser_selects.append(
                        WiserSelect(
                            data,
                            select_desc,
                            device,
                        )
                    )
        elif select_desc.device and getattrd(data.wiserhub, select_desc.device):
            device = getattrd(data.wiserhub, select_desc.device)
            if _attr_exist(device, select_desc):
                wiser_selects.append(
                    WiserSelect(
                        data,
                        select_desc,
                        device,
                    )
                )

    async_add_entities(wiser_selects)


class WiserSelect(WiserBaseEntity, SelectEntity):
    """Class to provide select entities for Wiser device control."""

    entity_description: WiserSelectEntityDescription
    _attr_has_entity_name = False if LEGACY_NAMES else True

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
