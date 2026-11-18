"""Regression tests for Home Assistant config-flow compatibility."""

import ast
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import voluptuous as vol

from test_ui_options import load_functions


COMPONENT = Path(__file__).parents[1] / "custom_components/wiser"


class SelectorCompatibilityTest(unittest.TestCase):
    """Exercise selector imports and configuration on old and new HA."""

    def _load(self, native_helper=None):
        """Execute the real selector imports and compatibility block."""
        selector_module = ModuleType("homeassistant.helpers.selector")
        if native_helper is not None:
            selector_module.make_selector_config_schema = native_helper

        class Selector:
            """Model the configuration contract of HA 2025.5 selectors."""

            def __init__(self, config=None):
                self.config = self.CONFIG_SCHEMA({} if config is None else config)

        selector_module.Selector = Selector
        selector_module.SELECTORS = SimpleNamespace(register=lambda _key: lambda cls: cls)
        for name in (
            "BooleanSelector", "EntitySelector", "EntitySelectorConfig",
            "SelectSelector", "SelectSelectorConfig", "SelectSelectorMode", "selector",
        ):
            setattr(selector_module, name, Mock())
        tree = ast.parse((COMPONENT / "config_flow.py").read_text())
        nodes = [
            node for node in tree.body
            if (
                isinstance(node, ast.ImportFrom)
                and node.module == "homeassistant.helpers.selector"
            ) or (
                isinstance(node, ast.Try)
                and any(
                    isinstance(child, ast.ImportFrom)
                    and child.module == "homeassistant.helpers.selector"
                    for child in node.body
                )
            ) or (
                isinstance(node, ast.ClassDef)
                and node.name in {
                    "OpenThermPresetsSelector", "ExternalTemperatureCalculationSelector"
                }
            )
        ]
        namespace = {
            "vol": vol,
            "Any": object,
            "MAX_OPENTHERM_HOT_WATER_PRESETS": 10,
        }
        load_functions(
            "config_flow.py", {"_validate_opentherm_hot_water_presets"}, namespace
        )
        with patch.dict(sys.modules, {selector_module.__name__: selector_module}):
            exec(compile(ast.Module(body=nodes, type_ignores=[]), "config_flow.py", "exec"), namespace)
        return SimpleNamespace(**namespace)

    def test_legacy_selectors_accept_empty_config_and_preserve_defaults(self):
        """Both editors can be constructed without the newer HA helper."""
        flow = self._load()
        for config in (None, {}):
            with self.subTest(config=config):
                self.assertEqual(
                    flow.OpenThermPresetsSelector(config).config,
                    {"minimum": 35.0, "maximum": 55.0},
                )
                self.assertEqual(flow.ExternalTemperatureCalculationSelector(config).config, {})
        # Newer Selector constructors pass None directly into CONFIG_SCHEMA.
        self.assertEqual(flow.ExternalTemperatureCalculationSelector.CONFIG_SCHEMA(None), {})

    def test_legacy_config_validates_bounds_and_read_only(self):
        """Retain configuration coercion and reject invalid editor options."""
        flow = self._load()
        self.assertEqual(
            flow.OpenThermPresetsSelector(
                {"minimum": "40", "maximum": "60", "read_only": True}
            ).config,
            {"minimum": 40.0, "maximum": 60.0, "read_only": True},
        )
        for config in ({"minimum": "bad"}, {"read_only": "yes"}, {"unexpected": True}):
            with self.subTest(config=config), self.assertRaises(vol.Invalid):
                flow.OpenThermPresetsSelector(config)

    def test_current_home_assistant_uses_native_helper(self):
        """Do not replace the native schema factory on newer HA."""
        native = Mock(return_value=vol.Schema({}))
        flow = self._load(native)
        self.assertIs(flow.make_selector_config_schema, native)
        self.assertEqual(native.call_count, 2)

    def test_expanded_presets_pass_the_form_schema(self):
        """Keep automatic timed defaults editable through HA validation."""
        flow = self._load()
        presets = [
            {"name": f"Preset {index}", "temperature": 45, "duration_minutes": 0}
            for index in range(10)
        ] + [
            {"name": f"Boost {duration}", "temperature": 50, "duration_minutes": duration}
            for duration in (15, 30, 45)
        ]
        schema = vol.Schema({"presets": flow.OpenThermPresetsSelector({
            "minimum": 40, "maximum": 50, "max_presets": len(presets)
        })})
        self.assertEqual(schema({"presets": presets})["presets"], [
            {**preset, "icon": ""} for preset in presets
        ])
        with self.assertRaises(vol.Invalid):
            flow.OpenThermPresetsSelector()(presets)
        for invalid in (
            presets + [{"name": "Extra", "temperature": 45}],
            [{**presets[0], "temperature": 55}, *presets[1:]],
            [{**presets[0], "name": "Auto"}, *presets[1:]],
        ):
            with self.subTest(invalid=invalid), self.assertRaises(vol.Invalid):
                schema({"presets": invalid})


class HubRegistryCompatibilityTest(unittest.TestCase):
    """Exercise hub naming through both device registry APIs."""

    def test_hub_names_use_available_registry_api(self):
        """Keep hub renaming working on both minimum and current HA."""
        for current_api in (False, True):
            with self.subTest(current_api=current_api):
                device = SimpleNamespace(id="hub-device")
                lookup = Mock(return_value=device)
                registry = SimpleNamespace(async_update_device=Mock())
                if current_api:
                    registry.async_get_device_by_identifier = lookup
                else:
                    registry.async_get_device = lookup
                data = SimpleNamespace(wiserhub=SimpleNamespace(
                    system=SimpleNamespace(name="WiserHeat123")
                ))
                hass = SimpleNamespace(data={"wiser": {"entry-id": {"data": data}}})
                functions = load_functions(
                    "__init__.py", {"_device_by_identifier", "update_hub_device_names"},
                    {
                        "DOMAIN": "wiser", "DATA": "data",
                        "dr": SimpleNamespace(async_get=lambda _hass: registry),
                        "get_hub_device_name": lambda _data: "Wiser HeatHub",
                    },
                )
                functions.update_hub_device_names(hass)
                if current_api:
                    lookup.assert_called_once_with(("wiser", "WiserHeat123"), "entry-id")
                else:
                    lookup.assert_called_once_with(identifiers={("wiser", "WiserHeat123")})
                registry.async_update_device.assert_called_once_with(
                    "hub-device", name="Wiser HeatHub"
                )
                self.assertFalse(data._wiser_show_hub_suffix)
                lookup.return_value = None
                registry.async_update_device.reset_mock()
                functions.update_hub_device_names(hass)
                registry.async_update_device.assert_not_called()


class ConfigFlowCompatibilityTest(unittest.TestCase):
    def test_connection_class_is_declared_only_in_manifest(self):
        """The deprecated ConfigFlow CONNECTION_CLASS must not be restored."""
        tree = ast.parse((COMPONENT / "config_flow.py").read_text())
        flow = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "WiserFlowHandler"
        )

        assignments = {
            target.id
            for node in flow.body
            if isinstance(node, (ast.Assign, ast.AnnAssign))
            for target in (
                node.targets if isinstance(node, ast.Assign) else [node.target]
            )
            if isinstance(target, ast.Name)
        }
        self.assertNotIn("CONNECTION_CLASS", assignments)

        manifest = json.loads((COMPONENT / "manifest.json").read_text())
        self.assertEqual(manifest["iot_class"], "local_polling")


if __name__ == "__main__":
    unittest.main()
