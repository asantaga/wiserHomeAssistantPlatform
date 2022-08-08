"""Wiser Frontend"""
from atexit import register
import logging
from datetime import timedelta
from typing import Any
from xmlrpc.client import boolean
from homeassistant.helpers.event import async_call_later
from ..const import (
    URL_BASE,
    WISER_CARD_FILENAMES
)

_LOGGER = logging.getLogger(__name__)

class WiserCardRegistration:

    def __init__(self, hass):
        self.hass = hass

    def register(self):
        self.register_wiser_path()
        if self.hass.data['lovelace']['mode'] == "storage":
            self.wait_for_lovelace_resources()
    
    # install card resources
    def register_wiser_path(self):
        # Register custom cards path
        self.hass.http.register_static_path(
            URL_BASE,
            self.hass.config.path("custom_components/wiser/frontend"),
            cache_headers=False
        )

    def wait_for_lovelace_resources(self) -> None:
        def check_lovelace_resources_loaded():
            if self.hass.data['lovelace']['resources'].loaded:
                self.hass.async_create_task(self.async_register_wiser_cards())
            else:
                _LOGGER.warning("Unable to install Wiser card resources because Lovelace resources not yet loaded.  Trying again in 5 seconds.")
                async_call_later(
                    self.hass,
                    5,
                    check_lovelace_resources_loaded
                )
        check_lovelace_resources_loaded()


    async def async_register_wiser_cards(self):
        _LOGGER.warning("Installing Lovelace resources for Wiser cards")
        for card_filename in WISER_CARD_FILENAMES:
            url = f"{URL_BASE}/{card_filename}"
            resource_loaded = [res["url"] for res in self.hass.data['lovelace']["resources"].async_items() if res["url"] == url]
            if not resource_loaded:
                resource_id = await self.hass.data['lovelace']["resources"].async_create_item({"res_type":"module", "url":url})
