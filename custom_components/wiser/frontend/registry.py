"""Discover frontend cards independently of integration releases."""

from hashlib import sha256
import json
import logging
from pathlib import Path
import re
from urllib.parse import urlsplit

import aiohttp
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..const import CARD_MANIFEST
from .card_files import _atomic_write, newer_version
from .manifest import REGISTRY_SCHEMA_VERSION, validate_manifest, validate_registry

_LOGGER = logging.getLogger(__name__)
REGISTRY_REPOSITORY = "andyblac/WiserFrontendPanelConfig"
REGISTRY_CACHE = ".storage/wiser_cards/registry.json"
REGISTRY_RELEASE_CACHE = ".storage/wiser_cards/registry-release.json"
REGISTRY_DATA = "wiser_frontend_registry"
REGISTRY_VERSION_DATA = "wiser_frontend_registry_version"
_MAX_SIZE = 256 * 1024


def get_manifest(hass):
    """Return the active registry, with bundled definitions as an offline fallback."""
    return hass.data.get(REGISTRY_DATA, CARD_MANIFEST)


def _merge_manifest(current, incoming):
    """Keep omitted cards while allowing the registry to update known cards."""
    merged = {card["id"]: card for card in current}
    for card in incoming:
        merged[card["id"]] = card
    return validate_manifest(list(merged.values()))


def _bundled_version():
    """Return the registry release bundled by the integration build."""
    try:
        record = json.loads(
            (Path(__file__).parent / "panel-config-release.json").read_text()
        )
        tag = record.get("tag") or record.get("version")
        return _release_version(tag) if tag else "0.0.0"
    except (OSError, ValueError, TypeError, KeyError):
        return "0.0.0"


def _load_cached(config_dir):
    try:
        cached = validate_registry(json.loads((Path(config_dir) / REGISTRY_CACHE).read_text()))
        manifest = _merge_manifest(CARD_MANIFEST, cached)
    except (OSError, ValueError, TypeError, KeyError):
        return CARD_MANIFEST, _bundled_version()
    try:
        release = json.loads(
            (Path(config_dir) / REGISTRY_RELEASE_CACHE).read_text()
        )
        version = _release_version(release["version"], allow_prerelease=True)
    except (OSError, ValueError, TypeError, KeyError):
        version = _bundled_version()
    return manifest, version


async def async_load_registry(hass):
    """Load the last valid registry without needing a network connection."""
    if REGISTRY_DATA not in hass.data:
        manifest, version = await hass.async_add_executor_job(
            _load_cached, hass.config.path()
        )
        hass.data.setdefault(REGISTRY_DATA, manifest)
        hass.data.setdefault(REGISTRY_VERSION_DATA, version)
    return get_manifest(hass)


def get_registry_version(hass):
    """Return the installed registry release version."""
    version = hass.data.get(REGISTRY_VERSION_DATA)
    return version if version is not None else _bundled_version()


def _store_registry(config_dir, manifest, version):
    document = json.dumps(
        {"schema_version": REGISTRY_SCHEMA_VERSION, "cards": manifest}
    ).encode()
    integration = Path(config_dir) / "custom_components/wiser/frontend"
    integration.mkdir(parents=True, exist_ok=True)
    _atomic_write(integration / "cards.json", document)
    _atomic_write(
        integration / "panel-config-release.json",
        json.dumps(
            {
                "repository": REGISTRY_REPOSITORY,
                "source": "runtime-update",
                "asset": "cards.json",
                "version": version,
            }
        ).encode(),
    )
    path = Path(config_dir) / REGISTRY_CACHE
    path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(
        path,
        document,
    )
    _atomic_write(
        Path(config_dir) / REGISTRY_RELEASE_CACHE,
        json.dumps({"version": version}).encode(),
    )


def _release_version(tag, allow_prerelease=False):
    """Validate a registry release tag for the selected update channel."""
    if not isinstance(tag, str):
        raise ValueError("Invalid frontend registry release version")
    value = tag.removeprefix("v")
    if not re.fullmatch(
        r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?", value
    ):
        raise ValueError("Invalid frontend registry release version")
    if "-" in value.split("+", 1)[0] and not allow_prerelease:
        raise ValueError("Frontend registry prerelease is not enabled")
    return value


def _validate_release(metadata, allow_prerelease=False):
    """Validate registry release metadata without downloading its asset."""
    if (
        not isinstance(metadata, dict)
        or metadata.get("draft")
        or not metadata.get("published_at")
        or (metadata.get("prerelease") and not allow_prerelease)
    ):
        raise ValueError("Expected a published frontend registry release")
    version = _release_version(metadata["tag_name"], allow_prerelease)
    if not isinstance(metadata.get("assets"), list):
        raise ValueError("Invalid frontend registry release assets")
    assets = [
        asset
        for asset in metadata["assets"]
        if isinstance(asset, dict)
        and asset.get("name") == "cards.json"
        and asset.get("state") == "uploaded"
    ]
    if len(assets) != 1:
        raise ValueError("Registry release must contain one cards.json asset")
    asset = assets[0]
    if (
        not isinstance(asset.get("browser_download_url"), str)
        or type(asset.get("size")) is not int
    ):
        raise ValueError("Invalid frontend registry asset metadata")
    url = urlsplit(asset["browser_download_url"])
    if (
        url.scheme != "https"
        or url.netloc != "github.com"
        or not url.path.startswith(f"/{REGISTRY_REPOSITORY}/releases/download/")
        or not 0 < asset["size"] <= _MAX_SIZE
    ):
        raise ValueError("Invalid frontend registry asset")
    return {
        "version": version,
        "asset": asset,
        "release_url": (
            f"https://github.com/{REGISTRY_REPOSITORY}/releases/tag/"
            f"{metadata['tag_name']}"
        ),
    }


def _select_release(releases, allow_prerelease):
    """Select the highest valid registry release allowed by the channel."""
    selected = None
    for metadata in releases:
        try:
            release = _validate_release(metadata, allow_prerelease)
        except (ValueError, KeyError, TypeError):
            continue
        if selected is None or newer_version(release["version"], selected["version"]):
            selected = release
    if selected is None:
        raise ValueError("No verified frontend registry release is available")
    return selected


async def async_check_registry_release(hass, allow_prerelease=False):
    """Check the latest registry release without changing installed config."""
    await async_load_registry(hass)
    session = async_get_clientsession(hass)
    endpoint = "releases?per_page=100" if allow_prerelease else "releases/latest"
    async with session.get(
        f"https://api.github.com/repos/{REGISTRY_REPOSITORY}/{endpoint}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "Wiser-Home-Assistant",
        },
        timeout=aiohttp.ClientTimeout(total=20),
    ) as response:
        response.raise_for_status()
        metadata = await response.json()
    return (
        _select_release(metadata, True)
        if allow_prerelease
        else _validate_release(metadata)
    )


async def async_install_registry_release(hass, release):
    """Download, verify, and atomically activate the offered registry release."""
    session = async_get_clientsession(hass)
    asset = release["asset"]
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
    if (
        asset.get("digest")
        and asset["digest"] != "sha256:" + sha256(contents).hexdigest()
    ):
        raise ValueError("Frontend registry checksum mismatch")
    manifest = _merge_manifest(
        get_manifest(hass), validate_registry(json.loads(contents))
    )
    await hass.async_add_executor_job(
        _store_registry, hass.config.path(), manifest, release["version"]
    )
    hass.data[REGISTRY_DATA] = manifest
    hass.data[REGISTRY_VERSION_DATA] = release["version"]
    return manifest
