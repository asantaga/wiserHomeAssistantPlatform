"""Offer independent, manually installed Wiser frontend updates."""

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

from .const import CARD_MANIFEST, DOMAIN
from .frontend import JSModuleRegistration, async_card_resource
from .frontend.card_files import newer_version, prune_card_cache, store_card
from .frontend.registry import async_load_registry
from .frontend.wiser_sidebar import async_update_wiser_panel

_LOGGER = logging.getLogger(__name__)
_MANAGER = "wiser_card_updates"
_MAX_DOWNLOAD = 20 * 1024 * 1024
_HACS_REPOSITORY_ID = "159080189"


def _release_version(tag, allow_prerelease=False):
    """Accept semantic card versions allowed by the selected release channel."""
    match = re.fullmatch(
        r"v?(\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?)",
        tag,
    )
    if not match:
        raise ValueError(f"Unsupported card release version: {tag}")
    if "-" in match[1].split("+", 1)[0] and not allow_prerelease:
        raise ValueError(f"Unsupported stable card release version: {tag}")
    return match[1]


def _validate_release(definition, release, allow_prerelease=False):
    """Validate release metadata before exposing an installable update."""
    repository, filename = definition["repository"], definition["filename"]
    if (
        release.get("draft")
        or (release.get("prerelease") and not allow_prerelease)
        or not release.get("published_at")
    ):
        raise ValueError("Expected a published stable card release")
    version = _release_version(release["tag_name"], allow_prerelease)
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


def _prereleases_enabled(hass):
    """Follow HACS' prerelease preference for this integration when available."""
    registry = er.async_get(hass)
    entity_id = registry.async_get_entity_id(
        "switch", "hacs", _HACS_REPOSITORY_ID
    )
    states = getattr(hass, "states", None)
    return bool(entity_id and states and states.is_state(entity_id, "on"))


def _select_release(definition, releases, allow_prerelease):
    """Select the highest valid published release allowed by the channel."""
    selected = None
    for metadata in releases:
        try:
            release = _validate_release(definition, metadata, allow_prerelease)
        except (ValueError, KeyError, TypeError):
            continue
        if selected is None or newer_version(release["version"], selected["version"]):
            selected = release
    if selected is None:
        raise ValueError("No verified card release is available")
    return selected


def _validate_download(definition, release, contents):
    """Verify the file before changing the currently installed card."""
    filename, component = definition["filename"], definition["component"]
    asset = release["asset"]
    if len(contents) != asset["size"]:
        raise ValueError("Card download size does not match release metadata")
    digest = "sha256:" + sha256(contents).hexdigest()
    if asset.get("digest") and asset["digest"] != digest:
        raise ValueError("Card download checksum does not match release metadata")
    if contents.lstrip().lower().startswith((b"<!doctype html", b"<html")):
        raise ValueError("Downloaded HTML instead of JavaScript")
    source = contents.decode("utf-8")
    if re.search(r"wiser/[a-z0-9_-]+_panel/configure", source):
        raise ValueError("Panel bundle must use the generic settings API")
    marker = re.search(
        rf"/\*!\s*WISER-CARD-VERSION {re.escape(filename[:-3])}\s+(\S+)\s*\*/", source
    )
    panel_component = definition.get("panel")
    if (
        not marker
        or marker[1] != release["version"]
        or component not in source
        or (panel_component and panel_component not in source)
    ):
        raise ValueError("Card version or sidebar component does not match the release")


async def async_setup_entry(hass, entry, async_add_entities):
    """Create shared update entities for all known cards, regardless of hub count."""
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
    """Discover cards daily and share their update entities across all hubs."""

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
        self.cards = {card["id"]: card for card in CARD_MANIFEST}
        self.added_cards = set()

    def add_entities(self, entry_id):
        """Transfer update-entity ownership to the selected hub."""
        self.owner = entry_id
        self.added_cards = set()
        self._add_discovered_entities()

    def _add_discovered_entities(self):
        """Attach newly discovered cards once, without reloading the integration."""
        if self.owner is None:
            return
        registry = er.async_get(self.hass)
        cards = self.cards.keys() - self.added_cards
        legacy_registry_entity = registry.async_get_entity_id(
            "update", DOMAIN, "wiser_frontend_registry_update"
        )
        if legacy_registry_entity:
            registry.async_remove(legacy_registry_entity)
        for card in sorted(cards):
            entity_id = registry.async_get_entity_id("update", DOMAIN, f"wiser_{card}_card_update")
            if entity_id:
                registry.async_update_entity(entity_id, config_entry_id=self.owner)
        entities = [WiserCardUpdate(self, card) for card in sorted(cards)]
        if entities:
            self.entries[self.owner](entities)
            self.added_cards.update(cards)

    async def _async_update_data(self):
        async with self.install_lock:
            manifest = await async_load_registry(self.hass)
            self.cards = {card["id"]: card for card in manifest}
            results = await asyncio.gather(*(self._check_card(card) for card in self.cards))
            self._add_discovered_entities()
            return dict(zip(self.cards, results))

    async def _check_card(self, card):
        definition = self.cards[card]
        repository, filename = definition["repository"], definition["filename"]
        _, _, installed = await async_card_resource(self.hass, filename)
        if installed == "missing":
            for legacy_filename in definition.get("legacy_filenames", []):
                _, _, legacy_version = await async_card_resource(
                    self.hass, legacy_filename
                )
                if legacy_version != "missing":
                    installed = legacy_version
                    break
        if card in self.pending_refresh:
            installed = self.pending_refresh[card][0]
        try:
            allow_prerelease = _prereleases_enabled(self.hass)
            endpoint = "releases?per_page=100" if allow_prerelease else "releases/latest"
            session = async_get_clientsession(self.hass)
            async with session.get(
                f"https://api.github.com/repos/{repository}/{endpoint}",
                headers={"Accept": "application/vnd.github+json", "User-Agent": "Wiser-Home-Assistant"},
                timeout=aiohttp.ClientTimeout(total=20),
            ) as response:
                response.raise_for_status()
                metadata = await response.json()
                release = (
                    _select_release(definition, metadata, True)
                    if allow_prerelease
                    else _validate_release(definition, metadata)
                )
            return {"installed": "0.0.0" if installed == "missing" else installed, "release": release, "error": None}
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
            definition = self.cards[card]
            filename = definition["filename"]
            active_path, _, installed = await async_card_resource(self.hass, filename)
            needs_download = installed == "missing" or newer_version(release["version"], installed)
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
                        _validate_download, definition, release, contents
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
                await async_update_wiser_panel(self.hass)
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

    @property
    def name(self):
        """Follow registry name changes without recreating the update entity."""
        return self.coordinator.cards[self.card]["name"]

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
