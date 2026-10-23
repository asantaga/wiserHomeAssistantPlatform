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
            "CONF_ADDITIONAL_SENSORS": "additional_sensors",
            "CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL": (
                "automations_external_room_control"
            ),
            "CONF_AUTOMATIONS_EXTERNAL_PASSIVE": (
                "automations_external_passive_mode"
            ),
            "CONF_AUTOMATIONS_PASSIVE": "automations_passive_mode",
            "CONF_AUTOMATIONS_PASSIVE_TYPE": "passive_type",
            "CONF_CONTROL_STRATEGY": "control_strategy",
            "CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS": (
                "external_room_control_assignments"
            ),
            "CONF_LEGACY_PASSIVE_TEMP_INCREMENT": (
                "passive_mode_temperature_increments"
            ),
            "CONF_TEMPERATURE_INCREMENT": "temperature_increment",
            "CONF_LEGACY_NAMING": "legacy_naming",
            "CONF_EQUIPMENT_SENSORS": "equipment_sensors",
            "CONF_SCHEDULE_SETPOINT_ROOMS": "schedule_setpoint_rooms",
            "CONF_OPENTHERM_EVER_CONNECTED": "opentherm_ever_connected",
            "CONF_OPENTHERM_HOT_WATER_CAPABLE": "opentherm_hot_water_capable",
            "CONF_OPENTHERM_HOT_WATER_CONTROL": "opentherm_hot_water_control",
            "CONF_OPENTHERM_HOT_WATER_SENSOR_ENTITY_ID": "opentherm_hot_water_sensor_entity_id",
            "CONF_SHOW_WISER_SIDEBAR": "show_wiser_sidebar",
            "CONF_NAME": "name",
            "DATA": "data",
            "DOMAIN": "wiser",
            "DEFAULT_PASSIVE_CONTROL_STRATEGY": "modulating",
            "DEFAULT_PASSIVE_TYPE": "internal",
            "PASSIVE_TYPE_EXTERNAL": "external",
            "PASSIVE_TYPE_INTERNAL": "internal",
            "PASSIVE_TYPES": ["internal", "external"],
            "HomeAssistant": object,
            "ConfigEntry": object,
            "FlowResult": dict,
            "Any": object,
            "_LOGGER": logging.getLogger(__name__),
            "validate_input": AsyncMock(return_value={"title": "Wiser", "unique_id": "1"}),
            "MAJOR_VERSION": 2026,
            "MINOR_VERSION": 8,
            "room_has_climate": lambda room: bool(room.devices),
            "room_supports_temperature_control": lambda room: bool(
                room.temperature_control
            ),
        }

    def test_passive_type_constants_are_imported(self):
        tree = ast.parse((COMPONENT / "config_flow.py").read_text())
        const_import = next(
            node
            for node in tree.body
            if isinstance(node, ast.ImportFrom)
            and node.level == 1
            and node.module == "const"
        )
        imported_names = {alias.name for alias in const_import.names}

        self.assertIn("PASSIVE_TYPE_INTERNAL", imported_names)
        self.assertIn("PASSIVE_TYPE_EXTERNAL", imported_names)

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

    def test_writable_hot_water_capability_is_remembered(self):
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
            data={"opentherm_ever_connected": True}
        )
        opentherm = SimpleNamespace(
            enabled=True,
            connection_status="Connected",
            boiler_parameters=SimpleNamespace(hw_setpoint_read_write=True),
        )
        coordinator = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(opentherm=opentherm)
            )
        )

        functions._remember_opentherm_connection(hass, entry, coordinator)

        update.assert_called_once_with(
            entry,
            data={
                "opentherm_ever_connected": True,
                "opentherm_hot_water_capable": True,
            },
        )

    def test_hot_water_support_survives_capability_data_gap(self):
        functions = load_functions(
            "opentherm_detection.py",
            {"opentherm_hot_water_control_is_supported"},
            self.namespace,
        )
        opentherm = SimpleNamespace(boiler_parameters=SimpleNamespace())

        self.assertTrue(
            functions.opentherm_hot_water_control_is_supported(
                SimpleNamespace(
                    data={"opentherm_hot_water_capable": True}, options={}
                ),
                opentherm,
            )
        )
        self.assertTrue(
            functions.opentherm_hot_water_control_is_supported(
                SimpleNamespace(
                    data={}, options={"opentherm_hot_water_control": True}
                ),
                opentherm,
            )
        )

    def test_hot_water_presets_follow_boiler_limits(self):
        self.namespace.update(
            vol=SimpleNamespace(Invalid=ValueError),
            MAX_OPENTHERM_HOT_WATER_PRESETS=10,
            DEFAULT_OPENTHERM_HOT_WATER_PRESET_TEMP=55.0,
            OPENTHERM_HOT_WATER_DEFAULT_BOOSTS=(15, 30, 45),
        )
        functions = load_functions(
            "config_flow.py",
            {
                "_default_opentherm_hot_water_presets",
                "_validate_opentherm_hot_water_presets",
            },
            self.namespace,
        )
        defaults = functions._default_opentherm_hot_water_presets(40, 50)
        self.assertTrue(
            all(preset["temperature"] == 50 for preset in defaults)
        )
        stored = [{
            "name": "Boost",
            "temperature": 55,
            "duration_minutes": 15,
        }]
        with self.assertRaises(ValueError):
            functions._validate_opentherm_hot_water_presets(stored, 40, 50)
        clamped = functions._validate_opentherm_hot_water_presets(
            stored, 40, 50, clamp_temperature=True
        )
        self.assertEqual(clamped[0]["temperature"], 50)

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

    def test_missing_system_preserves_remembered_connection(self):
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
        coordinator = SimpleNamespace(wiserhub=SimpleNamespace(system=None))

        functions._remember_opentherm_connection(hass, entry, coordinator)

        update.assert_not_called()
        sync_registry.assert_not_called()

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

        functions._sync_opentherm_entity_registry(
            object(),
            config_entry,
            SimpleNamespace(wiserhub=SimpleNamespace(system=None)),
        )
        registry.async_update_entity.assert_not_called()

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
            self.assertEqual(saved["minor_version"], 8)

    async def test_migration_preserves_native_passive_settings(self):
        functions = load_functions("__init__.py", {"async_migrate_entry"}, self.namespace)
        options = {
            "automations_passive_mode": {
                "automations_passive_mode": True,
                "passive_mode_temperature_increments": 1.5,
            },
            "automations_external_passive_mode": {"ignored": True},
        }
        entry = SimpleNamespace(version=1, minor_version=5, options=options)
        update = Mock()
        hass = SimpleNamespace(config_entries=SimpleNamespace(async_update_entry=update))

        self.assertTrue(await functions.async_migrate_entry(hass, entry))

        saved = update.call_args.kwargs
        self.assertEqual(
            saved["options"]["automations_passive_mode"],
            {
                "automations_passive_mode": True,
                "passive_type": "internal",
                "temperature_increment": 1.5,
            },
        )
        self.assertNotIn(
            "automations_external_passive_mode", saved["options"]
        )
        self.assertEqual(saved["minor_version"], 8)

    async def test_migration_keeps_original_passive_internal(self):
        functions = load_functions("__init__.py", {"async_migrate_entry"}, self.namespace)
        entry = SimpleNamespace(
            version=1,
            minor_version=6,
            options={
                "automations_passive_mode": {
                    "automations_passive_mode": True,
                    "temperature_increment": 0.5,
                    "control_strategy": "temperature_limiter",
                },
                "automations_external_room_control": {
                    "automations_external_room_control": True,
                },
            },
        )
        update = Mock()
        hass = SimpleNamespace(
            config_entries=SimpleNamespace(async_update_entry=update)
        )

        self.assertTrue(await functions.async_migrate_entry(hass, entry))

        saved = update.call_args.kwargs
        self.assertEqual(
            saved["options"]["automations_passive_mode"],
            {
                "automations_passive_mode": True,
                "passive_type": "internal",
                "temperature_increment": 0.5,
            },
        )
        self.assertNotIn(
            "automations_external_passive_mode", saved["options"]
        )
        self.assertEqual(saved["minor_version"], 8)

    async def test_migration_ignores_experimental_external_passive(self):
        functions = load_functions("__init__.py", {"async_migrate_entry"}, self.namespace)
        entry = SimpleNamespace(
            version=1,
            minor_version=7,
            options={
                "automations_external_passive_mode": {
                    "automations_external_passive_mode": True,
                    "control_strategy": "temperature_limiter",
                },
                "automations_external_room_control": {
                    "automations_external_room_control": True,
                },
            },
        )
        update = Mock()
        hass = SimpleNamespace(
            config_entries=SimpleNamespace(async_update_entry=update)
        )

        self.assertTrue(await functions.async_migrate_entry(hass, entry))

        saved = update.call_args.kwargs
        self.assertNotIn("automations_passive_mode", saved["options"])
        self.assertNotIn(
            "automations_external_passive_mode", saved["options"]
        )
        self.assertEqual(
            saved["options"]["automations_external_room_control"],
            {"automations_external_room_control": True},
        )
        self.assertEqual(saved["minor_version"], 8)

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
        self.assertNotIn("opentherm", result["menu_options"])
        self.assertNotIn("external_room_control_assignments", result["menu_options"])
        self.assertNotIn("equipment_sensors", result["menu_options"])
        self.assertNotIn("additional_sensors", result["menu_options"])

    async def test_additional_sensors_is_section_in_automation_parameters(self):
        source = (COMPONENT / "config_flow.py").read_text()
        tree = ast.parse(source)
        function = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "async_step_automation_params"
        )
        self.assertIn(
            "vol.Required(CONF_ADDITIONAL_SENSORS)", ast.unparse(function)
        )
        self.assertNotIn("async_step_additional_sensors", source)

    def test_room_choices_exclude_rooms_with_climate(self):
        functions = load_functions(
            "config_flow.py", {"_rooms_without_climate"}, self.namespace
        )
        kitchen = SimpleNamespace(id=4, name="Kitchen", devices=[])
        lounge = SimpleNamespace(id=5, name="Lounge", devices=[object()])
        flow = SimpleNamespace(
            hass=SimpleNamespace(
                data={
                    "wiser": {
                        "entry": {
                            "data": SimpleNamespace(
                                wiserhub=SimpleNamespace(
                                    rooms=SimpleNamespace(all=[kitchen, lounge])
                                )
                            )
                        }
                    }
                }
            ),
            config_entry=SimpleNamespace(entry_id="entry"),
        )

        self.assertEqual(functions._rooms_without_climate(flow), [kitchen])

    async def test_additional_sensor_section_preserves_other_options(self):
        functions = load_functions(
            "config_flow.py",
            {
                "async_step_automation_params",
                "_external_room_control_duplicate_entities",
            },
            self.namespace,
        )
        flow = SimpleNamespace(
            config_entry=SimpleNamespace(options={"scan_interval": 30}),
            async_create_entry=lambda **kwargs: kwargs,
        )

        saved = await functions.async_step_automation_params(
            flow,
            {
                "additional_sensors": {
                    "schedule_setpoint_rooms": ["4"]
                }
            },
        )
        self.assertEqual(
            saved["data"],
            {
                "scan_interval": 30,
                "additional_sensors": {
                    "schedule_setpoint_rooms": ["4"]
                },
            },
        )

    def test_external_room_control_room_fields_are_unique_and_readable(self):
        functions = load_functions(
            "config_flow.py", {"_external_room_control_room_fields"}, self.namespace
        )
        rooms = [
            SimpleNamespace(id=1, name="Office"),
            SimpleNamespace(id=3, name="Bedroom"),
            SimpleNamespace(id=4, name="andys Bedroom"),
            SimpleNamespace(id=2, name="Bedroom"),
        ]
        flow = SimpleNamespace(_wiser_rooms=lambda: rooms)

        fields = functions._external_room_control_room_fields(flow)

        self.assertEqual(
            list(fields.items()),
            [
                ("andys Bedroom", "4"),
                ("Bedroom (2)", "2"),
                ("Bedroom (3)", "3"),
                ("Office", "1"),
            ],
        )
        self.assertEqual(
            fields,
            {
                "andys Bedroom": "4",
                "Bedroom (2)": "2",
                "Bedroom (3)": "3",
                "Office": "1",
            },
        )

    def test_external_room_control_selector_uses_external_climates_in_room_area(self):
        rooms = [
            SimpleNamespace(id=1, name="Office"),
            SimpleNamespace(id=2, name="Bedroom"),
        ]
        entries = [
            SimpleNamespace(
                entity_id="climate.office_wiser", platform="wiser", area_id="office"
            ),
            SimpleNamespace(
                entity_id="climate.office_trv", platform="mqtt", area_id="office"
            ),
            SimpleNamespace(
                entity_id="switch.office", platform="mqtt", area_id="office"
            ),
            SimpleNamespace(
                entity_id="climate.bedroom_trv", platform="zha", area_id="bedroom"
            ),
            SimpleNamespace(
                entity_id="climate.other", platform="mqtt", area_id="other"
            ),
        ]
        entity_registry = SimpleNamespace(
            entities=SimpleNamespace(values=lambda: entries)
        )
        areas = {
            "Office": SimpleNamespace(id="office"),
            "Bedroom": SimpleNamespace(id="bedroom"),
        }
        area_registry = SimpleNamespace(
            async_get_area_by_name=lambda name: areas.get(name)
        )
        self.namespace.update(
            ar=SimpleNamespace(async_get=lambda _hass: area_registry),
            er=SimpleNamespace(
                async_get=lambda _hass: entity_registry,
                async_get_effective_area_id=lambda _hass, entry: entry.area_id,
            ),
        )
        functions = load_functions(
            "config_flow.py",
            {"_external_room_control_entities_by_room"},
            self.namespace,
        )
        flow = SimpleNamespace(hass=object(), _wiser_rooms=lambda: rooms)

        self.assertEqual(
            functions._external_room_control_entities_by_room(flow),
            {
                "1": ["climate.office_trv"],
                "2": ["climate.bedroom_trv"],
            },
        )

    def test_external_room_control_form_shows_only_temperature_control_rooms(self):
        functions = load_functions(
            "config_flow.py",
            {"_external_room_control_form_rooms"},
            self.namespace,
        )
        flow = SimpleNamespace(
            _external_room_control_room_fields=lambda: {
                "Bedroom": "2",
                "Kitchen": "3",
                "Utility": "4",
                "Office": "1",
            },
            _external_room_control_entities_by_room=lambda: {
                "1": ["climate.office_trv"],
                "2": [],
                "3": [],
                "4": [],
            },
            _wiser_rooms=lambda: [
                SimpleNamespace(id=1, temperature_control=True),
                SimpleNamespace(id=2, temperature_control=True),
                SimpleNamespace(id=3, temperature_control=True),
                SimpleNamespace(id=4, temperature_control=False),
            ],
        )

        room_fields, entities_by_room = functions._external_room_control_form_rooms(flow)

        self.assertEqual(
            room_fields,
            {
                "Bedroom": "2",
                "Kitchen": "3",
                "Office": "1",
            },
        )
        self.assertEqual(
            entities_by_room,
            {
                "1": ["climate.office_trv"],
                "2": [],
                "3": [],
                "4": [],
            },
        )

    def test_room_supports_temperature_control_uses_capability_and_fallbacks(self):
        functions = load_functions(
            "helpers.py", {"room_supports_temperature_control"}, {}
        )

        self.assertTrue(
            functions.room_supports_temperature_control(
                SimpleNamespace(
                    capabilities=SimpleNamespace(temperature_control=True)
                )
            )
        )
        self.assertFalse(
            functions.room_supports_temperature_control(
                SimpleNamespace(
                    capabilities=SimpleNamespace(temperature_control=False),
                    number_of_smartvalves=0,
                    number_of_heating_actuators=0,
                    roomstat_id=None,
                )
            )
        )
        self.assertTrue(
            functions.room_supports_temperature_control(
                SimpleNamespace(capabilities=None, number_of_smartvalves=1)
            )
        )

    def test_external_room_control_rejects_duplicate_room_assignments(self):
        functions = load_functions(
            "config_flow.py",
            {"_external_room_control_duplicate_entities"},
            self.namespace,
        )

        duplicates = functions._external_room_control_duplicate_entities(
            {
                "1": ["climate.office_trv", "climate.shared_trv"],
                "2": ["climate.shared_trv"],
                "3": ["climate.bedroom_trv"],
            }
        )

        self.assertEqual(duplicates, {"climate.shared_trv"})

    def test_external_passive_type_requires_an_assignment(self):
        functions = load_functions(
            "config_flow.py", {"_passive_types_for_assignments"}, self.namespace
        )

        self.assertEqual(
            functions._passive_types_for_assignments({}, True), ["internal"]
        )
        self.assertEqual(
            functions._passive_types_for_assignments({"1": []}, True), ["internal"]
        )
        self.assertEqual(
            functions._passive_types_for_assignments(
                {"1": ["climate.external_trv"]}, False
            ),
            ["internal"],
        )
        self.assertEqual(
            functions._passive_types_for_assignments(
                {"1": ["climate.external_trv"]}, True
            ),
            ["internal", "external"],
        )

    async def test_external_room_control_has_no_passive_strategy_settings(self):
        source = (COMPONENT / "config_flow.py").read_text()
        tree = ast.parse(source)
        function = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "async_step_automation_params"
        )
        external_schema = next(
            node
            for node in function.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "external_section_schema"
                for target in node.targets
            )
        )
        schema_source = ast.get_source_segment(source, external_schema)

        self.assertNotIn("CONF_CONTROL_STRATEGY", schema_source)
        self.assertNotIn("CONF_TEMPERATURE_INCREMENT", schema_source)

    async def test_passive_type_owns_control_strategy(self):
        source = (COMPONENT / "config_flow.py").read_text()
        tree = ast.parse(source)
        function = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "async_step_automation_params"
        )
        function_source = ast.get_source_segment(source, function)
        self.assertNotIn(
            "vol.Required(CONF_AUTOMATIONS_EXTERNAL_PASSIVE)", function_source
        )
        self.assertIn("CONF_AUTOMATIONS_PASSIVE_TYPE", function_source)
        self.assertIn("SelectSelectorMode.LIST", function_source)
        self.assertIn("CompactSelectSelector", function_source)
        self.assertIn("CONF_CONTROL_STRATEGY", function_source)
        self.assertIn("_passive_types_for_assignments", function_source)
        self.assertIn("if len(passive_types) > 1", function_source)
        self.assertIn("ConditionalSelectSelector", function_source)
        self.assertIn('"field": CONF_AUTOMATIONS_PASSIVE_TYPE', function_source)
        self.assertIn('"value": PASSIVE_TYPE_EXTERNAL', function_source)

    async def test_passive_type_switch_preserves_or_defaults_strategy(self):
        functions = load_functions(
            "config_flow.py", {"async_step_automation_params"}, self.namespace
        )
        flow = SimpleNamespace(
            config_entry=SimpleNamespace(
                options={
                    "automations_passive_mode": {
                        "automations_passive_mode": True,
                        "passive_type": "external",
                        "control_strategy": "temperature_limiter",
                    }
                }
            ),
            async_create_entry=lambda **kwargs: kwargs,
        )

        internal = await functions.async_step_automation_params(
            flow,
            {
                "automations_passive_mode": {
                    "automations_passive_mode": True,
                    "passive_type": "internal",
                }
            },
        )
        self.assertNotIn(
            "control_strategy",
            internal["data"]["automations_passive_mode"],
        )

        flow.config_entry.options = {
            "automations_external_room_control": {
                "automations_external_room_control": True,
                "external_room_control_assignments": {
                    "1": ["climate.external_trv"]
                }
            }
        }
        external = await functions.async_step_automation_params(
            flow,
            {
                "automations_passive_mode": {
                    "automations_passive_mode": True,
                    "passive_type": "external",
                }
            },
        )
        self.assertEqual(
            external["data"]["automations_passive_mode"]["control_strategy"],
            "modulating",
        )

        flow.config_entry.options = {}
        unavailable = await functions.async_step_automation_params(
            flow,
            {
                "automations_passive_mode": {
                    "automations_passive_mode": True,
                    "passive_type": "external",
                }
            },
        )
        self.assertEqual(
            unavailable["data"]["automations_passive_mode"]["passive_type"],
            "internal",
        )
        self.assertNotIn(
            "control_strategy",
            unavailable["data"]["automations_passive_mode"],
        )

    async def test_external_room_control_assignments_save_with_automation_options(self):
        registry = SimpleNamespace(async_get=lambda entity_id: None)
        self.namespace.update(
            CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL="external",
            CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS="assignments",
            DATA="data",
            DOMAIN="wiser",
            er=SimpleNamespace(async_get=lambda hass: registry),
        )
        functions = load_functions(
            "config_flow.py",
            {
                "async_step_automation_params",
                "_external_room_control_duplicate_entities",
            },
            self.namespace,
        )
        flow = SimpleNamespace(
            _external_room_control_form_rooms=lambda: (
                {
                    "Office": "1",
                    "Bedroom": "2",
                },
                {
                    "1": ["climate.office"],
                    "2": ["climate.bedroom"],
                },
            ),
            config_entry=SimpleNamespace(
                entry_id="entry",
                options={
                    "external": {
                        "external": True,
                        "assignments": {"1": ["climate.old_office"]},
                    }
                },
            ),
            hass=SimpleNamespace(data={}),
            async_create_entry=lambda **kwargs: kwargs,
        )

        result = await functions.async_step_automation_params(
            flow,
            {
                "external": {
                    "external": True,
                    "Office": ["climate.office"],
                    "Bedroom": ["climate.bedroom"],
                }
            },
        )

        self.assertEqual(
            result["data"]["external"]["assignments"],
            {
                "1": ["climate.office"],
                "2": ["climate.bedroom"],
            },
        )
        self.assertNotIn("Office", result["data"]["external"])
        self.assertNotIn("Bedroom", result["data"]["external"])

        removed = await functions.async_step_automation_params(
            flow,
            {
                "automations_passive_mode": {
                    "automations_passive_mode": True,
                    "passive_type": "external",
                },
                "external": {
                    "external": True,
                    "Office": [],
                    "Bedroom": [],
                },
            },
        )
        self.assertEqual(
            removed["data"]["automations_passive_mode"]["passive_type"],
            "internal",
        )
        self.assertNotIn(
            "control_strategy",
            removed["data"]["automations_passive_mode"],
        )

        disabled = await functions.async_step_automation_params(
            flow,
            {
                "automations_passive_mode": {
                    "automations_passive_mode": True,
                    "passive_type": "external",
                    "control_strategy": "temperature_limiter",
                },
                "external": {
                    "external": False,
                    "Office": ["climate.office"],
                    "Bedroom": ["climate.bedroom"],
                },
            },
        )
        self.assertEqual(
            disabled["data"]["automations_passive_mode"]["passive_type"],
            "internal",
        )
        self.assertNotIn(
            "control_strategy",
            disabled["data"]["automations_passive_mode"],
        )

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
            result["menu_options"].index("opentherm"),
            result["menu_options"].index("equipment_sensors"),
        )

    async def test_opentherm_menu_groups_control_and_sensors(self):
        self.namespace["opentherm_hot_water_control_is_supported"] = (
            lambda entry, opentherm: True
        )
        functions = load_functions(
            "config_flow.py", {"async_step_opentherm"}, self.namespace
        )
        flow = SimpleNamespace(
            _opentherm=lambda: object(),
            config_entry=SimpleNamespace(),
            async_show_menu=lambda **kwargs: kwargs,
        )
        result = await functions.async_step_opentherm(flow)
        self.assertEqual(result["step_id"], "opentherm")
        self.assertEqual(
            result["menu_options"],
            ["opentherm_hot_water_control", "opentherm_sensors"],
        )

    async def test_opentherm_menu_hides_unsupported_hot_water_control(self):
        self.namespace["opentherm_hot_water_control_is_supported"] = (
            lambda entry, opentherm: False
        )
        functions = load_functions(
            "config_flow.py", {"async_step_opentherm"}, self.namespace
        )
        flow = SimpleNamespace(
            _opentherm=lambda: object(),
            config_entry=SimpleNamespace(),
            async_show_menu=lambda **kwargs: kwargs,
        )
        result = await functions.async_step_opentherm(flow)
        self.assertEqual(result["menu_options"], ["opentherm_sensors"])

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
        self.assertNotIn("opentherm", result["menu_options"])

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
