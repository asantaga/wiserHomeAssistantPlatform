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
BINARY_SENSOR_SOURCE_PATH = (
    Path(__file__).parents[1] / "custom_components/wiser/binary_sensor.py"
)


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
        SensorDeviceClass=SimpleNamespace(
            TEMPERATURE="temperature",
            PRESSURE="pressure",
            POWER="power",
            VOLUME_FLOW_RATE="volume_flow_rate",
            DURATION="duration",
        ),
        SensorStateClass=SimpleNamespace(MEASUREMENT="measurement"),
        SensorEntity=SensorEntity,
    )
    _module(
        "homeassistant.const",
        ATTR_BATTERY_LEVEL="battery_level",
        LIGHT_LUX="lx",
        STATE_UNAVAILABLE="unavailable",
        STATE_UNKNOWN="unknown",
        STATE_ON="on",
        EntityCategory=SimpleNamespace(DIAGNOSTIC="diagnostic"),
        UnitOfTemperature=SimpleNamespace(CELSIUS="°C"),
        UnitOfTime=SimpleNamespace(HOURS="h"),
        UnitOfElectricCurrent=SimpleNamespace(),
        UnitOfElectricPotential=SimpleNamespace(),
        PERCENTAGE="%",
        UnitOfPower=SimpleNamespace(KILO_WATT="kW"),
        UnitOfEnergy=SimpleNamespace(),
        UnitOfPressure=SimpleNamespace(BAR="bar"),
        UnitOfVolumeFlowRate=SimpleNamespace(LITERS_PER_MINUTE="L/min"),
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
        CONF_OPENTHERM_SENSORS="opentherm_sensors",
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
        get_hub_via_device_info=lambda _data: {},
        get_unique_id=lambda *_args: "unique-id",
    )
    class WiserEntityMixin:
        pass

    _module("wiser.entity", WiserEntityMixin=WiserEntityMixin)
    def relative_modulation_level(opentherm):
        raw = opentherm.operational_data.json_data.get("RelativeModulationLevel")
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            return None
        if not 0 <= raw <= 1000:
            return None
        return raw / 10

    def opentherm_sensor_value(opentherm, key):
        if key == "delta_t":
            return round(
                opentherm.operational_data.ch_flow_temperature
                - opentherm.operational_data.ch_return_temperature,
                1,
            )
        if key == "relative_modulation_level":
            return relative_modulation_level(opentherm)
        if key == "estimated_boiler_output":
            data = opentherm.operational_data.json_data
            if not data["SlaveStatus"] & 8:
                return 0
            minimum = data["MinimumModulationLevel"]
            modulation = relative_modulation_level(opentherm)
            effective = minimum + modulation * (100 - minimum) / 100
            return round(data["MaximumCapacityKw"] * effective / 100, 2)
        if key == "coprocessor_version":
            return opentherm.json_data.get("CoprocessorVersion")
        if key == "coprocessor_update_status":
            return opentherm.json_data.get("CoprocessorUpdateStatus")
        if hasattr(opentherm, key):
            return getattr(opentherm, key)
        return getattr(opentherm.operational_data, key)

    _module(
        "wiser.opentherm",
        DEFAULT_OPENTHERM_SENSOR_KEYS=frozenset(
            {"ch_flow_temperature", "ch_return_temperature"}
        ),
        OPENTHERM_BINARY_SENSOR_KEYS=frozenset(
            {
                "ch1_flow_enabled",
                "ch2_flow_enabled",
                "hw_enabled",
                "boiler_ch_max_setpoint_read_write",
                "boiler_ch_max_setpoint_transfer_enable",
                "boiler_hw_setpoint_read_write",
                "boiler_hw_setpoint_transfer_enable",
            }
        ),
        OPENTHERM_DERIVED_SENSOR_KEYS=frozenset(
            {"delta_t", "estimated_boiler_output", "flame_statistics"}
        ),
        OPENTHERM_DIAGNOSTIC_SENSOR_KEYS=frozenset(
            {
                "boiler_ch_max_setpoint_read_write",
                "boiler_ch_max_setpoint_transfer_enable",
                "boiler_fault",
                "boiler_hw_setpoint_read_write",
                "boiler_hw_setpoint_transfer_enable",
                "connection_status",
                "coprocessor_update_status",
                "coprocessor_version",
                "diagnostic_event",
                "operating_mode",
                "slave_status",
                "tracked_room_id",
            }
        ),
        OPENTHERM_SENSOR_DEPENDENCIES={
            "estimated_boiler_output": frozenset(
                {
                    "flame_active",
                    "maximum_capacity_kw",
                    "minimum_modulation_level",
                    "relative_modulation_level",
                }
            )
        },
        OPENTHERM_SENSOR_NAMES={
            "ch1_flow_enabled": "CH1 flow enabled",
            "ch_pressure_bar": "CH pressure",
            "connection_status": "Connection status",
            "delta_t": "Delta-T",
            "estimated_boiler_output": "Estimated boiler output",
            "boiler_exhaust_temperature": "Boiler exhaust temperature",
            "maximum_capacity_kw": "Maximum boiler capacity",
            "minimum_modulation_level": "Minimum modulation level",
            "relative_modulation_level": "Relative modulation level",
            "coprocessor_version": "OpenTherm coprocessor version",
            "coprocessor_update_status": "OpenTherm coprocessor update status",
        },
        OPENTHERM_SENSOR_PATHS={
            "ch1_flow_enabled": ("ch1_flow_enabled",),
            "ch_pressure_bar": ("operational_data", "ch_pressure_bar"),
            "connection_status": ("connection_status",),
            "flame_statistics": ("operational_data", "slave_status"),
            "relative_modulation_level": (
                "operational_data",
                "relative_modulation_level",
            ),
        },
        OPENTHERM_SLAVE_STATUS_BITS={
            "boiler_fault": 0,
            "central_heating_active": 1,
            "hot_water_active": 2,
            "flame_active": 3,
            "cooling_active": 4,
            "central_heating_2_active": 5,
            "diagnostic_event": 6,
        },
        detected_opentherm_sensor_keys=lambda _opentherm: [],
        opentherm_sensor_value=opentherm_sensor_value,
        opentherm_sensor_is_enabled=lambda configured, key: (
            key in {"ch_flow_temperature", "ch_return_temperature"}
            if configured is None
            else (
                configured.get(
                    key, key in {"ch_flow_temperature", "ch_return_temperature"}
                )
                if isinstance(configured, dict)
                else key in configured
            )
        ),
        relative_modulation_level=relative_modulation_level,
    )
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


