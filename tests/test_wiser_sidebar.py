"""Test the shared Wiser sidebar and automatic panel discovery."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch


ROOT = Path(__file__).resolve().parents[1] / "custom_components/wiser"


class WiserSidebarTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        assets = Path(self.temporary.name)
        (assets / "wiser-schedule-card.js").write_text(
            'customElements.define("wiser-schedules-panel", class extends HTMLElement {})'
        )
        (assets / "wiser-zigbee-card.js").write_text(
            'customElements.define("wiser-zigbee-panel", class extends HTMLElement {})'
        )
        (assets / "wiser-rooms-card.js").write_text(
            'customElements.define("wiser-rooms-card", class extends HTMLElement {});'
            'customElements.define("wiser-rooms-panel", class extends HTMLElement {})'
        )

        self.frontend = ModuleType("homeassistant.components.frontend")
        self.frontend.async_remove_panel = Mock()
        self.frontend.async_register_built_in_panel = Mock()
        self.custom = ModuleType("homeassistant.components.panel_custom")
        self.custom.async_register_panel = AsyncMock()
        components = ModuleType("homeassistant.components")
        components.frontend = self.frontend
        components.panel_custom = self.custom

        package = ModuleType("wiser_sidebar_test.frontend")
        package.__path__ = [str(ROOT / "frontend")]
        package.card_version = Mock(return_value="1.0.0")

        async def card_resource(_hass, filename):
            path = assets / filename
            return path, f"/wiser/{filename}?v=1", "1"

        package.async_card_resource = card_resource
        constants = ModuleType("wiser_sidebar_test.const")
        for name, value in {
            "CONF_SHOW_WISER_SIDEBAR": "show_wiser_sidebar",
            "CONF_WISER_PANEL_CONFIG": "wiser_panel_config",
            "DATA": "data",
            "DOMAIN": "wiser",
            "URL_BASE": "/wiser",
        }.items():
            setattr(constants, name, value)
        constants.CARD_MANIFEST = json.loads(
            (Path(__file__).parent / "fixtures/frontend_cards.json").read_text()
        )

        registry = ModuleType("wiser_sidebar_test.frontend.registry")
        registry.get_manifest = lambda hass: constants.CARD_MANIFEST
        self.manifest = constants.CARD_MANIFEST

        with patch.dict(
            sys.modules,
            {
                "homeassistant": ModuleType("homeassistant"),
                "homeassistant.components": components,
                "wiser_sidebar_test": ModuleType("wiser_sidebar_test"),
                "wiser_sidebar_test.frontend": package,
                "wiser_sidebar_test.frontend.registry": registry,
                "wiser_sidebar_test.const": constants,
            },
        ):
            self.sidebar = importlib.import_module(
                "wiser_sidebar_test.frontend.wiser_sidebar"
            )
            self.entry_updates = importlib.import_module(
                "wiser_sidebar_test.frontend.entry_updates"
            )

        self.entries = []
        self.hass = SimpleNamespace(
            data={"wiser": {}},
            async_add_executor_job=AsyncMock(side_effect=lambda fn, *args: fn(*args)),
            config_entries=SimpleNamespace(async_entries=lambda _domain: self.entries),
        )

    def add_hub(self, name, options, loaded=True, disabled=False):
        entry = SimpleNamespace(
            entry_id=name,
            disabled_by=disabled,
            options=dict(options),
        )
        self.entries.append(entry)
        if loaded:
            self.hass.data["wiser"][name] = {
                "data": SimpleNamespace(
                    wiserhub=SimpleNamespace(system=SimpleNamespace(name=name))
                )
            }
        return entry

    async def test_single_option_registers_one_panel_with_discovered_panel_cards(self):
        self.add_hub(
            "hub-one",
            {
                "show_wiser_sidebar": True,
                "wiser_panel_config": {
                    "schedule": {"home_screen": "overview"},
                    "zigbee": {"orientation": "pie"},
                },
            },
        )
        self.add_hub("hub-two", {"show_wiser_sidebar": True})
        await self.sidebar.async_update_wiser_panel(self.hass)

        self.custom.async_register_panel.assert_awaited_once()
        args = self.custom.async_register_panel.call_args.kwargs
        self.assertEqual(args["frontend_url_path"], "wiser-panel")
        self.assertEqual(args["webcomponent_name"], "wiser-panel")
        self.assertEqual(args["sidebar_icon"], "wiser:wiser")
        self.assertEqual(
            [panel["id"] for panel in args["config"]["panels"]],
            ["schedule", "zigbee", "rooms"],
        )
        schedule, zigbee, rooms = args["config"]["panels"]
        self.assertEqual(schedule["default_title"], "Schedules")
        self.assertEqual(rooms["default_title"], "Rooms")
        self.assertEqual(schedule["config"]["hubs"], ["hub-one", "hub-two"])
        self.assertEqual(
            rooms["config"]["hub_ids"],
            {"hub-one": "hub-one", "hub-two": "hub-two"},
        )
        self.assertEqual(
            schedule["config"]["card_configs"]["hub-one"],
            {"home_screen": "overview"},
        )
        self.assertEqual(
            zigbee["config"]["card_configs"]["hub-one"],
            {"orientation": "pie"},
        )

    async def test_panel_route_stays_outside_static_resources_on_register_and_update(self):
        self.add_hub("hub", {})
        await self.sidebar.async_update_wiser_panel(self.hass)
        registered = self.custom.async_register_panel.call_args.kwargs
        route = "/" + registered["frontend_url_path"]
        static_root = self.sidebar.URL_BASE.rstrip("/")
        self.assertNotEqual(route, static_root)
        self.assertFalse(route.startswith(static_root + "/"))
        self.assertTrue(registered["module_url"].startswith(static_root + "/"))

        # Changing enabled hubs refreshes the same UI route, with static URLs intact.
        self.add_hub("another-hub", {})
        await self.sidebar.async_update_wiser_panel(self.hass)
        updated = self.frontend.async_register_built_in_panel.call_args.kwargs
        self.assertEqual(updated["frontend_url_path"], registered["frontend_url_path"])
        self.assertTrue(updated["update"])
        self.assertEqual(
            updated["config"]["_panel_custom"]["module_url"], registered["module_url"]
        )

    async def test_sidebar_is_enabled_by_default(self):
        self.add_hub("hub", {})
        await self.sidebar.async_update_wiser_panel(self.hass)
        self.custom.async_register_panel.assert_awaited_once()

    async def test_saved_tab_order_and_titles_are_applied_to_discovered_panels(self):
        self.add_hub(
            "hub",
            {
                "wiser_panel_config": {
                    "_panel_tabs": [
                        {"id": "rooms", "title": "Heating"},
                        {"id": "schedule", "title": "Programmes"},
                    ]
                }
            },
        )
        await self.sidebar.async_update_wiser_panel(self.hass)

        panels = self.custom.async_register_panel.call_args.kwargs["config"]["panels"]
        self.assertEqual(panels[0]["default_title"], "Rooms")
        self.assertEqual(
            [(panel["id"], panel["title"]) for panel in panels],
            [
                ("rooms", "Heating"),
                ("schedule", "Programmes"),
                ("zigbee", "Zigbee"),
            ],
        )

    async def test_renamed_panel_replaces_stored_legacy_default_title(self):
        rooms = next(card for card in self.manifest if card["id"] == "rooms")
        rooms.update(
            {
                "filename": "wiser-controls-card.js",
                "component": "wiser-controls-card",
                "panel": "wiser-controls-panel",
                "legacy_filenames": ["wiser-rooms-card.js"],
            }
        )
        (Path(self.temporary.name) / "wiser-controls-card.js").write_text(
            'customElements.define("wiser-controls-card", class extends HTMLElement {});'
            'customElements.define("wiser-controls-panel", class extends HTMLElement {})'
        )
        self.add_hub(
            "hub",
            {
                "wiser_panel_config": {
                    "_panel_tabs": [
                        {"id": "rooms", "title": "Rooms"},
                        {"id": "schedule", "title": "Programmes"},
                    ]
                }
            },
        )

        await self.sidebar.async_update_wiser_panel(self.hass)

        panels = self.custom.async_register_panel.call_args.kwargs["config"]["panels"]
        self.assertEqual(panels[0]["default_title"], "Controls")
        self.assertEqual(
            [(panel["id"], panel["title"]) for panel in panels],
            [
                ("rooms", "Controls"),
                ("schedule", "Programmes"),
                ("zigbee", "Zigbee"),
            ],
        )

    async def test_legacy_sidebar_options_do_not_control_unified_panel(self):
        self.add_hub(
            "hub",
            {"show_schedules_sidebar": False, "show_zigbee_sidebar": False},
        )
        await self.sidebar.async_update_wiser_panel(self.hass)
        self.custom.async_register_panel.assert_awaited_once()

    async def test_unified_setting_can_hide_sidebar(self):
        self.add_hub("hub", {"show_wiser_sidebar": False})
        await self.sidebar.async_update_wiser_panel(self.hass)
        self.custom.async_register_panel.assert_not_awaited()

    async def test_no_enabled_hubs_removes_existing_shared_panel(self):
        self.hass.data[self.sidebar.PANEL_STATE] = {"panels": []}
        self.add_hub("hub", {"show_wiser_sidebar": False})
        await self.sidebar.async_update_wiser_panel(self.hass)
        self.frontend.async_remove_panel.assert_called_once_with(self.hass, "wiser-panel")
        self.assertNotIn(self.sidebar.PANEL_STATE, self.hass.data)

    def test_shell_owns_panel_tabs_and_embeds_each_child_panel(self):
        source = (ROOT / "frontend/wiser-panel.js").read_text()
        self.assertIn('id="panel-tabs"', source)
        self.assertIn('sessionStorage.getItem(WISER_ACTIVE_PANEL_KEY)', source)
        self.assertIn('sessionStorage.setItem(WISER_ACTIVE_PANEL_KEY, id)', source)
        self.assertIn('id="settings"', source)
        self.assertIn('src="/wiser/wiser-logo.png"', source)
        self.assertIn('alt="Wiser"', source)
        self.assertNotIn("<h1>Wiser</h1>", source)
        self.assertIn('view.setAttribute("nested", "")', source)
        self.assertIn("panel.module_url", source)
        self.assertLess(
            source.index("view.hass = this._hass"),
            source.index("view.panel = { config: panel.config }"),
        )
        self.assertIn('tab.addEventListener("dragstart"', source)
        self.assertIn('tab.addEventListener("dblclick"', source)
        self.assertIn('type: "wiser/panel/configure_tabs"', source)
        self.assertIn("_mergeTabPreferences(panel.config)", source)
        self.assertIn(
            "input.value.trim() || panel.default_title || panel.title", source
        )

    def test_new_panel_websocket_commands_are_registered(self):
        source = (ROOT / "websockets.py").read_text()
        self.assertIn("async_register_command(hass, websocket_configure_panel)", source)
        self.assertNotIn("websocket_configure_rooms_panel", source)
        self.assertIn(
            "async_register_command(hass, websocket_configure_wiser_panel_tabs)",
            source,
        )

    async def test_new_registry_panel_is_discovered_and_saves_generic_settings(self):
        entry = self.add_hub("hub", {})
        self.manifest.append({
            "id": "new-registry-id",
            "filename": "wiser-energy-card.js", "name": "Wiser Energy Card",
            "panel": "wiser-energy-panel",
        })
        (Path(self.temporary.name) / "wiser-energy-card.js").write_text(
            'customElements.define("wiser-energy-panel", class extends HTMLElement {})'
        )
        await self.sidebar.async_update_wiser_panel(self.hass)
        panels = self.custom.async_register_panel.call_args.kwargs["config"]["panels"]
        self.assertEqual(panels[-1]["id"], "new-registry-id")
        self.assertEqual(panels[-1]["config"]["panel_id"], "new-registry-id")
        self.hass.config_entries.async_update_entry = Mock()
        self.sidebar.save_panel_config(self.hass, "new-registry-id", {"hub": {"columns": 3}})
        self.hass.config_entries.async_update_entry.assert_called_once_with(
            entry, options={"wiser_panel_config": {"new-registry-id": {"columns": 3}}}
        )
        self.sidebar.save_wiser_panel_tabs(self.hass, [{"id": "new-registry-id", "title": "Energy"}])
        self.hass.config_entries.async_update_entry.reset_mock()
        with self.assertRaises(ValueError):
            self.sidebar.save_panel_config(self.hass, "unknown", {"hub": {}})
        self.hass.config_entries.async_update_entry.assert_not_called()

    def test_panel_settings_save_without_standalone_sidebar_modules(self):
        self.add_hub("schedule-hub", {})
        self.add_hub("zigbee-hub", {})
        self.hass.config_entries.async_update_entry = Mock()
        self.sidebar.save_panel_config(
            self.hass, "schedule",
            {"schedule-hub": {"type": "custom:wiser-schedule-card", "home_screen": "overview"}},
        )
        self.sidebar.save_panel_config(
            self.hass, "zigbee",
            {"zigbee-hub": {"hub": "zigbee-hub", "orientation": "pie"}},
        )
        calls = self.hass.config_entries.async_update_entry.call_args_list
        self.assertEqual(
            calls[0].kwargs["options"],
            {"wiser_panel_config": {"schedule": {"home_screen": "overview"}}},
        )
        self.assertEqual(
            calls[1].kwargs["options"],
            {"wiser_panel_config": {"zigbee": {"orientation": "pie"}}},
        )

    async def test_all_panel_settings_apply_without_reloading_integration(self):
        entry = self.add_hub("hub", {"scan_interval": 30})
        entry.data = {"host": "wiser.local"}
        loaded = self.hass.data["wiser"][entry.entry_id]
        loaded["reload_settings"] = self.entry_updates.integration_reload_settings(entry)
        self.hass.config_entries.async_reload = AsyncMock()
        with patch.object(self.entry_updates, "async_update_wiser_panel", AsyncMock()) as refresh:
            for panel_id in ("schedule", "zigbee", "rooms", "future-panel"):
                entry.options["wiser_panel_config"] = {panel_id: {"columns": 3}}
                await self.entry_updates.async_handle_entry_update(self.hass, entry)
            self.assertEqual(refresh.await_count, 4)
            self.hass.config_entries.async_reload.assert_not_awaited()
            entry.options["scan_interval"] = 60
            await self.entry_updates.async_handle_entry_update(self.hass, entry)
            self.hass.config_entries.async_reload.assert_awaited_once_with(entry.entry_id)

    def test_invalid_panel_settings_do_not_partially_save(self):
        self.add_hub("first", {})
        self.add_hub("second", {})
        self.hass.config_entries.async_update_entry = Mock()
        with self.assertRaises(ValueError):
            self.sidebar.save_panel_config(
                self.hass, "schedule",
                {"first": {"home_screen": "overview"}, "second": {"bad": float("nan")}},
            )
        self.hass.config_entries.async_update_entry.assert_not_called()

    def test_rooms_panel_settings_use_generic_registry_and_drop_hub_filter(self):
        entry = self.add_hub(
            "hub",
            {"wiser_panel_config": {"future": {"enabled": True}}},
        )
        self.hass.config_entries.async_update_entry = Mock()
        self.sidebar.save_panel_config(
            self.hass, "rooms",
            {
                "hub": {
                    "type": "custom:wiser-rooms-card",
                    "hubs": ["entry"],
                    "_panel_hide_title": True,
                    "room_columns": 4,
                }
            },
        )
        self.hass.config_entries.async_update_entry.assert_called_once_with(
            entry,
            options={
                "wiser_panel_config": {
                    "future": {"enabled": True},
                    "rooms": {"room_columns": 4},
                }
            },
        )

    def test_panel_tab_layout_is_saved_for_every_enabled_hub(self):
        first = self.add_hub(
            "first",
            {"wiser_panel_config": {"rooms": {"room_columns": 4}}},
        )
        second = self.add_hub("second", {})
        self.hass.config_entries.async_update_entry = Mock()

        tabs = [
            {"id": "rooms", "title": "Heating"},
            {"id": "schedule", "title": "Schedules"},
            {"id": "zigbee", "title": "Devices"},
        ]
        self.sidebar.save_wiser_panel_tabs(self.hass, tabs)

        calls = self.hass.config_entries.async_update_entry.call_args_list
        self.assertEqual([call.args[0] for call in calls], [first, second])
        self.assertEqual(
            calls[0].kwargs["options"]["wiser_panel_config"],
            {
                "rooms": {"room_columns": 4},
                "_panel_tabs": tabs,
            },
        )
        self.assertEqual(
            calls[1].kwargs["options"]["wiser_panel_config"],
            {"_panel_tabs": tabs},
        )

    def test_invalid_or_duplicate_panel_tabs_are_rejected(self):
        self.add_hub("hub", {})
        self.hass.config_entries.async_update_entry = Mock()

        invalid_tabs = [
            {"id": "rooms", "title": "Heating"},
            {"id": "rooms", "title": "Duplicate"},
        ]
        with self.assertRaises(ValueError):
            self.sidebar.save_wiser_panel_tabs(self.hass, invalid_tabs)
        self.hass.config_entries.async_update_entry.assert_not_called()


if __name__ == "__main__":
    unittest.main()
