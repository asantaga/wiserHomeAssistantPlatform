"""Wiser Frontend"""
from atexit import register
import logging
from datetime import timedelta
import os
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
        def check_lovelace_resources_loaded(now):
            if self.hass.data['lovelace']['resources'].loaded:
                self.hass.async_create_task(self.async_register_wiser_cards())
            else:
                _LOGGER.debug("Unable to install Wiser card resources because Lovelace resources not yet loaded.  Trying again in 5 seconds.")
                async_call_later(
                    self.hass,
                    5,
                    check_lovelace_resources_loaded
                )
        check_lovelace_resources_loaded(0)


    async def async_register_wiser_cards(self):
        _LOGGER.debug("Installing Lovelace resources for Wiser cards")
        for card_filename in WISER_CARD_FILENAMES:
            url = f"{URL_BASE}/{card_filename}"
            resource_loaded = [res["url"] for res in self.hass.data['lovelace']["resources"].async_items() if res["url"] == url]
            if not resource_loaded:
                resource_id = await self.hass.data['lovelace']["resources"].async_create_item({"res_type":"module", "url":url})

    async def async_remove_gzip_files(self):
        path = self.hass.config.path("custom_components/wiser/frontend")
        gzip_files = [filename for filename in os.listdir(path) if filename.endswith(".gz")]

        for file in gzip_files:
            try:
                if os.path.getmtime(f"{path}/{file}") < os.path.getmtime(f"{path}/{file.replace('.gz','')}"):
                    _LOGGER.debug(f"Removing older gzip file - {file}")
                    os.remove(f"{path}/{file}")
            except:
                pass
