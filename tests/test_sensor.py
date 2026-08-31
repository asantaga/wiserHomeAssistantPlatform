"""Regression tests for Wiser sensor names without Home Assistant runtime deps."""

from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock


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
        SensorStateClass=SimpleNamespace(MEASUREMENT="measurement"),
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
        def __init__(self, coordinator, *args: object) -> None:
            self.coordinator = coordinator

        @property
        def available(self):
            return self.coordinator.last_update_success

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
        get_device_area_info=lambda _data, _device_id: {},
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

        self.assertEqual(sensor._attr_translation_key, "signal")

    def test_device_signal_uses_entity_only_name(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserDeviceSignalSensor)
        sensor._device_id = 1
        sensor._data = SimpleNamespace(
            wiserhub=SimpleNamespace(system=SimpleNamespace(name="WiserHeat045XXX"))
        )

        self.assertEqual(sensor._attr_translation_key, "signal")

    def test_sensor_uses_modern_home_assistant_naming(self) -> None:
        self.assertTrue(self.sensor_module.WiserSensor._attr_has_entity_name)

    def test_room_measurements_do_not_expose_lts_implementation_detail(self) -> None:
        room = SimpleNamespace(name="Andys Bedroom")
        roomstat = SimpleNamespace(room_id=1)
        data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                devices=SimpleNamespace(get_by_id=lambda _device_id: roomstat),
                rooms=SimpleNamespace(
                    get_by_id=lambda _room_id: room,
                    get_by_device_id=lambda _device_id: room,
                ),
                system=SimpleNamespace(name="WiserHeat123456"),
            )
        )

        temperature = self.sensor_module.WiserLTSTempSensor(
            data, 1, sensor_type="current_temp"
        )
        target = self.sensor_module.WiserLTSTempSensor(
            data, 1, sensor_type="current_target_temp"
        )
        humidity = self.sensor_module.WiserLTSHumiditySensor(data, 2)
        demand = self.sensor_module.WiserLTSDemandSensor(data, 1, "room")

        for sensor in (temperature, target, humidity, demand):
            self.assertNotIn("_attr_name", sensor.__dict__)
            self.assertTrue(sensor._sensor_type.startswith("LTS "))
        self.assertIsNone(getattr(temperature, "_attr_translation_key", None))
        self.assertEqual(target._attr_translation_key, "target_temperature")
        self.assertIsNone(getattr(humidity, "_attr_translation_key", None))
        self.assertEqual(demand._attr_translation_key, "heating_demand")

    def test_heating_demand_is_not_classified_as_power_factor(self) -> None:
        """A percentage heating demand is not an electrical power factor."""
        demand_class = next(
            node
            for node in ast.parse(SOURCE_PATH.read_text()).body
            if isinstance(node, ast.ClassDef)
            and node.name == "WiserLTSDemandSensor"
        )
        self.assertNotIn(
            "POWER_FACTOR",
            ast.unparse(demand_class),
        )

    def test_controller_signal_belongs_to_physical_hub(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserDeviceSignalSensor)
        sensor._device_id = 0
        sensor._data = object()

        self.assertEqual(sensor.device_info, {"identifiers": {("wiser", "hub")}})

    def test_hub_v2_setup_does_not_create_duplicate_equipment_readings(self) -> None:
        setup_source = SOURCE_PATH.read_text().split("class WiserSensor", 1)[0]
        self.assertNotIn("WiserEquipmentSensor(", setup_source)
        self.assertNotIn('legacy_name="Equipment Energy Delivered"', setup_source)

    def test_power_display_name_does_not_change_historical_unique_id_input(
        self,
    ) -> None:
        device = SimpleNamespace(id=9, room_id=0, product_type="SmartPlug")
        data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                devices=SimpleNamespace(get_by_id=lambda _device_id: device),
                rooms=SimpleNamespace(
                    get_by_device_id=lambda _device_id: None,
                ),
                system=SimpleNamespace(name="WiserHeat123456"),
            )
        )

        sensor = self.sensor_module.WiserLTSPowerSensor(
            data,
            9,
            sensor_type="Power",
            name="Power",
            legacy_name="Equipment Power",
        )

        self.assertNotIn("_attr_name", sensor.__dict__)
        self.assertIsNone(getattr(sensor, "_attr_translation_key", None))
        self.assertEqual(sensor._sensor_type, "Equipment Power ")

        energy = self.sensor_module.WiserLTSPowerSensor(
            data,
            9,
            sensor_type="Energy",
            name="Total Energy",
            legacy_name="Equipment Total Energy",
        )
        self.assertEqual(energy._attr_translation_key, "total_energy")
        self.assertEqual(energy._sensor_type, "Equipment Total Energy ")


