"""Diagnostics support for Wiser"""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
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

    return {
        "diagnostics_version": 2,
        "hub": anonymise_data(data.wiserhub.raw_hub_data),
        # Include registry metadata so migration failures can be diagnosed
        # without asking users to share Home Assistant's storage files.  The
        # list is restricted to this Wiser config entry and contains no state
        # values, credentials, network addresses, or device identifiers.
        "entity_registry": [
            {
                "entity_id": registry_entry.entity_id,
                "unique_id": registry_entry.unique_id,
                "device_id": registry_entry.device_id,
                "domain": registry_entry.domain,
                "platform": registry_entry.platform,
                "original_name": registry_entry.original_name,
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
    }
