"""Regression tests for Home Assistant entity naming conventions."""

import ast
import json
from pathlib import Path
import unittest


COMPONENT_PATH = Path(__file__).parents[1] / "custom_components/wiser"

ENTITY_BASE_CLASSES = {
    "binary_sensor.py": {
        "BaseBinarySensor",
        "SystemBinarySensor",
        "RoomBinarySensor",
    },
    "button.py": {"WiserButton"},
    "climate.py": {"WiserTempProbe", "WiserRoom", "WiserHotWater"},
    "cover.py": {"WiserShutter"},
    "light.py": {"WiserLight"},
    "number.py": {
        "WiserAwayModeTempNumber",
        "WiserFloorTempSensorNumber",
        "WiserDiscomfortIndoorTempNumber",
        "WiserDiscomfortOutdoorTempNumber",
    },
    "select.py": {"WiserSelectEntity"},
    "sensor.py": {"WiserSensor"},
    "switch.py": {"WiserSwitch"},
}


class EntityNamingTest(unittest.TestCase):
    """Ensure entity names rely on Home Assistant's device context."""

    def test_entity_bases_enable_modern_naming(self) -> None:
        for filename, class_names in ENTITY_BASE_CLASSES.items():
            tree = ast.parse((COMPONENT_PATH / filename).read_text())
            classes = {
                node.name: node
                for node in tree.body
                if isinstance(node, ast.ClassDef)
            }
            for class_name in class_names:
                assignments = {
                    target.id: statement.value
                    for statement in classes[class_name].body
                    if isinstance(statement, ast.Assign)
                    for target in statement.targets
                    if isinstance(target, ast.Name)
                }
                value = assignments.get("_attr_has_entity_name")
                self.assertIsInstance(value, ast.Constant, class_name)
                self.assertTrue(value.value, class_name)

    def test_names_do_not_embed_device_or_room_names(self) -> None:
        forbidden_helpers = {"get_device_name", "get_room_name"}
        for filename in ENTITY_BASE_CLASSES:
            tree = ast.parse((COMPONENT_PATH / filename).read_text())
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name != "name":
                    continue
                called_names = {
                    call.func.id
                    for call in ast.walk(node)
                    if isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                }
                self.assertFalse(
                    called_names & forbidden_helpers,
                    f"{filename}:{node.lineno} embeds device context",
                )

    def test_unique_ids_do_not_depend_on_new_entity_names(self) -> None:
        for filename in ENTITY_BASE_CLASSES:
            tree = ast.parse((COMPONENT_PATH / filename).read_text())
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name != "unique_id":
                    continue
                name_reads = [
                    attribute
                    for attribute in ast.walk(node)
                    if isinstance(attribute, ast.Attribute)
                    and isinstance(attribute.value, ast.Name)
                    and attribute.value.id == "self"
                    and attribute.attr == "name"
                ]
                self.assertEqual(
                    name_reads,
                    [],
                    f"{filename}:{node.lineno} unique ID depends on entity name",
                )

    def test_room_climate_has_a_translated_control_name(self) -> None:
        tree = ast.parse((COMPONENT_PATH / "climate.py").read_text())
        wiser_room = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "WiserRoom"
        )
        assignments = {
            target.id: statement.value
            for statement in wiser_room.body
            if isinstance(statement, ast.Assign)
            for target in statement.targets
            if isinstance(target, ast.Name)
        }
        translation_key = assignments.get("_attr_translation_key")
        self.assertIsInstance(translation_key, ast.Constant)
        self.assertEqual(translation_key.value, "heating")
        self.assertFalse(
            any(
                isinstance(node, ast.FunctionDef) and node.name == "name"
                for node in wiser_room.body
            )
        )

    def test_room_climate_translation_is_available(self) -> None:
        expected_names = {
            "strings.json": "Heating",
            "translations/en.json": "Heating",
            "translations/de.json": "Heizung",
            "translations/fr.json": "Chauffage",
        }
        for filename, expected_name in expected_names.items():
            translations = json.loads((COMPONENT_PATH / filename).read_text())
            self.assertEqual(
                translations["entity"]["climate"]["heating"]["name"],
                expected_name,
                filename,
            )

    def test_smart_plug_control_is_presented_as_an_outlet(self) -> None:
        tree = ast.parse((COMPONENT_PATH / "switch.py").read_text())
        smart_plug = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef)
            and node.name == "WiserSmartPlugSwitch"
        )
        device_class = next(
            statement.value
            for statement in smart_plug.body
            if isinstance(statement, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "_attr_device_class"
                for target in statement.targets
            )
        )
        self.assertIsInstance(device_class, ast.Attribute)
        self.assertEqual(device_class.attr, "OUTLET")

        init_method = next(
            node
            for node in smart_plug.body
            if isinstance(node, ast.FunctionDef) and node.name == "__init__"
        )
        self.assertTrue(
            any(
                isinstance(node, ast.Assign)
                and any(
                    isinstance(target, ast.Attribute)
                    and target.attr == "_attr_translation_key"
                    for target in node.targets
                )
                and isinstance(node.value, ast.Constant)
                and node.value.value == "outlet"
                for node in init_method.body
            )
        )

    def test_entity_translation_catalogs_have_matching_keys(self) -> None:
        """Every supported language must expose the same entity labels."""
        catalogs = {
            filename: json.loads((COMPONENT_PATH / filename).read_text())["entity"]
            for filename in (
                "strings.json",
                "translations/en.json",
                "translations/de.json",
                "translations/fr.json",
            )
        }
        expected = {
            domain: set(entries)
            for domain, entries in catalogs["strings.json"].items()
        }
        for filename, catalog in catalogs.items():
            self.assertEqual(
                {domain: set(entries) for domain, entries in catalog.items()},
                expected,
                filename,
            )

    def test_standard_measurements_do_not_duplicate_ha_translations(self) -> None:
        """Device classes let Home Assistant supply standard measurement names."""
        sensor_translations = json.loads(
            (COMPONENT_PATH / "strings.json").read_text()
        )["entity"]["sensor"]
        for key in (
            "battery",
            "current",
            "humidity",
            "illuminance",
            "power",
            "temperature",
            "voltage",
        ):
            self.assertNotIn(key, sensor_translations)

        sensor_source = (COMPONENT_PATH / "sensor.py").read_text()
        self.assertNotIn("self._attr_name = None", sensor_source)

    def test_custom_integration_translations_use_resolved_text(self) -> None:
        """Custom integrations cannot use Core's build-time translation references."""
        translations = json.loads(
            (COMPONENT_PATH / "translations/en.json").read_text()
        )
        expected = {
            ("select", "mode"): "Mode",
            ("switch", "identify"): "Identify",
            ("switch", "outlet"): "Outlet",
            ("binary_sensor", "is_open"): "Open",
            ("binary_sensor", "is_closed"): "Closed",
            ("binary_sensor", "active"): "Active",
            ("sensor", "target_temperature"): "Target temperature",
        }
        for (domain, key), expected_name in expected.items():
            self.assertEqual(
                translations["entity"][domain][key]["name"], expected_name
            )
        for filename in (
            "translations/en.json",
            "translations/de.json",
            "translations/fr.json",
        ):
            self.assertNotIn("[%key:", (COMPONENT_PATH / filename).read_text())
