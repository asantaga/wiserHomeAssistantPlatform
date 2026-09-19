"""Manage the shared Wiser zigbee sidebar panel."""

import logging

from .panel import SidebarPanel, async_update_panel, save_panel_config
from ..const import CONF_SHOW_ZIGBEE_SIDEBAR, CONF_ZIGBEE_PANEL_CONFIG

_LOGGER = logging.getLogger(__name__)

PANEL_PATH = "wiser-zigbee-panel"
PANEL_STATE = "wiser_zigbee_panel"

_ZIGBEE_PANEL = SidebarPanel(
    path=PANEL_PATH,
    state_key=PANEL_STATE,
    component="wiser-zigbee-panel",
    title="Wiser Zigbee",
    icon="wiser:zigbee",
    filename="wiser-zigbee-card.js",
    enabled_option=CONF_SHOW_ZIGBEE_SIDEBAR,
    config_option=CONF_ZIGBEE_PANEL_CONFIG,
    hub_error="Hub is not enabled in the zigbee panel",
    setting_error="Invalid Zigbee card setting",

)


async def async_update_zigbee_panel(hass):
    """Show zigbee for loaded hubs that have opted into the sidebar."""
    try:
        await async_update_panel(hass, _ZIGBEE_PANEL)
    except ValueError as err:
        # A sidebar route can already belong to a user dashboard. This
        # optional UI must not fail setup after entity platforms loaded.
        _LOGGER.warning(
            "Unable to register Wiser Zigbee sidebar at %s: %s", PANEL_PATH, err
        )


def save_zigbee_panel_config(hass, configs):
    """Validate all submitted settings before updating integration options."""
    save_panel_config(hass, _ZIGBEE_PANEL, configs)
