"""Regression tests for the Hot Water switch without Home Assistant runtime deps."""

from __future__ import annotations

import __future__
import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/switch.py"


def _module(name: str, **attributes: object) -> ModuleType:
    """Create and register a lightweight module stub."""
    module = ModuleType(name)
    module.__dict__.update(attributes)
    sys.modules[name] = module
    return module


def _load_switch_module() -> ModuleType:
    """Load the switch module with only the imports needed by this test."""
    _module("voluptuous", Schema=lambda *a, **k: None, Required=lambda *a, **k: None, Coerce=lambda *a, **k: None)

    _module("homeassistant")
    _module("homeassistant.components")

    class SwitchEntity:
        pass

    _module(
        "homeassistant.components.switch",
        SwitchDeviceClass=SimpleNamespace(OUTLET="outlet"),
        SwitchEntity=SwitchEntity,
    )
    _module("homeassistant.const", ATTR_ENTITY_ID="entity_id")
    _module("homeassistant.helpers")
    _module("homeassistant.helpers.config_validation", entity_id=lambda x: x)
    _module("homeassistant.core", HomeAssistant=object, callback=lambda func: func)

    class CoordinatorEntity:
        def __init__(self, *args: object) -> None:
            pass

        async def async_will_remove_from_hass(self) -> None:
            self.removed = True

    _module(
        "homeassistant.helpers.update_coordinator", CoordinatorEntity=CoordinatorEntity
    )

    package = _module("wiser")
    package.__path__ = []
    _module(
        "wiser.const",
        DATA="data",
        DOMAIN="wiser",
        ENTITY_PREFIX="Wiser",
        HOT_WATER="hot_water",
        MANUFACTURER="Drayton",
        MANUFACTURER_SCHNEIDER="Schneider Electric",
    )

    def hub_error_handler(func):
        return func

    _module(
        "wiser.helpers",
        active_wiser_rooms=lambda data: [
            room
            for room in data.wiserhub.rooms.all
            if str(getattr(room, "_data", {}).get("Invalid", "")).casefold()
            != "nothingassigned"
        ],
        get_device_name=lambda _data, device_id, device_type="device": (
            "Hot Water" if device_type == "Hot Water" else "Wiser HeatHub"
        ),
        get_hub_device_info=lambda _data: {"identifiers": {("wiser", "hub")}},
        get_hub_via_device_info=lambda _data: {},
        get_identifier=lambda *_args: "identifier",
        get_legacy_device_name=lambda *_args, **_kwargs: "Wiser HeatHub",
        get_legacy_unique_id=lambda *_args: "legacy-unique-id",
        get_light_entity_name=lambda _data, _light, entity_name: entity_name,
        get_physical_entity_unique_id=lambda *_args: "physical-entity-id",
        get_room_entity_unique_id=lambda *_args: "room-entity-id",
        get_unique_id=lambda *_args: "unique-id",
        get_uuid_unique_id=lambda *_args: "uuid-unique-id",
        hub_error_handler=hub_error_handler,
    )

    class WiserEntityMixin:
        pass

    _module("wiser.entity", WiserEntityMixin=WiserEntityMixin)

    class WiserScheduleEntity:
        pass

    _module("custom_components")
    _module("custom_components.wiser")
    _module("custom_components.wiser.schedules", WiserScheduleEntity=WiserScheduleEntity)

    spec = importlib.util.spec_from_file_location("wiser.switch", SOURCE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    # The integration targets Home Assistant's newer Python runtime. Compile
    # annotations lazily so this lightweight regression test also runs with the
    # older system Python available in the local development environment.
    source = SOURCE_PATH.read_text(encoding="utf-8")
    code = compile(
        source,
        SOURCE_PATH,
        "exec",
        flags=__future__.annotations.compiler_flag,
    )
    exec(code, module.__dict__)
    return module


class WiserHotWaterSwitchTest(unittest.TestCase):
    """Tests for the Hot Water on/off switch."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.switch_module = _load_switch_module()

    def _switch(self, *, current_state: str):
        hotwater = SimpleNamespace(
            id=0,
            current_state=current_state,
            override_state=self._record_override_state,
        )
        self._override_calls = []
        data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                hotwater=hotwater, system=SimpleNamespace(name="WiserHeat045XXX")
            )
        )
        switch = self.switch_module.WiserHotWaterSwitch(data, 0, "Hot Water")
        switch.async_force_update = self._noop_async
        return switch

    async def _record_override_state(self, state: str) -> None:
        self._override_calls.append(state)

    async def _noop_async(self, *_args, **_kwargs) -> None:
        return None

    def test_is_on_when_hot_water_current_state_is_on(self) -> None:
        switch = self._switch(current_state="On")

        self.assertTrue(switch.is_on)

    def test_is_off_when_hot_water_current_state_is_off(self) -> None:
        switch = self._switch(current_state="Off")

        self.assertFalse(switch.is_on)

    def test_turn_on_overrides_hot_water_state_to_on(self) -> None:
        switch = self._switch(current_state="Off")

        asyncio.run(switch.async_turn_on())

        self.assertEqual(self._override_calls, ["On"])

    def test_turn_off_overrides_hot_water_state_to_off(self) -> None:
        switch = self._switch(current_state="On")

        asyncio.run(switch.async_turn_off())

        self.assertEqual(self._override_calls, ["Off"])


class WiserPassiveModeRoomSupportTest(unittest.TestCase):
    """Tests for deciding which rooms receive a passive-mode switch."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.switch_module = _load_switch_module()

    def test_supports_smart_valve_room(self) -> None:
        room = SimpleNamespace(
            number_of_smartvalves=1,
            underfloor_heating_id=None,
        )

        self.assertTrue(self.switch_module._room_supports_passive_mode(room))

    def test_supports_ufh_only_room(self) -> None:
        room = SimpleNamespace(
            number_of_smartvalves=0,
            underfloor_heating_id=4,
        )

        self.assertTrue(self.switch_module._room_supports_passive_mode(room))

    def test_ignores_room_without_heating_device(self) -> None:
        room = SimpleNamespace(
            number_of_smartvalves=0,
            underfloor_heating_id=None,
        )

        self.assertFalse(self.switch_module._room_supports_passive_mode(room))


class WiserDeviceSwitchRefreshTest(unittest.TestCase):
    """Tests device switches when hub device data changes during refresh."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.switch_module = _load_switch_module()

    def test_missing_device_does_not_break_coordinator_refresh(self) -> None:
        device = SimpleNamespace(id=7, product_type="ButtonPanel", identify=True)
        devices = SimpleNamespace(all=[device], get_by_id=lambda _device_id: device)
        data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                devices=devices,
                system=SimpleNamespace(name="WiserHeat045XXX"),
            )
        )
        switch = self.switch_module.WiserDeviceSwitch(
            data,
            "Identify",
            "identify",
            "mdi:alarm-light",
            device.id,
            device=device,
        )
        writes = []
        switch.async_write_ha_state = lambda: writes.append(switch.is_on)

        devices.all = []
        switch._handle_coordinator_update()

        self.assertFalse(switch.available)
        self.assertFalse(switch.is_on)
        self.assertEqual(writes, [False])

        replacement = SimpleNamespace(
            id=7,
            product_type="ButtonPanel",
            identify=False,
        )
        devices.all = [replacement]
        switch._handle_coordinator_update()

        self.assertTrue(switch.available)
        self.assertFalse(switch.is_on)
        self.assertEqual(writes, [False, False])


class _FakeSmartPlug:
    def __init__(self, *, is_on: bool) -> None:
        self.is_on = is_on
        self.schedule = None
        self.control_source = "Manual"
        self.manual_state = "On" if is_on else "Off"
        self.mode = "Manual"
        self.name = "Test Plug"
        self.room_id = 0
        self.away_mode_action = "Off"
        self.scheduled_state = "Off"
        self.schedule_id = 0
        self.commands = []

    async def turn_on(self) -> None:
        # The real API object is not updated until the follow-up hub refresh.
        self.commands.append("turn_on")

    async def turn_off(self) -> None:
        self.commands.append("turn_off")


class WiserSmartPlugImmediateStateTest(unittest.TestCase):
    """Tests that smart-plug commands update the HA entity before refresh."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.switch_module = _load_switch_module()

    def _switch(self, *, is_on: bool):
        plug = _FakeSmartPlug(is_on=is_on)
        data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(name="WiserHeat045XXX"),
                devices=SimpleNamespace(get_by_id=lambda _id: plug),
                rooms=SimpleNamespace(get_by_id=lambda _id: None),
            )
        )
        switch = self.switch_module.WiserSmartPlugSwitch(data, 1, "Wiser Test Plug")
        events = []
        switch.async_write_ha_state = lambda: events.append(
            ("write", switch.is_on, switch.extra_state_attributes["output_state"])
        )

        async def refresh(delay=0):
            events.append(("refresh", delay, switch.is_on))

        switch.async_force_update = refresh
        scheduled = []
        switch._schedule_command_confirmation = scheduled.append
        return switch, plug, events, scheduled

    def test_turn_on_publishes_on_before_background_confirmation(self) -> None:
        switch, plug, events, scheduled = self._switch(is_on=False)

        asyncio.run(switch.async_turn_on())

        self.assertEqual(plug.commands, ["turn_on"])
        self.assertEqual(events, [("write", True, "On")])
        self.assertEqual(scheduled, [1])

    def test_turn_off_publishes_off_before_background_confirmation(self) -> None:
        switch, plug, events, scheduled = self._switch(is_on=True)

        asyncio.run(switch.async_turn_off())

        self.assertEqual(plug.commands, ["turn_off"])
        self.assertEqual(events, [("write", False, "Off")])
        self.assertEqual(scheduled, [1])

    def test_stale_first_refresh_retries_until_hub_confirms(self) -> None:
        switch, plug, events, scheduled = self._switch(is_on=False)
        asyncio.run(switch.async_turn_on())
        refreshes = []

        async def refresh(*_args, **_kwargs):
            refreshes.append(True)
            if len(refreshes) == 2:
                plug.is_on = True
            switch._handle_coordinator_update()

        switch.async_force_update = refresh
        asyncio.run(switch._async_confirm_command(1))

        self.assertEqual(len(refreshes), 2)
        self.assertIsNone(switch._optimistic_is_on)
        self.assertTrue(switch.is_on)

    def test_failed_confirmation_restores_hub_state(self) -> None:
        switch, _plug, _events, _scheduled = self._switch(is_on=False)
        switch._optimistic_gen = 1
        switch._optimistic_is_on = True
        switch._is_on = True

        async def fail_refresh(*_args, **_kwargs):
            raise RuntimeError("refresh failed")

        switch.async_force_update = fail_refresh

        with self.assertRaisesRegex(RuntimeError, "refresh failed"):
            asyncio.run(switch._async_confirm_command(1))

        self.assertIsNone(switch._optimistic_is_on)
        self.assertFalse(switch.is_on)

    def test_superseded_confirmation_does_not_clobber_newer_command(self) -> None:
        switch, plug, events, scheduled = self._switch(is_on=True)
        switch._optimistic_gen = 2
        switch._optimistic_is_on = False
        switch._is_on = False

        asyncio.run(switch._async_confirm_command(1))

        self.assertIs(switch._optimistic_is_on, False)
        self.assertFalse(switch.is_on)

    def test_failed_command_restores_hub_state(self) -> None:
        switch, plug, events, scheduled = self._switch(is_on=False)

        async def fail():
            raise RuntimeError("command failed")

        plug.turn_on = fail

        with self.assertRaisesRegex(RuntimeError, "command failed"):
            asyncio.run(switch.async_turn_on())

        self.assertEqual(scheduled, [])
        self.assertIsNone(switch._optimistic_is_on)
        self.assertFalse(switch.is_on)
        self.assertEqual(
            events,
            [("write", True, "On"), ("write", False, "Off")],
        )

    def test_new_confirmation_cancels_superseded_task(self) -> None:
        switch, _plug, _events, _scheduled = self._switch(is_on=False)
        tasks = []

        class FakeTask:
            cancelled = False

            def cancel(self):
                self.cancelled = True

        def create_task(coro, _name):
            coro.close()
            task = FakeTask()
            tasks.append(task)
            return task

        switch.hass = SimpleNamespace(async_create_task=create_task)
        switch.entity_id = "switch.test"

        # Restore the real method replaced by the helper's command spy.
        switch._schedule_command_confirmation = (
            self.switch_module.WiserSmartPlugSwitch._schedule_command_confirmation.__get__(
                switch
            )
        )
        switch._schedule_command_confirmation(1)
        switch._schedule_command_confirmation(2)

        self.assertTrue(tasks[0].cancelled)
        self.assertFalse(tasks[1].cancelled)

    def test_removal_invalidates_and_cancels_confirmation(self) -> None:
        switch, _plug, _events, _scheduled = self._switch(is_on=False)

        class FakeTask:
            cancelled = False

            def cancel(self):
                self.cancelled = True

        task = FakeTask()
        switch._confirmation_task = task
        previous_gen = switch._optimistic_gen

        asyncio.run(switch.async_will_remove_from_hass())

        self.assertTrue(task.cancelled)
        self.assertEqual(switch._optimistic_gen, previous_gen + 1)
        self.assertIsNone(switch._confirmation_task)
        self.assertTrue(switch.removed)


