"""Register Wiser frontend resources and independently updated card bundles."""

from hashlib import sha256
import re
import logging
import os
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.components.lovelace import MODE_STORAGE, LovelaceData
from homeassistant.const import MAJOR_VERSION, MINOR_VERSION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later

from .card_files import CARD_CACHE, CARD_CACHE_URL, resolve_card

from ..const import JSMODULES, URL_BASE  # noqa: TID252

_LOGGER = logging.getLogger(__name__)


def card_version(path: Path) -> str:
    """Resolve the card's banner variable, ignoring bundled library versions."""
    version_pattern = r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?"
    try:
        contents = path.read_bytes()
    except OSError:
        return "missing"
    source = contents.decode("utf-8", errors="replace")
    # Explicit build metadata is authoritative; legacy parsing remains below.
    marker = re.search(
        rf"/\*!\s*WISER-CARD-VERSION {re.escape(path.stem)}\s+({version_pattern})\s*\*/",
        source,
    )
    if marker:
        return marker[1]
    # New builds inline CARD_VERSION into the editor's version footer and
    # no longer emit the legacy startup banner.
    footer = re.search(
        rf'class=["\']version["\'][^`]*?common\.version["\']\)\}}:\s*'
        rf'\$\{{["\']({version_pattern})["\']\}}',
        source,
    )
    if path.stem == "wiser-zigbee-card" and footer:
        return footer[1]

    banner_name = "WISER-ZIGBEE(?:-NETWORK)?-CARD" if path.stem == "wiser-zigbee-card" else re.escape(path.stem.upper())
    banner = re.search(
        banner_name + r'[^`]*?common\.version[\"\']\)\}\s*\$\{([\w$]+)\}',
        source,
    )
    if banner:
        assignment = re.search(
            rf'(?<![\w$]){re.escape(banner[1])}\s*=\s*[\"\']({version_pattern})[\"\']',
            source,
        )
        if assignment:
            return assignment[1]
    # Still refresh caches for unfamiliar builds rather than advertise a stale
    # version from const.py. This is a content identifier, not a release number.
    return f"sha256-{sha256(contents).hexdigest()[:16]}"


async def async_card_resource(hass, filename):
    """Resolve the active card path, cache-busted URL, and version off the loop."""
    return await hass.async_add_executor_job(
        resolve_card, hass.config.path(), filename, card_version
    )


