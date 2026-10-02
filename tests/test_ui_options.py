"""Exercise UI options and migrations without requiring a running HA instance."""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

COMPONENT = Path(__file__).parents[1] / "custom_components/wiser"


def load_functions(filename, names, namespace):
    """Execute actual flow/migration methods with minimal HA dependencies."""
    tree = ast.parse((COMPONENT / filename).read_text())
    functions = [
        node for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in names
    ]
    for node in functions:
        node.decorator_list = []
    module = ast.Module(
        body=[
            ast.ImportFrom(
                module="__future__",
                names=[ast.alias(name="annotations")],
                level=0,
            ),
            *functions,
        ],
        type_ignores=[],
    )
    ast.fix_missing_locations(module)
    exec(compile(module, filename, "exec", dont_inherit=True), namespace)
    return SimpleNamespace(**namespace)


class UIOptionsTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.namespace = {
            "CONF_LEGACY_NAMING": "legacy_naming",
            "CONF_EQUIPMENT_SENSORS": "equipment_sensors",
            "CONF_SHOW_WISER_SIDEBAR": "show_wiser_sidebar",
            "CONF_NAME": "name",
            "DATA": "data",
            "DOMAIN": "wiser",
            "HomeAssistant": object,
            "ConfigEntry": object,
            "FlowResult": dict,
            "Any": object,
            "_LOGGER": logging.getLogger(__name__),
            "validate_input": AsyncMock(return_value={"title": "Wiser", "unique_id": "1"}),
            "MAJOR_VERSION": 2026,
            "MINOR_VERSION": 8,
        }

    async def test_new_manual_and_discovered_install_defaults(self):
        for method in ("async_step_user", "async_step_zeroconf_confirm"):
            for version, expected in (((2025, 12), True), ((2026, 7), True),
                                      ((2026, 8), False), ((2026, 9), False),
                                      ((2027, 1), False)):
                with self.subTest(method=method, version=version):
                    self.namespace.update(MAJOR_VERSION=version[0], MINOR_VERSION=version[1])
                    functions = load_functions("config_flow.py", {method}, self.namespace)
                    flow = SimpleNamespace(
                        hass=object(), async_set_unique_id=AsyncMock(),
                        _abort_if_unique_id_configured=Mock(),
                        async_create_entry=lambda **kwargs: kwargs,
                    )
                    result = await getattr(functions, method)(flow, {"host": "test"})
                    self.assertEqual(result["options"], {"legacy_naming": expected})

    async def test_migration_enables_legacy_and_preserves_other_options(self):
        functions = load_functions("__init__.py", {"async_migrate_entry"}, self.namespace)
        for options, expected in (({"scan_interval": 30}, True),
                                  ({"legacy_naming": False}, False)):
            entry = SimpleNamespace(version=1, minor_version=4, options=options)
            update = Mock()
            hass = SimpleNamespace(config_entries=SimpleNamespace(async_update_entry=update))
            self.assertTrue(await functions.async_migrate_entry(hass, entry))
            saved = update.call_args.kwargs
            self.assertEqual(
                saved["options"],
                options | {"legacy_naming": expected},
            )
            self.assertEqual(saved["minor_version"], 5)

    async def test_menu_available_without_opentherm(self):
        functions = load_functions("config_flow.py", {"async_step_init"}, self.namespace)
        flow = SimpleNamespace(
            _opentherm=lambda: None,
            _equipment_available=lambda: False,
            async_show_menu=lambda **kw: kw,
        )
        result = await functions.async_step_init(flow)
        self.assertIn("ui_options", result["menu_options"])
        self.assertNotIn("equipment_sensors", result["menu_options"])

    async def test_equipment_menu_is_below_opentherm(self):
        functions = load_functions(
            "config_flow.py", {"async_step_init"}, self.namespace
        )
        flow = SimpleNamespace(
            _opentherm=lambda: object(),
            _equipment_available=lambda: True,
            async_show_menu=lambda **kw: kw,
        )
        result = await functions.async_step_init(flow)
        self.assertLess(
            result["menu_options"].index("opentherm_sensors"),
            result["menu_options"].index("equipment_sensors"),
        )

    async def test_equipment_menu_does_not_require_opentherm(self):
        functions = load_functions(
            "config_flow.py", {"async_step_init"}, self.namespace
        )
        flow = SimpleNamespace(
            _opentherm=lambda: None,
            _equipment_available=lambda: True,
            async_show_menu=lambda **kw: kw,
        )
        result = await functions.async_step_init(flow)
        self.assertIn("equipment_sensors", result["menu_options"])
        self.assertNotIn("opentherm_sensors", result["menu_options"])

    def test_equipment_menu_requires_a_compatible_device(self):
        functions = load_functions(
            "config_flow.py", {"_equipment_available"}, self.namespace
        )

        def flow_with_devices(*, smartplugs=(), power_tags=(), actuators=()):
            devices = SimpleNamespace(
                smartplugs=SimpleNamespace(all=smartplugs),
                power_tags=SimpleNamespace(all=power_tags),
                heating_actuators=SimpleNamespace(all=actuators),
            )
            return SimpleNamespace(
                config_entry=SimpleNamespace(entry_id="entry"),
                hass=SimpleNamespace(
                    data={
                        "wiser": {
                            "entry": {
                                "data": SimpleNamespace(
                                    wiserhub=SimpleNamespace(devices=devices)
                                )
                            }
                        }
                    }
                ),
            )

        self.assertFalse(functions._equipment_available(flow_with_devices()))
        self.assertTrue(
            functions._equipment_available(
                flow_with_devices(
                    power_tags=(SimpleNamespace(equipment=object()),)
                )
            )
        )

    async def test_equipment_option_defaults_off_and_preserves_options(self):
        self.namespace.update(
            vol=SimpleNamespace(
                Optional=lambda key, default: (key, default),
                Schema=lambda data: data,
            ),
            BooleanSelector=lambda: bool,
        )
        functions = load_functions(
            "config_flow.py", {"async_step_equipment_sensors"}, self.namespace
        )
        flow = SimpleNamespace(
            _equipment_available=lambda: True,
            config_entry=SimpleNamespace(options={"scan_interval": 30}),
            async_show_form=lambda **kwargs: kwargs,
            async_create_entry=lambda **kwargs: kwargs,
        )
        form = await functions.async_step_equipment_sensors(flow)
        self.assertIn(("equipment_sensors", False), form["data_schema"])

        saved = await functions.async_step_equipment_sensors(
            flow, {"equipment_sensors": True}
        )
        self.assertEqual(
            saved["data"],
            {"scan_interval": 30, "equipment_sensors": True},
        )

    async def test_saving_ui_options_preserves_other_options(self):
        functions = load_functions("config_flow.py", {"async_step_ui_options"}, self.namespace)
        for enabled in (False, True):
            flow = SimpleNamespace(
                config_entry=SimpleNamespace(options={"scan_interval": 30}),
                async_create_entry=lambda **kwargs: kwargs,
            )
            preferences = {
                "legacy_naming": enabled,
                "show_wiser_sidebar": enabled,
            }
            result = await functions.async_step_ui_options(flow, preferences)
            self.assertEqual(result["data"], {"scan_interval": 30} | preferences)

    async def test_form_uses_saved_preference(self):
        self.namespace.update(
            vol=SimpleNamespace(Optional=lambda key, default: (key, default), Schema=lambda data: data),
            BooleanSelector=lambda: bool,
        )
        functions = load_functions("config_flow.py", {"async_step_ui_options"}, self.namespace)
        for enabled in (False, True):
            flow = SimpleNamespace(
                config_entry=SimpleNamespace(options={
                    "legacy_naming": enabled,
                    **({} if enabled else {"show_wiser_sidebar": False}),
                }),
                async_show_form=lambda **kwargs: kwargs,
            )
            result = await functions.async_step_ui_options(flow)
            self.assertIn(("legacy_naming", enabled), result["data_schema"])
            self.assertIn(("show_wiser_sidebar", enabled), result["data_schema"])
