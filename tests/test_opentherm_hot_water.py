"""Focused tests for the integration-owned OpenTherm hot-water schedule."""

import ast
import asyncio
from copy import deepcopy
from datetime import UTC, datetime, timedelta
import logging
from math import isfinite
from pathlib import Path
from time import strptime
from types import SimpleNamespace
from uuid import uuid4
import unittest
from unittest.mock import AsyncMock, Mock


COMPONENT = Path(__file__).parents[1] / "custom_components/wiser"
WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)


def _load_schedule_helpers():
    """Load pure schedule helpers without requiring Home Assistant."""
    tree = ast.parse((COMPONENT / "local_schedule.py").read_text())
    selected = [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name
        in {
            "_schedule_preset_options",
            "_default_schedule",
            "_validated_schedule",
            "_schedule_position",
        }
    ]
    namespace = {
        "deepcopy": deepcopy,
        "timedelta": timedelta,
        "strptime": strptime,
        "LOCAL_HOT_WATER_SCHEDULE_ID": -1000,
        "LOCAL_HOT_WATER_SCHEDULE_NAME": "OpenTherm Hot Water",
        "LOCAL_HOT_WATER_SCHEDULE_TYPE": "HotWater",
        "WEEKDAYS": WEEKDAYS,
    }
    exec(
        compile(ast.Module(body=selected, type_ignores=[]), "<helpers>", "exec"),
        namespace,
    )
    return namespace


HELPERS = _load_schedule_helpers()
default_schedule = HELPERS["_default_schedule"]
validated_schedule = HELPERS["_validated_schedule"]
schedule_position = HELPERS["_schedule_position"]


class OpenThermHotWaterBoostTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        tree = ast.parse((COMPONENT / "opentherm_hot_water.py").read_text())
        entity = next(
            node for node in tree.body
            if isinstance(node, ast.ClassDef)
            and node.name == "WiserOpenThermHotWater"
        )
        methods = {
            "operation_list", "_preset_for_mode", "_cancel_active_boost",
            "_remaining_boost_seconds", "_start_boost", "_async_boost_finished",
            "_async_finish_boost_safely", "async_set_operation_mode",
            "_handle_coordinator_update", "_queue_boost_finish",
            "_async_set_target", "_async_command_failed",
        }
        entity.bases = []
        entity.body = [node for node in entity.body if getattr(node, "name", "") in methods]
        finite_float = next(
            node for node in tree.body if getattr(node, "name", "") == "_finite_float"
        )
        self.timer = Mock(side_effect=lambda *_: Mock())
        self.tasks = []
        namespace = {
            "MODE_MANUAL": "Manual",
            "MODE_AUTO": "Auto",
            "STATE_OFF": "off",
            "asyncio": asyncio,
            "UTC": UTC,
            "datetime": datetime,
            "timedelta": timedelta,
            "async_call_later": self.timer,
            "callback": lambda method: method,
            "HomeAssistantError": RuntimeError,
            "_LOGGER": logging.getLogger(__name__),
            "isfinite": isfinite,
            "uuid4": uuid4,
            "DOMAIN": "wiser",
            "WISER_SERVICES": {
                "SERVICE_SEND_OPENTHERM_COMMAND": "set_opentherm_parameter",
            },
            "ATTR_HUB": "hub",
            "ATTR_OPENTHERM_ENDPOINT": "endpoint",
            "ATTR_OPENTHERM_PARAM": "parameter",
            "ATTR_OPENTHERM_TEMPERATURE": "temperature",
            "ATTR_OPENTHERM_REQUEST_ID": "request_id",
        }
        exec(
            compile(ast.Module(body=[finite_float, entity], type_ignores=[]),
                    "<hot-water-boost>", "exec"),
            namespace,
        )
        self.entity = namespace["WiserOpenThermHotWater"]()
        self.entity.hass = SimpleNamespace(async_create_task=self.tasks.append)
        self.entity._manual_temperature = 45
        self.entity.min_temp = 35
        self.entity._operation = "off"
        self.entity._presets = [
            {"name": "Guests", "temperature": 52, "duration_minutes": 23}
        ]
        self.entity._boost_deadline = None
        self.entity._boost_end = None
        self.entity._cancel_boost_timer = None
        self.entity._pending_boost_finish = None
        self.entity._target_write_in_progress = False
        self.entity.available = True
        self.entity._async_set_target = AsyncMock()
        self.entity._async_apply_schedule = AsyncMock()
        self.entity.async_write_ha_state = Mock()

    async def test_configured_boost_uses_its_own_target_and_duration(self):
        self.assertEqual(self.entity.operation_list, ["off", "Manual", "Auto", "Guests"])
        await self.entity.async_set_operation_mode("Guests")
        self.entity._async_set_target.assert_awaited_with(52, boost_finish=None)
        self.assertEqual(self.timer.call_args.args[1], 23 * 60)
        self.assertAlmostEqual(
            (self.entity._boost_end - datetime.now(UTC)).total_seconds(),
            23 * 60,
            delta=1,
        )
        self.timer.call_args.args[2](None)
        await self.tasks.pop()
        self.assertEqual(self.entity._operation, "Manual")
        self.assertIsNone(self.entity._boost_end)

    async def test_expired_boost_retries_after_hub_recovers(self):
        await self.entity.async_set_operation_mode("Guests")
        self.entity._async_set_target.side_effect = RuntimeError("Hub unavailable")
        self.timer.call_args.args[2](None)
        with self.assertLogs(__name__, level="WARNING"):
            await self.tasks.pop()
        self.assertEqual(self.entity._operation, "Guests")
        self.entity.available = False
        self.entity._handle_coordinator_update()
        self.assertEqual(self.tasks, [])

        self.entity.available = True
        self.entity._async_set_target.side_effect = None
        self.entity._handle_coordinator_update()
        self.entity._handle_coordinator_update()
        self.assertEqual(len(self.tasks), 1)
        await self.tasks.pop()
        self.entity._async_set_target.assert_awaited_with(
            45, boost_finish=("Manual", True)
        )
        self.assertEqual(self.entity._operation, "Manual")

    async def test_expired_boost_retry_does_not_override_new_mode(self):
        await self.entity.async_set_operation_mode("Guests")
        self.timer.call_args.args[2](None)
        await self.entity.async_set_operation_mode("off")
        await self.tasks.pop()
        self.entity._async_set_target.assert_awaited_with(35, boost_finish=None)
        self.assertEqual(self.entity._operation, "off")

    async def test_rejected_boost_return_retries_without_restoring_expired_preset(self):
        del self.entity._async_set_target
        self.entity.max_temp = 55
        self.entity._entry_id = "test-hub"
        self.entity._context = None
        call = AsyncMock()
        self.entity.hass.services = SimpleNamespace(async_call=call)
        await self.entity.async_set_operation_mode("Guests")
        self.timer.call_args.args[2](None)
        await self.tasks.pop()

        def reject_last_write():
            request = call.call_args.args[2]
            self.assertEqual(request["temperature"], 45)
            self.entity._async_command_failed(
                SimpleNamespace(data={"request_id": request["request_id"], "requested": 45})
            )
            self.assertEqual(self.entity._operation, "Manual")
            self.assertIsNone(self.entity._boost_end)

        reject_last_write()
        self.entity._handle_coordinator_update()
        await self.tasks.pop()
        reject_last_write()
        self.entity._handle_coordinator_update()
        self.assertEqual(self.tasks, [])
        self.assertEqual(call.await_count, 3)


