"""Exercise dashboard resource opt-out across hubs and independent card updates."""

import ast
import asyncio
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from test_ui_options import load_functions

loaded_wiser_entries = load_functions(
    "helpers.py", {"loaded_wiser_entries"}, {"DOMAIN": "wiser"}
).loaded_wiser_entries

FRONTEND = Path(__file__).resolve().parents[1] / "custom_components/wiser/frontend"


class DashboardResourcesTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.entries = [SimpleNamespace(entry_id="hub", disabled_by=None, options={})]
        self.items = [
            {"id": "legacy", "url": "/wiser/wiser-rooms-card.js?v=old"},
            {"id": "cached", "url": "/wiser/cards/wiser-controls-card-abc.js?v=old"},
            {"id": "schedule", "url": "/wiser/wiser-schedule-card.js?v=old"},
            {"id": "panel", "url": "/wiser/wiser-hub-panel.js?v=old"},
            {"id": "custom", "url": "/wiser/custom.js"},
            {"id": "other", "url": "/hacsfiles/another-card.js"},
        ]

        async def delete(resource_id):
            self.items[:] = [item for item in self.items if item["id"] != resource_id]

        async def create(resource):
            self.items.append({"id": f"new-{len(self.items)}", **resource})

        self.resources = SimpleNamespace(
            async_items=lambda: list(self.items), loaded=True,
            async_delete_item=AsyncMock(side_effect=delete),
            async_create_item=AsyncMock(side_effect=create),
            async_update_item=AsyncMock(),
        )
        self.hass = SimpleNamespace(
            data={"lovelace": SimpleNamespace(mode="storage", resources=self.resources), "wiser": {"hub": {}}},
            config_entries=SimpleNamespace(async_entries=lambda domain: self.entries),
        )
        self.manifest = [
            {"filename": "wiser-controls-card.js", "legacy_filenames": ["wiser-rooms-card.js"]},
            {"filename": "wiser-schedule-card.js"},
            {"filename": "wiser-hub-panel.js", "card": False},
        ]
        self.resolve = AsyncMock(side_effect=lambda hass, name: (None, f"/wiser/{name}?v=new", "new"))
        namespace = {
            "loaded_wiser_entries": loaded_wiser_entries,
            "asyncio": asyncio, "HomeAssistant": object, "LovelaceData": object,
            "Path": Path, "MAJOR_VERSION": 2025, "MINOR_VERSION": 5,
            "MODE_STORAGE": "storage", "URL_BASE": "/wiser", "DOMAIN": "wiser",
            "CONF_LOAD_DASHBOARD_CARDS": "load_dashboard_cards",
            "CARD_CACHE_URL": "/wiser/cards", "_LOGGER": Mock(),
            "get_manifest": lambda hass: self.manifest,
            "async_card_resource": self.resolve,
        }
        tree = ast.parse((FRONTEND / "__init__.py").read_text())
        nodes = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in {"JSModuleRegistration", "dashboard_cards_enabled"}]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(FRONTEND / "__init__.py"), "exec"), namespace)
        self.enabled = namespace["dashboard_cards_enabled"]
        self.registration = namespace["JSModuleRegistration"](self.hass)
        self.registration.async_remove_gzip_files = AsyncMock()

    def test_defaults_enabled_and_any_enabled_hub_keeps_shared_cards(self):
        self.assertTrue(self.enabled(self.hass))
        self.entries[0].options["load_dashboard_cards"] = False
        self.assertFalse(self.enabled(self.hass))
        self.entries.append(SimpleNamespace(entry_id="other", disabled_by=None, options={}))
        self.hass.data["wiser"]["other"] = {}
        self.assertTrue(self.enabled(self.hass))
        self.entries[1].options["load_dashboard_cards"] = False
        self.assertFalse(self.enabled(self.hass))

    async def test_opt_out_removes_current_cached_and_legacy_cards_only(self):
        self.entries[0].options["load_dashboard_cards"] = False
        await self.registration._async_register_modules()
        self.assertEqual({item["id"] for item in self.items}, {"panel", "custom", "other"})
        self.resolve.assert_not_awaited()
        self.resources.async_create_item.assert_not_awaited()
        self.resources.async_update_item.assert_not_awaited()
        # Restart/update registration must continue to honour the saved opt-out.
        await self.registration._async_register_modules()
        self.assertEqual(self.resources.async_delete_item.await_count, 3)
        self.resolve.assert_not_awaited()

    async def test_reenabling_restores_cards_and_preserves_panel_resources(self):
        self.entries[0].options["load_dashboard_cards"] = False
        await self.registration._async_register_modules()
        self.entries[0].options["load_dashboard_cards"] = True
        await self.registration._async_register_modules()
        urls = {item["url"] for item in self.items}
        self.assertIn("/wiser/wiser-controls-card.js?v=new", urls)
        self.assertIn("/wiser/wiser-schedule-card.js?v=new", urls)
        self.assertIn("/wiser/wiser-hub-panel.js?v=old", urls)
        self.assertEqual(self.resources.async_create_item.await_count, 2)
        self.assertEqual(self.resolve.await_count, 2)

    async def test_another_enabled_hub_prevents_unregistration(self):
        self.entries[0].options["load_dashboard_cards"] = False
        self.entries.append(SimpleNamespace(entry_id="other", disabled_by=None, options={"load_dashboard_cards": True}))
        self.hass.data["wiser"]["other"] = {}
        await self.registration._async_register_modules()
        self.assertEqual(self.resolve.await_count, 2)
        # Only a duplicate controls resource is removed during normal registration.
        self.assertEqual(self.resources.async_delete_item.await_count, 1)
        self.assertIn("schedule", {item["id"] for item in self.items})


    async def test_ignored_discoveries_do_not_override_saved_opt_out(self):
        self.entries[0].options["load_dashboard_cards"] = False
        self.entries.extend([
            SimpleNamespace(entry_id="ignored-1", source="ignore", disabled_by=None, options={}),
            SimpleNamespace(entry_id="ignored-2", source="ignore", disabled_by=None, options={}),
        ])
        self.assertFalse(self.enabled(self.hass))
        await self.registration._async_register_modules()
        self.assertEqual({item["id"] for item in self.items}, {"panel", "custom", "other"})
        self.resolve.assert_not_awaited()

    def test_unloaded_and_disabled_hubs_do_not_override_saved_opt_out(self):
        self.entries[0].options["load_dashboard_cards"] = False
        self.entries.extend([
            SimpleNamespace(entry_id="unloaded", disabled_by=None, options={}),
            SimpleNamespace(entry_id="disabled", disabled_by="user", options={}),
        ])
        self.hass.data["wiser"]["disabled"] = {}
        self.assertFalse(self.enabled(self.hass))
