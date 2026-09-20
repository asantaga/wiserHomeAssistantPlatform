"""Offer independent, manually installed updates for the shared frontend cards."""

from __future__ import annotations

import asyncio
from datetime import timedelta
from hashlib import sha256
import logging
import re
from urllib.parse import urlsplit

import aiohttp
from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.const import EntityCategory
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import CoordinatorEntity, DataUpdateCoordinator

from .const import DOMAIN
from .frontend import JSModuleRegistration, async_card_resource
from .frontend.card_files import newer_version, prune_card_cache, store_card
from .frontend.schedules_sidebar import async_update_schedules_panel
from .frontend.zigbee_sidebar import async_update_zigbee_panel

_LOGGER = logging.getLogger(__name__)
_MANAGER = "wiser_card_updates"
_MAX_DOWNLOAD = 20 * 1024 * 1024
_CARDS = {
    "schedule": ("andyblac/wiser-schedule-card", "wiser-schedule-card.js", "wiser-schedules-panel"),
    "zigbee": ("andyblac/wiser-zigbee-card", "wiser-zigbee-card.js", "wiser-zigbee-panel"),
}


def _release_version(tag):
    """Only accept stable semantic versions from published releases."""
    match = re.fullmatch(r"v?(\d+\.\d+\.\d+(?:\+[0-9A-Za-z.-]+)?)", tag)
    if not match:
        raise ValueError(f"Unsupported stable card release version: {tag}")
    return match[1]


def _validate_release(card, release):
    """Validate release metadata before exposing an installable update."""
    repository, filename, _ = _CARDS[card]
    if release.get("draft") or release.get("prerelease") or not release.get("published_at"):
        raise ValueError("Expected a published stable card release")
    version = _release_version(release["tag_name"])
    assets = [
        asset for asset in release["assets"]
        if asset["name"] == filename and asset.get("state") == "uploaded"
    ]
    if len(assets) != 1:
        raise ValueError(f"Release must include exactly one {filename}")
    asset = assets[0]
    url = urlsplit(asset["browser_download_url"])
    if (
        url.scheme != "https"
        or url.netloc != "github.com"
        or not url.path.startswith(f"/{repository}/releases/download/")
    ):
        raise ValueError("Invalid card release download URL")
    if not 100 <= asset["size"] <= _MAX_DOWNLOAD:
        raise ValueError("Invalid card release asset size")
    return {
        "version": version,
        "asset": asset,
        "release_url": f"https://github.com/{repository}/releases/tag/{release['tag_name']}",
    }


def _validate_download(card, release, contents):
    """Verify the file before changing the currently installed card."""
    _, filename, component = _CARDS[card]
    asset = release["asset"]
    if len(contents) != asset["size"]:
        raise ValueError("Card download size does not match release metadata")
    digest = "sha256:" + sha256(contents).hexdigest()
    if asset.get("digest") and asset["digest"] != digest:
        raise ValueError("Card download checksum does not match release metadata")
    if contents.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        raise ValueError("Downloaded HTML instead of JavaScript")
    source = contents.decode("utf-8")
    marker = re.search(
        rf"/\*!\s*WISER-CARD-VERSION {re.escape(filename[:-3])}\s+(\S+)\s*\*/", source
    )
    if not marker or marker[1] != release["version"] or component not in source:
        raise ValueError("Card version or sidebar component does not match the release")


async def async_setup_entry(hass, entry, async_add_entities):
    """Create one shared pair of update entities, regardless of hub count."""
    if _MANAGER not in hass.data:
        hass.data[_MANAGER] = CardUpdateCoordinator(hass)
    manager = hass.data[_MANAGER]
    async with manager.setup_lock:
        manager.entries[entry.entry_id] = async_add_entities
        if manager.owner is None:
            # Refresh failure only makes update entities unavailable; heating still loads.
            await manager.async_refresh()
            manager.add_entities(entry.entry_id)


async def async_unload_card_updates(hass, entry):
    """Hand shared update entities to another hub when their owner unloads."""
    manager = hass.data.get(_MANAGER)
    if manager is None:
        return
    async with manager.setup_lock:
        manager.entries.pop(entry.entry_id, None)
        if manager.owner == entry.entry_id:
            manager.owner = None
            if manager.entries:
                manager.add_entities(next(iter(manager.entries)))
        if not manager.entries:
            await manager.async_shutdown()
            hass.data.pop(_MANAGER, None)


