"""Test sidebar panel lifecycle without Home Assistant runtime dependencies."""

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch


ROOT = Path(__file__).resolve().parents[1] / "custom_components/wiser"


class ZigbeeSidebarTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.frontend = ModuleType("homeassistant.components.frontend")
        self.frontend.async_remove_panel = Mock()
        self.frontend.async_register_built_in_panel = Mock()
        self.custom = ModuleType("homeassistant.components.panel_custom")
        self.custom.async_register_panel = AsyncMock()
        components = ModuleType("homeassistant.components")
        components.frontend = self.frontend
        components.panel_custom = self.custom
        constants = ModuleType("sidebar_test.const")
        constants.CONF_SHOW_ZIGBEE_SIDEBAR = "show_zigbee_sidebar"
        constants.CONF_ZIGBEE_PANEL_CONFIG = "zigbee_panel_config"
        version_module = ModuleType("sidebar_test.frontend.zigbee_version")
        self.version_reader = Mock(return_value="4.5.6-beta.2")
        version_module.card_version = self.version_reader
        constants.DATA = "data"
        constants.DOMAIN = "wiser"
        constants.URL_BASE = "/wiser"
        constants.JSMODULES = [
            {"filename": "wiser-zigbee-card.js"}
        ]
        with patch.dict(sys.modules, {
            "homeassistant": ModuleType("homeassistant"),
            "homeassistant.components": components,
            "sidebar_test": ModuleType("sidebar_test"),
            "sidebar_test.frontend": version_module,
            "sidebar_test.const": constants,
        }):
            spec = importlib.util.spec_from_file_location(
                "sidebar_test.frontend.sidebar", ROOT / "frontend/zigbee_sidebar.py"
            )
            self.sidebar = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.sidebar)
        self.entries = []
        self.hass = SimpleNamespace(
            data={"wiser": {}},
            async_add_executor_job=AsyncMock(side_effect=lambda fn, *args: fn(*args)),
            config_entries=SimpleNamespace(async_entries=lambda _: self.entries),
        )

    def add_hub(self, name, enabled=None, loaded=True, disabled=False):
        entry = SimpleNamespace(
            entry_id=name, disabled_by=disabled, data={"host": "hub.local"},
            options={} if enabled is None else {"show_zigbee_sidebar": enabled},
        )
        self.entries.append(entry)
        if loaded:
            self.hass.data["wiser"][name] = {
                "data": SimpleNamespace(wiserhub=SimpleNamespace(
                    system=SimpleNamespace(name=name)
                ))
            }
        return entry

    async def test_default_disabled_and_unloaded_hubs_do_not_register(self):
        self.add_hub("default")
        self.add_hub("off", False)
        self.add_hub("unloaded", True, loaded=False)
        self.add_hub("disabled", True, disabled=True)
        await self.sidebar.async_update_zigbee_panel(self.hass)
        self.custom.async_register_panel.assert_not_called()
        self.frontend.async_remove_panel.assert_not_called()

    async def test_enable_registers_dedicated_panel_once(self):
        self.add_hub("hub", True)
        await self.sidebar.async_update_zigbee_panel(self.hass)
        await self.sidebar.async_update_zigbee_panel(self.hass)
        self.custom.async_register_panel.assert_awaited_once()
        args = self.custom.async_register_panel.call_args.kwargs
        self.assertEqual(args["frontend_url_path"], "wiser-zigbee")
        self.assertEqual(args["webcomponent_name"], "wiser-zigbee-panel")
        self.assertEqual(args["config"]["hubs"], ["hub"])
        self.assertEqual(args["config"]["card_url"], "/wiser/wiser-zigbee-card.js?v=4.5.6-beta.2")

    async def test_disable_last_hub_removes_panel(self):
        entry = self.add_hub("hub", True)
        await self.sidebar.async_update_zigbee_panel(self.hass)
        entry.options["show_zigbee_sidebar"] = False
        await self.sidebar.async_update_zigbee_panel(self.hass)
        self.frontend.async_remove_panel.assert_called_once_with(self.hass, "wiser-zigbee")
        self.assertNotIn(self.sidebar.PANEL_STATE, self.hass.data)

    async def test_unload_keeps_other_hub_then_removes_last(self):
        self.add_hub("first", True)
        self.add_hub("second", True)
        await self.sidebar.async_update_zigbee_panel(self.hass)
        self.hass.data["wiser"].pop("first")
        await self.sidebar.async_update_zigbee_panel(self.hass)
        self.assertEqual(
            self.frontend.async_register_built_in_panel.call_args.kwargs["config"]["hubs"],
            ["second"],
        )
        self.hass.data["wiser"].pop("second")
        await self.sidebar.async_update_zigbee_panel(self.hass)
        self.assertNotIn(self.sidebar.PANEL_STATE, self.hass.data)

    async def test_registration_failure_can_be_retried(self):
        self.add_hub("hub", True)
        self.custom.async_register_panel.side_effect = ValueError("registration failed")
        with self.assertRaises(ValueError):
            await self.sidebar.async_update_zigbee_panel(self.hass)
        self.assertNotIn(self.sidebar.PANEL_STATE, self.hass.data)
        self.custom.async_register_panel.side_effect = None
        await self.sidebar.async_update_zigbee_panel(self.hass)
        self.assertEqual(self.hass.data[self.sidebar.PANEL_STATE]["hubs"], ["hub"])

    async def test_saved_config_is_sent_to_panel(self):
        entry = self.add_hub("hub", True)
        entry.options["zigbee_panel_config"] = {"show_labels": True}
        await self.sidebar.async_update_zigbee_panel(self.hass)
        self.assertEqual(
            self.custom.async_register_panel.call_args.kwargs["config"]["card_configs"],
            {"hub": {"show_labels": True}},
        )

    def test_save_preserves_other_options(self):
        entry = self.add_hub("hub", True)
        entry.options["scan_interval"] = 30
        self.hass.config_entries.async_update_entry = Mock()
        self.sidebar.save_zigbee_panel_config(self.hass, {
            "hub": {"type": "custom:wiser-zigbee-card", "hub": "hub", "show_labels": True},
        })
        options = self.hass.config_entries.async_update_entry.call_args.kwargs["options"]
        self.assertEqual(options["scan_interval"], 30)
        self.assertTrue(options["show_zigbee_sidebar"])
        self.assertEqual(options["zigbee_panel_config"], {"show_labels": True})

    def test_invalid_settings_do_not_partially_save(self):
        self.add_hub("first", True)
        self.add_hub("second", True)
        self.hass.config_entries.async_update_entry = Mock()
        with self.assertRaises(ValueError):
            self.sidebar.save_zigbee_panel_config(self.hass, {
                "first": {"name": "Valid"}, "second": {"show_labels": "invalid"},
            })
        self.hass.config_entries.async_update_entry.assert_not_called()

    def test_current_external_card_editor_options_are_supported(self):
        self.add_hub("hub", True)
        self.hass.config_entries.async_update_entry = Mock()
        settings = {"orientation": "pie", "map_only": True, "show_labels": True, "layout_data": {"1": {"x": 12, "y": -30}}}
        self.sidebar.save_zigbee_panel_config(self.hass, {"hub": settings})
        self.assertEqual(
            self.hass.config_entries.async_update_entry.call_args.kwargs["options"]["zigbee_panel_config"],
            settings,
        )

    def test_invalid_coordinates_and_choices_are_rejected(self):
        self.add_hub("hub", True)
        self.hass.config_entries.async_update_entry = Mock()
        for settings in [
            {"orientation": "diagonal"}, {"link_status": "purple"},
            {"map_height": True}, {"map_height": 99},
            {"layout_data": {"1": {"x": float("nan"), "y": 0}}},
            {"layout_data": {"1": {"x": 0}}},
        ]:
            with self.assertRaises(ValueError):
                self.sidebar.save_zigbee_panel_config(self.hass, {"hub": settings})
        self.hass.config_entries.async_update_entry.assert_not_called()
    async def test_save_updates_panel_without_removing_route_or_reloading(self):
        entry = self.add_hub("hub", True)
        loaded = self.hass.data["wiser"]["hub"]
        loaded["reload_settings"] = self.sidebar.integration_reload_settings(entry)
        self.hass.config_entries.async_reload = AsyncMock()
        await self.sidebar.async_update_zigbee_panel(self.hass)
        entry.options = {**entry.options, "zigbee_panel_config": {"orientation": "pie"}}
        await self.sidebar.async_handle_entry_update(self.hass, entry)
        self.hass.config_entries.async_reload.assert_not_called()
        self.frontend.async_remove_panel.assert_not_called()
        self.frontend.async_register_built_in_panel.assert_called_once()
        update = self.frontend.async_register_built_in_panel.call_args.kwargs
        self.assertTrue(update["update"])
        self.assertEqual(update["frontend_url_path"], "wiser-zigbee")
        self.assertEqual(update["config"]["card_configs"]["hub"], {"orientation": "pie"})

    async def test_other_options_and_connection_changes_still_reload(self):
        entry = self.add_hub("hub", True)
        self.hass.data["wiser"]["hub"]["reload_settings"] = self.sidebar.integration_reload_settings(entry)
        self.hass.config_entries.async_reload = AsyncMock()
        entry.options = {**entry.options, "scan_interval": 60}
        await self.sidebar.async_handle_entry_update(self.hass, entry)
        self.hass.config_entries.async_reload.assert_awaited_once_with("hub")
        self.hass.config_entries.async_reload.reset_mock()
        entry.options.pop("scan_interval")
        entry.data = {"host": "other.local"}
        await self.sidebar.async_handle_entry_update(self.hass, entry)
        self.hass.config_entries.async_reload.assert_awaited_once_with("hub")

    async def test_bundle_version_change_updates_panel_without_settings_change(self):
        self.add_hub("hub", True)
        await self.sidebar.async_update_zigbee_panel(self.hass)
        self.version_reader.assert_called_with(ROOT / "frontend/wiser-zigbee-card.js")
        self.version_reader.return_value = "4.5.6-beta.3"
        await self.sidebar.async_update_zigbee_panel(self.hass)
        update = self.frontend.async_register_built_in_panel.call_args.kwargs
        self.assertEqual(update["config"]["card_url"], "/wiser/wiser-zigbee-card.js?v=4.5.6-beta.3")
        self.assertEqual(update["config"]["_panel_custom"]["module_url"], update["config"]["card_url"])
