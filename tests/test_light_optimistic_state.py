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
        MANUFACTURER_SCHNEIDER="Schneider",
    )

    def hub_error_handler(func):
        return func  # identity: let exceptions surface in tests

    _module(
        "wiser.helpers",
        get_device_name=lambda *_a, **_k: "Wiser Light",
        get_hub_via_device_info=lambda _data: {},
        get_identifier=lambda *_a, **_k: "identifier",
        get_light_entity_name=lambda _data, _light, entity_name: entity_name,
        get_unique_id=lambda *_a, **_k: "unique-id",
        hub_error_handler=hub_error_handler,
    )

    class WiserEntityMixin:
        pass

    _module("wiser.entity", WiserEntityMixin=WiserEntityMixin)

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
        self.name = "Test Light"
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
                    lights=SimpleNamespace(get_by_light_id=lambda _id: device)
                ),
            ),
            async_refresh=self._noop_async,
        )
        light = self.light_module.WiserLight(data, 1)
        light.async_write_ha_state = lambda: None  # not an HA-managed entity here
        return light, device

    async def _noop_async(self, *_args, **_kwargs):
        return None

    def test_single_command_returns_before_confirmation(self):
        light, device = self._light(is_on=False)
        scheduled = []
        light._schedule_command_confirmation = scheduled.append

        asyncio.run(light.async_turn_on())

        self.assertIs(light._optimistic_is_on, True)
        self.assertTrue(light.is_on)
        self.assertEqual(scheduled, [1])

    def test_superseded_confirmation_does_not_clobber_newer(self):
        light, device = self._light(is_on=False)
        light._optimistic_gen = 2
        light._optimistic_is_on = False
        light.async_force_update = self._noop_async

        asyncio.run(light._async_confirm_command(1))

        self.assertIs(light._optimistic_is_on, False)

    def test_latest_confirmation_clears_optimistic_state(self):
        light, device = self._light(is_on=False)
        light._optimistic_gen = 1
        light._optimistic_is_on = True
        refreshes = []

        async def stale_refresh(*_args, **_kwargs):
            refreshes.append(True)

        light.async_force_update = stale_refresh

        asyncio.run(light._async_confirm_command(1))

        self.assertEqual(len(refreshes), 2)
        self.assertIsNone(light._optimistic_is_on)

    def test_failed_confirmation_clears_optimistic_state(self):
        light, _device = self._light(is_on=False)
        light._optimistic_gen = 1
        light._optimistic_is_on = True

        async def fail_refresh(*_args, **_kwargs):
            raise RuntimeError("refresh failed")

        light.async_force_update = fail_refresh

        with self.assertRaisesRegex(RuntimeError, "refresh failed"):
            asyncio.run(light._async_confirm_command(1))

        self.assertIsNone(light._optimistic_is_on)

    def test_stale_first_refresh_retries_until_hub_confirms(self):
        light, device = self._light(is_on=False)
        light._optimistic_gen = 1
        light._optimistic_is_on = True
        refreshes = []

        async def refresh(*_args, **_kwargs):
            refreshes.append(True)
            if len(refreshes) == 2:
                device.is_on = True
            light._handle_coordinator_update()

        light.async_force_update = refresh

        asyncio.run(light._async_confirm_command(1))

        self.assertEqual(len(refreshes), 2)
        self.assertIsNone(light._optimistic_is_on)
        self.assertTrue(light.is_on)

    def test_failed_command_restores_hub_state(self):
        light, device = self._light(is_on=False)
        light._schedule_command_confirmation = lambda _gen: None

        async def fail():
            raise RuntimeError("command failed")

        device.turn_on = fail

        with self.assertRaisesRegex(RuntimeError, "command failed"):
            asyncio.run(light.async_turn_on())

        self.assertIsNone(light._optimistic_is_on)
        self.assertFalse(light.is_on)

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

    def test_brightness_optimistic_state_waits_for_matching_hub_value(self):
        light, device = self._light(is_on=True)
        light._optimistic_percentage = 60

        device.current_percentage = 20
        light._handle_coordinator_update()
        self.assertEqual(light._optimistic_percentage, 60)

        device.current_percentage = 60
        light._handle_coordinator_update()
        self.assertIsNone(light._optimistic_percentage)

    def test_new_confirmation_cancels_superseded_task(self):
        light, _device = self._light(is_on=False)
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

        light.hass = SimpleNamespace(async_create_task=create_task)
        light.entity_id = "light.test"

        light._schedule_command_confirmation(1)
        light._schedule_command_confirmation(2)

        self.assertTrue(tasks[0].cancelled)
        self.assertFalse(tasks[1].cancelled)

    def test_removal_invalidates_and_cancels_confirmation(self):
        light, _device = self._light(is_on=False)

        class FakeTask:
            cancelled = False

            def cancel(self):
                self.cancelled = True

        task = FakeTask()
        light._confirmation_task = task
        previous_gen = light._optimistic_gen

        asyncio.run(light.async_will_remove_from_hass())

        self.assertTrue(task.cancelled)
        self.assertEqual(light._optimistic_gen, previous_gen + 1)
        self.assertIsNone(light._confirmation_task)
        self.assertTrue(light.removed)


if __name__ == "__main__":
    unittest.main()
