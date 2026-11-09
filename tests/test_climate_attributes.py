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
        self.assertIn("wiser_climate_controls", ast.unparse(parent_guard.test))


class ClimateControlsFrontendTest(unittest.TestCase):
    """Keep the optional controls tied to native HA behaviour and Wiser data."""

    def setUp(self) -> None:
        self.source = (
            COMPONENT_PATH / "frontend" / "wiser-climate-controls.js"
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

    def test_applies_same_styling_to_native_thermostat_cards(self) -> None:
        self.assertIn("installNativeTemperatureControlStyling", self.source)
        self.assertIn("controlClass.prototype.updated", self.source)
        self.assertIn("wiserClimateControlsEnabled(this.stateObj)", self.source)
        self.assertIn("applyWiserClimateStyle(this, this.stateObj)", self.source)
        self.assertIn("clearWiserClimateStyle(this)", self.source)

    def test_extra_info_is_not_clipped_by_native_label_overflow(self) -> None:
        self.assertIn(".info::after", self.source)
        self.assertIn("--extra-info-margin-top, -6px", self.source)
        self.assertIn("max-width: 90%", self.source)
        self.assertNotIn(".info > p:last-of-type::after", self.source)

    def test_extra_info_uses_passive_mode_or_generic_demand(self) -> None:
        self.assertIn("attributes.passive_control_type", self.source)
        self.assertIn('return `Demand · ${demandForState(stateObj)}%`', self.source)
        self.assertNotIn("attributes?.demand_type", self.source)

    def test_hot_water_uses_native_water_heater_state_colours(self) -> None:
        for value in (
            "wiser_hot_water",
            "Heating water",
            "--state-water_heater-active-color",
            "--state-active-color",
            "--state-inactive-color",
            "--state-climate-heat-color",
        ):
            self.assertIn(value, self.source)
        self.assertNotIn("--hot-water-heating-color", self.source)
        self.assertNotIn("--hot-water-idle-color", self.source)

    def test_hot_water_climate_opts_into_shared_more_info(self) -> None:
        climate_source = (COMPONENT_PATH / "climate.py").read_text()
        wiser_hot_water = climate_source.partition("class WiserHotWater(")[2]

        self.assertIn('attrs["wiser_hot_water"] = True', wiser_hot_water)
        self.assertIn(
            'attrs["custom_ui_more_info"] = "wiser-climate-more-info"',
            wiser_hot_water,
        )
        self.assertIn("if self._data.wiser_climate_controls:", wiser_hot_water)

    def test_thermostat_card_supports_tile_style_inline_features(self) -> None:
        self.assertIn('"hui-thermostat-card"', self.source)
        self.assertIn("renderInlineThermostatFeatures", self.source)
        self.assertIn('config.features_position !== "inline"', self.source)
        self.assertIn("calculateFeatureLayout", self.source)
        self.assertIn('"climate-hvac-modes": "hvac_modes"', self.source)
        self.assertIn('feature.style === "dropdown"', self.source)
        self.assertIn("configuredModes.filter", self.source)
        self.assertIn("minimum: Math.max(buttons * 50, 60)", self.source)
        self.assertIn(
            'slot.style.flex = `${layout.units} 1 ${layout.minimum}px`', self.source
        )
        self.assertIn("isThermostatEditorPreview", self.source)
        self.assertIn("element?.preview === true", self.source)
        self.assertIn("element?.editMode === true", self.source)
        self.assertIn('max-width: 360px', self.source)
        self.assertIn('row.toggleAttribute("data-editor-preview"', self.source)
        self.assertIn('bottom.style.display = "none"', self.source)
        self.assertIn("bottom.columns = 1", self.source)
        self.assertNotIn("thermostatFeatureObservers", self.source)

    def test_preset_select_shows_responsive_boost_time_remaining(self) -> None:
        self.assertIn('"hui-climate-preset-modes-card-feature"', self.source)
        self.assertIn("boostMinutesRemaining", self.source)
        self.assertIn("attributes.boost_end", self.source)
        self.assertIn("attributes.boost_time_remaining", self.source)
        self.assertIn("addBoostCountdownOption", self.source)
        self.assertIn("getBoostPresetDisplayMode", self.source)
        self.assertIn('width >= 180 ? "full"', self.source)
        self.assertIn('width >= 105 ? "compact"', self.source)
        self.assertIn("__wiserBoostCountdownResizeObserver", self.source)
        self.assertIn("__wiserBoostCountdownTimer", self.source)
        self.assertIn("installBoostPresetEnhancement", self.source)
        self.assertIn(
            "feature.__wiserBoostCountdownResizeObserver?.disconnect()", self.source
        )
        self.assertNotIn("select.options =", self.source)
        self.assertNotIn("--wiser-boost-remaining", self.source)

    def test_thermostat_enhancement_refreshes_existing_browser_session(self) -> None:
        self.assertIn("__wiserInlineLayoutUpdateInstalled", self.source)
        self.assertIn("__wiserRenderInlineFeatures", self.source)
        self.assertIn("this.__wiserRenderInlineFeatures?.()", self.source)
        self.assertNotIn(
            "if (!cardClass || cardClass.prototype.__wiserInlineGridSizingInstalled) return;",
            self.source,
        )

    def test_thermostat_editor_exposes_native_feature_position_form(self) -> None:
        self.assertIn('"hui-thermostat-card-editor"', self.source)
        self.assertIn("createFeaturePositionSchema", self.source)
        self.assertIn('options: ["bottom", "inline"]', self.source)
        self.assertIn("tile_features_position_${value}.svg", self.source)
        self.assertIn(
            "Uses available width dynamically and wraps when needed", self.source
        )
        self.assertIn("renderThermostatFeaturePositionEditor", self.source)

    def test_preserves_native_climate_actions(self) -> None:
        self.assertIn('"set_hvac_mode"', self.source)
        self.assertIn('"set_preset_mode"', self.source)

    def test_coordinator_captures_the_config_entry_option(self) -> None:
        coordinator = (COMPONENT_PATH / "coordinator.py").read_text()
        self.assertIn(
            "self.wiser_climate_controls = config_entry.options.get(",
            coordinator,
        )
        self.assertIn("CONF_WISER_CLIMATE_CONTROLS, False", coordinator)


if __name__ == "__main__":
    unittest.main()
