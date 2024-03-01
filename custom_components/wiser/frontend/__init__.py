"""Wiser Frontend functions."""
import logging
import os

from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from ..const import URL_BASE, WISER_CARD_FILENAMES

_LOGGER = logging.getLogger(__name__)


class WiserCardRegistration:
    """Class for managing custom card registration."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Init class."""
        self.hass = hass

    async def async_register(self):
        """Register custom cards."""
        await self.async_register_wiser_path()
        if self.hass.data["lovelace"]["mode"] == "storage":
            await self.async_wait_for_lovelace_resources()

    # install card resources
    async def async_register_wiser_path(self):
        """Register wiser path."""
        # Register custom cards path
        self.hass.http.register_static_path(
            URL_BASE,
            self.hass.config.path("custom_components/wiser/frontend"),
            cache_headers=False,
        )

    async def async_wait_for_lovelace_resources(self) -> None:
        """Wait for lovelace resources to load."""

        async def check_lovelace_resources_loaded(now):
            if self.hass.data["lovelace"]["resources"].loaded:
                await self.async_register_wiser_cards()
            else:
                _LOGGER.debug(
                    "Unable to install Wiser card resources because Lovelace resources not yet loaded.  Trying again in 5 seconds"
                )
                async_call_later(self.hass, 5, check_lovelace_resources_loaded)

        await check_lovelace_resources_loaded(0)

    async def async_register_wiser_cards(self):
        """Register custom card resources."""
        _LOGGER.debug("Installing Lovelace resources for Wiser cards")
        for card_filename in WISER_CARD_FILENAMES:
            url = f"{URL_BASE}/{card_filename}"
            resource_loaded = [
                res["url"]
                for res in self.hass.data["lovelace"]["resources"].async_items()
                if res["url"] == url
            ]
            if not resource_loaded:
                await self.hass.data["lovelace"]["resources"].async_create_item(
                    {"res_type": "module", "url": url}
                )

    async def async_unregister(self):
        """Unregister custom cards."""
        # Unload lovelace module resource
        if self.hass.data["lovelace"]["mode"] == "storage":
            for card_filename in WISER_CARD_FILENAMES:
                url = f"{URL_BASE}/{card_filename}"
                wiser_resources = [
                    resource
                    for resource in self.hass.data["lovelace"][
                        "resources"
                    ].async_items()
                    if resource["url"] == url
                ]
                for resource in wiser_resources:
                    await self.hass.data["lovelace"]["resources"].async_delete_item(
                        resource.get("id")
                    )

    async def async_remove_gzip_files(self):
        """Remove cached gzip file versions."""
        path = self.hass.config.path("custom_components/wiser/frontend")
        gzip_files = [
            filename for filename in os.listdir(path) if filename.endswith(".gz")
        ]

        for file in gzip_files:
            try:
                if os.path.getmtime(f"{path}/{file}") < os.path.getmtime(
                    f"{path}/{file.replace('.gz','')}"
                ):
                    _LOGGER.debug("Removing older gzip file - %s", file)
                    os.remove(f"{path}/{file}")
            except OSError:
                pass
