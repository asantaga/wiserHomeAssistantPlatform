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
    )

    def hub_error_handler(func):
        return func

    _module(
        "wiser.helpers",
        get_device_name=lambda _data, device_id, device_type="device": (
            "Hot Water" if device_type == "Hot Water" else "Wiser HeatHub"
        ),
        get_hub_device_info=lambda _data: {"identifiers": {("wiser", "hub")}},
        get_hub_via_device_info=lambda _data: {},
        get_room_name=lambda *_args: "Room",
        get_identifier=lambda *_args: "identifier",
        get_legacy_device_name=lambda *_args, **_kwargs: "Wiser HeatHub",
        get_legacy_unique_id=lambda *_args: "legacy-unique-id",
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
        return switch, plug, events

    def test_turn_on_publishes_on_before_delayed_refresh(self) -> None:
        switch, plug, events = self._switch(is_on=False)

        asyncio.run(switch.async_turn_on())

        self.assertEqual(plug.commands, ["turn_on"])
        self.assertEqual(events, [("write", True, "On"), ("refresh", 2, True)])

    def test_turn_off_publishes_off_before_delayed_refresh(self) -> None:
        switch, plug, events = self._switch(is_on=True)

        asyncio.run(switch.async_turn_off())

        self.assertEqual(plug.commands, ["turn_off"])
        self.assertEqual(events, [("write", False, "Off"), ("refresh", 2, False)])


if __name__ == "__main__":
    unittest.main()