def _load_binary_sensor_module() -> ModuleType:
    """Load the binary sensor module using the shared HA stubs."""
    _load_sensor_module()

    class BinarySensorEntity:
        pass

    _module(
        "homeassistant.components.binary_sensor",
        BinarySensorDeviceClass=SimpleNamespace(
            SMOKE="smoke",
            HEAT="heat",
            TAMPER="tamper",
            PROBLEM="problem",
            POWER="power",
            OPENING="opening",
            WINDOW="window",
            DOOR="door",
            RUNNING="running",
        ),
        BinarySensorEntity=BinarySensorEntity,
    )

    spec = importlib.util.spec_from_file_location(
        "wiser.binary_sensor", BINARY_SENSOR_SOURCE_PATH
    )
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

    def test_flame_statistics_is_not_exposed_as_raw_slave_status(self) -> None:
        sensor = object.__new__(self.sensor_module.WiserLTSOpenthermSensor)
        sensor._lts_sensor_type = "opentherm_flow_temp"
        sensor._data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(
                    opentherm=SimpleNamespace(
                        ch1_flow_enabled=False,
                        connection_status="Connected",
                        operational_data=SimpleNamespace(
                            ch_pressure_bar=1.2,
                            json_data={},
                            slave_status=8,
                        ),
                    )
                )
            )
        )

        attributes = sensor.extra_state_attributes

        self.assertEqual(attributes["ch_pressure_bar"], 1.2)
        self.assertNotIn("flame_statistics", attributes)


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
        self.sensor = self.sensor_module.WiserOpenThermAttributeSensor(
            self.data, "relative_modulation_level"
        )
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
        self.assertEqual(
            self.sensor._attr_translation_key, "relative_modulation_level"
        )
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

