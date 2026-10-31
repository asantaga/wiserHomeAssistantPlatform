"""Regression tests for output-mode selects on multi-gang lights."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


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
    _module("homeassistant.components.select", SelectEntity=object)
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

    def test_select_resolves_multi_gang_light_by_light_id(self) -> None:
        light = SimpleNamespace(
            id=200,
            light_id=3,
            name="Dining Room Light 1",
            product_type="DimmableLight",
            available_output_mode=["Trailing Edge", "Leading Edge"],
            output_mode="Trailing Edge",
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

        self.assertIs(select._device, light)
        self.assertEqual(select._device_id, light.id)
        self.assertEqual(select.options, light.available_output_mode)
        self.assertEqual(select.unique_id[-1], light.light_id)

        select._handle_coordinator_update()

        self.assertIs(select._device, light)
        self.assertEqual(select.options, light.available_output_mode)


if __name__ == "__main__":
    unittest.main()
