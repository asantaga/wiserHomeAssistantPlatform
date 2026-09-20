"""Exercise persistent card installs and update entities without a running HA."""

import ast
from datetime import timedelta
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

ROOT = Path(__file__).resolve().parents[1] / "custom_components/wiser"


def module(name, **attrs):
    result = ModuleType(name)
    result.__dict__.update(attrs)
    return result


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


class Coordinator:
    def __init__(self, hass, logger, **kwargs):
        self.hass = hass
        self.options = kwargs
        self.data = {}
        self.async_update_listeners = Mock()
        self.async_shutdown = AsyncMock()

    async def async_refresh(self):
        self.data = await self._async_update_data()


class CoordinatorEntity:
    def __init__(self, coordinator):
        self.coordinator = coordinator

    @property
    def available(self):
        return True


class CardUpdatesTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)
        self.registry = SimpleNamespace(
            async_get_entity_id=Mock(return_value=None), async_update_entity=Mock()
        )
        self.session = Mock()
        self.registration = SimpleNamespace(async_register=AsyncMock())
        frontend = module("card_update_test.frontend", __path__=[str(ROOT / "frontend")])
        self.modules = patch.dict(sys.modules, {
            "card_update_test": module("card_update_test", __path__=[str(ROOT)]),
            "card_update_test.const": module("card_update_test.const", URL_BASE="/wiser", DOMAIN="wiser"),
            "card_update_test.frontend": frontend,
            "homeassistant": module("homeassistant"),
            "homeassistant.components": module("homeassistant.components"),
            "homeassistant.components.update": module("homeassistant.components.update", UpdateEntity=type("UpdateEntity", (), {}), UpdateEntityFeature=SimpleNamespace(INSTALL=1)),
            "homeassistant.const": module("homeassistant.const", EntityCategory=SimpleNamespace(CONFIG="config")),
            "homeassistant.exceptions": module("homeassistant.exceptions", HomeAssistantError=RuntimeError),
            "homeassistant.helpers": module("homeassistant.helpers"),
            "homeassistant.helpers.entity_registry": module("homeassistant.helpers.entity_registry", async_get=lambda _: self.registry),
            "homeassistant.helpers.aiohttp_client": module("homeassistant.helpers.aiohttp_client", async_get_clientsession=lambda _: self.session),
            "homeassistant.helpers.update_coordinator": module("homeassistant.helpers.update_coordinator", CoordinatorEntity=CoordinatorEntity, DataUpdateCoordinator=Coordinator),
            "card_update_test.frontend.schedules_sidebar": module("card_update_test.frontend.schedules_sidebar", async_update_schedules_panel=AsyncMock()),
            "card_update_test.frontend.zigbee_sidebar": module("card_update_test.frontend.zigbee_sidebar", async_update_zigbee_panel=AsyncMock()),
        })
        self.modules.start()
        self.addCleanup(self.modules.stop)
        self.files = load("card_update_test.frontend.card_files", ROOT / "frontend/card_files.py")
        self.version_reader = Mock(return_value="1.0.0")
        async def resource(hass, filename):
            return self.files.resolve_card(self.directory, filename, self.version_reader)
        frontend.async_card_resource = resource
        frontend.JSModuleRegistration = Mock(return_value=self.registration)
        self.updates = load("card_update_test.update", ROOT / "update.py")
        self.hass = SimpleNamespace(
            data={}, config=SimpleNamespace(path=lambda *args: str(self.directory.joinpath(*args))),
            async_add_executor_job=AsyncMock(side_effect=lambda fn, *args: fn(*args)),
        )
        self.coordinator = self.updates.CardUpdateCoordinator(self.hass)

    def payload(self, card="zigbee", version="2.0.0"):
        _, filename, component = self.updates._CARDS[card]
        return (f"/*! WISER-CARD-VERSION {filename[:-3]} {version} */\n"
                f"customElements.define('{component}', class extends HTMLElement {{}});").encode()

    def metadata(self, card="zigbee", version="2.0.0"):
        contents = self.payload(card, version)
        repo, filename, _ = self.updates._CARDS[card]
        return {
            "tag_name": f"v{version}", "published_at": "2026-09-20", "draft": False, "prerelease": False,
            "assets": [{"name": filename, "state": "uploaded", "size": len(contents),
                        "digest": "sha256:" + sha256(contents).hexdigest(),
                        "browser_download_url": f"https://github.com/{repo}/releases/download/v{version}/{filename}"}],
        }

    def response(self, *, json_data=None, contents=b"", error=None):
        response = SimpleNamespace(raise_for_status=Mock(side_effect=error), json=AsyncMock(return_value=json_data))
        async def chunks(size):
            yield contents
        response.content = SimpleNamespace(iter_chunked=chunks)
        context = type("ResponseContext", (), {
            "__aenter__": AsyncMock(return_value=response), "__aexit__": AsyncMock(return_value=False)
        })()
        return context

    def test_persistent_cache_survives_restart_and_newer_bundle_takes_precedence(self):
        contents = self.payload()
        self.files.store_card(self.directory, "wiser-zigbee-card.js", "2.0.0", contents)
        path, url, version = self.files.resolve_card(self.directory, "wiser-zigbee-card.js", self.version_reader)
        self.assertEqual(path.read_bytes(), contents)
        self.assertIn("/wiser/cards/", url)
        self.assertEqual(version, "2.0.0")
        self.version_reader.return_value = "3.0.0"
        path, url, version = self.files.resolve_card(self.directory, "wiser-zigbee-card.js", self.version_reader)
        self.assertEqual(path, ROOT / "frontend/wiser-zigbee-card.js")
        self.assertEqual(version, "3.0.0")

    def test_corrupt_cache_falls_back_to_bundled_card(self):
        self.files.store_card(self.directory, "wiser-zigbee-card.js", "2.0.0", self.payload())
        path, _, _ = self.files.resolve_card(self.directory, "wiser-zigbee-card.js", self.version_reader)
        path.write_bytes(b"corrupt")
        _, url, version = self.files.resolve_card(self.directory, "wiser-zigbee-card.js", self.version_reader)
        self.assertEqual(url, "/wiser/wiser-zigbee-card.js?v=1.0.0")
        self.assertEqual(version, "1.0.0")

    def test_failed_metadata_write_keeps_previous_version(self):
        self.files.store_card(self.directory, "wiser-zigbee-card.js", "2.0.0", self.payload())
        original = self.files._atomic_write
        def write(path, contents):
            if path.suffix == ".json":
                raise OSError("disk full")
            original(path, contents)
        with patch.object(self.files, "_atomic_write", side_effect=write):
            with self.assertRaises(OSError):
                self.files.store_card(self.directory, "wiser-zigbee-card.js", "3.0.0", self.payload(version="3.0.0"))
        self.assertEqual(self.files.resolve_card(self.directory, "wiser-zigbee-card.js", self.version_reader)[2], "2.0.0")

    def test_stable_checks_do_not_offer_downgrades_or_unknown_versions(self):
        self.assertTrue(self.files.newer_version("2.0.0", "2.0.0-rc1"))
        self.assertFalse(self.files.newer_version("2.0.0", "3.0.0-dev.84"))
        self.assertFalse(self.files.newer_version("2.0.0", "2.0.0"))
        self.assertFalse(self.files.newer_version("2.0.0", "sha256-abcd"))

    def test_rejects_prereleases_and_foreign_download_urls(self):
        for change in ("prerelease", "draft", "url", "size"):
            metadata = self.metadata()
            if change in ("prerelease", "draft"):
                metadata[change] = True
            elif change == "url":
                metadata["assets"][0]["browser_download_url"] = "https://example.com/card.js"
            else:
                metadata["assets"][0]["size"] = 21 * 1024 * 1024
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.updates._validate_release("zigbee", metadata)

    def test_rejects_bad_checksum_and_wrong_version_or_panel(self):
        release = self.updates._validate_release("zigbee", self.metadata())
        with self.assertRaises(ValueError):
            self.updates._validate_download("zigbee", release, self.payload().replace(b"2.0.0", b"9.0.0"))
        for contents in (self.payload(version="9.0.0"), self.payload().replace(b"wiser-zigbee-panel", b"other-widget-name")):
            release["asset"]["digest"] = None
            release["asset"]["size"] = len(contents)
            with self.assertRaises(ValueError):
                self.updates._validate_download("zigbee", release, contents)

    async def test_network_failure_does_not_block_other_card_or_hub_setup(self):
        import aiohttp
        self.session.get.side_effect = [self.response(error=aiohttp.ClientError("offline")), self.response(json_data=self.metadata())]
        with self.assertLogs("card_update_test.update", level="WARNING"):
            await self.coordinator.async_refresh()
        self.assertIsNone(self.coordinator.data["schedule"]["release"])
        self.assertEqual(self.coordinator.data["zigbee"]["release"]["version"], "2.0.0")
        self.assertEqual(self.coordinator.options["update_interval"], timedelta(hours=24))

    async def test_check_does_not_install_until_user_requests_it(self):
        self.session.get.return_value = self.response(json_data=self.metadata())
        state = await self.coordinator._check_card("zigbee")
        self.assertFalse((self.directory / self.files.CARD_CACHE).exists())
        self.coordinator.data["zigbee"] = state
        self.session.get.return_value = self.response(contents=self.payload())
        await self.coordinator.install("zigbee")
        self.assertEqual(self.coordinator.data["zigbee"]["installed"], "2.0.0")
        self.assertEqual(self.files.resolve_card(self.directory, "wiser-zigbee-card.js", self.version_reader)[2], "2.0.0")
        self.registration.async_register.assert_awaited_once()
        self.updates.async_update_schedules_panel.assert_awaited_once()
        self.updates.async_update_zigbee_panel.assert_awaited_once()
        self.assertFalse(self.coordinator.installing)

    async def test_invalid_download_keeps_existing_installation(self):
        release = self.updates._validate_release("zigbee", self.metadata())
        self.coordinator.data["zigbee"] = {"installed": "1.0.0", "release": release}
        self.session.get.return_value = self.response(contents=b"broken")
        with self.assertRaisesRegex(RuntimeError, "Unable to install"):
            await self.coordinator.install("zigbee")
        self.assertEqual(self.coordinator.data["zigbee"]["installed"], "1.0.0")
        self.assertFalse((self.directory / self.files.CARD_CACHE).exists())
        self.assertFalse(self.coordinator.installing)
        self.registration.async_register.assert_not_awaited()

    async def test_multiple_hubs_share_entities_and_transfer_when_owner_unloads(self):
        self.hass.data["wiser_card_updates"] = self.coordinator
        self.coordinator.async_refresh = AsyncMock()
        first, second = Mock(), Mock()
        await self.updates.async_setup_entry(self.hass, SimpleNamespace(entry_id="first"), first)
        await self.updates.async_setup_entry(self.hass, SimpleNamespace(entry_id="second"), second)
        self.coordinator.async_refresh.assert_awaited_once()
        self.assertEqual(len(first.call_args.args[0]), 2)
        second.assert_not_called()
        self.registry.async_get_entity_id.side_effect = lambda domain, platform, unique_id: f"update.{unique_id}"
        await self.updates.async_unload_card_updates(self.hass, SimpleNamespace(entry_id="first"))
        self.assertEqual(self.coordinator.owner, "second")
        self.assertEqual(len(second.call_args.args[0]), 2)
        self.assertEqual(self.registry.async_update_entity.call_args.kwargs["config_entry_id"], "second")
        await self.updates.async_unload_card_updates(self.hass, SimpleNamespace(entry_id="second"))
        self.coordinator.async_shutdown.assert_awaited_once()
        self.assertNotIn("wiser_card_updates", self.hass.data)

    async def test_update_entity_delegates_manual_install_and_exposes_release(self):
        self.coordinator.data["zigbee"] = {"installed": "1.0.0", "release": self.updates._validate_release("zigbee", self.metadata())}
        entity = self.updates.WiserCardUpdate(self.coordinator, "zigbee")
        self.assertTrue(entity.available)
        self.assertEqual(entity.installed_version, "1.0.0")
        self.assertEqual(entity.latest_version, "2.0.0")
        self.assertIn("/releases/tag/v2.0.0", entity.release_url)
        self.coordinator.install = AsyncMock()
        await entity.async_install(None, False)
        self.coordinator.install.assert_awaited_once_with("zigbee")

    async def test_lovelace_resource_moves_to_cached_url_without_duplicate(self):
        tree = ast.parse((ROOT / "frontend/__init__.py").read_text())
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "JSModuleRegistration")
        active = "/wiser/cards/wiser-zigbee-card-abc.js?v=2.0.0"
        resource = {"id": "card", "url": "/wiser/wiser-zigbee-card.js?v=1.0.0"}
        resources = SimpleNamespace(
            async_items=lambda: [resource], async_update_item=AsyncMock(),
            async_create_item=AsyncMock(), async_delete_item=AsyncMock(),
        )
        self.hass.data["lovelace"] = SimpleNamespace(mode="storage", resources=resources)
        namespace = {
            "HomeAssistant": object, "LovelaceData": object, "Path": Path,
            "MAJOR_VERSION": 2025, "MINOR_VERSION": 5,
            "MODE_STORAGE": "storage", "URL_BASE": "/wiser",
            "CARD_CACHE_URL": "/wiser/cards", "_LOGGER": Mock(),
            "JSMODULES": [{"filename": "wiser-zigbee-card.js", "name": "Zigbee"}],
            "async_card_resource": AsyncMock(return_value=(None, active, "2.0.0")),
        }
        exec(compile(ast.Module(body=[cls], type_ignores=[]), "frontend/__init__.py", "exec"), namespace)
        registration = namespace["JSModuleRegistration"](self.hass)
        registration.async_remove_gzip_files = AsyncMock()
        await registration._async_register_modules()
        resources.async_update_item.assert_awaited_once_with("card", {"res_type": "module", "url": active})
        resources.async_create_item.assert_not_awaited()
        resource["url"] = active
        resources.async_update_item.reset_mock()
        await registration._async_register_modules()
        resources.async_update_item.assert_not_awaited()
        resources.async_create_item.assert_not_awaited()
        await registration.async_unregister()
        resources.async_delete_item.assert_awaited_once_with("card")

    async def test_older_stable_release_is_not_installed_over_development_card(self):
        self.version_reader.return_value = "3.0.0-dev.84"
        self.coordinator.data["zigbee"] = {"release": self.updates._validate_release("zigbee", self.metadata())}
        await self.coordinator.install("zigbee")
        self.session.get.assert_not_called()
        self.assertFalse((self.directory / self.files.CARD_CACHE).exists())
