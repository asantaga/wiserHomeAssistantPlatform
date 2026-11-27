"""Manage optional browser pre-caching of shared frontend device artwork."""

from hashlib import sha256
from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url, remove_extra_js_url

from ..const import CONF_PRE_CACHE_RESOURCE_IMAGES, URL_BASE
from ..helpers import loaded_wiser_entries

PRECACHE_URL_KEY = "wiser_image_precache_url"


def image_precache_version() -> str:
    """Invalidate the loader when either its code or the image catalogue changes."""
    root = Path(__file__).parent
    return sha256(
        (root / "wiser-image-preload.js").read_bytes()
        + (root / "images/manifest.json").read_bytes()
    ).hexdigest()[:16]


async def async_update_image_precache(hass) -> None:
    """Enable shared pre-caching if any active Wiser hub requests it."""
    enabled = any(
        entry.options.get(CONF_PRE_CACHE_RESOURCE_IMAGES, False)
        for entry in loaded_wiser_entries(hass)
    )
    url = None
    if enabled:
        version = await hass.async_add_executor_job(image_precache_version)
        url = f"{URL_BASE}/wiser-image-preload.js?v={version}"
    previous = hass.data.get(PRECACHE_URL_KEY)
    if previous == url:
        return
    if previous:
        remove_extra_js_url(hass, previous)
    if url:
        add_extra_js_url(hass, url)
        hass.data[PRECACHE_URL_KEY] = url
    else:
        hass.data.pop(PRECACHE_URL_KEY, None)
