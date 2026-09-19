"""Test sidebar panel lifecycle without Home Assistant runtime dependencies."""

import importlib
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch


ROOT = Path(__file__).resolve().parents[1] / "custom_components/wiser"


class SchedulesSidebarTest(unittest.IsolatedAsyncioTestCase):
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
        constants.CONF_SHOW_SCHEDULES_SIDEBAR = "show_schedules_sidebar"
        constants.CONF_SCHEDULES_PANEL_CONFIG = "schedules_panel_config"
        constants.CONF_ZIGBEE_PANEL_CONFIG = "zigbee_panel_config"
        constants.CONF_SHOW_ZIGBEE_SIDEBAR = "show_zigbee_sidebar"
        version_module = ModuleType("sidebar_test.frontend.schedule_version")
        self.version_reader = Mock(return_value="4.5.6-beta.2")
        version_module.card_version = self.version_reader
        version_module.__path__ = [str(ROOT / "frontend")]
        constants.DATA = "data"
        constants.DOMAIN = "wiser"
        constants.URL_BASE = "/wiser"
        constants.JSMODULES = [
            {"filename": "wiser-schedule-card.js"}
        ]
        with patch.dict(sys.modules, {
            "homeassistant": ModuleType("homeassistant"),
            "homeassistant.components": components,
            "sidebar_test": ModuleType("sidebar_test"),
            "sidebar_test.frontend": version_module,
            "sidebar_test.const": constants,
        }):
            self.zigbee = importlib.import_module("sidebar_test.frontend.zigbee_sidebar")
            self.update_zigbee = AsyncMock(wraps=self.zigbee.async_update_zigbee_panel)
            self.zigbee.async_update_zigbee_panel = self.update_zigbee
            self.sidebar = importlib.import_module("sidebar_test.frontend.schedules_sidebar")
            self.entry_updates = importlib.import_module("sidebar_test.frontend.entry_updates")
        self.entries = []
        self.hass = SimpleNamespace(
            data={"wiser": {}},
            async_add_executor_job=AsyncMock(side_effect=lambda fn, *args: fn(*args)),
            config_entries=SimpleNamespace(async_entries=lambda _: self.entries),
        )

    def add_hub(self, name, enabled=None, loaded=True, disabled=False):
        entry = SimpleNamespace(
            entry_id=name, disabled_by=disabled, data={"host": "hub.local"},
            options={} if enabled is None else {"show_schedules_sidebar": enabled},
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
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.custom.async_register_panel.assert_not_called()
        self.frontend.async_remove_panel.assert_not_called()

    async def test_enable_registers_dedicated_panel_once(self):
        self.add_hub("hub", True)
        await self.sidebar.async_update_schedules_panel(self.hass)
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.custom.async_register_panel.assert_awaited_once()
        args = self.custom.async_register_panel.call_args.kwargs
        self.assertEqual(args["frontend_url_path"], "wiser-schedules")
        self.assertEqual(args["webcomponent_name"], "wiser-schedules-panel")
        self.assertEqual(args["config"]["hubs"], ["hub"])
        self.assertEqual(args["config"]["card_url"], "/wiser/wiser-schedule-card.js?v=4.5.6-beta.2")

    async def test_disable_last_hub_removes_panel(self):
        entry = self.add_hub("hub", True)
        await self.sidebar.async_update_schedules_panel(self.hass)
        entry.options["show_schedules_sidebar"] = False
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.frontend.async_remove_panel.assert_called_once_with(self.hass, "wiser-schedules")
        self.assertNotIn(self.sidebar.PANEL_STATE, self.hass.data)

    async def test_unload_keeps_other_hub_then_removes_last(self):
        self.add_hub("first", True)
        self.add_hub("second", True)
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.hass.data["wiser"].pop("first")
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.assertEqual(
            self.frontend.async_register_built_in_panel.call_args.kwargs["config"]["hubs"],
            ["second"],
        )
        self.hass.data["wiser"].pop("second")
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.assertNotIn(self.sidebar.PANEL_STATE, self.hass.data)

    async def test_registration_failure_can_be_retried(self):
        self.add_hub("hub", True)
        self.custom.async_register_panel.side_effect = ValueError("registration failed")
        with self.assertRaises(ValueError):
            await self.sidebar.async_update_schedules_panel(self.hass)
        self.assertNotIn(self.sidebar.PANEL_STATE, self.hass.data)
        self.custom.async_register_panel.side_effect = None
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.assertEqual(self.hass.data[self.sidebar.PANEL_STATE]["hubs"], ["hub"])

    async def test_saved_config_is_sent_to_panel(self):
        entry = self.add_hub("hub", True)
        entry.options["schedules_panel_config"] = {"hide_hw_schedule": True}
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.assertEqual(
            self.custom.async_register_panel.call_args.kwargs["config"]["card_configs"],
            {"hub": {"hide_hw_schedule": True}},
        )

    def test_save_preserves_other_options(self):
        entry = self.add_hub("hub", True)
        entry.options["scan_interval"] = 30
        self.hass.config_entries.async_update_entry = Mock()
        self.sidebar.save_schedules_panel_config(self.hass, {
            "hub": {"type": "custom:wiser-schedule-card", "hub": "hub", "hide_hw_schedule": True},
        })
        options = self.hass.config_entries.async_update_entry.call_args.kwargs["options"]
        self.assertEqual(options["scan_interval"], 30)
        self.assertTrue(options["show_schedules_sidebar"])
        self.assertEqual(options["schedules_panel_config"], {"hide_hw_schedule": True})

    def test_invalid_settings_do_not_partially_save(self):
        self.add_hub("first", True)
        self.add_hub("second", True)
        self.hass.config_entries.async_update_entry = Mock()
        with self.assertRaises(ValueError):
            self.sidebar.save_schedules_panel_config(self.hass, {
                "first": {"name": "Valid"}, "second": {"hide_hw_schedule": "invalid"},
            })
        self.hass.config_entries.async_update_entry.assert_not_called()

    def test_current_external_card_editor_options_are_supported(self):
        self.add_hub("hub", True)
        self.hass.config_entries.async_update_entry = Mock()
        settings = {"home_screen": "overview", "overview_details": True, "hide_card_background": True}
        self.sidebar.save_schedules_panel_config(self.hass, {"hub": settings})
        self.assertEqual(
            self.hass.config_entries.async_update_entry.call_args.kwargs["options"]["schedules_panel_config"],
            settings,
        )

    async def test_save_updates_panel_without_removing_route_or_reloading(self):
        entry = self.add_hub("hub", True)
        loaded = self.hass.data["wiser"]["hub"]
        loaded["reload_settings"] = self.entry_updates.integration_reload_settings(entry)
        self.hass.config_entries.async_reload = AsyncMock()
        await self.sidebar.async_update_schedules_panel(self.hass)
        entry.options = {**entry.options, "schedules_panel_config": {"home_screen": "overview"}}
        await self.entry_updates.async_handle_entry_update(self.hass, entry)
        self.hass.config_entries.async_reload.assert_not_called()
        self.frontend.async_remove_panel.assert_not_called()
        self.frontend.async_register_built_in_panel.assert_called_once()
        update = self.frontend.async_register_built_in_panel.call_args.kwargs
        self.assertTrue(update["update"])
        self.assertEqual(update["frontend_url_path"], "wiser-schedules")
        self.assertEqual(update["config"]["card_configs"]["hub"], {"home_screen": "overview"})

    async def test_other_options_and_connection_changes_still_reload(self):
        entry = self.add_hub("hub", True)
        self.hass.data["wiser"]["hub"]["reload_settings"] = self.entry_updates.integration_reload_settings(entry)
        self.hass.config_entries.async_reload = AsyncMock()
        entry.options = {**entry.options, "scan_interval": 60}
        await self.entry_updates.async_handle_entry_update(self.hass, entry)
        self.hass.config_entries.async_reload.assert_awaited_once_with("hub")
        self.hass.config_entries.async_reload.reset_mock()
        entry.options.pop("scan_interval")
        entry.data = {"host": "other.local"}
        await self.entry_updates.async_handle_entry_update(self.hass, entry)
        self.hass.config_entries.async_reload.assert_awaited_once_with("hub")

    async def test_new_bundle_updates_panel_version(self):
        self.add_hub("hub", True)
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.version_reader.return_value = "4.5.6-beta.3"
        await self.sidebar.async_update_schedules_panel(self.hass)
        config = self.frontend.async_register_built_in_panel.call_args.kwargs["config"]
        self.assertEqual(config["card_url"], "/wiser/wiser-schedule-card.js?v=4.5.6-beta.3")
        self.assertEqual(config["_panel_custom"]["module_url"], config["card_url"])

    async def test_zigbee_preferences_update_both_panels_without_reload(self):
        entry = self.add_hub("hub", True)
        self.hass.data["wiser"]["hub"]["reload_settings"] = self.entry_updates.integration_reload_settings(entry)
        self.hass.config_entries.async_reload = AsyncMock()
        entry.options["zigbee_panel_config"] = {"show_labels": True}
        await self.entry_updates.async_handle_entry_update(self.hass, entry)
        self.update_zigbee.assert_awaited_once_with(self.hass)
        self.hass.config_entries.async_reload.assert_not_called()

    async def test_panel_preferences_remain_independent_during_live_updates(self):
        entry = self.add_hub("hub", True)
        entry.options["show_zigbee_sidebar"] = True
        self.hass.data["wiser"]["hub"]["reload_settings"] = self.entry_updates.integration_reload_settings(entry)
        self.hass.config_entries.async_reload = AsyncMock()
        await self.entry_updates.async_handle_entry_update(self.hass, entry)
        self.assertEqual(self.custom.async_register_panel.await_count, 2)
        entry.options["zigbee_panel_config"] = {"orientation": "pie"}
        await self.entry_updates.async_handle_entry_update(self.hass, entry)
        self.hass.config_entries.async_reload.assert_not_called()
        self.frontend.async_register_built_in_panel.assert_called_once()
        self.assertEqual(
            self.frontend.async_register_built_in_panel.call_args.kwargs["frontend_url_path"],
            "wiser-zigbee-panel",
        )
        self.assertEqual(self.hass.data[self.sidebar.PANEL_STATE]["card_configs"], {"hub": {}})
        self.assertEqual(
            self.hass.data[self.zigbee.PANEL_STATE]["card_configs"],
            {"hub": {"orientation": "pie"}},
        )

    async def test_disabled_hub_with_same_name_cannot_override_settings(self):
        enabled = self.add_hub("enabled", True)
        enabled.options["schedules_panel_config"] = {"hide_hw_schedule": True}
        disabled = self.add_hub("disabled", True, disabled=True)
        disabled.options["schedules_panel_config"] = {"hide_hw_schedule": False}
        self.hass.data["wiser"]["disabled"]["data"].wiserhub.system.name = "enabled"
        await self.sidebar.async_update_schedules_panel(self.hass)
        self.assertEqual(
            self.custom.async_register_panel.call_args.kwargs["config"]["card_configs"],
            {"enabled": {"hide_hw_schedule": True}},
        )

    def test_disabled_hub_settings_cannot_be_saved(self):
        self.add_hub("disabled", True, disabled=True)
        self.hass.config_entries.async_update_entry = Mock()
        with self.assertRaises(ValueError):
            self.sidebar.save_schedules_panel_config(
                self.hass, {"disabled": {"hide_hw_schedule": True}}
            )
        self.hass.config_entries.async_update_entry.assert_not_called()
