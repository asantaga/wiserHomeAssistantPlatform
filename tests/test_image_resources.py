"""Verify shared artwork, optional pre-caching, and cache invalidation."""

import ast
from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from test_ui_options import load_functions

loaded_wiser_entries = load_functions(
    "helpers.py", {"loaded_wiser_entries"}, {"DOMAIN": "wiser"}
).loaded_wiser_entries

FRONTEND = Path(__file__).resolve().parents[1] / "custom_components/wiser/frontend"


class ImageResourcesTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        tree = ast.parse((FRONTEND / "image_resources.py").read_text())
        self.namespace = {
            "__file__": str(FRONTEND / "image_resources.py"),
            "Path": Path, "sha256": sha256,
            "loaded_wiser_entries": loaded_wiser_entries,
            "CONF_PRE_CACHE_RESOURCE_IMAGES": "pre_cache_resource_images",
            "DOMAIN": "wiser", "URL_BASE": "/wiser",
            "PRECACHE_URL_KEY": "wiser_image_precache_url",
            "add_extra_js_url": Mock(), "remove_extra_js_url": Mock(),
        }
        functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(FRONTEND / "image_resources.py"), "exec"), self.namespace)
        self.entries = []
        self.hass = SimpleNamespace(
            data={},
            config_entries=SimpleNamespace(async_entries=lambda domain: self.entries),
            async_add_executor_job=AsyncMock(side_effect=lambda fn: fn()),
        )

    async def update(self, *options):
        self.entries = [
            SimpleNamespace(entry_id=str(index), disabled_by=None, options=entry)
            for index, entry in enumerate(options)
        ]
        self.hass.data["wiser"] = {entry.entry_id: {} for entry in self.entries}
        await self.namespace["async_update_image_precache"](self.hass)

    async def test_registers_once_when_explicitly_enabled_across_hubs(self):
        await self.update({"pre_cache_resource_images": True})
        url = self.hass.data["wiser_image_precache_url"]
        self.assertTrue(url.startswith("/wiser/wiser-image-preload.js?v="))
        await self.update({"pre_cache_resource_images": True}, {"pre_cache_resource_images": True})
        self.namespace["add_extra_js_url"].assert_called_once_with(self.hass, url)
        self.namespace["remove_extra_js_url"].assert_not_called()

    async def test_precache_defaults_off(self):
        await self.update({})
        self.namespace["add_extra_js_url"].assert_not_called()
        self.hass.async_add_executor_job.assert_not_awaited()

    async def test_ignored_unloaded_and_disabled_hubs_cannot_enable_precache(self):
        await self.update({"pre_cache_resource_images": False})
        self.entries.extend([
            SimpleNamespace(entry_id="ignored-1", source="ignore", disabled_by=None, options={}),
            SimpleNamespace(entry_id="ignored-2", source="ignore", disabled_by=None, options={}),
            SimpleNamespace(entry_id="unloaded", disabled_by=None, options={"pre_cache_resource_images": True}),
            SimpleNamespace(entry_id="disabled", disabled_by="user", options={"pre_cache_resource_images": True}),
        ])
        self.hass.data["wiser"]["disabled"] = {}
        await self.namespace["async_update_image_precache"](self.hass)
        self.namespace["add_extra_js_url"].assert_not_called()
        self.hass.async_add_executor_job.assert_not_awaited()

    async def test_disabled_does_not_register_or_read_assets(self):
        await self.update({"pre_cache_resource_images": False})
        self.namespace["add_extra_js_url"].assert_not_called()
        self.hass.async_add_executor_job.assert_not_awaited()

    async def test_disable_removes_previous_loader_and_reenable_restores_it(self):
        await self.update({"pre_cache_resource_images": True})
        url = self.hass.data["wiser_image_precache_url"]
        await self.update({"pre_cache_resource_images": False})
        self.namespace["remove_extra_js_url"].assert_called_once_with(self.hass, url)
        self.assertNotIn("wiser_image_precache_url", self.hass.data)
        await self.update({"pre_cache_resource_images": True})
        self.assertEqual(self.namespace["add_extra_js_url"].call_count, 2)

    async def test_any_enabled_hub_requests_shared_precache(self):
        await self.update({"pre_cache_resource_images": False}, {"pre_cache_resource_images": True})
        self.namespace["add_extra_js_url"].assert_called_once()
        await self.update({"pre_cache_resource_images": False}, {"pre_cache_resource_images": False})
        self.namespace["remove_extra_js_url"].assert_called_once()

    async def test_new_catalogue_replaces_old_loader_url(self):
        await self.update({"pre_cache_resource_images": True})
        previous = self.hass.data["wiser_image_precache_url"]
        self.namespace["image_precache_version"] = lambda: "new-images"
        await self.update({"pre_cache_resource_images": True})
        self.namespace["remove_extra_js_url"].assert_called_once_with(self.hass, previous)
        self.namespace["add_extra_js_url"].assert_called_with(self.hass, "/wiser/wiser-image-preload.js?v=new-images")

    def test_catalogue_has_cacheable_content_addressed_pngs(self):
        catalogue = json.loads((FRONTEND / "images/manifest.json").read_text())
        self.assertEqual(catalogue["OnOffLight"], catalogue["LoadControl"])
        self.assertEqual(len(set(catalogue.values())), 18)
        for url in set(catalogue.values()):
            self.assertTrue(url.startswith("/wiser/images/devices/"))
            path = FRONTEND / url.removeprefix("/wiser/")
            data = path.read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertIn(sha256(data).hexdigest()[:12], path.stem)

    async def test_static_image_route_uses_browser_cache(self):
        tree = ast.parse((FRONTEND / "__init__.py").read_text())
        method = next(node for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef) and node.name == "_async_register_path")
        namespace = {
            "Path": Path, "__file__": str(FRONTEND / "__init__.py"),
            "CARD_CACHE": ".storage/wiser/cards", "CARD_CACHE_URL": "/wiser/cards",
            "URL_BASE": "/wiser", "StaticPathConfig": lambda *args: args,
            "_LOGGER": Mock(),
        }
        exec(compile(ast.Module(body=[method], type_ignores=[]), str(FRONTEND / "__init__.py"), "exec"), namespace)
        # Directory creation runs off the event loop; no real config folder needed.
        self.hass.async_add_executor_job = AsyncMock()
        self.hass.config = SimpleNamespace(path=lambda *parts: str(Path("/config", *parts)))
        self.hass.http = SimpleNamespace(async_register_static_paths=AsyncMock())
        await namespace["_async_register_path"](SimpleNamespace(hass=self.hass))
        routes = self.hass.http.async_register_static_paths.call_args.args[0]
        self.assertEqual(routes[0], ("/wiser/images", FRONTEND / "images", True))
        self.assertEqual(routes[1], ("/wiser", FRONTEND, False))
