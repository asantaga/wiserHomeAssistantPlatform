"""Manage the shared Wiser schedules sidebar panel."""

from .panel import SidebarPanel, async_update_panel, save_panel_config
from ..const import (
    CONF_SHOW_SCHEDULES_SIDEBAR, CONF_SCHEDULES_PANEL_CONFIG,
)

PANEL_PATH = "wiser-schedules"
PANEL_STATE = "wiser_schedules_panel"

_SCHEDULES_PANEL = SidebarPanel(
    path=PANEL_PATH,
    state_key=PANEL_STATE,
    component="wiser-schedules-panel",
    title="Wiser Schedules",
    icon="mdi:calendar-clock",
    filename="wiser-schedule-card.js",
    enabled_option=CONF_SHOW_SCHEDULES_SIDEBAR,
    config_option=CONF_SCHEDULES_PANEL_CONFIG,
    hub_error="Hub is not enabled in the schedules panel",
    setting_error="Invalid schedule card setting",

)


async def async_update_schedules_panel(hass):
    """Show schedules for loaded hubs that have opted into the sidebar."""
    await async_update_panel(hass, _SCHEDULES_PANEL)


def save_schedules_panel_config(hass, configs):
    """Validate all submitted settings before updating integration options."""
    save_panel_config(hass, _SCHEDULES_PANEL, configs)

