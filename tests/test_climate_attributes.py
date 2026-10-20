"""Regression tests for room climate state attributes."""

import ast
from pathlib import Path
import unittest


COMPONENT_PATH = Path(__file__).parents[1] / "custom_components/wiser"


def attribute_assignments(nodes):
    """Return the attrs keys assigned by the given nodes."""
    return [
        target.slice.value
        for node in nodes
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Subscript)
        and isinstance(target.value, ast.Name)
        and target.value.id == "attrs"
        and isinstance(target.slice, ast.Constant)
    ]


class RoomClimateAttributesTest(unittest.TestCase):
    """Ensure only OpenTherm-specific room attributes need OpenTherm."""

    def setUp(self) -> None:
        tree = ast.parse((COMPONENT_PATH / "climate.py").read_text())
        wiser_room = next(
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == "WiserRoom"
        )
        self.method = next(
            node
            for node in wiser_room.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "extra_state_attributes"
        )
        self.opentherm_guard = next(
            node
            for node in self.method.body
            if isinstance(node, ast.If) and "opentherm" in ast.unparse(node.test)
        )

    def test_percentage_demand_is_reported_without_opentherm(self) -> None:
        self.assertIn("percentage_demand", attribute_assignments(self.method.body))
        self.assertNotIn(
            "percentage_demand",
            attribute_assignments(ast.walk(self.opentherm_guard)),
        )

    def test_demand_type_is_reported_only_with_opentherm(self) -> None:
        guarded = set(ast.walk(self.opentherm_guard))
        unguarded = [node for node in ast.walk(self.method) if node not in guarded]
        self.assertIn("demand_type", attribute_assignments(guarded))
        self.assertNotIn("demand_type", attribute_assignments(unguarded))


if __name__ == "__main__":
    unittest.main()
