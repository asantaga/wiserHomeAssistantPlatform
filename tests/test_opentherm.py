"""OpenTherm action regression tests, without a running hub or HA instance."""

import ast
import importlib.util
import inspect
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

COMPONENT = Path(__file__).parents[1] / "custom_components/wiser"
LEGACY_URL = "{}:{}/data/v2/opentherm/"
MODERN_URL = "{}:{}/data/v2/openTherm/"


def _module(name, **attrs):
    module = ModuleType(name)
    module.__dict__.update(attrs)
    return module


def _load_helper():
    modules = {
        "aioWiserHeatAPI": _module("aioWiserHeatAPI"),
        "aioWiserHeatAPI.const": _module(
            "aioWiserHeatAPI.const",
            # aioWiserHeatAPI.helpers.version.Version exposes .version;
            # it is not a packaging.version.Version instance.
            OPENTHERMV2_MIN_VERSION=SimpleNamespace(version="4.32.47"),
            WISERHUBOPENTHERM=LEGACY_URL,
            WISERHUBOPENTHERMV2=MODERN_URL,
        ),
        "aioWiserHeatAPI.rest_controller": _module(
            "aioWiserHeatAPI.rest_controller",
            WiserRestActionEnum=SimpleNamespace(PATCH="PATCH"),
        ),
    }
    spec = importlib.util.spec_from_file_location(
        "wiser_opentherm_test", COMPONENT / "opentherm.py"
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


HELPER = _load_helper()


def _system(generation=2, firmware="4.48.2", device_firmware="1.0.0"):
    return SimpleNamespace(
        hardware_generation=generation,
        active_system_version=firmware,
        firmware_version=device_firmware,
        opentherm=SimpleNamespace(
            _wiser_rest_controller=SimpleNamespace(_do_hub_action=AsyncMock())
        ),
    )


class ParameterValueTest(unittest.TestCase):
    def test_ui_and_yaml_scalars_retain_the_correct_json_type(self):
        for raw, expected in (
            ("400", 400), (400, 400), (" 400 ", 400),
            ("40.5", 40.5), (40.5, 40.5), ("0", 0),
            ("true", True), (True, True), ("false", False), (False, False),
            ("Auto", "Auto"), ('"Auto"', "Auto"),
        ):
            with self.subTest(raw=raw):
                result = HELPER.parse_parameter_value(raw)
                self.assertEqual(result, expected)
                self.assertIs(type(result), type(expected))

    def test_rejects_empty_null_containers_and_nonfinite_values(self):
        for raw in ("", " ", "null", None, "[]", [], "{}", {},
                    "NaN", "Infinity", "-Infinity", float("nan"), float("inf")):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                HELPER.parse_parameter_value(raw)

    def test_known_temperature_feedback_is_compared_in_degrees(self):
        system = _system()
        system.opentherm.hw_flow_setpoint = 40
        system.opentherm.boiler_parameters = SimpleNamespace(
            hw_setpoint=50, ch_setpoint=70
        )

        self.assertTrue(
            HELPER.opentherm_parameter_matches(
                system, "", "dhwFlowSetpoint", 400
            )
        )
        self.assertFalse(
            HELPER.opentherm_parameter_matches(
                system, "", "dhwFlowSetpoint", 450
            )
        )
        self.assertTrue(
            HELPER.opentherm_parameter_matches(system, "", "dhwSetpoint", 500)
        )
        self.assertEqual(
            HELPER.opentherm_parameter_feedback(system, "", "dhwSetpoint"), 50
        )

    def test_unknown_or_unavailable_feedback_is_not_retryable(self):
        system = _system()
        system.opentherm.hw_flow_setpoint = None

        self.assertIsNone(
            HELPER.opentherm_parameter_matches(system, "", "unknown", 400)
        )
        self.assertIsNone(
            HELPER.opentherm_parameter_matches(
                system, "", "dhwFlowSetpoint", 400
            )
        )
        self.assertIsNone(
            HELPER.opentherm_parameter_matches(
                system, "customEndpoint", "dhwSetpoint", 500
            )
        )


class OpenThermSensorDiscoveryTest(unittest.TestCase):
    """Validate the selectable OpenTherm attribute catalogue."""

    def test_only_original_temperature_sensors_are_enabled_by_default(self):
        self.assertEqual(
            HELPER.DEFAULT_OPENTHERM_SENSOR_KEYS,
            {"ch_flow_temperature", "ch_return_temperature"},
        )
        self.assertNotIn(
            "relative_modulation_level", HELPER.DEFAULT_OPENTHERM_SENSOR_KEYS
        )
        self.assertNotIn("flame_statistics", HELPER.DEFAULT_OPENTHERM_SENSOR_KEYS)
        self.assertNotIn("delta_t", HELPER.DEFAULT_OPENTHERM_SENSOR_KEYS)
        self.assertNotIn(
            "estimated_boiler_output", HELPER.DEFAULT_OPENTHERM_SENSOR_KEYS
        )

    def test_detects_supported_fields_even_when_the_value_is_none(self):
        opentherm = SimpleNamespace(
            connection_status="Connected",
            operational_data=SimpleNamespace(
                ch_flow_temperature=42.0,
                relative_modulation_level=None,
            ),
        )

        self.assertEqual(
            HELPER.detected_opentherm_sensor_keys(opentherm),
            [
                "connection_status",
                "ch_flow_temperature",
                "relative_modulation_level",
            ],
        )

    def test_delta_t_is_detected_and_calculated_from_flow_and_return(self):
        opentherm = SimpleNamespace(
            operational_data=SimpleNamespace(
                ch_flow_temperature=42.4,
                ch_return_temperature=35.1,
            )
        )

        self.assertIn(
            "delta_t", HELPER.detected_opentherm_sensor_keys(opentherm)
        )
        self.assertEqual(HELPER.opentherm_sensor_value(opentherm, "delta_t"), 7.3)

        opentherm.operational_data.ch_return_temperature = None
        self.assertIsNone(HELPER.opentherm_sensor_value(opentherm, "delta_t"))

    def test_detects_and_reads_additional_boiler_telemetry(self):
        opentherm = SimpleNamespace(
            operational_data=SimpleNamespace(
                json_data={
                    "MinimumModulationLevel": 27,
                    "MaximumCapacityKw": 30,
                    "BoilerExhaustTemperature": 28,
                }
            )
        )

        detected = HELPER.detected_opentherm_sensor_keys(opentherm)
        expected = {
            "minimum_modulation_level": 27,
            "maximum_capacity_kw": 30,
            "boiler_exhaust_temperature": 28,
        }
        self.assertTrue(set(expected).issubset(detected))
        for key, value in expected.items():
            with self.subTest(key=key):
                self.assertEqual(HELPER.opentherm_sensor_value(opentherm, key), value)

    def test_estimated_output_accounts_for_minimum_modulation_and_flame(self):
        opentherm = SimpleNamespace(
            operational_data=SimpleNamespace(
                slave_status=8,
                json_data={
                    "MaximumCapacityKw": 30,
                    "MinimumModulationLevel": 27,
                    "RelativeModulationLevel": 52,
                    "SlaveStatus": 8,
                }
            )
        )

        self.assertIn(
            "estimated_boiler_output",
            HELPER.detected_opentherm_sensor_keys(opentherm),
        )
        self.assertEqual(
            HELPER.opentherm_sensor_value(opentherm, "estimated_boiler_output"),
            9.24,
        )

        opentherm.operational_data.json_data["SlaveStatus"] = 0
        opentherm.operational_data.slave_status = 0
        self.assertEqual(
            HELPER.opentherm_sensor_value(opentherm, "estimated_boiler_output"),
            0,
        )

        del opentherm.operational_data.json_data["RelativeModulationLevel"]
        self.assertNotIn(
            "estimated_boiler_output",
            HELPER.detected_opentherm_sensor_keys(opentherm),
        )

    def test_detects_and_reads_coprocessor_diagnostics(self):
        opentherm = SimpleNamespace(
            json_data={
                "CoprocessorVersion": "2.0.31",
                "CoprocessorUpdateStatus": "Success",
            },
            operational_data=SimpleNamespace(json_data={}),
        )

        detected = HELPER.detected_opentherm_sensor_keys(opentherm)
        self.assertIn("coprocessor_version", detected)
        self.assertIn("coprocessor_update_status", detected)
        self.assertEqual(
            HELPER.opentherm_sensor_value(opentherm, "coprocessor_version"),
            "2.0.31",
        )
        self.assertEqual(
            HELPER.opentherm_sensor_value(
                opentherm, "coprocessor_update_status"
            ),
            "Success",
        )

    def test_decodes_all_non_reserved_slave_status_bits(self):
        opentherm = SimpleNamespace(
            operational_data=SimpleNamespace(slave_status=0b01010101)
        )
        expected = {
            "boiler_fault": True,
            "central_heating_active": False,
            "hot_water_active": True,
            "flame_active": False,
            "cooling_active": True,
            "central_heating_2_active": False,
            "diagnostic_event": True,
        }

        self.assertEqual(set(HELPER.OPENTHERM_SLAVE_STATUS_BITS), set(expected))
        for key, state in expected.items():
            with self.subTest(key=key):
                self.assertIs(HELPER.opentherm_sensor_value(opentherm, key), state)

    def test_invalid_slave_status_is_unknown(self):
        for slave_status in (None, True, 1.5, "4"):
            with self.subTest(slave_status=slave_status):
                opentherm = SimpleNamespace(
                    operational_data=SimpleNamespace(slave_status=slave_status)
                )
                self.assertIsNone(
                    HELPER.opentherm_sensor_value(opentherm, "hot_water_active")
                )

    def test_catalogue_names_cover_every_selectable_field(self):
        self.assertEqual(
            set(HELPER.OPENTHERM_SENSOR_NAMES),
            set(HELPER.OPENTHERM_SENSOR_PATHS),
        )

    def test_categories_partition_every_selectable_field(self):
        category_keys = [
            key
            for keys in HELPER.OPENTHERM_SENSOR_CATEGORIES.values()
            for key in keys
        ]
        self.assertEqual(len(category_keys), len(set(category_keys)))
        self.assertEqual(set(category_keys), set(HELPER.OPENTHERM_SENSOR_PATHS))

    def test_options_form_labels_cover_every_selectable_field(self):
        for path in (
            COMPONENT / "strings.json",
            *sorted((COMPONENT / "translations").glob("*.json")),
        ):
            with self.subTest(path=path):
                strings = json.loads(path.read_text())
                steps = strings["options"]["step"]
                labels = {
                    key
                    for category in HELPER.OPENTHERM_SENSOR_CATEGORIES
                    for key in steps[category]["data"]
                }
                self.assertEqual(set(labels), set(HELPER.OPENTHERM_SENSOR_PATHS))

    def test_entity_names_are_translated_without_english_placeholders(self):
        binary_keys = set(HELPER.OPENTHERM_BINARY_SENSOR_KEYS)
        sensor_keys = set(HELPER.OPENTHERM_SENSOR_PATHS) - binary_keys - {
            "ch_flow_temperature",
            "ch_return_temperature",
            "flame_statistics",
        }
        for path in (
            COMPONENT / "strings.json",
            *sorted((COMPONENT / "translations").glob("*.json")),
        ):
            with self.subTest(path=path):
                entities = json.loads(path.read_text())["entity"]
                self.assertTrue(binary_keys.issubset(entities["binary_sensor"]))
                self.assertTrue(sensor_keys.issubset(entities["sensor"]))
                for domain, keys in (
                    ("binary_sensor", binary_keys),
                    ("sensor", sensor_keys),
                ):
                    for key in keys:
                        self.assertNotIn(
                            "{name}", entities[domain][key]["name"]
                        )

    def test_selected_sensor_options_support_lists_and_legacy_mappings(self):
        self.assertTrue(
            HELPER.opentherm_sensor_is_enabled(None, "ch_flow_temperature")
        )
        self.assertFalse(
            HELPER.opentherm_sensor_is_enabled(None, "relative_modulation_level")
        )
        self.assertTrue(
            HELPER.opentherm_sensor_is_enabled(
                ["relative_modulation_level"], "relative_modulation_level"
            )
        )
        self.assertFalse(
            HELPER.opentherm_sensor_is_enabled(
                {"ch_flow_temperature": False}, "ch_flow_temperature"
            )
        )

    def test_derived_sensor_dependencies_are_declared(self):
        self.assertEqual(
            HELPER.OPENTHERM_SENSOR_DEPENDENCIES["delta_t"],
            {"ch_flow_temperature", "ch_return_temperature"},
        )
        self.assertEqual(
            HELPER.OPENTHERM_SENSOR_DEPENDENCIES["estimated_boiler_output"],
            {
                "flame_active",
                "maximum_capacity_kw",
                "minimum_modulation_level",
                "relative_modulation_level",
            },
        )


class OpenThermWriteTest(unittest.IsolatedAsyncioTestCase):
    async def test_build_suffix_does_not_affect_endpoint_selection(self):
        for firmware, expected in (
            ("4.48.2-3735f20", MODERN_URL),
            ("4.32.47-3735f20", MODERN_URL),
            ("4.32.46-3735f20", LEGACY_URL),
            ("4.48.2-1234567", MODERN_URL),
            (" 4.48.2-3735f20 ", MODERN_URL),
        ):
            with self.subTest(firmware=firmware):
                system = _system(firmware=firmware)
                await HELPER.async_set_parameter(system, "", "dhwFlowSetpoint", "400")
                system.opentherm._wiser_rest_controller._do_hub_action.assert_awaited_once_with(
                    "PATCH", expected, {"dhwFlowSetpoint": 400}
                )

    async def test_routing_uses_system_version_not_device_firmware(self):
        for system_version, device_version, expected in (
            ("4.48.2", "1.0.0", MODERN_URL),
            ("4.32.46", "4.48.2", LEGACY_URL),
            ("4.48.2", "Unknown", MODERN_URL),
        ):
            with self.subTest(system_version=system_version, device_version=device_version):
                system = _system(firmware=system_version, device_firmware=device_version)
                await HELPER.async_set_parameter(system, "", "dhwFlowSetpoint", "400")
                system.opentherm._wiser_rest_controller._do_hub_action.assert_awaited_once_with(
                    "PATCH", expected, {"dhwFlowSetpoint": 400}
                )

    async def test_endpoint_selection_matches_library_reader(self):
        for generation, firmware, expected in (
            (1, "4.48.2", LEGACY_URL),
            (1, "Unknown", LEGACY_URL),
            (2, "4.32.46", LEGACY_URL),
            (2, "4.32.47", MODERN_URL),
            (2, "4.48.2", MODERN_URL),
        ):
            with self.subTest(generation=generation, firmware=firmware):
                system = _system(generation, firmware)
                await HELPER.async_set_parameter(system, "", "dhwFlowSetpoint", "400")
                system.opentherm._wiser_rest_controller._do_hub_action.assert_awaited_once_with(
                    "PATCH", expected, {"dhwFlowSetpoint": 400}
                )

    async def test_nested_endpoint_and_boolean(self):
        system = _system()
        await HELPER.async_set_parameter(
            system, "preDefinedRemoteBoilerParameters", "dhwSetpointTransferEnable", "true"
        )
        system.opentherm._wiser_rest_controller._do_hub_action.assert_awaited_once_with(
            "PATCH", MODERN_URL + "preDefinedRemoteBoilerParameters",
            {"dhwSetpointTransferEnable": True},
        )

    async def test_known_nested_parameter_infers_its_endpoint(self):
        system = _system()
        await HELPER.async_set_parameter(system, "", "dhwSetpoint", 500)
        system.opentherm._wiser_rest_controller._do_hub_action.assert_awaited_once_with(
            "PATCH",
            MODERN_URL + "preDefinedRemoteBoilerParameters",
            {"dhwSetpoint": 500},
        )

    async def test_explicit_endpoint_overrides_inference(self):
        system = _system()
        await HELPER.async_set_parameter(
            system, "customEndpoint", "dhwSetpoint", 500
        )
        system.opentherm._wiser_rest_controller._do_hub_action.assert_awaited_once_with(
            "PATCH", MODERN_URL + "customEndpoint", {"dhwSetpoint": 500}
        )

    async def test_invalid_inputs_never_send_a_request(self):
        for endpoint, parameter, value, firmware in (
            ("../domain/System", "dhwFlowSetpoint", 400, "4.48.2"),
            ("http://example.test", "dhwFlowSetpoint", 400, "4.48.2"),
            ("", "", 400, "4.48.2"),
            ("", "dhwFlowSetpoint", "null", "4.48.2"),
            ("", "dhwFlowSetpoint", 400, "Unknown"),
            ("", "dhwFlowSetpoint", 400, None),
            ("", "dhwFlowSetpoint", 400, "4.48"),
            ("", "dhwFlowSetpoint", 400, "4.48.2-"),
        ):
            with self.subTest(endpoint=endpoint, firmware=firmware):
                system = _system(firmware=firmware)
                with self.assertRaises(ValueError):
                    await HELPER.async_set_parameter(system, endpoint, parameter, value)
                system.opentherm._wiser_rest_controller._do_hub_action.assert_not_awaited()


class HomeAssistantError(Exception):
    pass


class OpenThermActionTest(unittest.IsolatedAsyncioTestCase):
    """Execute the real nested action handler with lightweight HA dependencies."""

    def setUp(self):
        self.listeners = {}

        def coordinator(name):
            listeners = self.listeners[name] = []

            def add_listener(listener):
                listeners.append(listener)

                def remove_listener():
                    if listener in listeners:
                        listeners.remove(listener)

                return remove_listener

            return SimpleNamespace(
                wiserhub=SimpleNamespace(system=_system()),
                async_refresh=AsyncMock(),
                async_add_listener=add_listener,
                last_update_status="Success",
            )

        self.first = coordinator("first")
        self.second = coordinator("second")
        self.tasks = []

        def create_task(coro, _name):
            task = __import__("asyncio").create_task(coro)
            self.tasks.append(task)
            return task

        self.hass = SimpleNamespace(
            async_create_task=create_task,
            bus=SimpleNamespace(async_fire=Mock()),
            services=SimpleNamespace(async_call=AsyncMock()),
            data={"wiser": {
            "first": {"data": self.first}, "second": {"data": self.second},
            }},
        )
        self.errors = {
            name: type(name, (Exception,), {}) for name in (
                "WiserHubRESTError", "WiserHubConnectionError",
                "WiserHubResponseError", "WiserHubAuthenticationError",
            )
        }
        self.env = {
            **self.errors,
            "HomeAssistantError": HomeAssistantError,
            "hass": self.hass, "data": self.first, "DOMAIN": "wiser", "DATA": "data",
            "ATTR_OPENTHERM_ENDPOINT": "endpoint", "ATTR_OPENTHERM_PARAM": "parameter",
            "ATTR_OPENTHERM_PARAM_VALUE": "parameter_value", "ATTR_HUB": "hub",
            "ATTR_OPENTHERM_TEMPERATURE": "temperature",
            "ATTR_OPENTHERM_REQUEST_ID": "request_id",
            "EVENT_OPENTHERM_COMMAND_FAILED": "wiser_opentherm_command_failed",
            "get_instance_count": lambda hass: len(hass.data["wiser"]),
            "is_wiser_config_id": lambda hass, hub: hub in hass.data["wiser"],
            "get_config_entry_id_by_name": lambda hass, hub: {"Other hub": "second"}.get(hub),
            "async_set_parameter": HELPER.async_set_parameter,
            "opentherm_parameter_matches": HELPER.opentherm_parameter_matches,
            "opentherm_parameter_feedback": HELPER.opentherm_parameter_feedback,
            "parse_parameter_value": HELPER.parse_parameter_value,
            "asyncio": __import__("asyncio"),
            "OPENTHERM_CONFIRMATION_WINDOW": 90,
            "_LOGGER": SimpleNamespace(
                warning=lambda *args: None, debug=lambda *args: None
            ),
        }
        source = ast.parse((COMPONENT / "services.py").read_text())
        handler = next(node for node in ast.walk(source)
                       if isinstance(node, ast.AsyncFunctionDef)
                       and node.name == "async_set_opentherm_parameter")
        self.assertEqual(handler.decorator_list, [])
        exec(compile(ast.Module(body=[handler], type_ignores=[]), "services.py", "exec"), self.env)
        self.handler = self.env[handler.name]
        self.assertTrue(inspect.iscoroutinefunction(self.handler))

    async def asyncTearDown(self):
        for task in self.tasks:
            if not task.done():
                task.cancel()
        if self.tasks:
            await __import__("asyncio").gather(
                *self.tasks, return_exceptions=True
            )

    async def call(self, hub="", value="400", request_id=None):
        payload = {
            "hub": hub, "endpoint": "", "parameter": "dhwFlowSetpoint", "parameter_value": value,
        }
        if request_id is not None:
            payload["request_id"] = request_id
        await self.handler(SimpleNamespace(
            data=payload,
            context=SimpleNamespace(id="test-context"),
        ))

    async def test_celsius_ui_temperature_is_converted_to_api_tenths(self):
        del self.hass.data["wiser"]["second"]
        await self.handler(
            SimpleNamespace(
                data={
                    "hub": "",
                    "endpoint": "",
                    "parameter": "dhwFlowSetpoint",
                    "temperature": 47.0,
                },
                context=SimpleNamespace(id="test-context"),
            )
        )
        self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action.assert_awaited_once_with(
            "PATCH", MODERN_URL, {"dhwFlowSetpoint": 470}
        )

    async def test_single_hub_defaults_to_current_instance(self):
        del self.hass.data["wiser"]["second"]
        await self.call()
        self.first.async_refresh.assert_awaited_once()

    async def test_reported_firmware_succeeds_through_action_handler(self):
        self.first.wiserhub.system.active_system_version = "4.48.2-3735f20"
        await self.call("first")
        self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action.assert_awaited_once_with(
            "PATCH", MODERN_URL, {"dhwFlowSetpoint": 400}
        )
        self.first.async_refresh.assert_awaited_once()

    async def test_known_mismatch_is_retried_once(self):
        del self.hass.data["wiser"]["second"]
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 35

        await self.call()

        # The immediate refresh is allowed to settle. A later successful
        # coordinator update confirms drift and triggers the single retry.
        await __import__("asyncio").sleep(0)
        self.assertEqual(len(self.listeners["first"]), 1)
        initial_listener = self.listeners["first"][0]
        self.listeners["first"][0]()
        while (
            self.first.async_refresh.await_count < 2
            or self.listeners["first"][0] is initial_listener
        ):
            await __import__("asyncio").sleep(0)
        # A post-retry update can still contain stale feedback. It must not
        # fail the command before the confirmation deadline.
        self.listeners["first"][0]()
        await __import__("asyncio").sleep(0)
        self.hass.services.async_call.assert_not_awaited()
        self.hass.bus.async_fire.assert_not_called()
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 40
        self.listeners["first"][0]()
        await __import__("asyncio").gather(*self.tasks)

        transport = self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action
        self.assertEqual(transport.await_count, 2)
        self.assertEqual(self.first.async_refresh.await_count, 2)

    async def test_initial_mismatch_is_retried_when_no_update_arrives(self):
        del self.hass.data["wiser"]["second"]
        self.env["OPENTHERM_CONFIRMATION_WINDOW"] = 0.05
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 35

        await self.call()

        # Even without another coordinator update, feedback that remains
        # mismatched at the deadline must trigger the one permitted retry.
        while self.first.async_refresh.await_count < 2:
            await __import__("asyncio").sleep(0.01)
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 40
        self.listeners["first"][0]()
        await __import__("asyncio").gather(*self.tasks)

        transport = self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action
        self.assertEqual(transport.await_count, 2)
        self.assertEqual(self.first.async_refresh.await_count, 2)
        self.hass.services.async_call.assert_not_awaited()
        self.hass.bus.async_fire.assert_not_called()

    async def test_matching_feedback_is_not_retried(self):
        del self.hass.data["wiser"]["second"]
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 40

        await self.call()

        transport = self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action
        self.assertEqual(transport.await_count, 1)
        self.assertEqual(self.first.async_refresh.await_count, 1)

    async def test_later_drift_within_confirmation_window_is_retried(self):
        del self.hass.data["wiser"]["second"]
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 40

        await self.call()
        await __import__("asyncio").sleep(0)
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 35
        initial_listener = self.listeners["first"][0]
        self.listeners["first"][0]()
        while (
            self.first.async_refresh.await_count < 2
            or self.listeners["first"][0] is initial_listener
        ):
            await __import__("asyncio").sleep(0)
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 40
        self.listeners["first"][0]()
        await __import__("asyncio").gather(*self.tasks)

        transport = self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action
        self.assertEqual(transport.await_count, 2)
        self.assertEqual(self.first.async_refresh.await_count, 2)

    async def test_persistent_warning_requires_post_retry_mismatch(self):
        del self.hass.data["wiser"]["second"]
        self.env["OPENTHERM_CONFIRMATION_WINDOW"] = 0.2
        self.first.wiserhub.system.name = "Test hub"
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 35

        await self.call(request_id="hot-water-preset-1")
        # Use most of the original write's window before confirming the
        # mismatch. The retry must still receive a complete new window.
        await __import__("asyncio").sleep(0.12)
        initial_listener = self.listeners["first"][0]
        self.listeners["first"][0]()
        while (
            self.first.async_refresh.await_count < 2
            or self.listeners["first"][0] is initial_listener
        ):
            await __import__("asyncio").sleep(0)
        self.hass.services.async_call.assert_not_awaited()
        self.listeners["first"][0]()
        await __import__("asyncio").sleep(0.12)
        self.hass.services.async_call.assert_not_awaited()
        self.hass.bus.async_fire.assert_not_called()
        await __import__("asyncio").gather(*self.tasks)

        self.hass.services.async_call.assert_awaited_once()
        self.hass.bus.async_fire.assert_called_once()
        event_type, event_data = self.hass.bus.async_fire.call_args.args[:2]
        self.assertEqual(event_type, "wiser_opentherm_command_failed")
        self.assertEqual(event_data["request_id"], "hot-water-preset-1")
        self.assertEqual(event_data["requested"], 40)
        self.assertEqual(event_data["reported"], 35)
        notification = self.hass.services.async_call.await_args.args[2]
        self.assertIn("40 °C", notification["message"])
        self.assertIn("35 °C", notification["message"])
        self.assertIn("confirmation window", notification["message"])
        self.assertIn("No further retry", notification["message"])

    async def test_background_retry_transport_error_is_reported(self):
        del self.hass.data["wiser"]["second"]
        self.env["OPENTHERM_CONFIRMATION_WINDOW"] = 0.05
        self.first.wiserhub.system.name = "Test hub"
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 35
        transport = self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action
        retry_failure = self.errors["WiserHubConnectionError"]("Hub unavailable")
        transport.side_effect = [None, retry_failure]

        await self.call(request_id="hot-water-preset-2")
        await __import__("asyncio").sleep(0)
        self.listeners["first"][0]()
        await __import__("asyncio").gather(*self.tasks)

        self.assertEqual(transport.await_count, 2)
        self.assertEqual(self.first.async_refresh.await_count, 1)
        self.hass.bus.async_fire.assert_called_once()
        event_type, event_data = self.hass.bus.async_fire.call_args.args[:2]
        self.assertEqual(event_type, "wiser_opentherm_command_failed")
        self.assertEqual(event_data["request_id"], "hot-water-preset-2")
        self.assertIn("Hub unavailable", event_data["error"])
        notification = self.hass.services.async_call.await_args.args[2]
        self.assertIn("retry could not be sent", notification["message"])
        self.assertIn("Hub unavailable", notification["message"])

    async def test_newer_command_cancels_older_confirmation(self):
        del self.hass.data["wiser"]["second"]
        self.first.wiserhub.system.opentherm.hw_flow_setpoint = 35

        await self.call(value="400")
        await __import__("asyncio").sleep(0)
        first_task = self.tasks[-1]
        await self.call(value="450")
        await __import__("asyncio").gather(first_task, return_exceptions=True)

        self.assertTrue(first_task.cancelled())
        self.assertEqual(
            self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action.await_count,
            2,
        )

    async def test_selected_hub_is_written_and_refreshed(self):
        for hub in ("second", "Other hub"):
            with self.subTest(hub=hub):
                self.second.async_refresh.reset_mock()
                transport = self.second.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action
                transport.reset_mock()
                await self.call(hub)
                transport.assert_awaited_once_with("PATCH", MODERN_URL, {"dhwFlowSetpoint": 400})
                self.second.async_refresh.assert_awaited_once()
                self.first.async_refresh.assert_not_awaited()
                self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action.assert_not_awaited()

    async def test_missing_multi_hub_selection_is_rejected(self):
        with self.assertRaisesRegex(HomeAssistantError, "specify a hub"):
            await self.call()

    async def test_invalid_hub_never_falls_back_to_another_hub(self):
        for single_hub in (False, True):
            if single_hub:
                del self.hass.data["wiser"]["second"]
            with self.assertRaisesRegex(HomeAssistantError, "not found"):
                await self.call("missing")
        self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action.assert_not_awaited()

    async def test_missing_opentherm_is_reported(self):
        self.first.wiserhub.system.opentherm = None
        with self.assertRaisesRegex(HomeAssistantError, "does not have OpenTherm"):
            await self.call("first")

    async def test_unloaded_hub_is_reported_without_writing_to_default(self):
        self.hass.data["wiser"]["second"] = {}
        with self.assertRaisesRegex(HomeAssistantError, "not loaded"):
            await self.call("second")
        self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action.assert_not_awaited()

    async def test_bad_value_becomes_an_action_error(self):
        with self.assertRaisesRegex(HomeAssistantError, "must not be empty"):
            await self.call("first", "")
        self.first.async_refresh.assert_not_awaited()

    async def test_library_errors_are_reported_including_wrapped_404(self):
        transport = self.first.wiserhub.system.opentherm._wiser_rest_controller._do_hub_action
        for error_class in self.errors.values():
            with self.subTest(error_class=error_class):
                error = error_class("Rest endpoint not found")
                transport.side_effect = error
                with self.assertRaisesRegex(HomeAssistantError, "dhwFlowSetpoint: Rest endpoint not found") as raised:
                    await self.call("first")
                self.assertIs(raised.exception.__cause__, error)
        self.first.async_refresh.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
