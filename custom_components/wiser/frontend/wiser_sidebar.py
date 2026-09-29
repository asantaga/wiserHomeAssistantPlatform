"""Manage the single shared Wiser sidebar panel."""

from __future__ import annotations

import math
from pathlib import Path

from homeassistant.components import frontend, panel_custom

from . import async_card_resource, card_version
from .registry import get_manifest
from ..const import (
    CONF_SHOW_WISER_SIDEBAR,
    CONF_WISER_PANEL_CONFIG,
    DATA,
    DOMAIN,
    URL_BASE,
)

# Keep the UI route outside URL_BASE: a direct request to the static-file
# directory returns 403 instead of loading the Home Assistant frontend.
PANEL_PATH = "wiser-panel"
PANEL_STATE = "wiser_sidebar_panel"
PANEL_COMPONENT = "wiser-panel"
PANEL_FILENAME = "wiser-panel.js"
_PANEL_TABS_CONFIG = "_panel_tabs"


def _panel_enabled(options):
    """Return the unified preference, enabled by default."""
    return options.get(CONF_SHOW_WISER_SIDEBAR, True)


def _enabled_entries(hass):
    """Yield loaded hubs enabled for the shared Wiser panel."""
    loaded = hass.data.get(DOMAIN, {})
    for entry in hass.config_entries.async_entries(DOMAIN):
        if (
            entry.entry_id in loaded
            and not entry.disabled_by
            and _panel_enabled(entry.options)
        ):
            yield loaded[entry.entry_id][DATA].wiserhub.system.name, entry


def _panel_title(component):
    """Derive a readable tab title from the panel custom element."""
    name = component.removeprefix("wiser-").removesuffix("-panel")
    return name.replace("-", " ").title()


def _stored_config(entry, panel_id):
    """Return settings from the shared container for any panel."""
    generic = entry.options.get(CONF_WISER_PANEL_CONFIG, {})
    if isinstance(generic, dict) and isinstance(generic.get(panel_id), dict):
        return dict(generic[panel_id])
    return {}


async def _discover_panels(hass, entries):
    """Find installed panel components from the active frontend registry."""
    panels = []
    hubs = [hub for hub, _ in entries]
    for module in get_manifest(hass):
        component = module.get("panel")
        if not component:
            continue
        filename = module["filename"]
        path, module_url, _ = await async_card_resource(hass, filename)
        try:
            source = await hass.async_add_executor_job(path.read_text, "utf-8")
        except OSError:
            continue
        if component not in source:
            continue
        panel_id = module["id"]
        panels.append(
            {
                "id": panel_id,
                "title": _panel_title(component),
                "component": component,
                "module_url": module_url,
                "config": {
                    "panel_id": panel_id,
                    "hubs": hubs,
                    "hub_ids": {
                        hub: entry.entry_id for hub, entry in entries
                    },
                    "card_configs": {
                        hub: _stored_config(entry, panel_id)
                        for hub, entry in entries
                    },
                    "card_url": module_url,
                },
            }
        )
    stored_tabs = None
    for _, entry in entries:
        generic = entry.options.get(CONF_WISER_PANEL_CONFIG, {})
        if isinstance(generic, dict) and isinstance(
            generic.get(_PANEL_TABS_CONFIG), list
        ):
            stored_tabs = generic[_PANEL_TABS_CONFIG]
            break

    if not stored_tabs:
        return panels

    preferences = {
        item["id"]: item
        for item in stored_tabs
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }
    for panel in panels:
        title = preferences.get(panel["id"], {}).get("title")
        if isinstance(title, str) and title.strip():
            panel["title"] = title.strip()

    order = {item["id"]: index for index, item in enumerate(stored_tabs)}
    discovered_order = {panel["id"]: index for index, panel in enumerate(panels)}
    panels.sort(
        key=lambda panel: (
            order.get(panel["id"], len(order) + discovered_order[panel["id"]])
        )
    )
    return panels