class WiserLTSOpenthermSensorDeviceTest(unittest.TestCase):
    """Tests for OpenTherm LTS sensor device assignment."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.sensor_module = _load_sensor_module()

    def test_opentherm_sensor_belongs_to_physical_hub(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserLTSOpenthermSensor)
        sensor._data = object()

        self.assertEqual(sensor.device_info, {"identifiers": {("wiser", "hub")}})


class WiserOpenThermModulationTest(unittest.TestCase):
    """Regression tests for the OpenTherm percentage sensor."""

    @classmethod
    def setUpClass(cls):
        cls.sensor_module = _load_sensor_module()

    def setUp(self):
        self.raw = {}
        self.opentherm = SimpleNamespace(
            operational_data=SimpleNamespace(json_data=self.raw),
            enabled=True,
            connection_status="Connected",
        )
        self.data = SimpleNamespace(
            last_update_success=True,
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(name="WiserHeat058A52", opentherm=self.opentherm),
                rooms=SimpleNamespace(get_by_device_id=lambda _device_id: None),
            ),
        )
        self.sensor = self.sensor_module.WiserOpenThermModulationSensor(self.data)
        self.sensor.async_write_ha_state = Mock()

    def test_reads_zero_and_fractional_percentages(self):
        for raw, expected in ((0, 0), (1, 0.1), (333, 33.3), (1000, 100)):
            with self.subTest(raw=raw):
                self.raw["RelativeModulationLevel"] = raw
                self.sensor._handle_coordinator_update()
                self.assertEqual(self.sensor.native_value, expected)
                self.assertEqual(self.sensor.state, expected)
        self.assertEqual(self.sensor.async_write_ha_state.call_count, 4)

    def test_absent_or_invalid_readings_are_unknown_not_zero(self):
        self.sensor._handle_coordinator_update()
        self.assertIsNone(self.sensor.native_value)
        for raw in (None, True, "0", -1, 1001, float("nan"), float("inf")):
            with self.subTest(raw=raw):
                self.raw["RelativeModulationLevel"] = raw
                self.sensor._handle_coordinator_update()
                self.assertIsNone(self.sensor.native_value)

    def test_sensor_metadata_and_hub_assignment(self):
        self.assertEqual(self.sensor.native_unit_of_measurement, "%")
        self.assertEqual(self.sensor.state_class, "measurement")
        self.assertEqual(self.sensor.icon, "mdi:fire")
        self.assertIsNone(getattr(self.sensor, "device_class", None))
        self.assertEqual(self.sensor._attr_translation_key, "relative_modulation_level")
        self.assertEqual(self.sensor._sensor_type, "relative_modulation_level")
        self.assertNotIn("_attr_name", self.sensor.__dict__)
        self.assertEqual(self.sensor.device_info, {"identifiers": {("wiser", "hub")}})

    def test_unavailable_when_disconnected_disabled_or_coordinator_fails(self):
        self.assertTrue(self.sensor.available)
        self.opentherm.connection_status = "Disconnected"
        self.assertFalse(self.sensor.available)
        self.opentherm.connection_status = "Connected"
        self.opentherm.enabled = False
        self.assertFalse(self.sensor.available)
        self.opentherm.enabled = True
        self.data.last_update_success = False
        self.assertFalse(self.sensor.available)

    def test_setup_only_adds_sensor_for_enabled_connected_opentherm(self):
        tree = ast.parse(SOURCE_PATH.read_text())
        setup = next(node for node in tree.body
                     if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_setup_entry")
        block = next(node for node in setup.body
                     if isinstance(node, ast.If)
                     and any(isinstance(child, ast.Call)
                             and isinstance(child.func, ast.Name)
                             and child.func.id == "WiserOpenThermModulationSensor"
                             for child in ast.walk(node)))
        for connected, enabled, expected in (
            ("Connected", True, 1), ("Disconnected", True, 0), ("Connected", False, 0)
        ):
            with self.subTest(connected=connected, enabled=enabled):
                self.opentherm.connection_status = connected
                self.opentherm.enabled = enabled
                sensors = []
                env = {**self.sensor_module.__dict__, "data": self.data, "wiser_sensors": sensors}
                exec(compile(ast.Module(body=[block], type_ignores=[]), "sensor.py", "exec"), env)
                self.assertEqual(sum(isinstance(sensor, self.sensor_module.WiserOpenThermModulationSensor)
                                     for sensor in sensors), expected)

    def test_translations_include_modulation_name(self):
        paths = [SOURCE_PATH.parent / "strings.json"]
        paths.extend(SOURCE_PATH.parent / "translations" / f"{language}.json"
                     for language in ("en", "de", "fr"))
        for path in paths:
            with self.subTest(path=path):
                translations = json.loads(path.read_text())
                self.assertTrue(translations["entity"]["sensor"]["relative_modulation_level"]["name"])
