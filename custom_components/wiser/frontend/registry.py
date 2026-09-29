"""Discover frontend cards independently of integration releases."""

from hashlib import sha256
import json
import logging
from pathlib import Path
from urllib.parse import urlsplit

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..const import CARD_MANIFEST
from .card_files import _atomic_write
from .manifest import validate_manifest

_LOGGER = logging.getLogger(__name__)
REGISTRY_REPOSITORY = "andyblac/WiserFrontendPanelConfig"
REGISTRY_CACHE = ".storage/wiser_cards/registry.json"
REGISTRY_DATA = "wiser_frontend_registry"
_MAX_SIZE = 256 * 1024


def get_manifest(hass):
    """Return the active registry, with bundled definitions as an offline fallback."""
    return hass.data.get(REGISTRY_DATA, CARD_MANIFEST)


def _merge_manifest(current, incoming):
    """Keep installed cards when a release omits them; preserve their identities."""
    merged = {card["id"]: card for card in current}
    for card in incoming:
        previous = merged.get(card["id"])
        if previous and any(
            previous[key] != card[key] for key in ("filename", "repository", "component", "panel")
        ):
            raise ValueError(f"Registry changes the identity of {card['id']}")
        merged[card["id"]] = card
    return validate_manifest(list(merged.values()))


def _load_cached(config_dir):
    try:
        cached = validate_manifest(json.loads((Path(config_dir) / REGISTRY_CACHE).read_text()))
        return _merge_manifest(CARD_MANIFEST, cached)
    except (OSError, ValueError, TypeError, KeyError):
        return CARD_MANIFEST


async def async_load_registry(hass):
    """Load the last valid registry without needing a network connection."""
    if REGISTRY_DATA not in hass.data:
        manifest = await hass.async_add_executor_job(_load_cached, hass.config.path())
        hass.data.setdefault(REGISTRY_DATA, manifest)
    return get_manifest(hass)


def _store_registry(config_dir, manifest):
    path = Path(config_dir) / REGISTRY_CACHE
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(path, json.dumps(manifest).encode())


async def async_refresh_registry(hass, allow_prerelease=False):
    """Check published registry releases, retaining the last good copy on failure."""
    await async_load_registry(hass)
    try:
        session = async_get_clientsession(hass)
        endpoint = "releases?per_page=100" if allow_prerelease else "releases/latest"
        async with session.get(
            f"https://api.github.com/repos/{REGISTRY_REPOSITORY}/{endpoint}",
            headers={"Accept": "application/vnd.github+json", "User-Agent": "Wiser-Home-Assistant"},
            timeout=aiohttp.ClientTimeout(total=20),
        ) as response:
            response.raise_for_status()
            metadata = await response.json()
        releases = metadata if isinstance(metadata, list) else [metadata]
        releases = [item for item in releases if isinstance(item, dict)
                    and not item.get("draft") and item.get("published_at")
                    and (allow_prerelease or not item.get("prerelease"))]
        if not releases:
            raise ValueError("No published frontend registry release")
        release = max(releases, key=lambda item: item["published_at"])
        if not isinstance(release.get("assets"), list):
            raise ValueError("Invalid frontend registry release assets")
        assets = [asset for asset in release["assets"]
                  if isinstance(asset, dict) and asset.get("name") == "cards.json"
                  and asset.get("state") == "uploaded"]
        if len(assets) != 1:
            raise ValueError("Registry release must contain one cards.json asset")
        asset = assets[0]
        if not isinstance(asset.get("browser_download_url"), str) or type(asset.get("size")) is not int:
            raise ValueError("Invalid frontend registry asset metadata")
        url = urlsplit(asset["browser_download_url"])
        if (url.scheme != "https" or url.netloc != "github.com"
                or not url.path.startswith(f"/{REGISTRY_REPOSITORY}/releases/download/")
                or not 0 < asset["size"] <= _MAX_SIZE):
            raise ValueError("Invalid frontend registry asset")
        async with session.get(
            asset["browser_download_url"], timeout=aiohttp.ClientTimeout(total=20)
        ) as response:
            response.raise_for_status()
            contents = bytearray()
            async for chunk in response.content.iter_chunked(65536):
                contents.extend(chunk)
                if len(contents) > _MAX_SIZE:
                    raise ValueError("Frontend registry is too large")
        if len(contents) != asset["size"]:
            raise ValueError("Frontend registry size mismatch")
        if asset.get("digest") and asset["digest"] != "sha256:" + sha256(contents).hexdigest():
            raise ValueError("Frontend registry checksum mismatch")
        manifest = _merge_manifest(get_manifest(hass), validate_manifest(json.loads(contents)))
        await hass.async_add_executor_job(_store_registry, hass.config.path(), manifest)
        hass.data[REGISTRY_DATA] = manifest
    except (aiohttp.ClientError, TimeoutError, OSError, ValueError, TypeError, KeyError) as err:
        _LOGGER.warning("Unable to refresh Wiser frontend registry; keeping cached cards: %s", err)
    return get_manifest(hass)