async def async_update_wiser_panel(hass):
    """Register, refresh, or remove the single Wiser sidebar panel."""
    entries = list(_enabled_entries(hass))
    if not entries:
        if PANEL_STATE in hass.data:
            frontend.async_remove_panel(hass, PANEL_PATH)
            hass.data.pop(PANEL_STATE)
        return

    panels = await _discover_panels(hass, entries)
    panel_path = Path(__file__).parent / PANEL_FILENAME
    panel_version = await hass.async_add_executor_job(card_version, panel_path)
    panel_url = f"{URL_BASE}/{PANEL_FILENAME}?v={panel_version}"
    # Include the shell URL so an integration reload refreshes a changed shell bundle.
    state = {"panels": panels, "module_url": panel_url}
    if state == hass.data.get(PANEL_STATE):
        return

    config = {
        **state,
        "_panel_custom": {
            "name": PANEL_COMPONENT,
            "module_url": panel_url,
            "embed_iframe": False,
            "trust_external": False,
        },
    }
    if PANEL_STATE in hass.data:
        frontend.async_register_built_in_panel(
            hass,
            component_name="custom",
            frontend_url_path=PANEL_PATH,
            sidebar_title="Wiser",
            sidebar_icon="wiser:wiser",
            config=config,
            update=True,
        )
    else:
        await panel_custom.async_register_panel(
            hass,
            frontend_url_path=PANEL_PATH,
            webcomponent_name=PANEL_COMPONENT,
            sidebar_title="Wiser",
            sidebar_icon="wiser:wiser",
            module_url=panel_url,
            config=state,
        )
    hass.data[PANEL_STATE] = state


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


def save_panel_config(hass, panel_id, configs):
    """Save settings for any registry-defined panel using the shared option."""
    if panel_id not in {card["id"] for card in get_manifest(hass) if card.get("panel")}:
        raise ValueError("Unknown Wiser panel")
    if type(configs) is not dict:
        raise ValueError("Invalid panel setting")
    entries = dict(_enabled_entries(hass))
    updates = []
    for hub, config in configs.items():
        if hub not in entries:
            raise ValueError("Hub is not available in the Wiser panel")
        if type(config) is not dict or not _is_json_value(config):
            raise ValueError("Invalid panel setting")
        settings = {
            key: value
            for key, value in config.items()
            if key not in {"type", "hub", "hubs", "_panel_hide_title"}
        }
        entry = entries[hub]
        generic = entry.options.get(CONF_WISER_PANEL_CONFIG, {})
        if not isinstance(generic, dict):
            generic = {}
        updates.append((entry, {**generic, panel_id: settings}))
    for entry, generic in updates:
        hass.config_entries.async_update_entry(
            entry,
            options={**entry.options, CONF_WISER_PANEL_CONFIG: generic},
        )


def save_wiser_panel_tabs(hass, tabs):
    """Save the shared panel tab order and custom titles for every hub."""
    if type(tabs) is not list:
        raise ValueError("Invalid Wiser panel tabs")

    known_ids = {module["id"] for module in get_manifest(hass) if module.get("panel")}
    saved_tabs = []
    seen = set()
    for tab in tabs:
        if type(tab) is not dict:
            raise ValueError("Invalid Wiser panel tab")
        panel_id = tab.get("id")
        title = tab.get("title")
        if (
            type(panel_id) is not str
            or panel_id not in known_ids
            or panel_id in seen
            or type(title) is not str
            or not title.strip()
            or len(title.strip()) > 64
        ):
            raise ValueError("Invalid Wiser panel tab")
        seen.add(panel_id)
        saved_tabs.append({"id": panel_id, "title": title.strip()})

    entries = list(_enabled_entries(hass))
    for _, entry in entries:
        generic = entry.options.get(CONF_WISER_PANEL_CONFIG, {})
        if not isinstance(generic, dict):
            generic = {}
        hass.config_entries.async_update_entry(
            entry,
            options={
                **entry.options,
                CONF_WISER_PANEL_CONFIG: {
                    **generic,
                    _PANEL_TABS_CONFIG: saved_tabs,
                },
            },
        )
