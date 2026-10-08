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


def function_call_lines(filename, function_name):
    """Return call names and line numbers from a function's syntax tree."""
    source = (COMPONENT / filename).read_text()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        # The local test runner can be older than the integration's supported
        # Python version. Platform setup precedes the entity classes, so parse
        # only that section when later syntax is unsupported by the runner.
        tree = ast.parse(source.partition("\nclass ")[0])
    function = next(
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == function_name
    )
    calls = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            calls.append((node.func.id, node.lineno))
        elif isinstance(node.func, ast.Attribute):
            calls.append((node.func.attr, node.lineno))
    return calls


class UIOptionsTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.namespace = {
            "CONF_LEGACY_NAMING": "legacy_naming",
            "CONF_EQUIPMENT_SENSORS": "equipment_sensors",
            "CONF_OPENTHERM_EVER_CONNECTED": "opentherm_ever_connected",
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

    def test_opentherm_detection_uses_live_or_remembered_connection(self):
        functions = load_functions(
            "opentherm_detection.py", {"opentherm_is_detected"}, self.namespace
        )
        disconnected = SimpleNamespace(
            enabled=True, connection_status="Disconnected"
        )
        connected = SimpleNamespace(enabled=True, connection_status="Connected")

        self.assertFalse(
            functions.opentherm_is_detected(
                SimpleNamespace(data={}), disconnected
            )
        )
        self.assertTrue(
            functions.opentherm_is_detected(SimpleNamespace(data={}), connected)
        )
        self.assertTrue(
            functions.opentherm_is_detected(
                SimpleNamespace(data={"opentherm_ever_connected": True}),
                disconnected,
            )
        )
        self.assertFalse(
            functions.opentherm_is_detected(SimpleNamespace(data={}), None)
        )

