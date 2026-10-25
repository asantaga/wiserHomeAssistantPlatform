"""Test External Room Control without requiring Home Assistant."""

from __future__ import annotations

import ast
from copy import deepcopy
from datetime import datetime
import logging
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock

COMPONENT = Path(__file__).parents[1] / "custom_components/wiser"


class ExternalRoomControlClimateContractTest(unittest.TestCase):
    """Guard the climate entity against owning Passive Mode behaviour."""

    def test_external_control_does_not_replace_room_preset_or_range(self):
        tree = ast.parse((COMPONENT / "climate.py").read_text())
        obsolete_names = {
            "TEXT_EXTERNAL_ROOM_CONTROL",
            "_external_room_control_preset_modes",
        }
        self.assertFalse(
            {
                node.id
                for node in ast.walk(tree)
                if isinstance(node, ast.Name) and node.id in obsolete_names
            }
        )

    def test_passive_types_share_one_room_level_entity(self):
        tree = ast.parse((COMPONENT / "switch.py").read_text())
        classes = {
            node.name: node
            for node in tree.body
            if isinstance(node, ast.ClassDef)
        }
        passive_turn_on = next(
            node
            for node in classes["WiserPassiveModeSwitch"].body
            if isinstance(node, ast.AsyncFunctionDef) and node.name == "async_turn_on"
        )
        self.assertNotIn(
            "external_room_control", ast.unparse(passive_turn_on)
        )
        self.assertNotIn("WiserExternalRoomControlSwitch", classes)
        self.assertNotIn("WiserExternalPassiveModeSwitch", classes)
        self.assertIn(
            "data.external_room_control.is_enabled(room.id)",
            (COMPONENT / "switch.py").read_text(),
        )
        self.assertIn(
            "if data.passive_mode_enabled",
            (COMPONENT / "switch.py").read_text(),
        )

    def test_climate_reports_external_passive_overrides(self):
        climate_source = (COMPONENT / "climate.py").read_text()

        self.assertIn(
            "external_room_control.has_passive_override(self._room_id)",
            climate_source,
        )

class FakeStore:
    """Minimal Home Assistant Store replacement."""

    def __init__(self, *_args):
        self.async_load = AsyncMock(return_value=None)
        self.async_save = AsyncMock()


class FakeRegistry:
    """Return no registry entry unless a test explicitly adds one."""

    def __init__(self):
        self.entries = {}

    def async_get(self, entity_id):
        return self.entries.get(entity_id)


def load_controller():
    """Load the real controller class with lightweight dependencies."""
    tree = ast.parse((COMPONENT / "external_room_control.py").read_text())
    class_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "ExternalRoomControlController"
    )
    module = ast.Module(body=[class_node], type_ignores=[])
    ast.fix_missing_locations(module)
    registry = FakeRegistry()
    namespace = {
        "ATTR_ENTITY_ID": "entity_id",
        "ATTR_MAX_TEMP": "max_temp",
        "ATTR_MIN_TEMP": "min_temp",
        "ATTR_TEMPERATURE": "temperature",
        "CLIMATE_DOMAIN": "climate",
        "CONF_AUTOMATIONS_EXTERNAL_ROOM_CONTROL": "automations_external_room_control",
        "CONF_EXTERNAL_ROOM_CONTROL_ASSIGNMENTS": "external_room_control_assignments",
        "CONTROL_STRATEGIES": ["modulating", "temperature_limiter"],
        "CONTROL_STRATEGY_TEMPERATURE_LIMITER": "temperature_limiter",
        "DEFAULT_PASSIVE_CONTROL_STRATEGY": "modulating",
        "DOMAIN": "wiser",
        "FROST_PROTECTION_TEMPERATURE": 5.0,
        "HomeAssistantError": Exception,
        "MAX_SCHEDULE_TEMPERATURE": 30.0,
        "OFF_TEMPERATURE": -20.0,
        "SERVICE_SET_TEMPERATURE": "set_temperature",
        "STATE_UNAVAILABLE": "unavailable",
        "STATE_UNKNOWN": "unknown",
        "STORAGE_VERSION": 1,
        "Store": FakeStore,
        "WEEKDAYS": (
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ),
        "_LOGGER": logging.getLogger(__name__),
        "datetime": datetime,
        "deepcopy": deepcopy,
        "dt_util": SimpleNamespace(now=datetime.now),
        "er": SimpleNamespace(async_get=lambda _hass: registry),
    }
    exec(compile(module, "external_room_control.py", "exec"), namespace)
    return namespace["ExternalRoomControlController"], registry


