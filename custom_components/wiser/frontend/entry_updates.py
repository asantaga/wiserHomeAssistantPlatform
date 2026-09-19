"""Apply panel preferences live and reload other integration settings."""

from .schedules_sidebar import async_update_schedules_panel
from .zigbee_sidebar import async_update_zigbee_panel
from ..const import CONF_SCHEDULES_PANEL_CONFIG, CONF_ZIGBEE_PANEL_CONFIG, DOMAIN


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
