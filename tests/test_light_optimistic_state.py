"""Regression tests for the optimistic light state, without Home Assistant runtime deps.

Covers the two guards that keep rapid/overlapping toggles from making the UI
revert to a stale value:
  * a generation counter, so a superseded command's delayed cleanup cannot wipe
    a newer command's optimistic value;
  * a confirm-on-coordinator-update clear, so the optimistic on/off override is
    only dropped once the hub actually reports the commanded state.
"""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/light.py"


def _module(name: str, **attributes: object) -> ModuleType:
    """Create and register a lightweight module stub."""
    module = ModuleType(name)
    module.__dict__.update(attributes)
    sys.modules[name] = module
    return module


def _load_light_module() -> ModuleType:
    """Load light.py with only the imports it needs stubbed out."""
    _module("homeassistant")
    _module("homeassistant.components")

    class LightEntity:
        pass

    _module(
        "homeassistant.components.light",
        ATTR_BRIGHTNESS="brightness",
        ColorMode=SimpleNamespace(ONOFF="onoff", BRIGHTNESS="brightness"),
        LightEntity=LightEntity,
    )
    _module("homeassistant.core", HomeAssistant=object, callback=lambda func: func)

    class CoordinatorEntity:
        def __init__(self, *args: object) -> None:
            pass

    _module(
        "homeassistant.helpers.update_coordinator", CoordinatorEntity=CoordinatorEntity
    )

    package = _module("wiser")
    package.__path__ = []
    _module("wiser.const", DATA="data", DOMAIN="wiser", MANUFACTURER_SCHNEIDER="Schneider")

    def hub_error_handler(func):
        return func  # identity: let exceptions surface in tests

    _module(
        "wiser.helpers",
        get_device_name=lambda *_a, **_k: "Wiser Light",
        get_identifier=lambda *_a, **_k: "identifier",
        get_unique_id=lambda *_a, **_k: "unique-id",
        hub_error_handler=hub_error_handler,
    )

    class WiserScheduleEntity:
        pass

    _module("wiser.schedules", WiserScheduleEntity=WiserScheduleEntity)

    spec = importlib.util.spec_from_file_location("wiser.light", SOURCE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _FakeDevice:
    def __init__(self, *, is_on=False, current_percentage=0):
        self.id = 1
        self.is_on = is_on
        self.current_percentage = current_percentage
        self.schedule = None

    async def turn_on(self):
        self.is_on = True

    async def turn_off(self):
        self.is_on = False

    async def set_current_percentage(self, percentage):
        self.current_percentage = percentage
        self.is_on = percentage > 0


class LightOptimisticStateTest(unittest.TestCase):
    """Tests for the optimistic on/off state and its two guards."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.light_module = _load_light_module()

    def _light(self, *, is_on=False):
        device = _FakeDevice(is_on=is_on)
        data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(name="WiserTEST"),
                devices=SimpleNamespace(
                    lights=SimpleNamespace(get_by_id=lambda _id: device)
                ),
            ),
            async_refresh=self._noop_async,
        )
        light = self.light_module.WiserLight(data, 1)
        light.async_write_ha_state = lambda: None  # not an HA-managed entity here
        return light, device

    async def _noop_async(self, *_args, **_kwargs):
        return None

    def test_single_command_clears_optimistic(self):
        light, device = self._light(is_on=False)
        light.async_force_update = self._noop_async
        asyncio.run(light.async_turn_on())
        # The one and only command clears its own optimistic state on cleanup.
        self.assertIsNone(light._optimistic_is_on)
        self.assertTrue(light.is_on)  # falls through to the (now on) device

    def test_superseded_command_does_not_clobber_newer(self):
        light, device = self._light(is_on=False)

        # Command A is turn_on. While A awaits its follow-up refresh, a newer
        # command B (turn_off) lands: it bumps the generation and sets its own
        # optimistic value. A's cleanup must then leave B's value alone.
        async def force_update_with_intervening_command(delay=0):
            light._optimistic_gen += 1
            light._optimistic_is_on = False  # command B = turn off

        light.async_force_update = force_update_with_intervening_command
        asyncio.run(light.async_turn_on())  # command A

        # Without the generation guard, A's finally would wipe this back to None
        # and the UI would revert to the stale device state.
        self.assertIs(light._optimistic_is_on, False)

    def test_coordinator_update_clears_optimistic_once_confirmed(self):
        light, device = self._light(is_on=False)
        light._optimistic_is_on = True  # a turn_on is pending
        light._optimistic_gen = 1

        # Hub still reports off -> keep the optimistic override (no revert).
        device.is_on = False
        light._handle_coordinator_update()
        self.assertIs(light._optimistic_is_on, True)

        # Hub now confirms on -> drop the override; the shown value is unchanged.
        device.is_on = True
        light._handle_coordinator_update()
        self.assertIsNone(light._optimistic_is_on)
        self.assertTrue(light.is_on)


if __name__ == "__main__":
    unittest.main()
