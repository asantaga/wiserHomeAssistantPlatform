"""Manage the shared Wiser schedules sidebar panel."""

from pathlib import Path

from homeassistant.components import frontend, panel_custom
from . import card_version
from .zigbee_sidebar import async_update_zigbee_panel

from ..const import (
    CONF_SHOW_SCHEDULES_SIDEBAR, CONF_SCHEDULES_PANEL_CONFIG, CONF_ZIGBEE_PANEL_CONFIG,
    DATA, DOMAIN, JSMODULES, URL_BASE,
)

PANEL_PATH = "wiser-schedules"
PANEL_STATE = "wiser_schedules_panel"


async def async_update_schedules_panel(hass):
    """Show schedules for loaded hubs that have opted into the sidebar."""
    loaded = hass.data.get(DOMAIN, {})
    hubs = [
        loaded[entry.entry_id][DATA].wiserhub.system.name
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id in loaded
        and not entry.disabled_by
        and entry.options.get(CONF_SHOW_SCHEDULES_SIDEBAR, False)
    ]
    card_configs = {
        loaded[entry.entry_id][DATA].wiserhub.system.name:
            dict(entry.options.get(CONF_SCHEDULES_PANEL_CONFIG, {}))
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id in loaded
        and loaded[entry.entry_id][DATA].wiserhub.system.name in hubs
    }
    state = {"hubs": hubs, "card_configs": card_configs}
    if hubs:
        card = next(module for module in JSMODULES if module["filename"] == "wiser-schedule-card.js")
        version = await hass.async_add_executor_job(
            card_version, Path(__file__).parent / card["filename"]
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
                sidebar_title="Wiser Schedules",
                sidebar_icon="mdi:calendar-clock",
                config={
                    **config,
                    "_panel_custom": {
                        "name": "wiser-schedules-panel",
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
                webcomponent_name="wiser-schedules-panel",
                sidebar_title="Wiser Schedules",
                sidebar_icon="mdi:calendar-clock",
                module_url=module_url,
                config=config,
            )
        hass.data[PANEL_STATE] = state


def save_schedules_panel_config(hass, configs):
    """Validate all submitted settings before updating integration options."""
    loaded = hass.data.get(DOMAIN, {})
    entries = {
        loaded[entry.entry_id][DATA].wiserhub.system.name: entry
        for entry in hass.config_entries.async_entries(DOMAIN)
        if entry.entry_id in loaded
        and not entry.disabled_by
        and entry.options.get(CONF_SHOW_SCHEDULES_SIDEBAR, False)
    }
    field_types = {
        "name": str, "selected_schedule": str, "view_type": str, "home_screen": str,
        "theme_colors": bool, "show_badges": bool, "show_schedule_id": bool,
        "display_only": bool, "hide_hw_schedule": bool, "admin_only": bool,
        "hide_card_borders": bool, "hide_card_background": bool, "overview_details": bool,
    }
    updates = []
    for hub, config in configs.items():
        if hub not in entries:
            raise ValueError("Hub is not enabled in the schedules panel")
        settings = {}
        for key, value in config.items():
            if key in {"type", "hub"}:
                continue
            if key not in field_types or type(value) is not field_types[key]:
                raise ValueError(f"Invalid schedule card setting: {key}")
            settings[key] = value
        updates.append((entries[hub], settings))
    for entry, settings in updates:
        hass.config_entries.async_update_entry(
            entry, options={**entry.options, CONF_SCHEDULES_PANEL_CONFIG: settings}
        )


def integration_reload_settings(entry):
    """Capture connection and entity options, excluding panel-only preferences."""
    return (
        dict(entry.data),
        {key: value for key, value in entry.options.items()
         if key not in {CONF_SCHEDULES_PANEL_CONFIG, CONF_ZIGBEE_PANEL_CONFIG}},
    )


async def async_handle_entry_update(hass, entry):
    """Apply panel preferences live; retain reloads for other integration changes."""
    loaded = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    settings = integration_reload_settings(entry)
    if loaded is not None and loaded.get("reload_settings") == settings:
        await async_update_schedules_panel(hass)
        await async_update_zigbee_panel(hass)
        return
    await hass.config_entries.async_reload(entry.entry_id)
