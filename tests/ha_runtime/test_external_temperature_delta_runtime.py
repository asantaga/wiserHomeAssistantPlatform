"""Exercise the delta sensor through Home Assistant's real state conversion."""

import ast
from datetime import timedelta
import math
from pathlib import Path
from types import SimpleNamespace
import unittest

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity


def load_delta_sensor():
    """Load the production class without importing unrelated integration platforms.

    HA's actual SensorEntity, CoordinatorEntity and unit converters are used.
    Only hub data and the naming mixin are replaced; neither controls conversion.
    """
    source = Path(__file__).parents[2] / "custom_components/wiser/sensor.py"
    node = next(
        node for node in ast.parse(source.read_text()).body
        if isinstance(node, ast.ClassDef)
        and node.name == "WiserExternalTemperatureDeltaSensor"
    )
    namespace = {
        "WiserEntityMixin": type("NamingMixin", (), {}),
        "CoordinatorEntity": CoordinatorEntity,
        "SensorEntity": SensorEntity,
        "SensorDeviceClass": SensorDeviceClass,
        "SensorStateClass": SensorStateClass,
        "EntityCategory": EntityCategory,
        "UnitOfTemperature": UnitOfTemperature,
        "callback": callback,
        "math": math,
        "timedelta": timedelta,
    }
    exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), namespace)
    return namespace[node.name]


class ExternalTemperatureDeltaRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sensor_class = load_delta_sensor()

    def setUp(self):
        self.external = 22.0
        self.room = SimpleNamespace(current_temperature=20.0)
        data = SimpleNamespace(
            config_entry=None,
            last_update_success=True,
            external_room_control=SimpleNamespace(
                external_temperature=lambda _room_id: self.external,
            ),
            wiserhub=SimpleNamespace(rooms=SimpleNamespace(
                get_by_id=lambda _room_id: self.room,
            )),
        )
        self.sensor = self.sensor_class(data, 1)
        self.sensor.entity_id = "sensor.test_external_temperature_delta"

    def test_fahrenheit_display_converts_difference_without_32_degree_offset(self):
        # This is the option set by HA when a user selects the displayed unit.
        self.sensor._sensor_option_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
        for external, expected in ((22.0, 3.6), (18.0, -3.6), (20.0, 0.0)):
            with self.subTest(external=external):
                self.external = external
                self.assertEqual(self.sensor.device_class, SensorDeviceClass.TEMPERATURE_DELTA)
                self.assertEqual(self.sensor.unit_of_measurement, UnitOfTemperature.FAHRENHEIT)
                self.assertAlmostEqual(self.sensor.state, expected)
                self.assertEqual(self.sensor.native_value, external - 20.0)

    def test_celsius_display_keeps_native_difference(self):
        self.sensor._sensor_option_unit_of_measurement = UnitOfTemperature.CELSIUS
        self.assertEqual(self.sensor.state, 2.0)
        self.assertEqual(self.sensor.state_class, SensorStateClass.MEASUREMENT)

    def test_missing_measurement_is_not_converted_to_a_number(self):
        self.sensor._sensor_option_unit_of_measurement = UnitOfTemperature.FAHRENHEIT
        self.external = None
        self.assertIsNone(self.sensor.state)
        self.assertFalse(self.sensor.available)


if __name__ == "__main__":
    unittest.main()
