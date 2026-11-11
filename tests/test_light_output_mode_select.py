"""Regression tests for output-mode selects on multi-gang lights."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock


SOURCE_PATH = (
    Path(__file__).parents[1] / "custom_components/wiser/select.py"
)


def _module(name: str, **attributes: object) -> ModuleType:
    module = ModuleType(name)
    module.__dict__.update(attributes)
    sys.modules[name] = module
    return module


def _load_select_module() -> ModuleType:
    _module("homeassistant")
    _module("homeassistant.components")
    class SelectEntity:
        pass

    _module("homeassistant.components.select", SelectEntity=SelectEntity)
    _module("homeassistant.helpers", entity_registry=SimpleNamespace(async_get=lambda hass: None))
    _module("homeassistant.exceptions", HomeAssistantError=type("HomeAssistantError", (Exception,), {}))
    _module("homeassistant.core", HomeAssistant=object, callback=lambda func: func)

    class CoordinatorEntity:
        def __init__(self, *_args: object) -> None:
            pass

        def _handle_coordinator_update(self) -> None:
            pass

    _module(
        "homeassistant.helpers.update_coordinator",
        CoordinatorEntity=CoordinatorEntity,
    )

    package = _module("wiser")
    package.__path__ = []
    _module(
        "wiser.const",
        DATA="data",
        DOMAIN="wiser",
        HOT_WATER="hot_water",
        MANUFACTURER="Schneider",
        CONF_AUTOMATIONS_PASSIVE="passive",
        CONF_PASSIVE_ROOM_STRATEGIES="strategies",
        CONTROL_STRATEGIES=[],
    )
    class WiserEntityMixin:
        pass

    _module("wiser.entity", WiserEntityMixin=WiserEntityMixin)
    _module(
        "wiser.helpers",
        get_device_name=lambda *_args, **_kwargs: "Wiser Light",
        get_hub_via_device_info=lambda _data: {},
        get_light_entity_name=lambda _data, light, suffix: f"{light.name} {suffix}",
        get_unique_id=lambda *args, **_kwargs: args,
        get_room_entity_unique_id=lambda *args: args,
        get_identifier=lambda *_args, **_kwargs: "identifier",
        hub_error_handler=lambda func: func,
    )
    _module("wiser.schedules", WiserScheduleEntity=object)

    spec = importlib.util.spec_from_file_location("wiser.select", SOURCE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LightOutputModeSelectTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.select_module = _load_select_module()

    def setUp(self) -> None:
        light = SimpleNamespace(
            id=200,
            light_id=3,
            name="Dining Room Light 1",
            product_type="DimmableLight",
            firmware_version="1.0",
            available_output_mode=["Auto", "RL_LED"],
            output_mode="Auto",
            set_output_mode=AsyncMock(return_value=True),
        )
        lights = SimpleNamespace(
            get_by_id=lambda _device_id: [light],
            get_by_light_id=lambda light_id: light if light_id == 3 else None,
        )
        data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(name="WiserTEST"),
                devices=SimpleNamespace(lights=lights),
            )
        )
        select = self.select_module.WiserLightOutputModeSelect(data, light.light_id)
        select.async_write_ha_state = lambda: None
        self.entity = select
        self.light = light
        self.data = data
        self.entity.async_force_update = AsyncMock()

    def test_select_resolves_multi_gang_light_by_light_id(self) -> None:
        select, light = self.entity, self.light

        self.assertIs(select._device, light)
        self.assertEqual(select._device_id, light.id)
        self.assertEqual(select.options, light.available_output_mode)
        self.assertEqual(select.unique_id[-1], light.light_id)

        self.data.wiserhub.devices.lights.get_by_light_id = lambda _id: SimpleNamespace(
            **{**vars(light), "output_mode": "RL_LED"}
        )
        select._handle_coordinator_update()

        self.assertEqual(select.current_option, "RL_LED")
        self.assertEqual(select.options, light.available_output_mode)

    def test_valid_selection_sends_to_channel_and_refreshes(self) -> None:
        asyncio.run(self.entity.async_select_option("RL_LED"))
        self.light.set_output_mode.assert_awaited_once_with("RL_LED")
        self.entity.async_force_update.assert_awaited_once()

    def test_invalid_selection_does_not_send(self) -> None:
        with self.assertRaises(self.select_module.HomeAssistantError):
            asyncio.run(self.entity.async_select_option("invalid"))
        self.light.set_output_mode.assert_not_awaited()
        self.entity.async_force_update.assert_not_awaited()

    def test_failed_selection_does_not_refresh(self) -> None:
        self.light.set_output_mode.return_value = False
        with self.assertRaises(self.select_module.HomeAssistantError):
            asyncio.run(self.entity.async_select_option("RL_LED"))
        self.entity.async_force_update.assert_not_awaited()

    def test_shared_physical_device_has_distinct_channel_ids(self) -> None:
        second = SimpleNamespace(**{**vars(self.light), "light_id": 4})
        self.data.wiserhub.devices.lights.get_by_light_id = lambda _id: second
        entity = self.select_module.WiserLightOutputModeSelect(self.data, 4)
        self.assertNotEqual(entity.unique_id, self.entity.unique_id)
        self.assertEqual(entity.device_info, self.entity.device_info)

    def test_setup_only_adds_supported_output_controls_with_api_support(self) -> None:
        light = self.light
        light.available_modes = ["Auto", "Manual"]
        light.schedule = None
        light.is_led_indicator_supported = False
        light.is_power_on_behaviour_supported = False
        light.is_dimmable = True
        light.is_output_mode_supported = True
        old_api = SimpleNamespace(**vars(light))
        del old_api.available_output_mode
        del old_api.set_output_mode
        unsupported = SimpleNamespace(**{**vars(light), "is_output_mode_supported": False})
        onoff = SimpleNamespace(**{**vars(light), "is_dimmable": False})
        empty = SimpleNamespace(count=0, all=[])
        hub = self.data.wiserhub
        hub.hotwater = None
        hub.rooms = SimpleNamespace(all=[])
        hub.devices.smartplugs = empty
        hub.devices.shutters = empty
        hub.devices.power_tags_c = empty
        hub.devices.lights.count = 4
        hub.devices.lights.all = [light, old_api, unsupported, onoff]
        hass = SimpleNamespace(data={"wiser": {"entry": {"data": self.data}}})
        entities = []
        asyncio.run(self.select_module.async_setup_entry(
            hass, SimpleNamespace(entry_id="entry"), entities.extend
        ))
        controls = [entity for entity in entities if isinstance(
            entity, self.select_module.WiserLightOutputModeSelect
        )]
        self.assertEqual(len(controls), 1)
        self.assertEqual(controls[0]._light_id, light.light_id)


if __name__ == "__main__":
    unittest.main()
