"""Regression tests for the Hot Water switch without Home Assistant runtime deps."""

from __future__ import annotations

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

    _module("homeassistant.components.switch", SwitchEntity=SwitchEntity)
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
        get_room_name=lambda *_args: "Room",
        get_identifier=lambda *_args: "identifier",
        get_unique_id=lambda *_args: "unique-id",
        hub_error_handler=hub_error_handler,
    )

    class WiserScheduleEntity:
        pass

    _module("custom_components")
    _module("custom_components.wiser")
    _module("custom_components.wiser.schedules", WiserScheduleEntity=WiserScheduleEntity)

    spec = importlib.util.spec_from_file_location("wiser.switch", SOURCE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
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


if __name__ == "__main__":
    unittest.main()
