"""Cover Platform Device for Wiser.

https://github.com/asantaga/wiserHomeAssistantPlatform
Angelosantagata@gmail.com

"""

from dataclasses import dataclass
import logging
from typing import Any

from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.shutter import _WiserShutter

from homeassistant.components.button import ButtonEntityDescription
from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverDeviceClass,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DATA, DOMAIN, LEGACY_NAMES, MANUFACTURER_SCHNEIDER
from .entity import WiserBaseEntity, WiserBaseEntityDescription, WiserDeviceAttribute
from .helpers import get_entities
from .schedules import WiserScheduleEntity

MANUFACTURER = MANUFACTURER_SCHNEIDER

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = (
    CoverEntityFeature.OPEN
    | CoverEntityFeature.CLOSE
    | CoverEntityFeature.SET_POSITION
    | CoverEntityFeature.STOP
)

TILT_SUPPORT_FLAGS = (
    CoverEntityFeature.OPEN_TILT
    | CoverEntityFeature.CLOSE_TILT
    | CoverEntityFeature.SET_TILT_POSITION
    | CoverEntityFeature.STOP_TILT
)


@dataclass(frozen=True, kw_only=True)
class WiserCoverEntityDescription(ButtonEntityDescription, WiserBaseEntityDescription):
    """A class that describes Wiser cover entities."""


WISER_COVERS: tuple[WiserCoverEntityDescription, ...] = (
    WiserCoverEntityDescription(
        key="shutter",
        name="Shutter",
        device_collection="devices.shutters",
        extra_state_attributes=[
            WiserDeviceAttribute("name"),
            WiserDeviceAttribute("model"),
            WiserDeviceAttribute("product_type"),
            WiserDeviceAttribute("product_identifier"),
            WiserDeviceAttribute("product_model"),
            WiserDeviceAttribute("serial_number"),
            WiserDeviceAttribute("firmware", "firmware_version"),
            WiserDeviceAttribute(
                "room",
                lambda d, h: h.rooms.get_by_id(d.room_id).name
                if d.room_id != 0
                else "Unassigned",
            ),
            WiserDeviceAttribute("shutter_id", "id"),
            WiserDeviceAttribute("away_mode_action"),
            WiserDeviceAttribute("mode"),
            WiserDeviceAttribute("lift_open_time", "drive_config.open_time"),
            WiserDeviceAttribute("lift_close_time", "drive_config.close_time"),
            WiserDeviceAttribute("control_source"),
            WiserDeviceAttribute("is_open"),
            WiserDeviceAttribute("is_closed"),
            WiserDeviceAttribute(
                "current_state",
                lambda x: "Open"
                if x.is_open
                else "Closed"
                if x.is_closed
                else "Middle",
            ),
            WiserDeviceAttribute("lift_movement"),
            WiserDeviceAttribute("current_lift"),
            WiserDeviceAttribute("manual_lift"),
            WiserDeviceAttribute("target_lift"),
            WiserDeviceAttribute("scheduled_lift"),
            WiserDeviceAttribute("current_tilt"),
            WiserDeviceAttribute("manual_tilt"),
            WiserDeviceAttribute("target_tilt"),
            WiserDeviceAttribute("tilt_time", "drive_config.tilt_time"),
            WiserDeviceAttribute("tilt_angle_closed", "drive_config.tilt_angle_closed"),
            WiserDeviceAttribute("tilt_angle_open", "drive_config.tilt_angle_open"),
            WiserDeviceAttribute("tilt_movement"),
            WiserDeviceAttribute("schedule_id", "schedule_id"),
            WiserDeviceAttribute("schedule_name", "schedule.name"),
            WiserDeviceAttribute("next_day_change", "schedule.next.day"),
            WiserDeviceAttribute("next_schedule_change", "schedule.next.time"),
            WiserDeviceAttribute("next_schedule_datetime", "schedule.next.datetime"),
            WiserDeviceAttribute("next_schedule_state", "schedule.next.setting"),
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
    entities = get_entities(data, WISER_COVERS, WiserShutter)
    async_add_entities(entities)

    return True


class WiserShutter(WiserBaseEntity, CoverEntity, WiserScheduleEntity):
    """Wisershutter ClientEntity Object."""

    entity_description: WiserCoverEntityDescription
    _attr_device_class: CoverDeviceClass = CoverDeviceClass.SHUTTER
    _attr_has_entity_name = not LEGACY_NAMES

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserCoverEntityDescription,
        device: _WiserDevice | _WiserShutter | None = None,
    ) -> None:
        """Initialise class instance for Wiser switch."""
        super().__init__(coordinator, description, device, "button")

    @property
    def supported_features(self):
        """Flag supported features."""
        if self._device.is_tilt_supported:
            return SUPPORT_FLAGS + TILT_SUPPORT_FLAGS
        return SUPPORT_FLAGS

    @property
    def current_cover_position(self) -> int | None:
        """Return shutter current position."""
        return self._device.current_lift

    @property
    def current_cover_tilt_position(self) -> int | None:
        """Return current position of shutter tilt."""
        return self._device.current_tilt

    @property
    def is_closed(self) -> bool:
        """Return if shutter is closed."""
        return self._device.is_closed

    @property
    def is_closing(self) -> bool:
        """Return if shutter is closing."""
        return self._device.is_closing

    @property
    def is_opening(self) -> bool:
        """Return if shutter is opening."""
        return self._device.is_opening

    async def async_close_cover(self, **kwargs) -> None:
        """Close the shutter."""
        _LOGGER.debug("Closing %s", self.name)
        await self._device.close()
        await self.async_force_update()

    async def async_open_cover(self, **kwargs) -> None:
        """Open the shutter."""
        _LOGGER.debug("Opening %s", self.name)
        await self._device.open()
        await self.async_force_update()

    async def async_set_cover_position(self, **kwargs) -> None:
        """Move the shutter to a specific position."""
        position = kwargs[ATTR_POSITION]
        _LOGGER.debug("Setting cover position for %s to %s", self.name, position)
        await self._device.open(position)
        await self.async_force_update()

    async def async_stop_cover(self, **kwargs) -> None:
        """Stop the shutter."""
        _LOGGER.debug("Stopping %s", self.name)
        await self._device.stop()
        await self.async_force_update()

    async def async_close_cover_tilt(self, **kwargs) -> None:
        """Close the shutter tilt."""
        _LOGGER.debug("Closing tilt of %s", self.name)
        await self._device.close_tilt()
        await self.async_force_update()

    async def async_open_cover_tilt(self, **kwargs: Any) -> None:
        """Open the cover tilt."""
        await self._device.open_tilt()
        await self.async_force_update()

    async def async_set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Move the shutter tilt to a specific position."""
        position = kwargs[ATTR_TILT_POSITION]
        _LOGGER.debug("Setting cover tilt position for %s to %s", self.name, position)
        await self._device.open_tilt(position)
        await self.async_force_update()

    async def async_stop_cover_tilt(self, **kwargs) -> None:
        """Stop the shutter tilt."""
        _LOGGER.debug("Stopping tilt of %s", self.name)
        await self._device.stop_tilt()
        await self.async_force_update()
