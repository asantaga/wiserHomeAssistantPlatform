"""Regression tests for the per-light power-on-level number entity."""

import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


SOURCE_PATH = (
    Path(__file__).parents[1] / "custom_components/wiser/number.py"
)


def _module(name: str, **attributes: object) -> ModuleType:
    module = ModuleType(name)
    module.__dict__.update(attributes)
    sys.modules[name] = module
    return module


def _load_number_module() -> ModuleType:
    _module("homeassistant")
    _module("homeassistant.components")

    class NumberEntity:
        pass

    _module(
        "homeassistant.components.number",
        NumberEntity=NumberEntity,
        NumberMode=SimpleNamespace(AUTO="auto"),
    )
    _module("homeassistant.core", HomeAssistant=object, callback=lambda func: func)
    _module("homeassistant.const", __version__="2026.8.0")
    _module(
        "homeassistant.exceptions",
        HomeAssistantError=type("HomeAssistantError", (Exception,), {}),
    )

    class CoordinatorEntity:
        def __init__(self, *args: object) -> None:
            pass

    _module(
        "homeassistant.helpers.update_coordinator",
        CoordinatorEntity=CoordinatorEntity,
    )

    package = _module("wiser")
    package.__path__ = []
    _module("wiser.const", DATA="data", DOMAIN="wiser")

    def hub_error_handler(func):
        return func

    _module(
        "wiser.helpers",
        get_device_name=lambda *_args: "Wiser Light",
        get_hub_device_info=lambda _data: {},
        get_hub_via_device_info=lambda _data: {},
        get_identifier=lambda *_args: "identifier",
        get_physical_entity_unique_id=lambda *_args: repr(_args),
        get_unique_id=lambda *_args: repr(_args),
        hub_error_handler=hub_error_handler,
    )
    _module("wiser.entity", WiserEntityMixin=type("WiserEntityMixin", (), {}))

    wiser_api = _module("aioWiserHeatAPI")
    wiser_api.__path__ = []
    _module(
        "aioWiserHeatAPI.wiserhub",
        TEMP_MINIMUM=5,
        TEMP_MAXIMUM=30,
    )

    class AwesomeVersion:
        def __init__(self, _version: str) -> None:
            pass

        def __lt__(self, _other: str) -> bool:
            return False

    _module("awesomeversion", AwesomeVersion=AwesomeVersion)

    spec = importlib.util.spec_from_file_location("wiser.number", SOURCE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class _FakeLight:
    def __init__(self, light_id: int) -> None:
        self.id = 1
        self.light_id = light_id
        self.name = f"Light {light_id}"
        self.power_on_level = 25
        self.is_power_on_behaviour_supported = False
        self.set_value = None
        self.command_result = True
        self.sent_command = None

    async def set_power_on_level(self, value: int) -> bool:
        self.set_value = value
        self.power_on_level = value
        return self.command_result

    async def _send_command(self, command: dict) -> bool:
        self.sent_command = command
        self.power_on_level = command["PowerOnLevel"]
        return self.command_result


class NumberPowerOnLevelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.number_module = _load_number_module()

    def setUp(self) -> None:
        self.light = _FakeLight(light_id=12)
        self.light.is_dimmable = True
        self.light.is_power_on_behaviour_supported = True
        lookups = []
        lights_by_id = {self.light.light_id: self.light}

        def get_by_light_id(light_id):
            lookups.append(light_id)
            return lights_by_id[light_id]

        self.data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                devices=SimpleNamespace(
                    lights=SimpleNamespace(get_by_light_id=get_by_light_id)
                )
            ),
            async_refresh=self._refresh,
        )
        self.lookups = lookups
        self.lights_by_id = lights_by_id
        self.entity = self.number_module.WiserPowerOnLevelNumber(self.data, 12)
        self.entity.async_write_ha_state = lambda: None
        self.refresh_count = 0

    async def _refresh(self) -> None:
        self.refresh_count += 1

    def test_initializes_and_refreshes_from_light_collection(self) -> None:
        self.assertEqual(self.entity.native_value, 25)
        self.assertEqual(self.lookups, [12])

        self.light.power_on_level = 40
        self.entity._handle_coordinator_update()

        self.assertEqual(self.entity.native_value, 40)
        self.assertEqual(self.lookups, [12, 12])

    def test_sets_level_on_resolved_light(self) -> None:
        asyncio.run(self.entity.async_set_native_value(60.0))

        self.assertEqual(self.light.set_value, 60)
        self.assertIs(type(self.light.set_value), int)
        self.assertEqual(self.refresh_count, 1)

    def test_rejects_fractional_power_on_level(self) -> None:
        with self.assertRaisesRegex(
            self.number_module.HomeAssistantError, "whole number"
        ):
            asyncio.run(self.entity.async_set_native_value(41.5))

        self.assertIsNone(self.light.set_value)
        self.assertEqual(self.refresh_count, 0)

    def test_failed_hub_command_is_reported_without_refresh(self) -> None:
        self.light.command_result = False

        with self.assertRaisesRegex(
            self.number_module.HomeAssistantError, "did not confirm"
        ):
            asyncio.run(self.entity.async_set_native_value(60))

        self.assertEqual(self.light.set_value, 60)
        self.assertEqual(self.refresh_count, 0)

    def test_uses_pinned_api_command_when_public_setter_is_missing(self) -> None:
        self.light.set_power_on_level = None

        asyncio.run(self.entity.async_set_native_value(70.0))

        self.assertEqual(self.light.sent_command, {"PowerOnLevel": 70})
        self.assertIs(type(self.light.sent_command["PowerOnLevel"]), int)
        self.assertEqual(self.refresh_count, 1)

    def test_unique_id_is_per_light_channel(self) -> None:
        self.lights_by_id[13] = _FakeLight(light_id=13)
        second_entity = self.number_module.WiserPowerOnLevelNumber(self.data, 13)

        self.assertNotEqual(self.entity.unique_id, second_entity.unique_id)
        self.assertEqual(self.entity.device_info["identifiers"], {("wiser", "identifier")})

    def test_setup_adds_number_only_for_supported_dimmable_lights(self) -> None:
        system = SimpleNamespace(
            hardware_generation=1,
            away_mode_target_temperature=18,
            name="Wiser Hub",
        )
        self.data.wiserhub.system = system
        self.data.wiserhub.devices.heating_actuators = SimpleNamespace(all=[])
        self.light.power_on_level = None
        second_supported_light = _FakeLight(light_id=15)
        second_supported_light.is_dimmable = True
        second_supported_light.is_power_on_behaviour_supported = True
        self.lights_by_id[second_supported_light.light_id] = second_supported_light
        non_dimmable_light = SimpleNamespace(
            light_id=13,
            is_dimmable=False,
            is_power_on_behaviour_supported=True,
        )
        unsupported_dimmer = SimpleNamespace(
            light_id=14,
            is_dimmable=True,
            is_power_on_behaviour_supported=False,
        )
        self.data.wiserhub.devices.lights.count = 4
        self.data.wiserhub.devices.lights.all = [
            self.light,
            second_supported_light,
            non_dimmable_light,
            unsupported_dimmer,
        ]
        hass = SimpleNamespace(
            data={
                "wiser": {
                    "entry": {"data": self.data},
                }
            }
        )
        entities = []

        asyncio.run(
            self.number_module.async_setup_entry(
                hass,
                SimpleNamespace(entry_id="entry"),
                entities.extend,
            )
        )

        power_level_entities = [
            entity
            for entity in entities
            if isinstance(entity, self.number_module.WiserPowerOnLevelNumber)
        ]
        self.assertEqual(len(power_level_entities), 2)
        self.assertEqual(
            {entity._light_id for entity in power_level_entities},
            {self.light.light_id, second_supported_light.light_id},
        )
        self.assertEqual(
            len({entity.unique_id for entity in power_level_entities}), 2
        )
        self.assertIsNone(
            next(
                entity.native_value
                for entity in power_level_entities
                if entity._light_id == self.light.light_id
            )
        )

    def test_invalid_values_do_not_send_commands(self) -> None:
        for value in (-1, 101, 41.5, True, False, "50", None, float("nan"), float("inf")):
            with self.subTest(value=value):
                with self.assertRaises(self.number_module.HomeAssistantError):
                    asyncio.run(self.entity.async_set_native_value(value))
                self.assertIsNone(self.light.set_value)
                self.assertEqual(self.refresh_count, 0)

    def test_percentage_boundaries_are_sent_as_integers(self) -> None:
        for value in (0.0, 100.0):
            with self.subTest(value=value):
                asyncio.run(self.entity.async_set_native_value(value))
                self.assertEqual(self.light.set_value, value)
                self.assertIs(type(self.light.set_value), int)

    def test_coordinator_replaces_the_channel_object(self) -> None:
        replacement = _FakeLight(12)
        replacement.power_on_level = 75
        self.lights_by_id[12] = replacement
        self.entity._handle_coordinator_update()
        self.assertEqual(self.entity.native_value, 75)
        asyncio.run(self.entity.async_set_native_value(80))
        self.assertEqual(replacement.set_value, 80)
        self.assertIsNone(self.light.set_value)


if __name__ == "__main__":
    unittest.main()
