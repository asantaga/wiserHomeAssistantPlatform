"""Regression tests for Wiser sensor names without Home Assistant runtime deps."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/sensor.py"


def _module(name: str, **attributes: object) -> ModuleType:
    """Create and register a lightweight module stub."""
    module = ModuleType(name)
    module.__dict__.update(attributes)
    sys.modules[name] = module
    return module


def _load_sensor_module() -> ModuleType:
    """Load the sensor module with only the imports needed by this test."""
    _module("aioWiserHeatAPI")
    _module("aioWiserHeatAPI.const", TEXT_UNKNOWN="Unknown")
    _module("aioWiserHeatAPI.wiserhub", TEMP_OFF="Off")

    _module("homeassistant")
    _module("homeassistant.components")

    class SensorEntity:
        pass

    _module(
        "homeassistant.components.sensor",
        SensorDeviceClass=SimpleNamespace(),
        SensorStateClass=SimpleNamespace(),
        SensorEntity=SensorEntity,
    )
    _module(
        "homeassistant.const",
        ATTR_BATTERY_LEVEL="battery_level",
        LIGHT_LUX="lx",
        STATE_UNAVAILABLE="unavailable",
        STATE_UNKNOWN="unknown",
        UnitOfTemperature=SimpleNamespace(),
        UnitOfElectricCurrent=SimpleNamespace(),
        UnitOfElectricPotential=SimpleNamespace(),
        PERCENTAGE="%",
        UnitOfPower=SimpleNamespace(),
        UnitOfEnergy=SimpleNamespace(),
    )
    _module("homeassistant.core", HomeAssistant=object, callback=lambda func: func)
    _module("homeassistant.helpers")

    class CoordinatorEntity:
        def __init__(self, *args: object) -> None:
            pass

    _module(
        "homeassistant.helpers.update_coordinator", CoordinatorEntity=CoordinatorEntity
    )

    package = _module("wiser")
    package.__path__ = []
    _module(
        "wiser.const",
        DATA="data",
        DOMAIN="wiser",
        HOT_WATER="hot_water",
        MANUFACTURER="Drayton",
        MANUFACTURER_SCHNEIDER="Schneider Electric",
        SIGNAL_STRENGTH_ICONS={},
        VERSION="test",
    )
    _module(
        "wiser.helpers",
        get_device_name=lambda _data, device_id, device_type="device": (
            "Wiser HeatHub"
            if device_type == "HeatHub"
            else "Wiser iTRV Kitchen" if device_id else "Wiser HeatHub"
        ),
        get_identifier=lambda *_args: "identifier",
        get_unique_id=lambda *_args: "unique-id",
    )

    spec = importlib.util.spec_from_file_location("wiser.sensor", SOURCE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class WiserDeviceSignalSensorNameTest(unittest.TestCase):
    """Tests for controller and device signal sensor names."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.sensor_module = _load_sensor_module()

    def test_controller_signal_name_includes_hub_name(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserDeviceSignalSensor)
        sensor._device_id = 0
        sensor._data = SimpleNamespace(
            wiserhub=SimpleNamespace(system=SimpleNamespace(name="WiserHeat045XXX"))
        )

        self.assertEqual(sensor.name, "Wiser HeatHub WiserHeat045XXX Signal")

    def test_device_signal_name_is_unchanged(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserDeviceSignalSensor)
        sensor._device_id = 1
        sensor._data = SimpleNamespace(
            wiserhub=SimpleNamespace(system=SimpleNamespace(name="WiserHeat045XXX"))
        )

        self.assertEqual(sensor.name, "Wiser iTRV Kitchen Signal")


class WiserBatterySensorAvailabilityTest(unittest.TestCase):
    """Regression tests for battery availability when level text is absent."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.sensor_module = _load_sensor_module()

    def _sensor(self, *, level: str, voltage: float | None):
        sensor = object.__new__(self.sensor_module.WiserBatterySensor)
        sensor._device = SimpleNamespace(
            battery=SimpleNamespace(level=level, voltage=voltage)
        )
        return sensor

    def test_voltage_keeps_battery_available_when_level_is_unknown(self) -> None:
        sensor = self._sensor(level="Unknown", voltage=3.0)

        self.assertTrue(sensor.available)

    def test_unknown_level_and_voltage_keeps_battery_unavailable(self) -> None:
        sensor = self._sensor(level="Unknown", voltage=None)

        self.assertFalse(sensor.available)

    def test_known_level_keeps_battery_available_without_voltage(self) -> None:
        sensor = self._sensor(level="Normal", voltage=None)

        self.assertTrue(sensor.available)


class WiserUFHMeasuredTemperatureTest(unittest.TestCase):
    """Tests for the UFH controller measured-temperature sensor."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.sensor_module = _load_sensor_module()

    def test_measured_temperature_uses_ufh_device_value(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserLTSTempSensor)
        sensor._lts_sensor_type = "ufh_measured_temp"
        sensor._sensor_type = "UFH Measured Temperature"
        sensor._device_id = 42
        sensor._data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                devices=SimpleNamespace(
                    get_by_id=lambda device_id: SimpleNamespace(
                        current_temperature=21.5
                    )
                )
            )
        )
        sensor.async_write_ha_state = lambda: None

        sensor._handle_coordinator_update()

        self.assertEqual(sensor.native_value, 21.5)
