"""Support for Wiser lights via Wiser Hub."""

from dataclasses import dataclass
import logging

from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.light import _WiserDimmableLight, _WiserLight

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, LEGACY_NAMES, MANUFACTURER_SCHNEIDER
from .entity import (
    WiserBaseEntity,
    WiserBaseEntityDescription,
    WiserDeviceAttribute,
    WiserV2DeviceAttribute,
)
from .helpers import get_entities
from .schedules import WiserScheduleEntity

MANUFACTURER = MANUFACTURER_SCHNEIDER

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class WiserLightEntityDescription(LightEntityDescription, WiserBaseEntityDescription):
    """A class that describes Wiser light entities."""


WISER_LIGHTS: tuple[WiserLightEntityDescription, ...] = (
    # OnOffLights
    WiserLightEntityDescription(
        key="light",
        name="Light",
        device_collection="devices.lights",
        supported=lambda dev, hub: not dev.is_dimmable,
        extra_state_attributes=[
            WiserDeviceAttribute("room_id"),
            WiserDeviceAttribute(
                "room",
                lambda d, h: h.rooms.get_by_id(d.room_id).name
                if d.room_id != 0
                else "Unassigned",
            ),
            # Identification
            WiserDeviceAttribute("device_id", "id"),
            # Settings
            WiserDeviceAttribute("is_dimmable"),
            WiserDeviceAttribute("mode"),
            WiserDeviceAttribute("away_mode_action"),
            # Command State
            WiserDeviceAttribute("control_source"),
            # Status
            WiserDeviceAttribute("current_state"),
            WiserDeviceAttribute("target_state"),
            # V2 only attributes
            WiserV2DeviceAttribute("type", "type_comm"),
            WiserV2DeviceAttribute("uuid"),
            WiserV2DeviceAttribute("endpoint"),
        ],
    ),
    # Dimable Lights
    WiserLightEntityDescription(
        key="light",
        name="Light",
        device_collection="devices.lights",
        supported=lambda dev, hub: dev.is_dimmable,
        extra_state_attributes=[
            WiserDeviceAttribute("room_id"),
            WiserDeviceAttribute(
                "room",
                lambda d, h: h.rooms.get_by_id(d.room_id).name
                if d.room_id != 0
                else "Unassigned",
            ),
            # Identification
            WiserDeviceAttribute("device_id", "id"),
            # Settings
            WiserDeviceAttribute("is_dimmable"),
            WiserDeviceAttribute("mode"),
            WiserDeviceAttribute("away_mode_action"),
            # Command State
            WiserDeviceAttribute("control_source"),
            # Status
            WiserDeviceAttribute("current_state"),
            WiserDeviceAttribute("target_state"),
            # Settings
            WiserDeviceAttribute("output_range_minimum", "output_range.minimum"),
            WiserDeviceAttribute("output_range_maximum", "output_range.maximum"),
            WiserDeviceAttribute("current_percentage"),
            WiserDeviceAttribute("current_level"),
            WiserDeviceAttribute("target_percentage"),
            WiserDeviceAttribute("manual_level"),
            WiserDeviceAttribute("override_level"),
            # V2 only attributes
            WiserV2DeviceAttribute("type", "type_comm"),
            WiserV2DeviceAttribute("uuid"),
            WiserV2DeviceAttribute("endpoint"),
        ],
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Initialize the entry."""
    data = hass.data[DOMAIN][config_entry.entry_id][DATA]  # Get Handler
    entities = get_entities(data, WISER_LIGHTS, WiserLight)
    async_add_entities(entities)

    return True


class WiserLight(WiserBaseEntity, LightEntity, WiserScheduleEntity):
    """Class for light devices."""

    entity_description: WiserLightEntityDescription
    _attr_has_entity_name = not LEGACY_NAMES

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserLightEntityDescription,
        device: _WiserDevice | _WiserLight | _WiserDimmableLight | None = None,
    ) -> None:
        """Initialise class instance for Wiser switch."""
        super().__init__(coordinator, description, device, "button")

    @property
    def is_dimmable(self):
        """Return if light is dimmable."""
        return self._device.is_dimmable

    @property
    def color_mode(self):
        """Return current color mode of light."""
        return ColorMode.BRIGHTNESS if self.is_dimmable else ColorMode.ONOFF

    @property
    def supported_color_modes(self):
        """Return supported modes for light."""
        return {ColorMode.BRIGHTNESS} if self.is_dimmable else {ColorMode.ONOFF}

    @property
    def is_on(self):
        """Return true if light is on."""
        return self._device.is_on

    @property
    def brightness(self):
        """Return the brightness of this light between 0..100."""
        if not self.is_dimmable:
            return None

        bright_pct = self._device.current_percentage
        if bright_pct is None:
            return None

        return round(255 * bright_pct / 100.0)

    async def async_turn_on(self, **kwargs):
        """Turn light on."""
        if (brightness := kwargs.get(ATTR_BRIGHTNESS)) is not None and self.is_dimmable:
            brightness_pct = int(brightness / 255.0 * 100)

            _LOGGER.debug(
                "Setting brightness of %s to %s",
                self.name,
                brightness_pct,
            )

            await self._device.set_current_percentage(brightness_pct)
        else:
            _LOGGER.debug("Turning on %s", self.name)
            await self._device.turn_on()

        await self.async_force_update(2)
        return True

    async def async_turn_off(self, **kwargs):
        """Turn light off."""
        _LOGGER.debug("Turning off %s", self.name)
        await self._device.turn_off()
        await self.async_force_update(2)
        return True
