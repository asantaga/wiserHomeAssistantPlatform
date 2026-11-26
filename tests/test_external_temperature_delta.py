"""External feedback metadata and measured-temperature comparison regressions."""

import ast
import asyncio
from datetime import timedelta
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from test_external_room_control import FakeDateTimeUtil, load_controller
from test_sensor import _load_sensor_module


class ExternalTemperatureDeltaTest(unittest.TestCase):
    def setUp(self):
        self.module = _load_sensor_module()
        # These identities include the hub and room, not their display names
        # or the replaceable source entity.
        self.unique_id = lambda data, room_id, kind: f"{data.hub_id}-{room_id}-{kind}"
        self.module.get_room_entity_unique_id = self.unique_id
        self.room = SimpleNamespace(
            id=1, name="Office", current_temperature=20.0,
            current_target_temperature=28.0, number_of_smartvalves=1,
            roomstat_id=None, devices=[],
        )
        self.rooms = {1: self.room}
        self.data = SimpleNamespace(
            hub_id="hub-a", last_update_success=True,
            wiserhub=SimpleNamespace(rooms=SimpleNamespace(
                all=[self.room], get_by_id=self.rooms.get,
            )),
        )
        controller_class, _registry = load_controller()
        self.controller = controller_class.__new__(controller_class)
        self.controller.coordinator = self.data
        self.controller.temperature_sensors = {"1": "sensor.office"}
        self.controller.assignments = {}
        self.controller.temperature_stale_minutes = 30
        self.source = SimpleNamespace(
            state="21.5", attributes={"unit_of_measurement": "°C"},
            last_reported=FakeDateTimeUtil.utcnow(),
        )
        self.states = {"sensor.office": self.source}
        self.hass = SimpleNamespace(states=SimpleNamespace(get=self.states.get))
        self.controller.hass = self.hass
        self.data.external_room_control = self.controller
        self.sensor = self.module.WiserExternalTemperatureDeltaSensor(self.data, 1)
        self.registry = SimpleNamespace(
            async_get_entity_id=Mock(return_value="sensor.office_difference"),
            async_get=Mock(return_value=SimpleNamespace(config_entry_id="entry-a")),
            async_remove=Mock(),
        )
        sys.modules["homeassistant.helpers.entity_registry"].async_get = (
            lambda _hass: self.registry
        )

    def test_difference_uses_original_measurement_not_target(self):
        self.assertEqual(self.sensor.native_value, 1.5)
        self.room.current_target_temperature = 35.0
        self.assertEqual(self.sensor.native_value, 1.5)
        self.source.state = "18.5"
        self.assertEqual(self.sensor.native_value, -1.5)
        self.source.state = "20"
        self.assertEqual(self.sensor.native_value, 0)
        self.assertTrue(self.sensor.available)

    def test_fahrenheit_source_is_converted_before_subtraction(self):
        self.source.attributes["unit_of_measurement"] = "°F"
        self.source.state = "71.6"
        self.assertEqual(self.sensor.native_value, 2.0)

    def test_delta_metadata_allows_scaled_not_absolute_conversion(self):
        self.assertEqual(self.sensor._attr_native_unit_of_measurement, "°C")
        self.assertEqual(self.sensor._attr_state_class, "measurement")
        self.assertNotIn("state", type(self.sensor).__dict__)
        # Legacy HA lacks TEMPERATURE_DELTA: deliberately no temperature class,
        # so a Celsius difference will not be converted as an absolute reading.
        self.assertIsNone(self.sensor._attr_device_class)
        self.module.SensorDeviceClass.TEMPERATURE_DELTA = "temperature_delta"
        source = ast.parse(Path(self.module.__file__).read_text())
        node = next(node for node in source.body if isinstance(node, ast.ClassDef)
                    and node.name == "WiserExternalTemperatureDeltaSensor")
        namespace = dict(self.module.__dict__)
        exec(compile(ast.Module(body=[node], type_ignores=[]), "sensor.py", "exec"), namespace)
        self.assertEqual(namespace[node.name]._attr_device_class, "temperature_delta")

    def test_unusable_readings_are_unavailable_not_zero(self):
        for state in ("unknown", "unavailable", "nan", "inf", "bad"):
            with self.subTest(state=state):
                self.source.state = state
                self.assertIsNone(self.sensor.native_value)
                self.assertFalse(self.sensor.available)
        self.source.state = "21.5"
        self.source.attributes["unit_of_measurement"] = "invalid"
        self.assertFalse(self.sensor.available)
        self.source.attributes["unit_of_measurement"] = "°C"
        self.states.clear()
        self.assertFalse(self.sensor.available)

    def test_stale_source_and_hub_failure_are_unavailable(self):
        self.source.last_reported -= timedelta(minutes=31)
        self.assertIsNone(self.sensor.native_value)
        self.assertFalse(self.sensor.available)
        self.source.last_reported = FakeDateTimeUtil.utcnow()
        self.assertTrue(self.sensor.available)
        self.data.last_update_success = False
        self.assertFalse(self.sensor.available)

    def test_missing_invalid_or_removed_wiser_measurement(self):
        for value in (None, float("nan"), float("inf"), True, "unknown"):
            with self.subTest(value=value):
                self.room.current_temperature = value
                self.assertIsNone(self.sensor.native_value)
        self.rooms.clear()
        self.assertFalse(self.sensor.available)

    def test_actuator_only_or_ineligible_room_is_not_feedback(self):
        self.controller.temperature_sensors = {}
        self.controller.assignments = {"1": ["climate.external"]}
        self.assertIsNone(self.controller.external_temperature(1))
        self.assertFalse(self.sensor.available)
        self.controller.temperature_sensors = {"1": "sensor.office"}
        self.room.roomstat_id = 3
        self.assertIsNone(self.controller.external_temperature(1))

    def test_identity_is_stable_across_renaming_and_source_reassignment(self):
        original_id = self.sensor.unique_id
        self.room.name = "Renamed"
        self.controller.temperature_sensors["1"] = "sensor.replacement"
        self.states["sensor.replacement"] = SimpleNamespace(
            state="19", attributes={"unit_of_measurement": "°C"},
        )
        self.assertEqual(self.sensor.unique_id, original_id)
        self.assertEqual(self.sensor.native_value, -1)
        self.assertEqual(self.sensor.extra_state_attributes, {
            "external_temperature_sensor": "sensor.replacement",
            "difference_direction": "external_minus_wiser",
        })
        other_data = SimpleNamespace(**{**vars(self.data), "hub_id": "hub-b"})
        other = self.module.WiserExternalTemperatureDeltaSensor(other_data, 1)
        self.assertNotEqual(other.unique_id, original_id)

    def test_setup_creates_only_feedback_and_removes_unassigned_registry_entry(self):
        entry = SimpleNamespace(entry_id="entry-a")
        sensors = self.module._external_temperature_delta_sensors(self.hass, entry, self.data)
        self.assertEqual([sensor.unique_id for sensor in sensors], [self.sensor.unique_id])
        self.registry.async_remove.assert_not_called()
        self.controller.temperature_sensors = {}
        self.assertEqual(self.module._external_temperature_delta_sensors(
            self.hass, entry, self.data), [])
        self.registry.async_remove.assert_called_once_with("sensor.office_difference")

    def test_cleanup_does_not_remove_another_config_entry(self):
        self.controller.temperature_sensors = {}
        self.registry.async_get.return_value.config_entry_id = "entry-b"
        self.module._external_temperature_delta_sensors(
            self.hass, SimpleNamespace(entry_id="entry-a"), self.data)
        self.registry.async_remove.assert_not_called()

    def test_ineligible_room_keeps_sensor_until_assignment_is_removed(self):
        entry = SimpleNamespace(entry_id="entry-a")
        self.room.roomstat_id = 3
        sensors = self.module._external_temperature_delta_sensors(
            self.hass, entry, self.data
        )
        self.assertEqual([sensor.unique_id for sensor in sensors], [self.sensor.unique_id])
        self.assertFalse(sensors[0].available)
        self.registry.async_remove.assert_not_called()

        self.room.roomstat_id = None
        self.assertTrue(sensors[0].available)
        self.controller.temperature_sensors.clear()
        self.assertEqual(self.module._external_temperature_delta_sensors(
            self.hass, entry, self.data
        ), [])
        self.registry.async_remove.assert_called_once_with("sensor.office_difference")

    def _climate_attributes(self):
        source = Path(self.module.__file__).with_name("climate.py")
        room_class = next(node for node in ast.parse(source.read_text()).body
                          if isinstance(node, ast.ClassDef) and node.name == "WiserRoom")
        method = next(node for node in room_class.body if isinstance(node, ast.FunctionDef)
                      and node.name == "_external_temperature_attributes")
        namespace = {"DOMAIN": "wiser", "get_room_entity_unique_id": self.unique_id}
        exec(compile(ast.Module(body=[method], type_ignores=[]), "climate.py", "exec"), namespace)
        entity = SimpleNamespace(_data=self.data, _room_id=1, hass=self.hass)
        return namespace[method.name](entity)

    def test_climate_metadata_distinguishes_assignment_from_availability(self):
        self.assertEqual(self._climate_attributes(), {
            "external_temperature_sensor": "sensor.office",
            "is_external_temperature_feedback": True,
            "external_temperature_available": True,
            "external_temperature_delta_entity_id": "sensor.office_difference",
        })
        self.source.state = "unavailable"
        attrs = self._climate_attributes()
        self.assertTrue(attrs["is_external_temperature_feedback"])
        self.assertFalse(attrs["external_temperature_available"])
        self.controller.temperature_sensors = {}
        self.controller.assignments = {"1": ["climate.external"]}
        self.assertEqual(self._climate_attributes(), {
            "external_temperature_sensor": None,
            "is_external_temperature_feedback": False,
            "external_temperature_available": False,
            "external_temperature_delta_entity_id": None,
        })

    def test_disabled_or_not_registered_delta_has_no_fabricated_entity_id(self):
        self.registry.async_get_entity_id.return_value = None
        attrs = self._climate_attributes()
        self.assertIsNone(attrs["external_temperature_delta_entity_id"])
        self.assertTrue(attrs["is_external_temperature_feedback"])

    def test_source_changes_expiry_and_hub_updates_publish_and_unsubscribe(self):
        callbacks = {}
        unsubscribers = []
        def track(_hass, arg, callback):
            callbacks["source"] = callback
            self.assertEqual(arg, ["sensor.office"])
            return Mock()
        def interval(_hass, callback, duration):
            callbacks["expiry"] = callback
            self.assertEqual(duration, timedelta(seconds=30))
            return Mock()
        async def added(_self):
            pass
        self.sensor.hass = self.hass
        self.sensor.async_on_remove = unsubscribers.append
        self.sensor.async_write_ha_state = Mock()
        event = SimpleNamespace(async_track_state_change_event=track,
                                async_track_time_interval=interval)
        with patch.dict(sys.modules, {"homeassistant.helpers.event": event}), patch.object(
            self.module.CoordinatorEntity, "async_added_to_hass", added, create=True
        ):
            asyncio.run(self.sensor.async_added_to_hass())
        callbacks["source"](None)
        callbacks["expiry"](None)
        self.sensor._handle_coordinator_update()
        self.assertEqual(self.sensor.async_write_ha_state.call_count, 3)
        self.assertEqual(len(unsubscribers), 2)


if __name__ == "__main__":
    unittest.main()
