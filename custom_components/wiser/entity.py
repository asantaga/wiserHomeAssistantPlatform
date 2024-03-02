"""Base entity class for Wiser devices."""
import asyncio
from collections.abc import Callable, Mapping
from inspect import signature
import logging
from typing import Any

from aioWiserHeatAPI.heating_actuator import _WiserHeatingActuator
from aioWiserHeatAPI.helpers.device import _WiserDevice
from aioWiserHeatAPI.moments import _WiserMoment
from aioWiserHeatAPI.room import _WiserRoom
from aioWiserHeatAPI.system import _WiserSystem

from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)

from .const import DOMAIN, ENTITY_PREFIX, LEGACY_NAMES, MANUFACTURER, ROOM
from .helpers import (
    WiserDeviceAttribute,
    WiserHubAttribute,
    get_entity_description_attribute_from_function,
    get_entity_name,
    get_identifier,
    get_legacy_entity_name,
    get_legacy_unique_id,
    get_unique_id,
    getattrd,
)

_LOGGER = logging.getLogger(__name__)


class WiserBaseEntity(CoordinatorEntity):
    """Base entity for Wiser entities."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        description: Any,
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
        self._attr_has_entity_name = (
            False
            if LEGACY_NAMES
            and (
                description.legacy_type
                or description.legacy_name_fn
                or description.device
            )
            else True
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
        # TODO: Neaten this up when finished
        name = self._attr_name
        if not self._attr_has_entity_name:
            name = get_legacy_entity_name(
                self._data, self.entity_description, self._device
            )
        elif (
            hasattr(self.entity_description, "name_fn")
            and self.entity_description.name_fn
        ):
            name = get_entity_description_attribute_from_function(
                self._data, self._device, self.entity_description.name_fn
            )
        return name

    @property
    def unique_id(self):
        """Return unique id."""
        if not self._attr_has_entity_name:
            if hasattr(self.entity_description, "legacy_type"):
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
            for (
                name,
                value,
            ) in self.entity_description.extra_state_attributes.items():
                if isinstance(value, str):
                    attrs[name] = value
                elif isinstance(value, WiserHubAttribute):
                    try:
                        attrs[name] = getattrd(self._data.wiserhub, value.path)
                    except AttributeError:
                        continue
                elif isinstance(value, WiserDeviceAttribute):
                    try:
                        attrs[name] = getattrd(self._device, value.path)
                    except AttributeError:
                        continue
                elif isinstance(value, Callable):
                    # Get number of params
                    no_of_params = len(signature(value).parameters)
                    try:
                        if no_of_params == 2:
                            attrs[name] = value(self._data, self._device)
                        else:
                            attrs[name] = value(self._device)
                    except AttributeError:
                        continue
        return attrs