class OpenThermHotWaterScheduleTest(unittest.TestCase):
    def test_control_uses_water_heater_operations(self):
        source = (COMPONENT / "opentherm_hot_water.py").read_text()
        self.assertIn(
            "CoordinatorEntity, RestoreEntity, WaterHeaterEntity", source
        )
        self.assertIn("STATE_OFF,", source)
        self.assertIn("MODE_MANUAL,", source)
        self.assertIn("MODE_AUTO,", source)

    def test_card_feature_uses_hot_water_mode_icons(self):
        source = (COMPONENT / "frontend/wiser-hot-water-control.js").read_text()
        self.assertIn('off: "mdi:power"', source)
        self.assertIn('Manual: "mdi:water-thermometer"', source)
        self.assertIn('Auto: "mdi:calendar-clock"', source)
        self.assertIn('operation_mode: value', source)
        self.assertIn(
            '"opentherm-hot-water-control-presets-feature"', source
        )
        self.assertIn('name: "Hot-water control modes"', source)
        self.assertIn('name: "Hot-water control presets"', source)

    def test_control_exposes_configured_presets(self):
        source = (COMPONENT / "opentherm_hot_water.py").read_text()
        self.assertIn('"opentherm_presets": self._presets', source)
        self.assertIn('*(preset["name"] for preset in self._presets)', source)
        self.assertIn('self._start_boost(preset["duration_minutes"])', source)

    def test_external_temperature_sensor_updates_and_falls_back_to_opentherm(self):
        source = (COMPONENT / "opentherm_hot_water.py").read_text()
        self.assertIn("CONF_OPENTHERM_HOT_WATER_SENSOR_ENTITY_ID", source)
        self.assertIn("self.hass.states.get(", source)
        self.assertIn("TemperatureConverter.convert(", source)
        self.assertIn("async_track_state_change_event(", source)
        self.assertIn("self._async_temperature_sensor_changed", source)
        self.assertIn(
            'getattr(operational_data, "hw_temperature", None)', source
        )

    def test_preset_editor_opens_directly_from_nested_options_dialog(self):
        source = (COMPONENT / "frontend/wiser-hot-water-control.js").read_text()
        self.assertIn('PRESETS_SELECTOR_KEY = "opentherm_presets_v2"', source)
        self.assertIn("document.body.querySelector(PRESETS_DIALOG_TYPE)", source)
        self.assertIn("document.body.append(dialog)", source)
        self.assertIn("dialog.showDialog(dialogParams)", source)

    def test_restart_of_timed_boost_reapplies_manual_target(self):
        source = (COMPONENT / "opentherm_hot_water.py").read_text()
        self.assertIn("reset_expired_boost = bool", source)
        self.assertIn(
            "self._queue_boost_finish(self._operation)",
            source,
        )

    def test_confirmed_command_failure_restores_previous_ui_operation(self):
        source = (COMPONENT / "opentherm_hot_water.py").read_text()
        self.assertIn("ATTR_OPENTHERM_REQUEST_ID: request_id", source)
        self.assertIn("EVENT_OPENTHERM_COMMAND_FAILED", source)
        self.assertIn("self._operation = previous_operation", source)
        self.assertIn("self._cancel_active_boost()", source)
        self.assertIn("self._pending_previous_boost_seconds", source)
        self.assertIn("self._start_boost(previous_boost_seconds / 60)", source)
        self.assertIn("self._operation = previous_operation", source)
        self.assertIn("(MODE_AUTO, failed_temperature)", source)
        self.assertIn("except HomeAssistantError:", source)

    def test_preset_editor_uses_boiler_temperature_limits(self):
        source = (COMPONENT / "frontend/wiser-hot-water-control.js").read_text()
        self.assertIn("min: this._minimum", source)
        self.assertIn("max: this._maximum", source)
        self.assertIn("temperature >= this._minimum", source)
        self.assertIn("temperature <= this._maximum", source)
        self.assertIn(
            "save.disabled = this._validateDraftTemperature() === undefined", source
        )
        self.assertNotIn("temperature between 35 and 55", source)

    def test_presets_are_list_only(self):
        source = (COMPONENT / "frontend/wiser-hot-water-control.js").read_text()
        self.assertNotIn("display_style", source)
        self.assertNotIn('displayStyle.label = "Show as"', source)
        self.assertIn(
            "return PRIMARY_MODES.filter((mode) => entityModes.includes(mode))",
            source,
        )

    def test_default_schedule_starts_safe_and_covers_every_day(self):
        schedule = default_schedule(35)
        self.assertEqual(schedule["Id"], -1000)
        self.assertEqual(schedule["Type"], "HotWater")
        self.assertEqual(schedule["MinSetpoint"], 35)
        self.assertEqual(schedule["MaxSetpoint"], 55)
        self.assertEqual(
            [day["day"] for day in schedule["ScheduleData"]], list(WEEKDAYS)
        )
        self.assertTrue(
            all(
                day["slots"]
                == [
                    {"Time": "00:00", "Setpoint": "35"},
                    {"Time": "06:00", "Setpoint": "45"},
                    {"Time": "09:00", "Setpoint": "35"},
                    {"Time": "17:00", "Setpoint": "45"},
                    {"Time": "22:00", "Setpoint": "35"},
                ]
                for day in schedule["ScheduleData"]
            )
        )

    def test_schedule_uses_latest_slot_and_reports_next_transition(self):
        schedule = default_schedule(35)
        monday = schedule["ScheduleData"][0]
        monday["slots"] = [
            {"Time": "06:00", "Setpoint": "50"},
            {"Time": "08:00", "Setpoint": "35"},
        ]
        value, next_event, next_temperature = schedule_position(
            schedule, datetime(2026, 10, 5, 7, 0)
        )
        self.assertEqual(value, 50)
        self.assertEqual(next_event, datetime(2026, 10, 5, 8, 0))
        self.assertEqual(next_temperature, 35)

    def test_schedule_wraps_to_the_previous_and_next_week(self):
        schedule = default_schedule(35)
        for day in schedule["ScheduleData"]:
            day["slots"] = []
        schedule["ScheduleData"][6]["slots"] = [
            {"Time": "22:00", "Setpoint": "48"}
        ]
        value, next_event, next_temperature = schedule_position(
            schedule, datetime(2026, 10, 5, 5, 0)
        )
        self.assertEqual(value, 48)
        self.assertEqual(next_event, datetime(2026, 10, 11, 22, 0))
        self.assertEqual(next_temperature, 48)

    def test_single_slot_at_current_time_advances_one_week(self):
        schedule = default_schedule(35)
        for day in schedule["ScheduleData"]:
            day["slots"] = []
        schedule["ScheduleData"][0]["slots"] = [
            {"Time": "06:00", "Setpoint": "50"}
        ]
        value, next_event, next_temperature = schedule_position(
            schedule, datetime(2026, 10, 5, 6, 0)
        )
        self.assertEqual(value, 50)
        self.assertEqual(next_event, datetime(2026, 10, 12, 6, 0))
        self.assertEqual(next_temperature, 50)

    def test_schedule_changes_at_exact_sunday_minute(self):
        schedule = default_schedule(35)
        sunday = schedule["ScheduleData"][6]
        sunday["slots"] = [
            {"Time": "14:00", "Setpoint": "49"},
            {"Time": "19:15", "Setpoint": "45"},
        ]

        value, next_event, next_temperature = schedule_position(
            schedule, datetime(2026, 10, 11, 19, 15, 32)
        )

        self.assertEqual(value, 45)
        self.assertEqual(next_event, datetime(2026, 10, 12, 0, 0))
        self.assertEqual(next_temperature, 35)

    def test_schedule_has_timer_and_coordinator_recovery_paths(self):
        source = (COMPONENT / "opentherm_hot_water.py").read_text()
        self.assertIn("async_track_point_in_time(", source)
        self.assertIn("next_event + timedelta(seconds=1)", source)
        self.assertIn("def _handle_coordinator_update", source)
        self.assertIn(
            "(MODE_AUTO, temperature) != self._last_schedule_request",
            source,
        )

    def test_temperature_change_in_auto_is_a_temporary_override(self):
        source = (COMPONENT / "opentherm_hot_water.py").read_text()
        self.assertIn("auto_override = self._operation == MODE_AUTO", source)
        self.assertIn("previous_schedule_request =", source)
        self.assertIn("self._target_write_in_progress = True", source)
        self.assertIn(
            "self._operation == MODE_AUTO and not self._target_write_in_progress",
            source,
        )
        self.assertIn("if auto_override:", source)
        self.assertIn("self._scheduled_temperature()", source)
        self.assertIn("self._operation = MODE_MANUAL", source)

    def test_validation_normalizes_and_rejects_unsafe_setpoints(self):
        schedule = default_schedule(35)
        schedule["ScheduleData"][0]["slots"] = [
            {"Time": "08:30", "Setpoint": "45.5"},
            {"Time": "06:00", "Setpoint": 50},
        ]
        normalized = validated_schedule(schedule, 35, 55)
        self.assertEqual(
            [slot["Time"] for slot in normalized["ScheduleData"][0]["slots"]],
            ["06:00", "08:30"],
        )

        schedule["ScheduleData"][0]["slots"][0]["Setpoint"] = 60
        with self.assertRaises(ValueError):
            validated_schedule(schedule, 35, 55)

    def test_schedule_card_off_value_uses_safe_low_setpoint(self):
        schedule = default_schedule(40)
        schedule["ScheduleData"][0]["slots"][0]["Setpoint"] = "Off"
        normalized = validated_schedule(schedule, 40, 55)
        self.assertEqual(
            normalized["ScheduleData"][0]["slots"][0]["Setpoint"], "40"
        )

    def test_non_timed_presets_can_be_scheduled_and_resolve_to_temperature(self):
        presets = [
            {
                "name": "Hand wash",
                "icon": "mdi:hand-wash",
                "temperature": 42,
                "duration_minutes": 0,
            },
            {
                "name": "Boost 30 Mins",
                "icon": "mdi:numeric-1",
                "temperature": 50,
                "duration_minutes": 30,
            },
        ]
        schedule = default_schedule(35, 55, 45, presets)
        self.assertEqual(
            schedule["PresetOptions"],
            [
                {
                    "name": "Hand wash",
                    "icon": "mdi:hand-wash",
                    "temperature": 42.0,
                }
            ],
        )
        schedule["ScheduleData"][0]["slots"] = [
            {"Time": "06:00", "Setpoint": "hand WASH"}
        ]
        normalized = validated_schedule(schedule, 35, 55, presets)
        self.assertEqual(
            normalized["ScheduleData"][0]["slots"][0]["Setpoint"],
            "Hand wash",
        )
        value, _, _ = schedule_position(
            normalized, datetime(2026, 10, 5, 7, 0)
        )
        self.assertEqual(value, 42)

        schedule["ScheduleData"][0]["slots"][0]["Setpoint"] = (
            "Boost 30 Mins"
        )
        with self.assertRaisesRegex(ValueError, "Unknown hot-water preset"):
            validated_schedule(schedule, 35, 55, presets)

    def test_removed_preset_falls_back_to_safe_minimum_when_loading(self):
        schedule = default_schedule(35)
        schedule["ScheduleData"][0]["slots"][0]["Setpoint"] = "Deleted"
        normalized = validated_schedule(
            schedule, 35, 55, [], replace_unknown_presets=True
        )
        self.assertEqual(
            normalized["ScheduleData"][0]["slots"][0]["Setpoint"], "35"
        )


if __name__ == "__main__":
    unittest.main()