    def test_first_opentherm_connection_is_remembered_once(self):
        sync_registry = Mock()
        self.namespace["_sync_opentherm_entity_registry"] = sync_registry
        functions = load_functions(
            "__init__.py", {"_remember_opentherm_connection"}, self.namespace
        )
        update = Mock()
        hass = SimpleNamespace(
            config_entries=SimpleNamespace(async_update_entry=update)
        )
        entry = SimpleNamespace(data={"host": "wiser.local"})
        opentherm = SimpleNamespace(
            enabled=True, connection_status="Disconnected"
        )
        coordinator = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(opentherm=opentherm)
            )
        )

        functions._remember_opentherm_connection(hass, entry, coordinator)
        update.assert_not_called()
        sync_registry.assert_called_once_with(
            hass, entry, coordinator, detected=False
        )

        sync_registry.reset_mock()
        functions._remember_opentherm_connection(hass, entry, coordinator)
        update.assert_not_called()
        sync_registry.assert_not_called()

        opentherm.connection_status = "Connected"
        functions._remember_opentherm_connection(hass, entry, coordinator)
        update.assert_called_once_with(
            entry,
            data={"host": "wiser.local", "opentherm_ever_connected": True},
        )
        sync_registry.assert_called_once_with(
            hass, entry, coordinator, detected=True
        )

        update.reset_mock()
        sync_registry.reset_mock()
        entry.data = {"host": "wiser.local", "opentherm_ever_connected": True}
        opentherm.connection_status = "Disconnected"
        functions._remember_opentherm_connection(hass, entry, coordinator)
        update.assert_not_called()
        sync_registry.assert_not_called()

    def test_disabling_opentherm_clears_remembered_connection(self):
        sync_registry = Mock()
        self.namespace["_sync_opentherm_entity_registry"] = sync_registry
        functions = load_functions(
            "__init__.py", {"_remember_opentherm_connection"}, self.namespace
        )
        update = Mock()
        hass = SimpleNamespace(
            config_entries=SimpleNamespace(async_update_entry=update)
        )
        entry = SimpleNamespace(
            data={
                "host": "wiser.local",
                "opentherm_ever_connected": True,
            }
        )
        coordinator = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(
                    opentherm=SimpleNamespace(
                        enabled=False,
                        connection_status="Disconnected",
                    )
                )
            )
        )

        functions._remember_opentherm_connection(hass, entry, coordinator)

        update.assert_called_once_with(
            entry,
            data={"host": "wiser.local"},
        )
        sync_registry.assert_called_once_with(
            hass, entry, coordinator, detected=False
        )

    def test_opentherm_registry_entries_are_disabled_without_detection(self):
        integration = "integration"
        registry = SimpleNamespace(async_update_entity=Mock())
        entries = [
            SimpleNamespace(
                domain="sensor",
                unique_id="flow",
                entity_id="sensor.boiler_flow_temperature",
                disabled_by=None,
            ),
            SimpleNamespace(
                domain="sensor",
                unique_id="return",
                entity_id="sensor.boiler_return_temperature",
                disabled_by="user",
            ),
            SimpleNamespace(
                domain="sensor",
                unique_id="cloud",
                entity_id="sensor.cloud",
                disabled_by=None,
            ),
        ]
        fake_er = SimpleNamespace(
            RegistryEntryDisabler=SimpleNamespace(INTEGRATION=integration),
            async_get=lambda _hass: registry,
            async_entries_for_config_entry=lambda _registry, _entry_id: entries,
        )
        self.namespace.update(
            er=fake_er,
            opentherm_entity_unique_ids=lambda _data: {
                ("sensor", "flow"),
                ("sensor", "return"),
            },
            opentherm_is_detected=lambda entry, opentherm: bool(
                entry.data.get("opentherm_ever_connected")
                or opentherm.connection_status == "Connected"
            ),
        )
        functions = load_functions(
            "__init__.py", {"_sync_opentherm_entity_registry"}, self.namespace
        )
        config_entry = SimpleNamespace(entry_id="entry", data={})
        coordinator = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(
                    opentherm=SimpleNamespace(connection_status="Disconnected")
                )
            )
        )

        functions._sync_opentherm_entity_registry(
            object(), config_entry, coordinator
        )
        registry.async_update_entity.assert_called_once_with(
            "sensor.boiler_flow_temperature", disabled_by=integration
        )

        registry.async_update_entity.reset_mock()
        entries[0].disabled_by = integration
        config_entry.data["opentherm_ever_connected"] = True
        functions._sync_opentherm_entity_registry(
            object(), config_entry, coordinator
        )
        registry.async_update_entity.assert_called_once_with(
            "sensor.boiler_flow_temperature", disabled_by=None
        )

    def test_options_hide_opentherm_until_detected(self):
        detection = load_functions(
            "opentherm_detection.py", {"opentherm_is_detected"}, self.namespace
        )
        self.namespace["opentherm_is_detected"] = detection.opentherm_is_detected
        self.namespace.update(DATA="data", DOMAIN="wiser")
        functions = load_functions("config_flow.py", {"_opentherm"}, self.namespace)
        opentherm = SimpleNamespace(
            enabled=True, connection_status="Disconnected"
        )
        coordinator = SimpleNamespace(
            wiserhub=SimpleNamespace(system=SimpleNamespace(opentherm=opentherm))
        )
        flow = SimpleNamespace(
            config_entry=SimpleNamespace(entry_id="entry", data={}),
            hass=SimpleNamespace(data={"wiser": {"entry": {"data": coordinator}}}),
        )

        self.assertIsNone(functions._opentherm(flow))
        flow.config_entry.data["opentherm_ever_connected"] = True
        self.assertIs(functions._opentherm(flow), opentherm)

    def test_sensor_setup_requires_detected_opentherm(self):
        for filename in ("sensor.py", "binary_sensor.py"):
            with self.subTest(filename=filename):
                calls = function_call_lines(filename, "async_setup_entry")
                self.assertIn("opentherm_is_detected", {name for name, _ in calls})

    def test_detection_precedes_listener_and_reload_snapshot(self):
        calls = function_call_lines("__init__.py", "async_setup_entry")
        call_lines = {name: line for name, line in calls}

        self.assertLess(
            call_lines["_remember_opentherm_connection"],
            call_lines["add_update_listener"],
        )
        self.assertLess(
            call_lines["add_update_listener"],
            call_lines["integration_reload_settings"],
        )

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
            config_entry=SimpleNamespace(options={}),
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
            config_entry=SimpleNamespace(options={}),
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
            config_entry=SimpleNamespace(options={}),
            async_show_menu=lambda **kw: kw,
        )
        result = await functions.async_step_init(flow)
        self.assertIn("equipment_sensors", result["menu_options"])
        self.assertNotIn("opentherm_sensors", result["menu_options"])

    async def test_enabled_equipment_option_remains_available_during_data_gap(self):
        self.namespace.update(
            vol=SimpleNamespace(
                Optional=lambda key, default: (key, default),
                Schema=lambda data: data,
            ),
            BooleanSelector=lambda: bool,
        )
        functions = load_functions(
            "config_flow.py",
            {"async_step_init", "async_step_equipment_sensors"},
            self.namespace,
        )
        flow = SimpleNamespace(
            _opentherm=lambda: None,
            _equipment_available=lambda: False,
            config_entry=SimpleNamespace(options={"equipment_sensors": True}),
            async_show_menu=lambda **kwargs: kwargs,
            async_show_form=lambda **kwargs: kwargs,
            async_create_entry=lambda **kwargs: kwargs,
        )

        menu = await functions.async_step_init(flow)
        self.assertIn("equipment_sensors", menu["menu_options"])

        form = await functions.async_step_equipment_sensors(flow)
        self.assertIn(("equipment_sensors", True), form["data_schema"])

        saved = await functions.async_step_equipment_sensors(
            flow, {"equipment_sensors": False}
        )
        self.assertEqual(saved["data"], {"equipment_sensors": False})

    async def test_unconfigured_equipment_option_aborts_without_data(self):
        functions = load_functions(
            "config_flow.py", {"async_step_equipment_sensors"}, self.namespace
        )
        flow = SimpleNamespace(
            _equipment_available=lambda: False,
            config_entry=SimpleNamespace(options={}),
            async_abort=lambda **kwargs: kwargs,
        )

        result = await functions.async_step_equipment_sensors(flow)
        self.assertEqual(result["reason"], "equipment_not_available")

    def test_equipment_menu_requires_a_compatible_device(self):
        functions = load_functions(
            "config_flow.py", {"_equipment_available"}, self.namespace
        )

        def flow_with_devices(
            *, smartplugs=(), power_tags=(), power_tags_c=(), actuators=()
        ):
            devices = SimpleNamespace(
                smartplugs=SimpleNamespace(all=smartplugs),
                power_tags=SimpleNamespace(all=power_tags),
                power_tags_c=SimpleNamespace(all=power_tags_c),
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
        self.assertFalse(
            functions._equipment_available(
                flow_with_devices(
                    smartplugs=(SimpleNamespace(equipment=None),),
                    actuators=(SimpleNamespace(equipment=None),),
                )
            )
        )
        self.assertTrue(
            functions._equipment_available(
                flow_with_devices(
                    power_tags_c=(SimpleNamespace(equipment=object()),)
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
