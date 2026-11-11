"""Smart-plug selector translations, API compatibility and refresh tests."""

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
        get_device_name=lambda *_args, **_kwargs: "Wiser Plug",
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


def make_plug(plug_id=12, **overrides):
    """Provide a plug whose physical and domain IDs differ."""
    fields = {
        "id": plug_id,
        "device_type_id": 4,
        "product_type": "SmartPlug",
        "firmware_version": "1.0",
        "schedule": None,
        "available_modes": ["Auto", "Manual"],
        "mode": "Auto",
        "set_mode": AsyncMock(return_value=True),
        "is_led_indicator_supported": True,
        "available_led_indicator": ["ReverseWithLoad", "ConsistentWithLoad", "AlwaysOn", "AlwaysOff"],
        "led_indicator": "ConsistentWithLoad",
        "set_led_indicator": AsyncMock(return_value=True),
    }
    return SimpleNamespace(**{**fields, **overrides})


class SmartPlugSelectTest(unittest.TestCase):
    """Test setup, stable identity, translated values and command failures."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_select_module()

    def setUp(self) -> None:
        self.plug = make_plug()
        self.plugs = {12: self.plug}
        empty = SimpleNamespace(all=[], count=0)
        self.data = SimpleNamespace(wiserhub=SimpleNamespace(
            system=SimpleNamespace(name="WiserTEST"),
            hotwater=None,
            rooms=SimpleNamespace(all=[]),
            devices=SimpleNamespace(
                smartplugs=SimpleNamespace(
                    get_by_id=self.plugs.get, all=[self.plug], count=1,
                ),
                lights=empty, shutters=empty, power_tags_c=empty,
            ),
        ))

    def entity(self, entity_class):
        """Build a selector and record refresh calls."""
        entity = entity_class(self.data, 12)
        entity.async_force_update = AsyncMock()
        entity.async_write_ha_state = lambda: None
        return entity

    def test_translated_options_round_trip_and_accept_legacy_values(self) -> None:
        for cls in (self.module.WiserSmartPlugModeSelect, self.module.WiserSmartPlugLedIndicatorSelect):
            entity = self.entity(cls)
            self.assertEqual(entity.options, list(cls._option_values))
            for key, raw in cls._option_values.items():
                with self.subTest(entity=cls.__name__, option=key):
                    setattr(self.plug, cls._value_attribute, raw)
                    self.assertEqual(entity.current_option, key)
                    setter = getattr(self.plug, cls._setter)
                    for value in (key, raw):
                        setter.reset_mock()
                        asyncio.run(entity.async_select_option(value))
                        setter.assert_awaited_once_with(raw)
                        entity.async_force_update.assert_awaited()

    def test_invalid_or_unsupported_led_options_do_not_send(self) -> None:
        entity = self.entity(self.module.WiserSmartPlugLedIndicatorSelect)
        for option in ("invalid", "off_after_2s", "OffAfter2s"):
            with self.subTest(option=option):
                with self.assertRaises(self.module.HomeAssistantError):
                    asyncio.run(entity.async_select_option(option))
        self.plug.set_led_indicator.assert_not_awaited()
        entity.async_force_update.assert_not_awaited()
        self.assertEqual(entity.current_option, "consistent_with_load")

    def test_hub_rejection_is_reported_without_refresh(self) -> None:
        for cls in (self.module.WiserSmartPlugModeSelect, self.module.WiserSmartPlugLedIndicatorSelect):
            with self.subTest(entity=cls.__name__):
                entity = self.entity(cls)
                getattr(self.plug, cls._setter).return_value = False
                with self.assertRaises(self.module.HomeAssistantError):
                    asyncio.run(entity.async_select_option(entity.options[0]))
                entity.async_force_update.assert_not_awaited()

    def test_refresh_replaces_device_and_options(self) -> None:
        entity = self.entity(self.module.WiserSmartPlugLedIndicatorSelect)
        replacement = make_plug(led_indicator="AlwaysOff", available_led_indicator=["AlwaysOff"])
        self.plugs[12] = replacement
        entity._handle_coordinator_update()
        self.assertIs(entity._device, replacement)
        self.assertEqual(entity.current_option, "always_off")
        self.assertEqual(entity.options, ["always_off"])
        with self.assertRaises(self.module.HomeAssistantError):
            asyncio.run(entity.async_select_option("always_on"))
        replacement.led_indicator = "Unknown"
        self.assertIsNone(entity.current_option)

    def test_led_identity_is_stable_and_separate_from_mode(self) -> None:
        led = self.entity(self.module.WiserSmartPlugLedIndicatorSelect)
        mode = self.entity(self.module.WiserSmartPlugModeSelect)
        self.assertEqual(led.unique_id[-2:], ("led-indicator", 12))
        self.assertEqual(mode.unique_id[-2:], ("mode-select", 12))
        self.assertNotEqual(led.unique_id, mode.unique_id)
        self.assertEqual(led.device_info["identifiers"], mode.device_info["identifiers"])

    def test_setup_skips_unsupported_and_older_apis(self) -> None:
        supported = self.plug
        unsupported = make_plug(13, is_led_indicator_supported=False)
        old_api = make_plug(14)
        del old_api.is_led_indicator_supported
        del old_api.available_led_indicator
        del old_api.set_led_indicator
        missing_setter = make_plug(15)
        del missing_setter.set_led_indicator
        missing_options = make_plug(16)
        del missing_options.available_led_indicator
        plugs = [supported, unsupported, old_api, missing_setter, missing_options]
        self.plugs.update({plug.id: plug for plug in plugs})
        self.data.wiserhub.devices.smartplugs.all = plugs
        self.data.wiserhub.devices.smartplugs.count = len(plugs)
        hass = SimpleNamespace(data={"wiser": {"entry": {"data": self.data}}})
        entities = []
        asyncio.run(self.module.async_setup_entry(
            hass, SimpleNamespace(entry_id="entry"), entities.extend,
        ))
        self.assertEqual(sum(isinstance(e, self.module.WiserSmartPlugModeSelect) for e in entities), 5)
        leds = [e for e in entities if isinstance(e, self.module.WiserSmartPlugLedIndicatorSelect)]
        self.assertEqual(len(leds), 1)
        self.assertEqual(leds[0]._device_id, 12)

    def test_all_languages_translate_options(self) -> None:
        import json
        for path in [SOURCE_PATH.parent / "strings.json", *(SOURCE_PATH.parent / "translations").glob("*.json")]:
            catalogue = json.loads(path.read_text())["entity"]["select"]
            for cls in (self.module.WiserSmartPlugModeSelect, self.module.WiserSmartPlugLedIndicatorSelect):
                with self.subTest(path=path.name, entity=cls.__name__):
                    translation = catalogue[cls._attr_translation_key]
                    self.assertTrue(translation["name"])
                    self.assertEqual(set(translation["state"]), set(cls._option_values))
                    self.assertTrue(all(translation["state"].values()))


if __name__ == "__main__":
    unittest.main()