class _FakeEVSE:
    def __init__(self, *, is_on: bool) -> None:
        self.is_on = is_on
        self.control_state = "selfManagement" if is_on else "consumptionForceOff"
        self.model = "EVSCKT/OUTLET/1"
        self.firmware_version = "2.10.0"
        self.commands = []

    async def turn_on(self) -> None:
        self.commands.append("turn_on")

    async def turn_off(self) -> None:
        self.commands.append("turn_off")


class WiserEVSESwitchTest(unittest.TestCase):
    """Tests for EV charger switch commands and registry identity."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.switch_module = _load_switch_module()

    def _switch(self, *, is_on: bool):
        device = _FakeEVSE(is_on=is_on)
        evse = SimpleNamespace(get_by_id=lambda _id: device)
        data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(name="WiserHeat045XXX"),
                devices=SimpleNamespace(evse=evse),
            )
        )
        switch = self.switch_module.WiserEVSESwitch(data, 12)
        switch.async_force_update = self._noop_async
        return switch, device

    async def _noop_async(self, *_args, **_kwargs) -> None:
        return None

    def test_turn_on_returns_control_to_wiser(self) -> None:
        switch, device = self._switch(is_on=False)

        asyncio.run(switch.async_turn_on())

        self.assertEqual(device.commands, ["turn_on"])

    def test_turn_off_force_disables_charging(self) -> None:
        switch, device = self._switch(is_on=True)

        asyncio.run(switch.async_turn_off())

        self.assertEqual(device.commands, ["turn_off"])

    def test_uses_physical_device_identity(self) -> None:
        switch, _device = self._switch(is_on=True)

        self.assertEqual(switch.unique_id, "physical-entity-id")
        self.assertEqual(switch.device_info["model"], "EVSCKT/OUTLET/1")


if __name__ == "__main__":
    unittest.main()