class JSModuleRegistration:
    """Register Javascript modules."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialise."""
        self.hass = hass
        self.lovelace: LovelaceData = self.hass.data.get("lovelace")
        if self.lovelace is None:
            self.resource_mode = None
            return

        # Fix for change to name of mode to reousrce_mode in 2026.2
        if (MAJOR_VERSION, MINOR_VERSION) >= (2026, 2):
            self.resource_mode = self.lovelace.resource_mode
        else:
            self.resource_mode = self.lovelace.mode

    async def async_register(self):
        """Register view_assist path."""
        await self._async_register_path()
        icon_version = await self.hass.async_add_executor_job(
            card_version, Path(__file__).parent / "wiser-icons.js"
        )
        add_extra_js_url(self.hass, f"{URL_BASE}/wiser-icons.js?v={icon_version}")


        if self.lovelace and self.resource_mode == MODE_STORAGE:
            await self._async_wait_for_lovelace_resources()

    # install card resources
    async def _async_register_path(self):
        """Register resource path if not already registered."""
        cache = Path(self.hass.config.path(CARD_CACHE))
        await self.hass.async_add_executor_job(lambda: cache.mkdir(parents=True, exist_ok=True))
        if not self.hass.data.get("wiser_card_cache_registered"):
            try:
                await self.hass.http.async_register_static_paths(
                    [StaticPathConfig(CARD_CACHE_URL, cache, False)]
                )
            except RuntimeError:
                # Another hub may have registered the shared path during setup.
                _LOGGER.debug("Card cache path already registered")
            self.hass.data["wiser_card_cache_registered"] = True
        try:
            await self.hass.http.async_register_static_paths(
                [StaticPathConfig(URL_BASE, Path(__file__).parent, False)]
            )
            _LOGGER.debug("Registered resource path from %s", Path(__file__).parent)
        except RuntimeError:
            # Runtime error is likley this is already registered.
            _LOGGER.debug("Resource path already registered")

    async def _async_wait_for_lovelace_resources(self) -> None:
        """Wait for lovelace resources to have loaded."""

        async def _check_lovelace_resources_loaded(now):
            if self.lovelace.resources.loaded:
                await self._async_register_modules()
            else:
                _LOGGER.debug(
                    "Unable to install resources because Lovelace resources have not yet loaded.  Trying again in 5 seconds"
                )
                async_call_later(self.hass, 5, _check_lovelace_resources_loaded)

        await _check_lovelace_resources_loaded(0)

    async def _async_register_modules(self):
        """Register modules if not already registered."""
        _LOGGER.debug("Installing javascript modules")

        # Get resources already registered
        resources = [
            resource
            for resource in self.lovelace.resources.async_items()
            if resource["url"].startswith(URL_BASE)
        ]

        for module in JSMODULES:
            url = f"{URL_BASE}/{module.get('filename')}"

            _, active_url, version = await async_card_resource(self.hass, module["filename"])

            card_registered = False

            for resource in resources:
                if (
                    self._get_resource_path(resource["url"]) == url
                    or self._get_resource_path(resource["url"]).startswith(
                        f"{CARD_CACHE_URL}/{Path(module['filename']).stem}-"
                    )
                ):
                    card_registered = True
                    # check version
                    if resource["url"] != active_url:
                        # Update card version
                        _LOGGER.debug(
                            "Updating %s to version %s",
                            module.get("name"),
                            version,
                        )
                        await self.lovelace.resources.async_update_item(
                            resource.get("id"),
                            {
                                "res_type": "module",
                                "url": active_url,
                            },
                        )
                        # Remove old gzipped files
                        await self.async_remove_gzip_files()
                    else:
                        _LOGGER.debug(
                            "%s already registered as version %s",
                            module.get("name"),
                            version,
                        )

            if not card_registered:
                _LOGGER.debug(
                    "Registering %s as version %s",
                    module.get("name"),
                    version,
                )
                await self.lovelace.resources.async_create_item(
                    {"res_type": "module", "url": active_url}
                )

    def _get_resource_path(self, url: str):
        return url.split("?")[0]

    def _get_resource_version(self, url: str):
        return parse_qs(urlsplit(url).query).get("v", [None])[0]

    async def async_unregister(self):
        """Unload lovelace module resource."""
        if self.resource_mode == MODE_STORAGE:
            for module in JSMODULES:
                url = f"{URL_BASE}/{module.get('filename')}"
                wiser_resources = [
                    resource
                    for resource in self.lovelace.resources.async_items()
                    if str(resource["url"]).startswith(url)
                    or str(resource["url"]).startswith(
                        f"{CARD_CACHE_URL}/{Path(module['filename']).stem}-"
                    )
                ]
                for resource in wiser_resources:
                    await self.lovelace.resources.async_delete_item(resource.get("id"))

    async def async_remove_gzip_files(self):
        """Remove cached gzip files."""
        await self.hass.async_add_executor_job(self.remove_gzip_files)

    def remove_gzip_files(self):
        """Remove cached gzip files."""
        path = self.hass.config.path("custom_components/wiser/frontend")

        gzip_files = [
            filename for filename in os.listdir(path) if filename.endswith(".gz")
        ]

        for file in gzip_files:
            try:
                if (
                    Path.stat(f"{path}/{file}").st_mtime
                    < Path.stat(f"{path}/{file.replace('.gz', '')}").st_mtime
                ):
                    _LOGGER.debug("Removing older gzip file - %s", file)
                    Path.unlink(f"{path}/{file}")
            except OSError:
                pass
