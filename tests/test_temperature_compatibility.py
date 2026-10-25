"""Regression tests for Home Assistant temperature property compatibility."""

import ast
from pathlib import Path
import unittest


COMPONENT = Path(__file__).parents[1] / "custom_components/wiser"


def _classes(filename):
    tree = ast.parse((COMPONENT / filename).read_text())
    return {
        node.name: node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
    }


def _is_missing_native_guard(node, base_name, native_name):
    test = node.test if isinstance(node, ast.If) else None
    call = test.operand if isinstance(test, ast.UnaryOp) else None
    return bool(
        isinstance(test, ast.UnaryOp)
        and isinstance(test.op, ast.Not)
        and isinstance(call, ast.Call)
        and isinstance(call.func, ast.Name)
        and call.func.id == "hasattr"
        and len(call.args) == 2
        and isinstance(call.args[0], ast.Name)
        and call.args[0].id == base_name
        and isinstance(call.args[1], ast.Constant)
        and call.args[1].value == native_name
    )


def _assert_property_alias(test, class_node, base_name, legacy_name):
    native_name = f"native_{legacy_name}"
    methods = {
        node.name
        for node in class_node.body
        if isinstance(node, ast.FunctionDef)
    }
    test.assertIn(native_name, methods)
    test.assertNotIn(legacy_name, methods)

    guarded_aliases = [
        node
        for node in class_node.body
        if _is_missing_native_guard(node, base_name, native_name)
        and any(
            isinstance(statement, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == legacy_name
                for target in statement.targets
            )
            and isinstance(statement.value, ast.Name)
            and statement.value.id == native_name
            for statement in node.body
        )
    ]
    test.assertEqual(len(guarded_aliases), 1)


class TemperatureCompatibilityTest(unittest.TestCase):
    def test_climate_entities_use_native_properties_with_legacy_aliases(self):
        classes = _classes("climate.py")
        expected = {
            "WiserTempProbe": {
                "current_temperature",
                "target_temperature_high",
                "target_temperature_low",
                "temperature_unit",
            },
            "WiserRoom": {
                "current_temperature",
                "target_temperature",
                "target_temperature_high",
                "target_temperature_low",
                "temperature_unit",
            },
            "WiserHotWater": {
                "current_temperature",
                "target_temperature_high",
                "target_temperature_low",
                "temperature_unit",
            },
        }

        for class_name, properties in expected.items():
            for property_name in properties:
                with self.subTest(class_name=class_name, property=property_name):
                    _assert_property_alias(
                        self,
                        classes[class_name],
                        "ClimateEntity",
                        property_name,
                    )

    def test_water_heater_uses_native_properties_with_legacy_aliases(self):
        water_heater = _classes("opentherm_hot_water.py")[
            "WiserOpenThermHotWater"
        ]
        for property_name in (
            "current_temperature",
            "target_temperature",
        ):
            with self.subTest(property=property_name):
                _assert_property_alias(
                    self,
                    water_heater,
                    "WaterHeaterEntity",
                    property_name,
                )

        assignments = {
            target.id: statement.value
            for statement in water_heater.body
            if isinstance(statement, ast.Assign)
            for target in statement.targets
            if isinstance(target, ast.Name)
        }
        self.assertIn("_attr_native_temperature_unit", assignments)
        self.assertNotIn("_attr_temperature_unit", assignments)
        guarded_legacy_unit = [
            node
            for node in water_heater.body
            if _is_missing_native_guard(
                node,
                "WaterHeaterEntity",
                "native_temperature_unit",
            )
            and any(
                isinstance(statement, ast.Assign)
                and any(
                    isinstance(target, ast.Name)
                    and target.id == "_attr_temperature_unit"
                    for target in statement.targets
                )
                for statement in node.body
            )
        ]
        self.assertEqual(len(guarded_legacy_unit), 1)

    def test_internal_hot_water_logic_uses_native_properties(self):
        climate_source = (COMPONENT / "climate.py").read_text()
        opentherm_source = (COMPONENT / "opentherm_hot_water.py").read_text()

        self.assertNotIn("self.current_temperature", climate_source)
        self.assertNotIn("self.target_temperature_high", climate_source)
        self.assertNotIn("self.target_temperature_low", climate_source)
        self.assertNotIn("self.current_temperature", opentherm_source)
        self.assertNotIn("self.target_temperature", opentherm_source)


if __name__ == "__main__":
    unittest.main()
