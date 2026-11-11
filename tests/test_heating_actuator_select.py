"""Heating-actuator output selector translations and compatibility tests."""

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
    _module("homeassistant.const", EntityCategory=SimpleNamespace(CONFIG="config"))

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


def make_actuator(device_id=12, **overrides):
    """Use distinct physical and actuator-domain IDs to detect lookup mistakes."""
    return SimpleNamespace(**{
        **{
            "id": device_id,
            "device_type_id": 4,
            "product_type": "HeatingActuator",
            "firmware_version": "1.0",
            "available_output_type": ["Relay", "FilPilote"],
            "output_type": "Relay",
            "set_output_type": AsyncMock(return_value=True),
        },
        **overrides,
    })


class HeatingActuatorOutputTypeTest(unittest.TestCase):
    """Validate translated values, command results and older API handling."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_select_module()

    def setUp(self) -> None:
        self.actuator = make_actuator()
        self.actuators = {12: self.actuator}
        empty = SimpleNamespace(all=[], count=0)
        self.data = SimpleNamespace(wiserhub=SimpleNamespace(
            system=SimpleNamespace(name="WiserTEST"),
            hotwater=None,
            rooms=SimpleNamespace(all=[]),
            devices=SimpleNamespace(
                heating_actuators=SimpleNamespace(
                    all=[self.actuator], get_by_id=self.actuators.get,
                ),
                smartplugs=empty, lights=empty, shutters=empty, power_tags_c=empty,
            ),
        ))
        self.entity = self.module.WiserHeatingActuatorOutputTypeSelect(self.data, 12)
        self.entity.async_force_update = AsyncMock()
        self.entity.async_write_ha_state = lambda: None

    def test_translated_values_and_legacy_options_round_trip(self) -> None:
        self.assertEqual(self.entity.options, ["relay", "pilot_wire"])
        for key, raw in (("relay", "Relay"), ("pilot_wire", "FilPilote")):
            with self.subTest(key=key):
                self.actuator.output_type = raw
                self.assertEqual(self.entity.current_option, key)
                for option in (key, raw):
                    self.actuator.set_output_type.reset_mock()
                    self.entity.async_force_update.reset_mock()
                    asyncio.run(self.entity.async_select_option(option))
                    self.actuator.set_output_type.assert_awaited_once_with(raw)
                    self.entity.async_force_update.assert_awaited_once()

    def test_invalid_values_do_not_send(self) -> None:
        for option in ("invalid", "", "fil_pilote", " Relay "):
            with self.subTest(option=option):
                with self.assertRaises(self.module.HomeAssistantError):
                    asyncio.run(self.entity.async_select_option(option))
        self.actuator.set_output_type.assert_not_awaited()
        self.entity.async_force_update.assert_not_awaited()
        self.assertEqual(self.entity.current_option, "relay")

    def test_rejected_command_does_not_refresh(self) -> None:
        self.actuator.set_output_type.return_value = False
        with self.assertRaises(self.module.HomeAssistantError):
            asyncio.run(self.entity.async_select_option("pilot_wire"))
        self.actuator.set_output_type.assert_awaited_once_with("FilPilote")
        self.entity.async_force_update.assert_not_awaited()
        self.assertEqual(self.entity.current_option, "relay")

    def test_refresh_uses_physical_lookup_and_replaces_options(self) -> None:
        replacement = make_actuator(output_type="FilPilote", available_output_type=["FilPilote"])
        self.actuators[12] = replacement
        self.entity._handle_coordinator_update()
        self.assertIs(self.entity._device, replacement)
        self.assertEqual(self.entity.options, ["pilot_wire"])
        self.assertEqual(self.entity.current_option, "pilot_wire")
        with self.assertRaises(self.module.HomeAssistantError):
            asyncio.run(self.entity.async_select_option("relay"))
        replacement.output_type = "Unknown"
        self.assertIsNone(self.entity.current_option)

    def test_identity_grouping_and_configuration_category(self) -> None:
        self.assertEqual(self.entity.unique_id[-2:], ("output-type", 12))
        self.assertEqual(self.entity._device_id, 12)
        self.assertEqual(self.entity._attr_entity_category, "config")
        self.assertEqual(self.entity.device_info["identifiers"], {("wiser", "identifier")})
        self.actuators[13] = make_actuator(13)
        second = self.module.WiserHeatingActuatorOutputTypeSelect(self.data, 13)
        self.assertNotEqual(self.entity.unique_id, second.unique_id)

    def test_setup_skips_old_apis_and_unsupported_output_types(self) -> None:
        old_api = make_actuator(13)
        del old_api.available_output_type
        del old_api.set_output_type
        missing_setter = make_actuator(14)
        del missing_setter.set_output_type
        missing_options = make_actuator(15)
        del missing_options.available_output_type
        unknown = make_actuator(16, output_type="Unknown")
        not_advertised = make_actuator(17, available_output_type=[])
        unsupported = make_actuator(18, output_type="FutureType", available_output_type=["FutureType"])
        pilot = make_actuator(19, output_type="FilPilote")
        actuators = [self.actuator, old_api, missing_setter, missing_options, unknown,
                     not_advertised, unsupported, pilot]
        self.actuators.update({actuator.id: actuator for actuator in actuators})
        self.data.wiserhub.devices.heating_actuators.all = actuators
        hass = SimpleNamespace(data={"wiser": {"entry": {"data": self.data}}})
        entities = []
        asyncio.run(self.module.async_setup_entry(
            hass, SimpleNamespace(entry_id="entry"), entities.extend,
        ))
        self.assertEqual({e._device_id for e in entities}, {12, 19})
        self.assertTrue(all(isinstance(e, self.module.WiserHeatingActuatorOutputTypeSelect) for e in entities))

    def test_all_languages_have_translated_names_and_options(self) -> None:
        import json
        for path in [SOURCE_PATH.parent / "strings.json", *(SOURCE_PATH.parent / "translations").glob("*.json")]:
            with self.subTest(path=path.name):
                translation = json.loads(path.read_text())["entity"]["select"]["heating_actuator_output_type"]
                self.assertTrue(translation["name"])
                self.assertEqual(set(translation["state"]), {"relay", "pilot_wire"})
                self.assertTrue(all(translation["state"].values()))


if __name__ == "__main__":
    unittest.main()
