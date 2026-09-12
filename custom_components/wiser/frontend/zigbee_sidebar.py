"""Manage the shared Wiser zigbee sidebar panel."""

import math
from pathlib import Path

from homeassistant.components import frontend, panel_custom

from . import card_version

from ..const import (
    CONF_SHOW_ZIGBEE_SIDEBAR, CONF_ZIGBEE_PANEL_CONFIG,
    DATA, DOMAIN, JSMODULES, URL_BASE,
)

PANEL_PATH = "wiser-zigbee"
PANEL_STATE = "wiser_zigbee_panel"


async def async_update_zigbee_panel(hass):
    """Show zigbee for loaded hubs that have opted into the sidebar."""
    loaded = hass.data.get(DOMAIN, {})
    hubs = [
        loaded[entry.entry_id][DATA].wiserhub.system.name
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id in loaded
        and not entry.disabled_by
        and entry.options.get(CONF_SHOW_ZIGBEE_SIDEBAR, False)
    ]
    card_configs = {
        loaded[entry.entry_id][DATA].wiserhub.system.name:
            dict(entry.options.get(CONF_ZIGBEE_PANEL_CONFIG, {}))
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id in loaded
        and loaded[entry.entry_id][DATA].wiserhub.system.name in hubs
    }
    state = {"hubs": hubs, "card_configs": card_configs}
    if hubs:
        card = next(
            module for module in JSMODULES
            if module["filename"] == "wiser-zigbee-card.js"
        )
        version = await hass.async_add_executor_job(
            card_version,
            Path(__file__).parent / card["filename"],
        )
        state["card_url"] = f"{URL_BASE}/{card['filename']}?v={version}"
    if state == hass.data.get(PANEL_STATE) or (not hubs and PANEL_STATE not in hass.data):
        return

    if not hubs and PANEL_STATE in hass.data:
        frontend.async_remove_panel(hass, PANEL_PATH)
        hass.data.pop(PANEL_STATE)

    if hubs:
        config = dict(state)
        module_url = config["card_url"]
        if PANEL_STATE in hass.data:
            # Keep the route registered while notifying clients of new settings.
            frontend.async_register_built_in_panel(
                hass,
                component_name="custom",
                frontend_url_path=PANEL_PATH,
                sidebar_title="Wiser Zigbee",
                sidebar_icon="mdi:zigbee",
                config={
                    **config,
                    "_panel_custom": {
                        "name": "wiser-zigbee-panel",
                        "module_url": module_url,
                        "embed_iframe": False,
                        "trust_external": False,
                    },
                },
                update=True,
            )
        else:
            await panel_custom.async_register_panel(
                hass,
                frontend_url_path=PANEL_PATH,
                webcomponent_name="wiser-zigbee-panel",
                sidebar_title="Wiser Zigbee",
                sidebar_icon="mdi:zigbee",
                module_url=module_url,
                config=config,
            )
        hass.data[PANEL_STATE] = state


def save_zigbee_panel_config(hass, configs):
    """Validate all submitted settings before updating integration options."""
    loaded = hass.data.get(DOMAIN, {})
    entries = {
        loaded[entry.entry_id][DATA].wiserhub.system.name: entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id in loaded
        and not entry.disabled_by
        and entry.options.get(CONF_SHOW_ZIGBEE_SIDEBAR, False)
    }
    field_types = {
        "name": str, "layout_id": str, "layout_seed": str,
        "auto_update": bool, "log_seed": bool, "map_only": bool,
        "show_device_list": bool, "show_labels": bool, "magnifier": bool,
        "orientation": str, "group_by": str, "link_status": str,
        "map_height": (int, type(None)), "layout_data": dict,
    }
    choices = {
        "orientation": {"vertical", "horizontal", "pie"},
        "group_by": {"none", "area"},
        "link_status": {"links", "icons", "both", "none"},
    }
    updates = []
    for hub, config in configs.items():
        if hub not in entries:
            raise ValueError("Hub is not enabled in the zigbee panel")
        settings = {}
        for key, value in config.items():
            if key in {"type", "hub"}:
                continue
            if key not in field_types or type(value) not in (field_types[key] if isinstance(field_types[key], tuple) else (field_types[key],)):
                raise ValueError(f"Invalid Zigbee card setting: {key}")
            if key in choices and value not in choices[key]:
                raise ValueError(f"Invalid Zigbee card setting: {key}")
            if key == "map_height" and value is not None and not 100 <= value <= 2000:
                raise ValueError("Map height must be between 100 and 2000")
            if key == "layout_data":
                for position in value.values():
                    if not isinstance(position, dict) or set(position) != {"x", "y"}:
                        raise ValueError("Invalid layout position")
                    if any(type(n) not in (int, float) or not math.isfinite(n) for n in position.values()):
                        raise ValueError("Invalid layout coordinates")
            settings[key] = value
        updates.append((entries[hub], settings))
    for entry, settings in updates:
        hass.config_entries.async_update_entry(
            entry, options={**entry.options, CONF_ZIGBEE_PANEL_CONFIG: settings}
        )


def integration_reload_settings(entry):
    """Exclude panel-only preferences from integration reload decisions."""
    return (dict(entry.data), {
        key: value for key, value in entry.options.items()
        if key != CONF_ZIGBEE_PANEL_CONFIG
    })


async def async_handle_entry_update(hass, entry):
    """Save panel preferences live; reload for connection and entity options."""
    loaded = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if loaded is not None and loaded.get("reload_settings") == integration_reload_settings(entry):
        await async_update_zigbee_panel(hass)
        return
    await hass.config_entries.async_reload(entry.entry_id)