class WiserOpenThermAttributeSensorTest(unittest.TestCase):
    """Tests for opt-in OpenTherm attribute entities."""

    @classmethod
    def setUpClass(cls):
        cls.sensor_module = _load_sensor_module()

    def setUp(self):
        self.opentherm = SimpleNamespace(
            operational_data=SimpleNamespace(ch_pressure_bar=1.2, json_data={}),
            json_data={},
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
        self.sensor = self.sensor_module.WiserOpenThermAttributeSensor(
            self.data, "ch_pressure_bar"
        )
        self.sensor.async_write_ha_state = Mock()

    def test_reads_selected_attribute_with_measurement_metadata(self):
        self.sensor._handle_coordinator_update()

        self.assertEqual(self.sensor.native_value, 1.2)
        self.assertEqual(self.sensor.native_unit_of_measurement, "bar")
        self.assertEqual(self.sensor.device_class, "pressure")
        self.assertEqual(self.sensor.state_class, "measurement")
        self.assertEqual(self.sensor._attr_translation_key, "ch_pressure_bar")
        self.assertEqual(self.sensor._sensor_type, "opentherm_ch_pressure_bar")
        self.assertEqual(self.sensor.device_info, {"identifiers": {("wiser", "hub")}})

    def test_connection_sensor_remains_available_when_disconnected(self):
        sensor = self.sensor_module.WiserOpenThermAttributeSensor(
            self.data, "ch_pressure_bar"
        )
        self.opentherm.connection_status = "Disconnected"
        self.assertFalse(sensor.available)

        connection = self.sensor_module.WiserOpenThermAttributeSensor(
            self.data, "connection_status"
        )
        self.assertTrue(connection.available)
        self.assertEqual(connection._attr_entity_category, "diagnostic")

    def test_delta_t_has_temperature_measurement_metadata(self):
        self.opentherm.operational_data.ch_flow_temperature = 42.4
        self.opentherm.operational_data.ch_return_temperature = 35.1
        delta_t = self.sensor_module.WiserOpenThermAttributeSensor(
            self.data, "delta_t"
        )
        delta_t.async_write_ha_state = Mock()

        delta_t._handle_coordinator_update()

        self.assertEqual(delta_t.native_value, 7.3)
        self.assertEqual(delta_t.native_unit_of_measurement, "°C")
        self.assertEqual(delta_t.device_class, "temperature")
        self.assertEqual(delta_t.state_class, "measurement")
        self.assertEqual(delta_t.icon, "mdi:delta")
        self.assertEqual(delta_t._sensor_type, "opentherm_delta_t")

    def test_additional_boiler_readings_have_native_metadata(self):
        readings = {
            "boiler_exhaust_temperature": (28, "°C", "temperature", "mdi:smoke"),
            "maximum_capacity_kw": (30, "kW", "power", "mdi:flash"),
            "minimum_modulation_level": (27, "%", None, "mdi:percent"),
        }
        for key, (value, unit, device_class, icon) in readings.items():
            with self.subTest(key=key):
                setattr(self.opentherm.operational_data, key, value)
                sensor = self.sensor_module.WiserOpenThermAttributeSensor(
                    self.data, key
                )
                sensor.async_write_ha_state = Mock()

                sensor._handle_coordinator_update()

                self.assertEqual(sensor.native_value, value)
                self.assertEqual(sensor.native_unit_of_measurement, unit)
                self.assertEqual(sensor.device_class, device_class)
                self.assertEqual(sensor.state_class, "measurement")
                self.assertEqual(sensor.icon, icon)

    def test_estimated_boiler_output_uses_capacity_and_modulation(self):
        self.opentherm.operational_data.json_data = {
            "MaximumCapacityKw": 30,
            "MinimumModulationLevel": 27,
            "RelativeModulationLevel": 52,
            "SlaveStatus": 8,
        }
        sensor = self.sensor_module.WiserOpenThermAttributeSensor(
            self.data, "estimated_boiler_output"
        )
        sensor.async_write_ha_state = Mock()

        sensor._handle_coordinator_update()

        self.assertEqual(sensor.native_value, 9.24)
        self.assertEqual(sensor.native_unit_of_measurement, "kW")
        self.assertEqual(sensor.device_class, "power")
        self.assertEqual(sensor.state_class, "measurement")
        self.assertEqual(sensor.icon, "mdi:flash")

        self.opentherm.operational_data.json_data["SlaveStatus"] = 0
        sensor._handle_coordinator_update()
        self.assertEqual(sensor.native_value, 0)

    def test_coprocessor_fields_are_diagnostic_sensors(self):
        self.opentherm.json_data = {
            "CoprocessorVersion": "2.0.31",
            "CoprocessorUpdateStatus": "Success",
        }
        for key, expected, icon in (
            ("coprocessor_version", "2.0.31", "mdi:chip"),
            ("coprocessor_update_status", "Success", "mdi:update"),
        ):
            with self.subTest(key=key):
                sensor = self.sensor_module.WiserOpenThermAttributeSensor(
                    self.data, key
                )
                sensor.async_write_ha_state = Mock()
                sensor._handle_coordinator_update()

                self.assertEqual(sensor.native_value, expected)
                self.assertEqual(sensor._attr_entity_category, "diagnostic")
                self.assertIsNone(sensor.state_class)
                self.assertEqual(sensor.icon, icon)

                self.opentherm.connection_status = "Disconnected"
                self.assertTrue(sensor.available)
                self.opentherm.connection_status = "Connected"


class WiserOpenThermFlameStatisticsSensorTest(unittest.TestCase):
    """Tests for the optional rolling flame-runtime entity."""

    @classmethod
    def setUpClass(cls):
        cls.sensor_module = _load_sensor_module()

    def test_metadata_identity_and_runtime_conversion(self):
        data = SimpleNamespace(
            last_update_success=True,
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(name="WiserHeat058A52"),
                rooms=SimpleNamespace(get_by_device_id=lambda _device_id: None),
            ),
        )
        sensor = self.sensor_module.WiserOpenThermFlameStatisticsSensor(data)
        sensor.async_write_ha_state = Mock()
        sensor._history_coordinator = SimpleNamespace(
            last_update_success=True,
            data=SimpleNamespace(seconds_matched=5400),
        )

        sensor._handle_history_update()

        self.assertEqual(sensor.native_value, 1.5)
        self.assertEqual(sensor._attr_native_unit_of_measurement, "h")
        self.assertEqual(sensor._attr_device_class, "duration")
        self.assertEqual(sensor._attr_state_class, "measurement")
        self.assertEqual(sensor._attr_translation_key, "flame_statistics")
        self.assertEqual(sensor._sensor_type, "opentherm_flame_statistics")
        self.assertEqual(sensor.device_info, {"identifiers": {("wiser", "hub")}})
        self.assertTrue(sensor.available)