class ExternalRoomControlControllerTest(unittest.IsolatedAsyncioTestCase):
    """Exercise target mirroring and Passive schedule ownership."""

    def setUp(self):
        controller_class, self.registry = load_controller()
        self.room = SimpleNamespace(
            id=1,
            mode="Auto",
            is_boosted=False,
            is_away_mode=False,
            is_passive_mode=False,
            passive_mode_enabled=False,
            passive_mode_lower_temp=15.0,
            passive_mode_upper_temp=20.0,
            configured_passive_mode_upper_temp=20.0,
            current_temperature=17.0,
            current_target_temperature=19.0,
            is_override=False,
            schedule=None,
            set_passive_mode_lower_temp=AsyncMock(),
            set_passive_mode_upper_temp=AsyncMock(),
            set_passive_mode=AsyncMock(),
            set_target_temperature=AsyncMock(),
            cancel_overrides=AsyncMock(),
        )
        wiserhub = SimpleNamespace(
            rooms=SimpleNamespace(all=[self.room]),
            system=SimpleNamespace(sunrise_times={}, sunset_times={}),
        )
        self.state = SimpleNamespace(
            state="heat",
            attributes={"temperature": 25.0, "min_temp": 5.0, "max_temp": 30.0},
        )
        self.hass = SimpleNamespace(
            states=SimpleNamespace(get=lambda _entity_id: self.state),
            services=SimpleNamespace(async_call=AsyncMock()),
        )
        config_entry = SimpleNamespace(
            entry_id="entry",
            options={
                "automations_external_room_control": {
                    "automations_external_room_control": True,
                    "external_room_control_assignments": {
                        "1": ["climate.external_trv"]
                    },
                }
            },
        )
        coordinator = SimpleNamespace(
            wiserhub=wiserhub,
            passive_mode_enabled=True,
            passive_room_strategies={},
            passive_temperature_increment=0.5,
        )
        coordinator.passive_room_strategy = lambda room_id: (
            coordinator.passive_room_strategies.get(str(room_id), "modulating")
        )
        self.controller = controller_class(self.hass, config_entry, coordinator)
        self.controller._rooms = {
            "1": {
                "passive_upper_override": None,
                "passive_lower_override": None,
                "passive_override_schedule_transition": None,
                "passive_schedule_original_enabled": None,
            }
        }
        self.controller._upper_schedules = {}
        self.controller._lower_schedules = {}

    async def test_mirrors_normal_wiser_room_target(self):
        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 19.0},
            blocking=True,
        )

    async def test_modulating_passive_mode_mirrors_room_target(self):
        self.room.is_passive_mode = True
        self.room.passive_mode_enabled = True
        self.room.current_target_temperature = 15.0

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 15.0},
            blocking=True,
        )

    async def test_temperature_limiter_opens_external_trv_below_upper(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = True
        self.room.passive_mode_enabled = True
        self.room.current_temperature = 17.0
        self.room.passive_mode_upper_temp = 20.0

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 30.0},
            blocking=True,
        )

    async def test_external_limiter_uses_native_passive_flag(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = False
        self.room.passive_mode_enabled = False
        self.room.current_temperature = 17.0
        self.room.current_target_temperature = 19.0
        self.room.passive_mode_lower_temp = 15.0
        self.room.passive_mode_upper_temp = 20.0

        await self.controller.async_update()

        self.room.set_target_temperature.assert_not_awaited()
        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 19.0},
            blocking=True,
        )

    async def test_external_limiter_respects_room_off(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.mode = "Off"
        self.room.current_target_temperature = -20.0
        self.room.passive_mode_lower_temp = 15.0
        self.room.passive_mode_upper_temp = 20.0

        await self.controller.async_update()

        self.room.set_target_temperature.assert_not_awaited()
        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 5.0},
            blocking=True,
        )

    async def test_temperature_limiter_closes_external_trv_at_upper(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = True
        self.room.passive_mode_enabled = True
        self.room.current_temperature = 20.0
        self.room.passive_mode_upper_temp = 20.0

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 5.0},
            blocking=True,
        )

    async def test_temperature_limiter_uses_hysteresis_before_reopening(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = True
        self.room.passive_mode_enabled = True
        self.room.passive_mode_upper_temp = 20.0
        self.room.current_temperature = 20.0

        await self.controller.async_update()

        self.state.attributes["temperature"] = 5.0
        self.hass.services.async_call.reset_mock()
        self.room.current_temperature = 19.8
        await self.controller.async_update()
        self.hass.services.async_call.assert_not_awaited()

        self.room.current_temperature = 19.5
        await self.controller.async_update()
        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 30.0},
            blocking=True,
        )

    async def test_temperature_limiter_uses_immediate_upper_override(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = True
        self.room.passive_mode_enabled = True
        self.room.current_temperature = 20.0
        self.room.passive_mode_upper_temp = 23.0
        self.room.is_override = True

        await self.controller.async_set_upper_temperature(1, 20.0)
        await self.controller.async_update()

        self.assertEqual(self.controller.upper_temperature(1), 20.0)
        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 5.0},
            blocking=True,
        )

    async def test_auto_upper_override_clears_at_next_schedule(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = True
        self.room.schedule = SimpleNamespace(
            id=7,
            next=SimpleNamespace(datetime=datetime(2026, 10, 17, 9, 0)),
        )

        await self.controller.async_set_upper_temperature(1, 21.0)

        self.room.set_target_temperature.assert_not_awaited()
        self.assertTrue(self.controller.has_passive_override(1))
        self.room.is_override = True
        await self.controller.async_update()
        self.assertEqual(self.controller.upper_temperature(1), 21.0)

        self.room.schedule.next.datetime = datetime(2026, 10, 17, 10, 0)
        await self.controller.async_update()

        self.assertEqual(self.controller.upper_temperature(1), 20.0)
        self.assertFalse(self.controller.has_passive_override(1))

    async def test_auto_lower_slider_creates_schedule_override(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = True
        self.room.passive_mode_enabled = True
        self.room.schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
        )

        await self.controller.async_set_passive_lower_temperature(1, 17.0)

        self.room.set_target_temperature.assert_awaited_once_with(17.0)
        self.assertEqual(
            self.controller._rooms["1"]["passive_lower_override"], 17.0
        )
        self.assertTrue(self.controller.has_passive_override(1))

    async def test_auto_lower_override_clears_at_next_schedule(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = True
        self.room.passive_mode_enabled = True
        self.room.schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            next=SimpleNamespace(datetime=datetime(2026, 10, 17, 9, 0)),
        )

        await self.controller.async_set_passive_lower_temperature(1, 17.0)
        self.room.is_override = True
        await self.controller.async_update()
        self.assertEqual(
            self.controller.passive_lower_temperature(self.room), 17.0
        )

        self.room.schedule.next.datetime = datetime(2026, 10, 17, 10, 0)
        await self.controller.async_update()

        self.assertIsNone(
            self.controller._rooms["1"]["passive_lower_override"]
        )

    async def test_combined_auto_range_change_keeps_new_lower_override(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = True
        self.room.passive_mode_enabled = True
        self.room.schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
        )

        await self.controller.async_set_passive_lower_temperature(1, 17.0)
        await self.controller.async_set_upper_temperature(1, 22.0)

        self.room.set_target_temperature.assert_awaited_once_with(17.0)
        self.assertEqual(
            self.controller._rooms["1"]["passive_upper_override"], 22.0
        )

    def test_lower_override_keeps_external_upper_limit(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_override = True
        self.room.passive_mode_enabled = True
        self.room.passive_mode_upper_temp = 17.5
        self.room.schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            current_setting=22.0,
        )
        self.controller._settings(1)["passive_lower_override"] = 19.0

        self.assertEqual(
            self.controller.passive_lower_temperature(self.room), 17.5
        )

    async def test_auto_upper_slider_is_external_limiter_only(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.is_passive_mode = True
        self.room.passive_mode_enabled = True
        self.room.schedule = SimpleNamespace(id=7)

        await self.controller.async_set_upper_temperature(1, 22.0)
        self.room.is_override = True

        self.room.set_target_temperature.assert_not_awaited()
        self.assertEqual(
            self.controller.passive_upper_temperature(self.room), 22.0
        )

    async def test_modulating_keeps_native_manual_upper_setting(self):
        self.room.mode = "Manual"

        await self.controller.async_set_upper_temperature(1, 22.0)

        self.room.set_passive_mode_upper_temp.assert_awaited_once_with(22.0)
        self.assertIsNone(
            self.controller._rooms["1"]["passive_upper_override"]
        )

    async def test_cancel_override_restores_native_upper_temperature(self):
        self.room.is_override = True
        self.controller._rooms["1"]["passive_upper_override"] = 18.0

        await self.controller.async_cancel_upper_override(1)

        self.assertEqual(self.controller.upper_temperature(1), 20.0)
        self.assertFalse(self.controller.has_passive_override(1))

    async def test_boost_and_away_still_follow_wiser_target(self):
        self.room.is_boosted = True
        self.room.is_away_mode = True
        self.room.current_target_temperature = 23.0

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 23.0},
            blocking=True,
        )

    async def test_off_target_is_clamped_to_external_minimum(self):
        self.room.mode = "Off"
        self.room.current_target_temperature = -20.0
        self.state.attributes["min_temp"] = 7.0

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 7.0},
            blocking=True,
        )

    async def test_target_is_clamped_to_external_maximum(self):
        self.room.current_target_temperature = 32.0

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 30.0},
            blocking=True,
        )

    async def test_matching_target_does_not_write_again(self):
        self.state.attributes["temperature"] = 19.0

        await self.controller.async_update()

        self.hass.services.async_call.assert_not_awaited()

    async def test_unavailable_external_entity_is_retried_on_later_updates(self):
        self.state.state = "unavailable"
        await self.controller.async_update()
        self.hass.services.async_call.assert_not_awaited()

        self.state.state = "heat"
        await self.controller.async_update()
        self.hass.services.async_call.assert_awaited_once()

    async def test_never_controls_a_wiser_climate_entity(self):
        self.registry.entries["climate.external_trv"] = SimpleNamespace(
            platform="wiser"
        )

        await self.controller.async_update()

        self.hass.services.async_call.assert_not_awaited()

    async def test_assignment_enables_control_without_a_room_switch(self):
        self.assertTrue(self.controller.is_enabled(1))

        self.controller.available = False

        self.assertFalse(self.controller.is_enabled(1))

    async def test_limiter_requires_room_strategy(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.controller.coordinator.passive_room_strategies = {}

        self.assertFalse(self.controller.uses_temperature_limiter(self.room))

    async def test_limiter_strategy_is_selected_per_room(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.controller.assignments["2"] = ["climate.second_trv"]

        self.assertTrue(self.controller.uses_temperature_limiter(1))
        self.assertFalse(self.controller.uses_temperature_limiter(2))

    async def test_native_passive_state_gates_limiter_runtime(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }

        self.assertTrue(self.controller.uses_temperature_limiter(self.room))
        self.assertFalse(self.room.is_passive_mode)

    async def test_duplicate_assignments_are_ignored_at_runtime(self):
        controller_class, _registry = load_controller()
        config_entry = SimpleNamespace(
            entry_id="entry",
            options={
                "automations_external_room_control": {
                    "automations_external_room_control": True,
                    "external_room_control_assignments": {
                        "1": ["climate.shared_trv"],
                        "2": ["climate.shared_trv"],
                    },
                }
            },
        )
        controller = controller_class(
            self.hass,
            config_entry,
            SimpleNamespace(
                wiserhub=SimpleNamespace(
                    rooms=SimpleNamespace(all=[self.room, SimpleNamespace(id=2)]),
                    system=SimpleNamespace(sunrise_times={}, sunset_times={}),
                )
            ),
        )

        self.assertEqual(controller.assigned_entity_ids(1), [])
        self.assertEqual(controller.assigned_entity_ids(2), [])

    async def test_load_removes_obsolete_external_range_state(self):
        self.controller._store.async_load.return_value = {
            "rooms": {
                "1": {
                    "enabled": True,
                    "lower": 15.0,
                    "upper": 20.0,
                    "upper_override": 21.0,
                    "open_targets": {"climate.external_trv": 25.0},
                    "controlled_targets": {"climate.external_trv": 20.0},
                }
            },
            "upper_schedules": {"7": {"Monday": {"06:00": 22.0}}},
        }

        await self.controller.async_load()

        self.assertEqual(
            self.controller._rooms["1"],
            {
                "passive_upper_override": None,
                "passive_lower_override": None,
                "passive_override_schedule_transition": None,
                "passive_schedule_original_enabled": None,
            },
        )
        self.assertEqual(
            self.controller._upper_schedules,
            {"7": {"Monday": {"06:00": 22.0}}},
        )

    async def test_native_passive_schedule_works_when_native_type_selected(self):
        self.controller.coordinator.passive_room_strategies = {}
        self.room.passive_mode_enabled = True
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": "20"}],
                    }
                ]
            },
        )

        data = self.controller.schedule_data(schedule)

        self.assertTrue(data["PassiveRange"])
        self.assertEqual(data["PassiveRangeType"], "native")
        self.assertEqual(
            data["ScheduleData"][0]["slots"][0]["Setpoint"], 15.0
        )
        self.assertEqual(
            data["ScheduleData"][0]["slots"][0]["UpperSetpoint"], 20.0
        )

    def test_scheduled_passive_controls_are_exposed_and_evaluated(self):
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [
                            {"Time": "06:00", "Setpoint": "20"},
                            {"Time": "18:00", "Setpoint": "16"},
                        ],
                    }
                ]
            },
        )
        self.room.schedule = schedule
        self.controller._passive_control_schedules = {
            "7": {
                "Monday": {
                    "06:00": {
                        "scheduled": True,
                        "enabled": True,
                        "strategy": "modulating",
                        "lower": 15.0,
                        "upper": 20.0,
                    },
                    "18:00": {
                        "scheduled": True,
                        "enabled": False,
                        "strategy": "temperature_limiter",
                        "lower": 16.0,
                        "upper": 21.0,
                    },
                }
            }
        }

        data = self.controller.schedule_data(schedule)

        self.assertEqual(data["Capabilities"], {"PassiveControl": True})
        self.assertEqual(
            data["PassiveControlDefaults"],
            {"Enabled": False, "Strategy": "modulating"},
        )
        self.assertTrue(data["PassiveControl"])
        self.assertEqual(data["PassiveRangeType"], "scheduled")
        self.assertEqual(
            data["ScheduleData"][0]["slots"][0],
            {
                "Time": "06:00",
                "Setpoint": 15.0,
                "UpperSetpoint": 20.0,
                "PassiveScheduled": True,
                "PassiveMode": True,
                "PassiveStrategy": "modulating",
            },
        )
        self.assertEqual(
            self.controller.scheduled_passive_control(
                1, datetime(2026, 10, 19, 12, 0)
            )["strategy"],
            "modulating",
        )
        self.assertFalse(
            self.controller.scheduled_passive_control(
                1, datetime(2026, 10, 19, 20, 0)
            )["enabled"]
        )

    def test_validated_passive_controls_select_the_hub_setpoint(self):
        schedule = {
            "PassiveControl": True,
            "PassiveRange": True,
            "PassiveRangeType": "native",
            "PassiveControlDefaults": {
                "Enabled": True,
                "Strategy": "temperature_limiter",
            },
            "ScheduleData": [
                {
                    "day": "Monday",
                    "slots": [
                        {
                            "Time": "06:00",
                            "Setpoint": 15,
                            "UpperSetpoint": 20,
                            "PassiveScheduled": True,
                            "PassiveMode": True,
                            "PassiveStrategy": "modulating",
                        },
                        {
                            "Time": "18:00",
                            "Setpoint": 16,
                            "UpperSetpoint": 21,
                            "PassiveScheduled": True,
                            "PassiveMode": True,
                            "PassiveStrategy": "temperature_limiter",
                        },
                        {
                            "Time": "22:00",
                            "Setpoint": 14,
                            "UpperSetpoint": 18,
                            "PassiveScheduled": True,
                            "PassiveMode": False,
                            "PassiveStrategy": "temperature_limiter",
                        },
                        {
                            "Time": "23:00",
                            "Setpoint": 17,
                            "UpperSetpoint": 22,
                            "PassiveScheduled": False,
                        },
                    ],
                }
            ],
        }

        controls, native = self.controller.validated_passive_control_schedule(
            schedule
        )

        self.assertEqual(controls["Monday"]["06:00"]["lower"], 15.0)
        self.assertEqual(
            [slot["Setpoint"] for slot in native["ScheduleData"][0]["slots"]],
            [20.0, 16.0, 14.0, 22],
        )
        self.assertFalse(controls["Monday"]["23:00"]["scheduled"])
        self.assertNotIn("PassiveControl", native)
        self.assertNotIn("Capabilities", native)
        self.assertNotIn("PassiveControlDefaults", native)
        self.assertNotIn("UpperSetpoint", native["ScheduleData"][0]["slots"][0])

    def test_schedule_uses_the_current_room_mode_as_period_defaults(self):
        self.room.passive_mode_enabled = True
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": "17"}],
                    }
                ]
            },
        )
        self.room.schedule = schedule

        data = self.controller.schedule_data(schedule)

        self.assertEqual(
            data["PassiveControlDefaults"],
            {"Enabled": True, "Strategy": "temperature_limiter"},
        )
        self.assertEqual(data["ScheduleData"][0]["slots"][0]["Setpoint"], "17")
        self.assertEqual(data["ScheduleData"][0]["slots"][0]["UpperSetpoint"], 20.0)

    def test_only_heating_schedules_publish_passive_control_capability(self):
        schedule = SimpleNamespace(
            id=7,
            schedule_type="OnOff",
            assignment_ids=[],
            ws_schedule_data={"ScheduleData": []},
        )

        self.assertNotIn("Capabilities", self.controller.schedule_data(schedule))

    def test_unassigned_schedule_can_use_temperature_limiter(self):
        schedule = SimpleNamespace(assignment_ids=[])

        self.assertTrue(
            self.controller.schedule_supports_temperature_limiter(schedule)
        )

    async def test_update_applies_scheduled_passive_mode(self):
        self.room.schedule = SimpleNamespace(
            id=7,
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "00:00", "Setpoint": "20"}],
                    }
                ]
            },
        )
        self.controller._passive_control_schedules = {
            "7": {
                "Monday": {
                    "00:00": {
                        "scheduled": True,
                        "enabled": True,
                        "strategy": "modulating",
                        "lower": 15.0,
                        "upper": 20.0,
                    }
                }
            }
        }

        await self.controller.async_update()

        self.room.set_passive_mode.assert_awaited_once_with(True)
        self.room.cancel_overrides.assert_not_awaited()
        self.assertFalse(
            self.controller._rooms["1"]["passive_schedule_original_enabled"]
        )

        self.room.passive_mode_enabled = True
        self.controller._passive_control_schedules["7"]["Monday"]["00:00"] = {
            "scheduled": False
        }
        await self.controller.async_update()

        self.assertEqual(
            self.room.set_passive_mode.await_args_list[-1].args,
            (False,),
        )
        self.room.cancel_overrides.assert_awaited_once()

    async def test_native_passive_lower_uses_local_schedule(self):
        self.controller.coordinator.passive_room_strategies = {}
        self.room.passive_mode_enabled = True
        self.room.is_passive_mode = True
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": "20"}],
                    }
                ]
            },
        )
        self.room.schedule = schedule
        self.controller._lower_schedules = {
            "7": {"Monday": {"06:00": 17.0}}
        }

        self.assertEqual(
            self.controller.passive_lower_temperature(
                self.room, datetime(2026, 10, 12, 12, 0)
            ),
            17.0,
        )

    async def test_external_passive_schedule_works_when_external_type_selected(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.passive_mode_enabled = True
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": "20"}],
                    }
                ]
            },
        )

        data = self.controller.schedule_data(schedule)

        self.assertEqual(data["PassiveRangeType"], "external")
        self.assertEqual(data["ScheduleData"][0]["slots"][0]["Setpoint"], "20")
        self.assertEqual(
            data["ScheduleData"][0]["slots"][0]["UpperSetpoint"], 20.0
        )

    async def test_external_passive_schedule_uses_room_schedule_link(self):
        """Expose the range when the API assignment cache is not populated."""
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.passive_mode_enabled = True
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[],
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": "18"}],
                    }
                ]
            },
        )
        self.room.schedule = schedule

        data = self.controller.schedule_data(schedule)

        self.assertTrue(data["PassiveRange"])
        self.assertEqual(data["PassiveRangeType"], "external")
        self.assertEqual(
            data["ScheduleData"][0]["slots"][0]["UpperSetpoint"], 20.0
        )

    async def test_shared_schedule_does_not_become_external_range(self):
        """Do not change normal rooms through a shared limiter schedule."""
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.passive_mode_enabled = True
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1, 2],
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": "18"}],
                    }
                ]
            },
        )
        self.room.schedule = schedule
        normal_room = SimpleNamespace(
            id=2,
            schedule=schedule,
            passive_mode_enabled=False,
        )
        self.controller.coordinator.wiserhub.rooms.all.append(normal_room)

        data = self.controller.schedule_data(schedule)

        self.assertNotIn("PassiveRange", data)
        self.assertEqual(data["ScheduleData"], schedule.ws_schedule_data["ScheduleData"])
        self.assertEqual(data["Capabilities"], {"PassiveControl": True})

    async def test_failed_upper_schedule_save_restores_memory(self):
        self.controller._upper_schedules = {
            "7": {"Monday": {"06:00": 20.0}}
        }
        self.controller._store.async_save.side_effect = RuntimeError("save failed")

        with self.assertRaisesRegex(RuntimeError, "save failed"):
            await self.controller.async_save_upper_schedule(
                7, {"Monday": {"06:00": 22.0}}
            )

        self.assertEqual(
            self.controller._upper_schedules,
            {"7": {"Monday": {"06:00": 20.0}}},
        )

    async def test_copy_schedule_metadata_replaces_stale_target_values(self):
        self.controller._upper_schedules = {
            "8": {"Monday": {"06:00": 99.0}}
        }
        self.controller._lower_schedules = {
            "8": {"Monday": {"06:00": 12.0}}
        }
        self.controller._passive_control_schedules = {
            "7": {
                "Monday": {
                    "06:00": {
                        "enabled": True,
                        "strategy": "modulating",
                        "lower": 15.0,
                        "upper": 20.0,
                    }
                }
            }
        }

        await self.controller.async_copy_schedule_metadata(7, 8)

        self.assertNotIn("8", self.controller._upper_schedules)
        self.assertNotIn("8", self.controller._lower_schedules)
        self.assertEqual(
            self.controller._passive_control_schedules["8"],
            self.controller._passive_control_schedules["7"],
        )

    async def test_external_limiter_lower_uses_hub_schedule_target(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.passive_mode_enabled = True
        self.room.is_passive_mode = True
        self.room.schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            current_setting=17.0,
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [
                            {"Time": "06:00", "Setpoint": "20"},
                            {"Time": "18:00", "Setpoint": "22"},
                        ],
                    }
                ]
            },
        )
        self.assertEqual(
            self.controller.passive_lower_temperature(
                self.room, datetime(2026, 10, 12, 19, 0)
            ),
            17.0,
        )

    async def test_external_passive_schedule_rejects_invalid_range(self):
        schedule = {
            "ScheduleData": [
                {
                    "day": "Monday",
                    "slots": [
                        {
                            "Time": "06:00",
                            "Setpoint": 21,
                            "UpperSetpoint": 20,
                        }
                    ],
                }
            ]
        }

        with self.assertRaisesRegex(ValueError, "must not be below"):
            self.controller.validated_upper_schedule(7, schedule)

    async def test_migrates_experimental_lower_schedule_to_hub(self):
        self.controller.coordinator.passive_room_strategies = {
            "1": "temperature_limiter"
        }
        self.room.passive_mode_enabled = True
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": 22.0}],
                    }
                ]
            },
            set_schedule_from_ws_data=AsyncMock(),
        )
        self.controller.coordinator.wiserhub.schedules = SimpleNamespace(
            heating_schedules=[schedule]
        )
        self.controller._lower_schedules = {
            "7": {"Monday": {"06:00": 18.0}}
        }

        changed = await self.controller.async_migrate_legacy_schedule_ownership()

        self.assertTrue(changed)
        schedule.set_schedule_from_ws_data.assert_awaited_once_with(
            {
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": 18.0}],
                    }
                ]
            }
        )
        self.assertEqual(
            self.controller._upper_schedules,
            {"7": {"Monday": {"06:00": 22.0}}},
        )
        self.assertEqual(self.controller._lower_schedules, {})

    async def test_switching_back_to_native_restores_upper_to_hub(self):
        self.controller.coordinator.passive_room_strategies = {}
        self.room.passive_mode_enabled = True
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": 18.0}],
                    }
                ]
            },
            set_schedule_from_ws_data=AsyncMock(),
        )
        self.controller.coordinator.wiserhub.schedules = SimpleNamespace(
            heating_schedules=[schedule]
        )
        self.controller._upper_schedules = {
            "7": {"Monday": {"06:00": 22.0}}
        }

        changed = await self.controller.async_migrate_legacy_schedule_ownership()

        self.assertTrue(changed)
        schedule.set_schedule_from_ws_data.assert_awaited_once_with(
            {
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": 22.0}],
                    }
                ]
            }
        )
        self.assertEqual(
            self.controller._lower_schedules,
            {"7": {"Monday": {"06:00": 18.0}}},
        )
        self.assertEqual(self.controller._upper_schedules, {})


if __name__ == "__main__":
    unittest.main()
