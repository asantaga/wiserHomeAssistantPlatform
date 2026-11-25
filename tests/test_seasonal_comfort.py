"""Regression tests for seasonal comfort controls and weather sensors."""

from types import SimpleNamespace
import unittest
from unittest.mock import Mock

from test_sensor import _load_sensor_module


class WiserWeatherSensorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_sensor_module()

    def setUp(self):
        self.data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(
                    name="WiserHeat123456",
                    weather=SimpleNamespace(
                        temperature=-25.0, next_day_2pm_temperature=12.5
                    ),
                ),
                rooms=SimpleNamespace(get_by_device_id=lambda _: None),
            )
        )

    def test_only_current_temperature_has_measurement_statistics(self):
        for key, expected in (
            ("temperature", "measurement"),
            ("next_day_2pm_temperature", None),
        ):
            with self.subTest(sensor_type=key):
                sensor = self.module.WiserLTSWeatherSensor(self.data, 0, key)
                self.assertEqual(getattr(sensor, "state_class", None), expected)
                self.assertEqual(sensor.device_class, "temperature")
                self.assertEqual(sensor.native_unit_of_measurement, "°C")

    def test_weather_readings_update_and_tolerate_missing_data(self):
        for key, expected in (
            ("temperature", -25.0), ("next_day_2pm_temperature", 12.5)
        ):
            with self.subTest(sensor_type=key):
                sensor = self.module.WiserLTSWeatherSensor(self.data, 0, key)
                sensor.async_write_ha_state = Mock()
                sensor._handle_coordinator_update()
                self.assertEqual(sensor.native_value, expected)
                weather = self.data.wiserhub.system.weather
                self.data.wiserhub.system.weather = None
                sensor._handle_coordinator_update()
                self.assertIsNone(sensor.native_value)
                self.data.wiserhub.system.weather = weather