class WiserOpenThermAttributeBinarySensorTest(unittest.TestCase):
    """Tests for boolean OpenTherm attributes exposed as binary sensors."""

    @classmethod
    def setUpClass(cls):
        cls.binary_sensor_module = _load_binary_sensor_module()

    def setUp(self):
        self.opentherm = SimpleNamespace(
            ch1_flow_enabled=False,
            operational_data=SimpleNamespace(json_data={}),
            enabled=True,
            connection_status="Connected",
        )
        self.data = SimpleNamespace(
            last_update_success=True,
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(
                    name="WiserHeat058A52", opentherm=self.opentherm
                ),
                rooms=SimpleNamespace(get_by_device_id=lambda _device_id: None),
            ),
        )
        self.sensor = (
            self.binary_sensor_module.WiserOpenThermAttributeBinarySensor(
                self.data, "ch1_flow_enabled"
            )
        )
        self.sensor.async_write_ha_state = Mock()

    def test_reads_boolean_attribute_and_uses_hub_device(self):
        self.assertFalse(self.sensor.is_on)

        self.sensor._handle_coordinator_update()
        self.assertFalse(self.sensor.is_on)

        self.opentherm.ch1_flow_enabled = True
        self.sensor._handle_coordinator_update()
        self.assertTrue(self.sensor.is_on)
        self.assertEqual(self.sensor._attr_translation_key, "ch1_flow_enabled")
        self.assertEqual(
            self.sensor.device_info, {"identifiers": {("wiser", "hub")}}
        )

    def test_unavailable_when_opentherm_disconnects(self):
        self.assertTrue(self.sensor.available)
        self.opentherm.connection_status = "Disconnected"
        self.assertFalse(self.sensor.available)

    def test_slave_status_flag_uses_running_device_class(self):
        self.binary_sensor_module.opentherm_sensor_value = (
            lambda opentherm, _key: bool(opentherm.operational_data.slave_status & 4)
        )
        self.opentherm.operational_data.slave_status = 4
        sensor = self.binary_sensor_module.WiserOpenThermAttributeBinarySensor(
            self.data, "hot_water_active"
        )
        sensor.async_write_ha_state = Mock()

        sensor._handle_coordinator_update()

        self.assertTrue(sensor.is_on)
        self.assertEqual(sensor._attr_device_class, "running")

    def test_capability_flag_is_a_diagnostic_entity(self):
        sensor = self.binary_sensor_module.WiserOpenThermAttributeBinarySensor(
            self.data, "boiler_ch_max_setpoint_read_write"
        )

        self.assertEqual(sensor._attr_entity_category, "diagnostic")
