"""OpenTherm action regression tests, without a running hub or HA instance."""

import ast
import importlib.util
import inspect
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock, patch

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
        self.first = SimpleNamespace(wiserhub=SimpleNamespace(system=_system()), async_refresh=AsyncMock())
        self.second = SimpleNamespace(wiserhub=SimpleNamespace(system=_system()), async_refresh=AsyncMock())
        self.hass = SimpleNamespace(data={"wiser": {
            "first": {"data": self.first}, "second": {"data": self.second},
        }})
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
            "get_instance_count": lambda hass: len(hass.data["wiser"]),
            "is_wiser_config_id": lambda hass, hub: hub in hass.data["wiser"],
            "get_config_entry_id_by_name": lambda hass, hub: {"Other hub": "second"}.get(hub),
            "async_set_parameter": HELPER.async_set_parameter,
        }
        source = ast.parse((COMPONENT / "services.py").read_text())
        handler = next(node for node in ast.walk(source)
                       if isinstance(node, ast.AsyncFunctionDef)
                       and node.name == "async_set_opentherm_parameter")
        self.assertEqual(handler.decorator_list, [])
        exec(compile(ast.Module(body=[handler], type_ignores=[]), "services.py", "exec"), self.env)
        self.handler = self.env[handler.name]
        self.assertTrue(inspect.iscoroutinefunction(self.handler))

    async def call(self, hub="", value="400"):
        await self.handler(SimpleNamespace(data={
            "hub": hub, "endpoint": "", "parameter": "dhwFlowSetpoint", "parameter_value": value,
        }))

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
