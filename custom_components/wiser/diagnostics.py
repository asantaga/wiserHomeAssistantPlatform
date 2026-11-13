"""Diagnostics support for Wiser"""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.device_registry import DeviceEntry
from aioWiserHeatAPI.cli import anonymise_data

from .const import DOMAIN


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    return _async_get_diagnostics(hass, entry)


@callback
def _async_get_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device: DeviceEntry | None = None,
) -> dict[str, Any]:
    data = hass.data[DOMAIN][entry.entry_id]["data"]
    entity_registry = er.async_get(hass)
    entity_entries = er.async_entries_for_config_entry(
        entity_registry, entry.entry_id
    )
    device_registry = dr.async_get(hass)
    device_entries = dr.async_entries_for_config_entry(
        device_registry, entry.entry_id
    )

    return {
        "diagnostics_version": 3,
        "hub": anonymise_data(data.wiserhub.raw_hub_data),
        # Include registry metadata so migration failures can be diagnosed
        # without asking users to share Home Assistant's storage files.
        # Registry lists are restricted to this Wiser config entry. Names and
        # naming inputs are needed to diagnose entity-ID regeneration.
        "entity_registry": [
            {
                "entity_id": registry_entry.entity_id,
                "unique_id": registry_entry.unique_id,
                "device_id": registry_entry.device_id,
                "domain": registry_entry.domain,
                "platform": registry_entry.platform,
                "original_name": registry_entry.original_name,
                "name": getattr(registry_entry, "name", None),
                "has_entity_name": getattr(registry_entry, "has_entity_name", None),
                "object_id_base": getattr(registry_entry, "object_id_base", None),
                "suggested_object_id": getattr(
                    registry_entry, "suggested_object_id", None
                ),
                "disabled_by": getattr(
                    registry_entry.disabled_by, "value", registry_entry.disabled_by
                ),
                "created_at": (
                    registry_entry.created_at.isoformat()
                    if registry_entry.created_at is not None
                    else None
                ),
            }
            for registry_entry in sorted(
                entity_entries, key=lambda item: item.entity_id
            )
        ],
        "device_registry": [
            {
                "id": device_entry.id,
                "name": device_entry.name,
                "name_by_user": device_entry.name_by_user,
                "effective_name": device_entry.name_by_user or device_entry.name,
            }
            for device_entry in sorted(device_entries, key=lambda item: item.id)
        ],
    }
