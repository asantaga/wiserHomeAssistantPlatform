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
    _module("aioWiserHeatAPI.wiserhub", TEMP_MINIMUM=5, TEMP_OFF="Off")

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
        get_hub_device_info=lambda _data: {"identifiers": {("wiser", "hub")}},
        get_unique_id=lambda *_args: "unique-id",
    )
    class WiserEntityMixin:
        pass

    _module("wiser.entity", WiserEntityMixin=WiserEntityMixin)
    _module(
        "wiser.temperature",
        room_target_temperature=lambda room, frost_temp, off_temp: (
            frost_temp
            if room.mode == "Off" or room.current_target_temperature == off_temp
            else room.current_target_temperature
        ),
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

    def test_hub_signal_uses_entity_only_name(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserDeviceSignalSensor)
        sensor._device_id = 0
        sensor._data = SimpleNamespace(
            wiserhub=SimpleNamespace(system=SimpleNamespace(name="WiserHeat045XXX"))
        )

        self.assertEqual(sensor.name, "Signal")

    def test_device_signal_uses_entity_only_name(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserDeviceSignalSensor)
        sensor._device_id = 1
        sensor._data = SimpleNamespace(
            wiserhub=SimpleNamespace(system=SimpleNamespace(name="WiserHeat045XXX"))
        )

        self.assertEqual(sensor.name, "Signal")

    def test_sensor_uses_modern_home_assistant_naming(self) -> None:
        self.assertTrue(self.sensor_module.WiserSensor._attr_has_entity_name)

    def test_controller_signal_belongs_to_physical_hub(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserDeviceSignalSensor)
        sensor._device_id = 0
        sensor._data = object()

        self.assertEqual(sensor.device_info, {"identifiers": {("wiser", "hub")}})


class WiserLTSOpenthermSensorDeviceTest(unittest.TestCase):
    """Tests for OpenTherm LTS sensor device assignment."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.sensor_module = _load_sensor_module()

    def test_opentherm_sensor_belongs_to_physical_hub(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserLTSOpenthermSensor)
        sensor._data = object()

        self.assertEqual(sensor.device_info, {"identifiers": {("wiser", "hub")}})