class CardUpdateCoordinator(DataUpdateCoordinator):
    """Share one daily GitHub check and install lock across both cards and all hubs."""

    def __init__(self, hass):
        super().__init__(
            hass, _LOGGER, name="Wiser card updates", config_entry=None,
            update_interval=timedelta(hours=24),
        )
        self.setup_lock = asyncio.Lock()
        self.install_lock = asyncio.Lock()
        self.entries = {}
        self.owner = None
        self.installing = set()
        self.pending_refresh = {}
        self.data = {}

    def add_entities(self, entry_id):
        """Transfer registry ownership before attaching the shared entities."""
        registry = er.async_get(self.hass)
        for card in _CARDS:
            entity_id = registry.async_get_entity_id("update", DOMAIN, f"wiser_{card}_card_update")
            if entity_id:
                registry.async_update_entity(entity_id, config_entry_id=entry_id)
        self.owner = entry_id
        self.entries[entry_id]([WiserCardUpdate(self, card) for card in _CARDS])

    async def _async_update_data(self):
        async with self.install_lock:
            results = await asyncio.gather(*(self._check_card(card) for card in _CARDS))
            return dict(zip(_CARDS, results))

    async def _check_card(self, card):
        repository, filename, _ = _CARDS[card]
        _, _, installed = await async_card_resource(self.hass, filename)
        if card in self.pending_refresh:
            installed = self.pending_refresh[card][0]
        try:
            session = async_get_clientsession(self.hass)
            async with session.get(
                f"https://api.github.com/repos/{repository}/releases/latest",
                headers={"Accept": "application/vnd.github+json", "User-Agent": "Wiser-Home-Assistant"},
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                response.raise_for_status()
                release = _validate_release(card, await response.json())
            return {"installed": installed, "release": release, "error": None}
        except (aiohttp.ClientError, TimeoutError, ValueError, KeyError, TypeError) as err:
            _LOGGER.warning("Unable to check %s card releases: %s", card, err)
            return {"installed": installed, "release": None, "error": str(err)}

    async def install(self, card):
        """Install only the release offered to the user; never silently advance it."""
        async with self.install_lock:
            state = self.data.get(card, {})
            release = state.get("release")
            if not release:
                raise HomeAssistantError("No verified card release is available")
            _, filename, _ = _CARDS[card]
            active_path, _, installed = await async_card_resource(self.hass, filename)
            needs_download = newer_version(release["version"], installed)
            if not needs_download and card not in self.pending_refresh:
                return
            self.installing.add(card)
            self.async_update_listeners()
            try:
                if needs_download:
                    session = async_get_clientsession(self.hass)
                    async with session.get(
                        release["asset"]["browser_download_url"],
                        timeout=aiohttp.ClientTimeout(total=120),
                    ) as response:
                        response.raise_for_status()
                        chunks = []
                        size = 0
                        async for chunk in response.content.iter_chunked(65536):
                            size += len(chunk)
                            if size > _MAX_DOWNLOAD:
                                raise ValueError("Card download exceeds size limit")
                            chunks.append(chunk)
                        contents = b"".join(chunks)
                    await self.hass.async_add_executor_job(
                        _validate_download, card, release, contents
                    )
                    await self.hass.async_add_executor_job(
                        store_card, self.hass.config.path(), filename,
                        release["version"], contents,
                    )
                    # Keep offering the update until every frontend registration succeeds.
                    # Retain the previous asset while a failed refresh can still reference it.
                    self.pending_refresh.setdefault(card, (installed, active_path))
                registration = JSModuleRegistration(self.hass)
                await registration.async_register()
                await async_update_schedules_panel(self.hass)
                await async_update_zigbee_panel(self.hass)
                active_path, _, installed = await async_card_resource(self.hass, filename)
                _, previous_path = self.pending_refresh.pop(card)
                state["installed"] = installed
                await self.hass.async_add_executor_job(
                    prune_card_cache, self.hass.config.path(), filename,
                    {active_path, previous_path},
                )
            except (
                aiohttp.ClientError, TimeoutError, OSError, ValueError,
                RuntimeError, HomeAssistantError,
            ) as err:
                raise HomeAssistantError(f"Unable to install card update: {err}") from err
            finally:
                self.installing.discard(card)
                self.async_update_listeners()


class WiserCardUpdate(CoordinatorEntity, UpdateEntity):
    """A user-installed frontend card update, separate from hub firmware."""

    _attr_supported_features = UpdateEntityFeature.INSTALL
    _attr_entity_category = EntityCategory.CONFIG
    _attr_has_entity_name = True
    _attr_release_summary = "Refresh your browser after installation to load the updated card."

    def __init__(self, coordinator, card):
        super().__init__(coordinator)
        self.card = card
        self._attr_unique_id = f"wiser_{card}_card_update"
        self._attr_translation_key = f"{card}_card"

    @property
    def available(self):
        return super().available and self.coordinator.data.get(self.card, {}).get("release") is not None

    @property
    def installed_version(self):
        return self.coordinator.data.get(self.card, {}).get("installed")

    @property
    def latest_version(self):
        release = self.coordinator.data.get(self.card, {}).get("release")
        return release["version"] if release else None

    @property
    def release_url(self):
        release = self.coordinator.data.get(self.card, {}).get("release")
        return release["release_url"] if release else None

    @property
    def in_progress(self):
        return self.card in self.coordinator.installing

    def version_is_newer(self, latest_version, installed_version):
        return newer_version(latest_version, installed_version)

    async def async_install(self, version, backup, **kwargs):
        """Install only after an explicit Home Assistant update action."""
        await self.coordinator.install(self.card)
