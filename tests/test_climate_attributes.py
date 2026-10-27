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

    def test_custom_more_info_is_guarded_by_ui_option(self) -> None:
        custom_assignment = next(
            node
            for node in ast.walk(self.method)
            if isinstance(node, ast.Assign)
            and "custom_ui_more_info" in attribute_assignments([node])
        )
        parent_guard = next(
            node
            for node in self.method.body
            if isinstance(node, ast.If)
            and custom_assignment in set(ast.walk(node))
        )
        self.assertIn("wiser_climate_more_info", ast.unparse(parent_guard.test))


class ClimateMoreInfoFrontendTest(unittest.TestCase):
    """Keep the optional control tied to native HA behaviour and Wiser data."""

    def setUp(self) -> None:
        self.source = (
            COMPONENT_PATH / "frontend" / "wiser-climate-more-info.js"
        ).read_text()

    def test_reuses_native_temperature_control(self) -> None:
        self.assertIn('"ha-state-control-climate-temperature"', self.source)
        self.assertIn("this._temperatureControl.stateObj = stateObj", self.source)
        self.assertIn("preventInteractionOnScroll", self.source)
        self.assertIn('stateObj.attributes.current_humidity', self.source)
        self.assertIn('"current_humidity"', self.source)

    def test_applies_passive_and_demand_styling(self) -> None:
        for value in (
            "percentage_demand",
            "is_passive",
            "--passive-auto-color",
            "--passive-heat-color",
            "--radial-glow-color",
            "--label-text-highlight-color",
            "--wiser-extra-info-text",
        ):
            self.assertIn(value, self.source)

    def test_preserves_native_climate_actions(self) -> None:
        self.assertIn('"set_hvac_mode"', self.source)
        self.assertIn('"set_preset_mode"', self.source)

    def test_coordinator_captures_the_config_entry_option(self) -> None:
        coordinator = (COMPONENT_PATH / "coordinator.py").read_text()
        self.assertIn(
            "self.wiser_climate_more_info = config_entry.options.get(",
            coordinator,
        )
        self.assertIn("CONF_WISER_CLIMATE_MORE_INFO, False", coordinator)


if __name__ == "__main__":
    unittest.main()
