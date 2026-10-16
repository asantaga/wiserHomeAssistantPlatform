"""Test External Passive Mode without requiring Home Assistant."""

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


def load_climate_function(name):
    """Load a standalone climate helper without Home Assistant dependencies."""
    tree = ast.parse((COMPONENT / "climate.py").read_text())
    function_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name == name
    )
    module = ast.Module(body=[function_node], type_ignores=[])
    ast.fix_missing_locations(module)
    namespace = {
        "STATUS_BOOST": "Boost",
        "TEXT_EXTERNAL_PASSIVE": "External Passive",
    }
    exec(compile(module, "climate.py", "exec"), namespace)
    return namespace[name]


class ExternalPassiveClimateContractTest(unittest.TestCase):
    """Guard the climate entity against removed controller properties."""

    def test_external_passive_is_listed_before_boost_presets(self):
        preset_modes = load_climate_function("_external_passive_preset_modes")

        self.assertEqual(
            preset_modes(
                [
                    "Advance Schedule",
                    "Cancel Overrides",
                    "Boost 30m",
                    "Boost 1h",
                ]
            ),
            [
                "Advance Schedule",
                "Cancel Overrides",
                "External Passive",
                "Boost 30m",
                "Boost 1h",
            ],
        )

    def test_external_passive_is_not_duplicated(self):
        preset_modes = load_climate_function("_external_passive_preset_modes")

        self.assertEqual(
            preset_modes(["External Passive", "Boost 30m"]),
            ["External Passive", "Boost 30m"],
        )

    def test_climate_does_not_read_removed_temperature_increment(self):
        tree = ast.parse((COMPONENT / "climate.py").read_text())
        stale_references = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Attribute)
            and node.attr == "temperature_increment"
            and isinstance(node.value, ast.Attribute)
            and node.value.attr == "external_passive"
        ]

        self.assertEqual(stale_references, [])

    def test_external_passive_preset_is_not_sent_to_the_hub(self):
        """The local state indicator must be handled before native presets."""
        tree = ast.parse((COMPONENT / "climate.py").read_text())
        function = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.AsyncFunctionDef)
            and node.name == "async_set_preset_mode"
        )
        guard = next(
            node
            for node in ast.walk(function)
            if isinstance(node, ast.If)
            and any(
                isinstance(item, ast.Name)
                and item.id == "TEXT_EXTERNAL_PASSIVE"
                for item in ast.walk(node.test)
            )
        )
        native_call = next(
            node
            for node in ast.walk(function)
            if isinstance(node, ast.Await)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "set_preset"
        )

        self.assertLess(guard.lineno, native_call.lineno)
        self.assertTrue(any(isinstance(item, ast.Return) for item in guard.body))

    def test_saved_upper_schedule_is_applied_immediately(self):
        """A schedule save must rerun valve control after local upper values persist."""
        tree = ast.parse((COMPONENT / "websockets.py").read_text())
        save_call = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Await)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "async_save_upper_schedule"
        )
        update_call = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Await)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "async_update"
            and isinstance(node.value.func.value, ast.Attribute)
            and node.value.func.value.attr == "external_passive"
        )

        self.assertLess(save_call.lineno, update_call.lineno)


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
    tree = ast.parse((COMPONENT / "external_passive.py").read_text())
    class_node = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        and node.name == "ExternalPassiveController"
    )
    module = ast.Module(body=[class_node], type_ignores=[])
    ast.fix_missing_locations(module)
    registry = FakeRegistry()
    namespace = {
        "ATTR_ENTITY_ID": "entity_id",
        "ATTR_MAX_TEMP": "max_temp",
        "ATTR_TEMPERATURE": "temperature",
        "CLIMATE_DOMAIN": "climate",
        "CONF_AUTOMATIONS_EXTERNAL_PASSIVE": "automations_external_passive_mode",
        "CONF_EXTERNAL_PASSIVE_ASSIGNMENTS": "external_passive_mode_assignments",
        "DEFAULT_LOWER_TEMPERATURE": 14.0,
        "DEFAULT_OPEN_TEMPERATURE": 25.0,
        "DEFAULT_UPPER_TEMPERATURE": 18.0,
        "DOMAIN": "wiser",
        "FROST_PROTECTION_TEMPERATURE": 5.0,
        "HomeAssistantError": Exception,
        "MAX_SCHEDULE_TEMPERATURE": 30.0,
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
    exec(compile(module, "external_passive.py", "exec"), namespace)
    return namespace["ExternalPassiveController"], registry


class ExternalPassiveControllerTest(unittest.IsolatedAsyncioTestCase):
    """Exercise target calculation and safety boundaries."""

    def setUp(self):
        controller_class, self.registry = load_controller()
        self.external_room = SimpleNamespace(
            id=1,
            mode="Auto",
            is_boosted=False,
            is_away_mode=False,
            is_passive_mode=False,
            percentage_demand=100,
            current_temperature=17.0,
            current_target_temperature=15.0,
            scheduled_target_temperature=14.0,
            is_override=False,
            schedule=None,
            set_target_temperature=AsyncMock(),
            cancel_overrides=AsyncMock(),
        )
        wiserhub = SimpleNamespace(
            rooms=SimpleNamespace(all=[self.external_room]),
            system=SimpleNamespace(sunrise_times={}, sunset_times={}),
        )
        self.state = SimpleNamespace(
            state="heat", attributes={"temperature": 25.0}
        )
        self.hass = SimpleNamespace(
            states=SimpleNamespace(get=lambda _entity_id: self.state),
            services=SimpleNamespace(async_call=AsyncMock()),
        )
        options = {
            "automations_external_passive_mode": {
                "automations_external_passive_mode": True,
                "external_passive_mode_assignments": {
                    "1": ["climate.external_trv"]
                },
            }
        }
        config_entry = SimpleNamespace(options=options, entry_id="entry")
        coordinator = SimpleNamespace(wiserhub=wiserhub)
        self.controller = controller_class(
            self.hass, config_entry, coordinator
        )
        self.controller._rooms = {
            "1": {
                "enabled": True,
                "lower": 15.0,
                "upper": 20.0,
                "upper_override": None,
                "open_targets": {},
            }
        }
        self.controller._upper_schedules = {}

    async def test_auto_lower_threshold_uses_hub_schedule(self):
        """Auto mode reads the hub schedule instead of stored parallel state."""
        self.external_room.current_target_temperature = 20.0

        self.assertEqual(self.controller.lower_temperature(1), 14.0)

    async def test_user_lower_override_uses_existing_wiser_override(self):
        """Changing the lower threshold uses the native room override API."""
        await self.controller.async_set_lower_temperature(1, 16.0)

        self.external_room.set_target_temperature.assert_awaited_once_with(16.0)

    async def test_native_override_becomes_lower_threshold(self):
        """The current Wiser target replaces the schedule during an override."""
        self.external_room.is_override = True
        self.external_room.current_target_temperature = 16.0

        self.assertEqual(self.controller.lower_temperature(1), 16.0)

    async def test_load_prunes_targets_for_entities_no_longer_assigned(self):
        """Stored fallback targets do not grow after assignments change."""
        self.controller._store.async_load.return_value = {
            "rooms": {
                "1": {
                    "enabled": True,
                    "lower": 15.0,
                    "upper": 20.0,
                    "open_targets": {
                        "climate.external_trv": 25.0,
                        "climate.removed_trv": 22.0,
                    },
                }
            }
        }

        await self.controller.async_load()

        self.assertEqual(
            self.controller._rooms["1"]["open_targets"],
            {"climate.external_trv": 25.0},
        )
        self.controller._store.async_save.assert_awaited_once_with(
            {
                "rooms": self.controller._rooms,
                "upper_schedules": {},
            }
        )

    async def test_between_thresholds_keeps_external_valve_open(self):
        """Incidental heat is allowed without creating Wiser demand."""
        self.external_room.current_temperature = 18.0

        await self.controller.async_update()

        self.external_room.set_target_temperature.assert_not_awaited()
        self.hass.services.async_call.assert_not_awaited()

    async def test_schedule_payload_pairs_native_lower_with_local_upper(self):
        """Heating schedules expose an upper value without replacing Setpoint."""
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "Id": 7,
                "Type": "Heating",
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": "14"}],
                    }
                ],
            },
        )

        data = self.controller.schedule_data(schedule)

        self.assertTrue(data["ExternalPassiveRange"])
        self.assertEqual(
            data["ScheduleData"][0]["slots"][0]["Setpoint"], "14"
        )
        self.assertEqual(
            data["ScheduleData"][0]["slots"][0]["UpperSetpoint"], 20.0
        )

    async def test_disabled_feature_does_not_decorate_heating_schedule(self):
        """Global disablement removes External Passive schedule fields."""
        self.controller.available = False
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "Id": 7,
                "Type": "Heating",
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": "14"}],
                    }
                ],
            },
        )

        data = self.controller.schedule_data(schedule)

        self.assertNotIn("ExternalPassiveRange", data)
        self.assertNotIn("UpperSetpoint", data["ScheduleData"][0]["slots"][0])

    async def test_disabled_room_does_not_decorate_heating_schedule(self):
        """A room with its External Passive switch off uses a native schedule."""
        self.controller._rooms["1"]["enabled"] = False
        schedule = SimpleNamespace(
            id=7,
            schedule_type="Heating",
            assignment_ids=[1],
            ws_schedule_data={
                "Id": 7,
                "Type": "Heating",
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [{"Time": "06:00", "Setpoint": "14"}],
                    }
                ],
            },
        )

        data = self.controller.schedule_data(schedule)

        self.assertNotIn("ExternalPassiveRange", data)
        self.assertNotIn("UpperSetpoint", data["ScheduleData"][0]["slots"][0])

    async def test_current_upper_uses_matching_local_schedule_slot(self):
        """The upper threshold follows the slot times owned by the hub schedule."""
        self.external_room.schedule = SimpleNamespace(
            id=7,
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [
                            {"Time": "06:00", "Setpoint": "14"},
                            {"Time": "18:00", "Setpoint": "16"},
                        ],
                    }
                ]
            },
        )
        self.controller._upper_schedules = {
            "7": {"Monday": {"06:00": 20.0, "18:00": 22.0}}
        }

        self.assertEqual(
            self.controller._scheduled_upper_temperature(
                self.external_room, datetime(2026, 10, 12, 19, 0)
            ),
            22.0,
        )

    async def test_advance_schedule_uses_next_upper_slot(self):
        """Wiser Advance Schedule advances the paired upper threshold too."""
        self.external_room.schedule = SimpleNamespace(
            id=7,
            ws_schedule_data={
                "ScheduleData": [
                    {
                        "day": "Monday",
                        "slots": [
                            {"Time": "06:00", "Setpoint": "14"},
                            {"Time": "18:00", "Setpoint": "16"},
                        ],
                    }
                ]
            },
        )
        self.controller._upper_schedules = {
            "7": {"Monday": {"06:00": 20.0, "18:00": 22.0}}
        }

        next_upper = self.controller._scheduled_upper_temperature(
            self.external_room,
            datetime(2026, 10, 12, 10, 0),
            next_period=True,
        )

        self.assertEqual(next_upper, 22.0)

    async def test_upper_schedule_rejects_value_below_native_lower(self):
        """Each local upper limit must preserve a valid temperature range."""
        schedule = {
            "ScheduleData": [
                {
                    "day": "Monday",
                    "slots": [
                        {
                            "Time": "06:00",
                            "Setpoint": "18",
                            "UpperSetpoint": 17,
                        }
                    ],
                }
            ]
        }

        with self.assertRaisesRegex(ValueError, "must not be below"):
            self.controller.validated_upper_schedule(7, schedule)

    async def test_open_valve_uses_its_advertised_maximum_temperature(self):
        """The valve stays fully open when its climate entity reports a maximum."""
        self.external_room.current_temperature = 18.0
        self.state.attributes["max_temp"] = 30.0

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 30.0},
            blocking=True,
        )

    async def test_invalid_maximum_falls_back_to_remembered_target(self):
        """An unusable advertised maximum cannot replace the safe fallback."""
        self.external_room.current_temperature = 19.5
        self.state.attributes.update({"temperature": 5.0, "max_temp": "unknown"})
        self.controller._rooms["1"]["open_targets"] = {
            "climate.external_trv": 22.0
        }

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 22.0},
            blocking=True,
        )

    async def test_closes_at_upper_limit_using_frost_protection_target(self):
        """Reaching the upper cutoff closes the valve at 5 C internally."""
        self.external_room.current_temperature = 20.0

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 5.0},
            blocking=True,
        )
        self.assertEqual(
            self.controller._rooms["1"]["open_targets"],
            {"climate.external_trv": 25.0},
        )

    async def test_reopens_below_upper_limit_to_remembered_target(self):
        """Cooling below the upper cutoff restores the prior valve target."""
        self.external_room.current_temperature = 19.5
        self.state.attributes["temperature"] = 5.0
        self.controller._rooms["1"]["open_targets"] = {
            "climate.external_trv": 25.0
        }

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 25.0},
            blocking=True,
        )

    async def test_boost_opens_a_previously_closed_external_valve(self):
        """A native room boost must not be blocked by the external limiter."""
        self.external_room.is_boosted = True
        self.state.attributes.update({"temperature": 5.0, "max_temp": 30.0})

        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 30.0},
            blocking=True,
        )

    async def test_duplicate_assignments_are_ignored_at_runtime(self):
        """Old invalid options cannot make two rooms fight over one TRV."""
        controller_class, _registry = load_controller()
        second_room = SimpleNamespace(id=2)
        coordinator = SimpleNamespace(
            wiserhub=SimpleNamespace(
                rooms=SimpleNamespace(all=[self.external_room, second_room]),
                system=SimpleNamespace(sunrise_times={}, sunset_times={}),
            )
        )
        config_entry = SimpleNamespace(
            entry_id="entry",
            options={
                "automations_external_passive_mode": {
                    "automations_external_passive_mode": True,
                    "external_passive_mode_assignments": {
                        "1": ["climate.shared_trv"],
                        "2": ["climate.shared_trv"],
                    },
                }
            },
        )

        controller = controller_class(self.hass, config_entry, coordinator)

        self.assertEqual(controller.assigned_entity_ids(1), [])
        self.assertEqual(controller.assigned_entity_ids(2), [])

    async def test_orphaned_upper_schedules_are_removed_after_refresh(self):
        """Schedules deleted outside Home Assistant do not leave reusable data."""
        self.controller.coordinator.wiserhub.schedules = SimpleNamespace(
            heating_schedules=[SimpleNamespace(id=7)]
        )
        self.controller._upper_schedules = {
            "7": {"Monday": {"06:00": 20.0}},
            "9": {"Monday": {"06:00": 24.0}},
        }

        await self.controller.async_update()

        self.assertEqual(
            self.controller._upper_schedules,
            {"7": {"Monday": {"06:00": 20.0}}},
        )
        self.controller._store.async_save.assert_awaited()

    async def test_restores_non_default_external_target(self):
        """A valve's own normal target is remembered rather than forced to 25 C."""
        self.external_room.current_temperature = 20.0
        self.state.attributes["temperature"] = 22.0
        await self.controller.async_update()

        self.hass.services.async_call.reset_mock()
        self.external_room.current_temperature = 19.0
        self.state.attributes["temperature"] = 5.0
        await self.controller.async_update()

        self.hass.services.async_call.assert_awaited_once_with(
            "climate",
            "set_temperature",
            {"entity_id": "climate.external_trv", "temperature": 22.0},
            blocking=True,
        )

    async def test_never_controls_a_wiser_climate_entity(self):
        """A mistaken Wiser-to-Wiser assignment cannot create heat demand."""
        self.registry.entries["climate.external_trv"] = SimpleNamespace(
            platform="wiser"
        )

        await self.controller.async_update()

        self.hass.services.async_call.assert_not_awaited()

    async def test_disabling_leaves_valve_alone_and_persists_the_switch(self):
        """Turning the mode off cancels the room override but leaves its valve alone."""
        self.state.attributes["temperature"] = 18.0

        await self.controller.async_set_enabled(1, False)

        self.controller._store.async_save.assert_awaited_once()
        self.external_room.cancel_overrides.assert_awaited_once_with()
        self.hass.services.async_call.assert_not_awaited()

    async def test_disabling_by_string_room_id_cancels_the_matching_override(self):
        """Settings-form room IDs use strings but still resolve the Wiser room."""
        await self.controller.async_set_enabled("1", False)

        self.external_room.cancel_overrides.assert_awaited_once_with()

    async def test_inactive_room_leaves_valve_alone(self):
        """Room off, boost, or away states relinquish external TRV control."""
        self.external_room.mode = "Off"

        await self.controller.async_update()

        self.hass.services.async_call.assert_not_awaited()


if __name__ == "__main__":
    unittest.main()
