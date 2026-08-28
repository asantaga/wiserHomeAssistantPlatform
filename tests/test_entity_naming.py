"""Regression tests for Home Assistant entity naming conventions."""

import ast
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

    def test_all_entity_unique_ids_are_uuid_backed(self) -> None:
        uuid_helpers = {"get_unique_id", "get_uuid_unique_id"}
        for filename in ENTITY_BASE_CLASSES:
            tree = ast.parse((COMPONENT_PATH / filename).read_text())
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name != "unique_id":
                    continue
                called_names = {
                    call.func.id
                    for call in ast.walk(node)
                    if isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name)
                }
                self.assertTrue(
                    called_names & uuid_helpers,
                    f"{filename}:{node.lineno} does not generate a UUID",
                )

    def test_room_climate_has_a_concise_control_name(self) -> None:
        tree = ast.parse((COMPONENT_PATH / "climate.py").read_text())
        wiser_room = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "WiserRoom"
        )
        name_method = next(
            node
            for node in wiser_room.body
            if isinstance(node, ast.FunctionDef) and node.name == "name"
        )
        return_statement = next(
            node for node in name_method.body if isinstance(node, ast.Return)
        )
        self.assertIsInstance(return_statement.value, ast.Constant)
        self.assertEqual(return_statement.value.value, "Heating")

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

        name_method = next(
            node
            for node in smart_plug.body
            if isinstance(node, ast.FunctionDef) and node.name == "name"
        )
        returned = next(
            node.value for node in name_method.body if isinstance(node, ast.Return)
        )
        self.assertEqual(returned.value, "Outlet")
