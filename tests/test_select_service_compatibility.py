"""Exercise translated selects through Home Assistant's service validation."""

import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from test_smartplug_select import _load_select_module


class SelectServiceCompatibilityTest(unittest.IsolatedAsyncioTestCase):
    """Keep legacy service values without publishing duplicate UI options."""

    @classmethod
    def setUpClass(cls):
        cls.module = _load_select_module()
        module = cls.module

        async def async_handle_select_option(entity, option):
            """Model HA's validation before dispatch to async_select_option."""
            if not entity.options or option not in entity.options:
                raise module.HomeAssistantError(f"Invalid select option: {option}")
            entity.validated_options.append(option)
            await entity.async_select_option(option)

        module.SelectEntity.async_handle_select_option = async_handle_select_option

    def entities(self):
        """Build each translated selector using its real API option mapping."""
        for name, options_attribute in (
            ("WiserSmartPlugModeSelect", "available_modes"),
            ("WiserSmartPlugLedIndicatorSelect", "available_led_indicator"),
            ("WiserLightModeSelect", "available_modes"),
            ("WiserLightPowerOnBehaviourSelect", "available_power_on_behaviour"),
            ("WiserLightLedIndicatorSelect", "available_led_indicator"),
            ("WiserLightOutputModeSelect", "available_output_mode"),
            ("WiserHeatingActuatorOutputTypeSelect", "available_output_type"),
        ):
            entity_class = getattr(self.module, name)
            values = entity_class._option_values
            device = SimpleNamespace(
                id=12, light_id=12, product_type="Test", schedule=None,
                **{options_attribute: list(values.values())},
            )
            setter_name = getattr(entity_class, "_setter", "set_output_type")
            setattr(device, setter_name, AsyncMock(return_value=True))
            collection = SimpleNamespace(
                get_by_id=lambda _id: device,
                get_by_light_id=lambda _id: device,
            )
            data = SimpleNamespace(wiserhub=SimpleNamespace(
                system=SimpleNamespace(name="WiserTest"),
                devices=SimpleNamespace(
                    smartplugs=collection, lights=collection,
                    heating_actuators=collection,
                ),
            ))
            entity = entity_class(data, 12)
            entity.async_force_update = AsyncMock()
            entity.validated_options = []
            yield entity, getattr(device, setter_name)

    async def test_service_accepts_legacy_and_translated_values(self):
        """Both spellings must pass HA validation and send the API value."""
        for entity, setter in self.entities():
            options = list(entity.options)
            for key, raw in entity._option_values.items():
                for option in (key, raw):
                    with self.subTest(entity=type(entity).__name__, option=option):
                        setter.reset_mock()
                        await entity.async_handle_select_option(option)
                        self.assertEqual(entity.validated_options[-1], key)
                        setter.assert_awaited_once_with(raw)
                        self.assertEqual(entity.options, options)

    async def test_service_rejects_unknown_and_unsupported_legacy_values(self):
        """Aliases must not bypass capability validation or send commands."""
        for entity, setter in self.entities():
            raw = next(iter(entity._option_values.values()))
            entity._options.remove(raw)
            for option in (raw, "not_an_option"):
                with self.subTest(entity=type(entity).__name__, option=option):
                    with self.assertRaises(self.module.HomeAssistantError):
                        await entity.async_handle_select_option(option)
            setter.assert_not_awaited()
            entity.async_force_update.assert_not_awaited()
