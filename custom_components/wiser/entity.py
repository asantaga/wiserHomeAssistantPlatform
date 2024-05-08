"""Base entity class for Wiser devices."""

import asyncio
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from inspect import signature
import logging
from typing import Any

from aioWiserHeatAPI.heating_actuator import _WiserHeatingActuator
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.moments import _WiserMoment
from aioWiserHeatAPI.room import _WiserRoom
from aioWiserHeatAPI.system import _WiserSystem

from homeassistant.core import callback
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, LEGACY_NAMES, MANUFACTURER, ROOM
from .helpers import (
    get_entity_name,
    get_identifier,
    get_legacy_entity_name,
    get_legacy_unique_id,
    get_unique_id,
    getattrd,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class WiserAttribute:
    """Class to hold attribute definition."""

    name: str
    path: Callable | str | None = None


@dataclass
class WiserStaticAttribute(WiserAttribute):
    """Hub attribute definition."""


@dataclass
class WiserHubAttribute(WiserAttribute):
    """Hub attribute definition."""


@dataclass
class WiserDeviceAttribute(WiserAttribute):
    """Device attribute definition."""


@dataclass(frozen=True, kw_only=True)
class WiserBaseEntityDescription(EntityDescription):
    """Base extension class for Wiser entity descriptions."""

    device: str | None = None
    device_collection: list | None = None
    supported: Callable[[Any], bool] = lambda device, hub: True
    value_fn: Callable[[Any], bool] | None = None
    name_fn: Callable[[Any], str] | None = None
    legacy_name_fn: Callable[[Any], str] | None = None
    legacy_type: str = None
    icon_fn: Callable[[Any], str] | None = None
    extra_state_attributes: list[
        dict[str, str] | WiserDeviceAttribute | WiserHubAttribute
    ] = None
    delay: int | None = None
    entity_class: Any | None = None


class WiserBaseEntity(CoordinatorEntity):
    """Base entity for Wiser entities."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: WiserBaseEntityDescription,
        device: _WiserDevice
        | _WiserRoom
        | _WiserSystem
        | _WiserHeatingActuator
        | None = None,
        entity_class: str | None = None,
    ) -> None:
        """Init wiser sensor."""
        super().__init__(coordinator)
        self._data = coordinator
        self._device = device
        self._attr_has_entity_name = not (
            LEGACY_NAMES
            and (
                description.legacy_type
                or description.legacy_name_fn
                or description.device
            )
        )
        self.entity_class = entity_class
        self.entity_description = description
        self._attr_name = description.name
        self.schedule = (
            self._device.schedule
            if hasattr(self._device, "schedule") and self._device.schedule
            else None
        )

    async def async_force_update(self, delay: int = 0):
        """Force update form hub."""
        _LOGGER.debug("Hub update initiated by %s", self.name)
        if delay:
            await asyncio.sleep(delay)
        await self._data.async_refresh()

    @callback
    def _handle_coordinator_update(self) -> None:
        """Fetch new state data for the sensor."""
        super()._handle_coordinator_update()
        if isinstance(self._device, _WiserDevice):
            self._device = self._data.wiserhub.devices.get_by_id(self._device.id)
        elif isinstance(self._device, _WiserRoom):
            self._device = self._data.wiserhub.rooms.get_by_id(self._device.id)
        elif self.entity_description.device:
            self._device = getattrd(self._data.wiserhub, self.entity_description.device)

        self.schedule = (
            self._device.schedule
            if hasattr(self._device, "schedule") and self._device.schedule
            else None
        )

        self.async_write_ha_state()

    @property
    def device_info(self):
        """Return device specific attributes."""
        return {
            "name": get_entity_name(self._data, self._device),
            "identifiers": {
                (
                    DOMAIN,
                    get_identifier(self._data, self._device),
                )
            },
            "manufacturer": MANUFACTURER,
            "model": ROOM
            if isinstance(self._device, _WiserRoom)
            else self._device.product_type
            if isinstance(self._device, _WiserDevice)
            else self._data.wiserhub.system.product_type,
            "sw_version": self._device.firmware_version
            if isinstance(self._device, _WiserDevice)
            else self._data.wiserhub.system.firmware_version,
            "via_device": (DOMAIN, self._data.wiserhub.system.name),
        }

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self._device and self.entity_description.icon_fn is not None:
            return self.entity_description.icon_fn(self._device)
        return self.entity_description.icon

    @property
    def name(self) -> str:
        """Return entity name."""
        name = self._attr_name
        if not self._attr_has_entity_name:
            name = get_legacy_entity_name(
                self._data, self.entity_description, self._device
            )
        elif (
            hasattr(self.entity_description, "name_fn")
            and self.entity_description.name_fn
        ):
            name = self._get_callable_value(self.entity_description.name_fn)
        return name

    @property
    def unique_id(self):
        """Return unique id."""
        if not self._attr_has_entity_name:
            if (
                hasattr(self.entity_description, "legacy_type")
                and self.entity_description.legacy_type
            ):
                return get_legacy_unique_id(
                    self._data, self.entity_description, self._device
                )
        return get_unique_id(
            self._data,
            self.entity_class,
            self.entity_description.key,
            (
                self._device.id
                if isinstance(self._device, _WiserDevice | _WiserRoom | _WiserMoment)
                else 0
            ),
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Return extra state attributes for sensor."""
        attrs = {}
        if self.entity_description.extra_state_attributes:
            for attr_desc in self.entity_description.extra_state_attributes:
                if isinstance(attr_desc, WiserHubAttribute):
                    try:
                        if isinstance(attr_desc.path, Callable):
                            attrs[attr_desc.name] = self._get_callable_value(
                                attr_desc.path
                            )
                        else:
                            attrs[attr_desc.name] = getattrd(
                                self._data.wiserhub, attr_desc.path
                            )
                    except AttributeError:
                        continue
                elif isinstance(attr_desc, WiserDeviceAttribute):
                    try:
                        if isinstance(attr_desc.path, Callable):
                            attrs[attr_desc.name] = self._get_callable_value(
                                attr_desc.path
                            )
                        else:
                            attrs[attr_desc.name] = getattrd(
                                self._device,
                                attr_desc.path if attr_desc.path else attr_desc.name,
                            )
                    except AttributeError:
                        continue
                elif isinstance(attr_desc, WiserAttribute):
                    attrs[attr_desc.name] = attr_desc.path

        # return dict(sorted(attrs.items()))
        return attrs

    def _get_callable_value(self, func: Callable):
        """Get return value from lambda callable."""
        no_of_params = len(signature(func).parameters)
        try:
            if no_of_params == 2:
                return func(self._device, self._data.wiserhub)
            return func(self._device)
        except AttributeError:
            return None
