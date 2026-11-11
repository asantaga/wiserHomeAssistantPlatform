"""Brightness attributes on on/off lights and dimmers, including older APIs."""

from types import SimpleNamespace
import unittest

from test_light_optimistic_state import _load_light_module


class LightAttributesTest(unittest.TestCase):
    """Expose available brightness data without inventing values for older APIs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_light_module()

    def make_entity(self, *, dimmable=False, brightness_data=True):
        """Create an entity with the metadata used by its state attributes."""
        device = SimpleNamespace(**{
            field: "test" for field in (
                "name", "model", "product_type", "product_identifier", "product_model",
                "serial_number", "firmware_version", "type_comm", "uuid", "mode",
                "away_mode_action", "control_source", "current_state", "target_state",
            )
        })
        device.room_id = 1
        device.endpoint = 1
        device.is_dimmable = dimmable
        device.is_output_mode_supported = False
        device.is_led_indicator_supported = False
        device.is_power_on_behaviour_supported = False
        device.schedule_id = 0
        device.schedule = None
        device.output_range = SimpleNamespace(minimum=0, maximum=100)
        device.current_percentage = 30
        device.current_level = 30
        device.override_level = 0
        if brightness_data:
            device.target_percentage = 45
            device.manual_level = 20
            device.scheduled_percentage = 0
        entity_class = self.module.WiserDimmableLight if dimmable else self.module.WiserLight
        entity = entity_class.__new__(entity_class)
        entity._device = device
        entity._device_id = 12
        entity._data = SimpleNamespace(wiserhub=SimpleNamespace(
            rooms=SimpleNamespace(get_by_id=lambda _id: None)
        ))
        return entity

    def test_brightness_attributes_are_available_on_both_light_types(self) -> None:
        for dimmable in (False, True):
            with self.subTest(dimmable=dimmable):
                attrs = self.make_entity(dimmable=dimmable).extra_state_attributes
                self.assertEqual(attrs["target_percentage"], 45)
                self.assertEqual(attrs["manual_level"], 20)
                self.assertEqual(attrs["scheduled_percentage"], 0)

    def test_older_onoff_api_without_brightness_data_still_reports_state(self) -> None:
        attrs = self.make_entity(brightness_data=False).extra_state_attributes
        self.assertEqual(attrs["current_state"], "test")
        for key in ("target_percentage", "manual_level", "scheduled_percentage"):
            self.assertNotIn(key, attrs)


if __name__ == "__main__":
    unittest.main()
