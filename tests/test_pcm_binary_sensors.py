"""Regression tests for PCM and RMB system binary sensors."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from types import SimpleNamespace
import unittest


BINARY_SENSOR_SOURCE = (
    Path(__file__).parents[1] / "custom_components/wiser/binary_sensor.py"
)


class SystemFeatureBinarySensorTest(unittest.TestCase):
    """Check system feature detection and entity setup wiring."""

    @classmethod
    def setUpClass(cls) -> None:
        source = BINARY_SENSOR_SOURCE.read_text(encoding="utf-8")
        tree = ast.parse(source)
        wanted = {
            "_supports_v2_system_property",
            "_supports_rmb_follow_smart",
        }
        functions = [
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name in wanted
        ]
        namespace = {}
        exec(
            compile(
                ast.Module(body=functions, type_ignores=[]),
                str(BINARY_SENSOR_SOURCE),
                "exec",
            ),
            namespace,
        )
        cls.supports_property = staticmethod(
            namespace["_supports_v2_system_property"]
        )
        cls.supports_rmb = staticmethod(namespace["_supports_rmb_follow_smart"])
        cls.tree = tree

    def test_pcm_properties_support_false_as_a_present_value(self) -> None:
        data = SimpleNamespace(
            hub_version=2,
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(pcm_online=False, can_activate_pcm=False)
            ),
        )

        self.assertTrue(self.supports_property(data, "pcm_online"))
        self.assertTrue(self.supports_property(data, "can_activate_pcm"))

    def test_pcm_properties_are_not_supported_when_missing_or_on_v1(self) -> None:
        data = SimpleNamespace(
            hub_version=2, wiserhub=SimpleNamespace(system=SimpleNamespace())
        )
        self.assertFalse(self.supports_property(data, "pcm_online"))
        self.assertFalse(self.supports_property(data, "can_activate_pcm"))

        data.hub_version = 1
        data.wiserhub.system.pcm_online = True
        self.assertFalse(self.supports_property(data, "pcm_online"))

    def test_rmb_detection_uses_api_property_casing(self) -> None:
        data = SimpleNamespace(
            hub_version=2,
            wiserhub=SimpleNamespace(system=SimpleNamespace(RMB_follow_smart=False)),
        )
        self.assertTrue(self.supports_rmb(data))

        data.wiserhub.system = SimpleNamespace(rmb_follow_smart=True)
        self.assertFalse(self.supports_rmb(data))

    def test_setup_registers_pcm_and_rmb_entities_behind_property_guards(self) -> None:
        setup = next(
            node
            for node in self.tree.body
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "async_setup_entry"
        )
        expected = {
            "pcm_online": "WiserPCMOnline",
            "can_activate_pcm": "WiserCanActivatePCM",
        }
        for property_name, entity_class in expected.items():
            with self.subTest(property_name=property_name):
                guard = next(
                    node
                    for node in ast.walk(setup)
                    if isinstance(node, ast.If)
                    and isinstance(node.test, ast.Call)
                    and isinstance(node.test.func, ast.Name)
                    and node.test.func.id == "_supports_v2_system_property"
                    and len(node.test.args) == 2
                    and isinstance(node.test.args[1], ast.Constant)
                    and node.test.args[1].value == property_name
                )
                calls = {
                    node.func.id
                    for node in ast.walk(guard)
                    if isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                }
                self.assertIn(entity_class, calls)

        rmb_guard = next(
            node
            for node in ast.walk(setup)
            if isinstance(node, ast.If)
            and isinstance(node.test, ast.Call)
            and isinstance(node.test.func, ast.Name)
            and node.test.func.id == "_supports_rmb_follow_smart"
        )
        rmb_calls = {
            node.func.id
            for node in ast.walk(rmb_guard)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
        }
        self.assertIn("WiserRMBFollowSmart", rmb_calls)

    def test_entity_translations_exist(self) -> None:
        strings_path = BINARY_SENSOR_SOURCE.parents[0] / "strings.json"
        french_path = BINARY_SENSOR_SOURCE.parents[0] / "translations/fr.json"
        for path in (strings_path, french_path):
            with self.subTest(path=path.name):
                translations = json.loads(path.read_text(encoding="utf-8"))[
                    "entity"
                ]["binary_sensor"]
                self.assertIn("pcm_online", translations)
                self.assertIn("can_activate_pcm", translations)
                self.assertIn("rmb_follow_smart", translations)


if __name__ == "__main__":
    unittest.main()
