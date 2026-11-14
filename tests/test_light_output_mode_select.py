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
        get_light_translation_context=lambda _data, light, key: (
            (key + "_channel", {"channel": light.channel})
            if getattr(light, "channel", "") else (key, {})
        ),
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
        self.assertEqual(select.options, ["auto", "rl_led"])
        self.assertEqual(select.unique_id[-1], light.light_id)

        self.data.wiserhub.devices.lights.get_by_light_id = lambda _id: SimpleNamespace(
            **{**vars(light), "output_mode": "RL_LED"}
        )
        select._handle_coordinator_update()

        self.assertEqual(select.current_option, "rl_led")
        self.assertEqual(select.options, ["auto", "rl_led"])

    def test_valid_selection_sends_to_channel_and_refreshes(self) -> None:
        asyncio.run(self.entity.async_select_option("rl_led"))
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
            asyncio.run(self.entity.async_select_option("rl_led"))
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

    def test_legacy_api_option_still_sends_the_original_value(self) -> None:
        asyncio.run(self.entity.async_select_option("RL_LED"))
        self.light.set_output_mode.assert_awaited_once_with("RL_LED")


class LightConfigurationTranslationsTest(unittest.TestCase):
    """Translate option states while retaining the API command contract."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_select_module()

    def make_entity(self, entity_class, options_attribute, state_attribute, options):
        """Create a configuration select backed by a distinct light channel."""
        light = SimpleNamespace(
            id=200, light_id=3, product_type="DimmableLight", firmware_version="1.0", schedule=None,
        )
        setattr(light, options_attribute, options)
        setattr(light, state_attribute, options[0])
        setter = AsyncMock(return_value=True)
        setattr(light, entity_class._setter, setter)
        data = SimpleNamespace(wiserhub=SimpleNamespace(
            system=SimpleNamespace(name="Test"),
            devices=SimpleNamespace(lights=SimpleNamespace(get_by_light_id=lambda _id: light)),
        ))
        entity = entity_class(data, 3)
        entity.async_force_update = AsyncMock()
        entity.async_write_ha_state = lambda: None
        return entity, light, setter

    def test_power_on_and_led_options_round_trip(self) -> None:
        for cls_name, options_attr, state_attr in (
            ("WiserLightModeSelect", "available_modes", "mode"),
            ("WiserLightPowerOnBehaviourSelect", "available_power_on_behaviour", "power_on_behaviour"),
            ("WiserLightLedIndicatorSelect", "available_led_indicator", "led_indicator"),
        ):
            entity_class = getattr(self.module, cls_name)
            mapping = entity_class._option_values
            entity, light, setter = self.make_entity(
                entity_class, options_attr, state_attr, list(mapping.values())
            )
            self.assertEqual(entity.options, list(mapping))
            for key, raw in mapping.items():
                with self.subTest(entity=cls_name, option=key):
                    setattr(light, state_attr, raw)
                    self.assertEqual(entity.current_option, key)
                    for option in (key, raw):
                        setter.reset_mock()
                        asyncio.run(entity.async_select_option(option))
                        setter.assert_awaited_once_with(raw)

    def test_only_hub_supported_options_are_exposed(self) -> None:
        entity, light, setter = self.make_entity(
            self.module.WiserLightLedIndicatorSelect,
            "available_led_indicator", "led_indicator", ["AlwaysOn"],
        )
        self.assertEqual(entity.options, ["always_on"])
        with self.assertRaises(self.module.HomeAssistantError):
            asyncio.run(entity.async_select_option("always_off"))
        setter.assert_not_awaited()
        light.led_indicator = "Unknown"
        self.assertIsNone(entity.current_option)

    def test_channel_names_use_placeholders_with_translated_labels(self) -> None:
        import json
        catalogue = json.loads((SOURCE_PATH.parent / "translations/en.json").read_text())
        for cls_name, options_attr, state_attr in (
            ("WiserLightModeSelect", "available_modes", "mode"),
            ("WiserLightPowerOnBehaviourSelect", "available_power_on_behaviour", "power_on_behaviour"),
            ("WiserLightLedIndicatorSelect", "available_led_indicator", "led_indicator"),
            ("WiserLightOutputModeSelect", "available_output_mode", "output_mode"),
        ):
            cls = getattr(self.module, cls_name)
            names = []
            ids = []
            for channel, light_id in (("Light 1", 3), ("Light 2", 4)):
                entity, light, _ = self.make_entity(
                    cls, options_attr, state_attr, list(cls._option_values.values())
                )
                light.channel = channel
                light.light_id = light_id
                entity = cls(entity._data, light_id)
                translation = catalogue["entity"]["select"][entity._attr_translation_key]
                names.append(translation["name"].format(**entity._attr_translation_placeholders))
                ids.append(entity.unique_id)
            with self.subTest(entity=cls_name):
                self.assertNotEqual(names[0], names[1])
                self.assertTrue(names[0].startswith("Light 1 "))
                self.assertTrue(names[1].startswith("Light 2 "))
                self.assertNotEqual(ids[0], ids[1])

    def test_all_catalogues_translate_each_configuration_option(self) -> None:
        import json
        component = SOURCE_PATH.parent
        for path in [component / "strings.json", *(component / "translations").glob("*.json")]:
            catalogue = json.loads(path.read_text())["entity"]["select"]
            for cls_name in (
                "WiserLightModeSelect", "WiserLightPowerOnBehaviourSelect", "WiserLightLedIndicatorSelect", "WiserLightOutputModeSelect"
            ):
                cls = getattr(self.module, cls_name)
                with self.subTest(path=path.name, entity=cls_name):
                    states = catalogue[cls._attr_translation_key]["state"]
                    self.assertEqual(set(states), set(cls._option_values))
                    self.assertTrue(all(isinstance(label, str) and label for label in states.values()))
                    channel = catalogue[cls._attr_translation_key + "_channel"]
                    self.assertEqual(channel["state"], states)
                    self.assertIn("{channel}", channel["name"])


if __name__ == "__main__":
    unittest.main()
