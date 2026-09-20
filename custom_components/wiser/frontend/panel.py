"""Shared lifecycle and settings persistence for Wiser sidebar panels."""

from __future__ import annotations

import math
from dataclasses import dataclass

from homeassistant.components import frontend, panel_custom

from . import async_card_resource
from ..const import DATA, DOMAIN


@dataclass(frozen=True)
class SidebarPanel:
    """Describe a sidebar panel and the card settings it accepts."""

    path: str
    state_key: str
    component: str
    title: str
    icon: str
    filename: str
    enabled_option: str
    config_option: str
    hub_error: str
    setting_error: str


def _enabled_entries(hass, panel):
    """Yield loaded, enabled hubs that opted into this panel."""
    loaded = hass.data.get(DOMAIN, {})
    for entry in hass.config_entries.async_entries(DOMAIN):
        if (
            entry.entry_id in loaded
            and not entry.disabled_by
            and entry.options.get(panel.enabled_option, False)
        ):
            yield loaded[entry.entry_id][DATA].wiserhub.system.name, entry


async def async_update_panel(hass, panel):
    """Register, refresh, or remove a panel according to its enabled hubs."""
    entries = list(_enabled_entries(hass, panel))
    if not entries:
        if panel.state_key in hass.data:
            frontend.async_remove_panel(hass, panel.path)
            hass.data.pop(panel.state_key)
        return

    _, module_url, _ = await async_card_resource(hass, panel.filename)
    state = {
        "hubs": [hub for hub, _ in entries],
        "card_configs": {
            hub: dict(entry.options.get(panel.config_option, {}))
            for hub, entry in entries
        },
        "card_url": module_url,
    }
    if state == hass.data.get(panel.state_key):
        return

    if panel.state_key in hass.data:
        # Keep the route registered while notifying clients of new settings.
        frontend.async_register_built_in_panel(
            hass,
            component_name="custom",
            frontend_url_path=panel.path,
            sidebar_title=panel.title,
            sidebar_icon=panel.icon,
            config={
                **state,
                "_panel_custom": {
                    "name": panel.component,
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
            frontend_url_path=panel.path,
            webcomponent_name=panel.component,
            sidebar_title=panel.title,
            sidebar_icon=panel.icon,
            module_url=module_url,
            config=dict(state),
        )
    # Only record successfully applied settings so failed updates can be retried.
    hass.data[panel.state_key] = state


def _is_json_value(value, depth=0):
    """Accept finite JSON data, including future card options."""
    if depth > 64:
        return False
    if type(value) in (str, bool, int, type(None)):
        return True
    if type(value) is float:
        return math.isfinite(value)
    if type(value) is list:
        return all(_is_json_value(item, depth + 1) for item in value)
    if type(value) is dict:
        return all(
            type(key) is str and _is_json_value(item, depth + 1)
            for key, item in value.items()
        )
    return False


def save_panel_config(hass, panel, configs):
    """Validate every hub's settings before persisting any options.

    Cards own their display options. Only validate JSON structure here so new
    card settings do not require an integration release.
    """
    if type(configs) is not dict:
        raise ValueError(panel.setting_error)
    entries = dict(_enabled_entries(hass, panel))
    updates = []
    for hub, config in configs.items():
        if hub not in entries:
            raise ValueError(panel.hub_error)
        if type(config) is not dict or not _is_json_value(config):
            raise ValueError(panel.setting_error)
        settings = {}
        for key, value in config.items():
            if key in {"type", "hub"}:
                continue
            settings[key] = value
        updates.append((entries[hub], settings))
    for entry, settings in updates:
        hass.config_entries.async_update_entry(
            entry, options={**entry.options, panel.config_option: settings}
        )
