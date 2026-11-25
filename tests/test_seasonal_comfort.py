"""Regression tests for seasonal comfort controls and weather sensors."""

from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock, patch

from test_sensor import _load_sensor_module
from test_switch_hot_water import _load_switch_module


class WiserWeatherSensorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_sensor_module()

    def setUp(self):
        self.data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(
                    name="WiserHeat123456",
                    weather=SimpleNamespace(
                        temperature=-25.0, next_day_2pm_temperature=12.5
                    ),
                ),
                rooms=SimpleNamespace(get_by_device_id=lambda _: None),
            )
        )

    def test_only_current_temperature_has_measurement_statistics(self):
        for key, expected in (
            ("temperature", "measurement"),
            ("next_day_2pm_temperature", None),
        ):
            with self.subTest(sensor_type=key):
                sensor = self.module.WiserLTSWeatherSensor(self.data, 0, key)
                self.assertEqual(getattr(sensor, "state_class", None), expected)
                self.assertEqual(sensor.device_class, "temperature")
                self.assertEqual(sensor.native_unit_of_measurement, "°C")

    def test_weather_readings_update_and_tolerate_missing_data(self):
        for key, expected in (
            ("temperature", -25.0), ("next_day_2pm_temperature", 12.5)
        ):
            with self.subTest(sensor_type=key):
                sensor = self.module.WiserLTSWeatherSensor(self.data, 0, key)
                sensor.async_write_ha_state = Mock()
                sensor._handle_coordinator_update()
                self.assertEqual(sensor.native_value, expected)
                weather = self.data.wiserhub.system.weather
                self.data.wiserhub.system.weather = None
                sensor._handle_coordinator_update()
                self.assertIsNone(sensor.native_value)
                self.data.wiserhub.system.weather = weather


class WiserSeasonalShutterTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_switch_module()

    def setUp(self):
        self.shutter = SimpleNamespace(
            id=12, name="Bedroom", product_type="Shutter",
            firmware_version="test", respect_seasonal_comfort=True,
            room_with_temperature_sensor="7", covering_type="Window",
            set_respect_seasonal_comfort=AsyncMock(),
        )
        self.current_shutter = self.shutter
        self.data = SimpleNamespace(
            last_update_success=True,
            async_refresh=AsyncMock(),
            wiserhub=SimpleNamespace(
                system=SimpleNamespace(name="WiserHeat123456"),
                devices=SimpleNamespace(get_by_id=lambda _: self.current_shutter),
                rooms=SimpleNamespace(get_by_id=lambda _: SimpleNamespace(name="Lounge")),
            ),
        )
        self.name_patch = patch.object(
            self.module, "get_device_name",
            side_effect=lambda data, device_id: data.wiserhub.devices.get_by_id(device_id).name,
        )
        self.name_patch.start()
        self.addCleanup(self.name_patch.stop)
        self.entity = self.module.WiserShutterSeasonalComfortSwitch(
            self.data, 12, "Wiser Bedroom"
        )
        self.entity.async_write_ha_state = Mock()

    async def test_removed_shutter_becomes_unavailable_and_preserves_metadata(self):
        original_info = self.entity.device_info
        self.current_shutter = None
        self.entity._handle_coordinator_update()
        self.assertFalse(self.entity.available)
        self.assertFalse(self.entity.is_on)
        self.assertEqual(self.entity.device_info, original_info)
        self.assertEqual(self.entity.extra_state_attributes, {})
        self.entity.async_write_ha_state.assert_called_once_with()

    async def test_commands_ignore_shutter_removed_before_coordinator_callback(self):
        self.current_shutter = None
        await self.entity.async_turn_on()
        await self.entity.async_turn_off()
        self.shutter.set_respect_seasonal_comfort.assert_not_awaited()
        self.data.async_refresh.assert_not_awaited()

    async def test_reappearing_shutter_refreshes_state_metadata_and_commands(self):
        self.current_shutter = None
        self.entity._handle_coordinator_update()
        replacement = SimpleNamespace(
            **{**vars(self.shutter), "name": "Renamed", "firmware_version": "new",
               "respect_seasonal_comfort": False,
               "set_respect_seasonal_comfort": AsyncMock()}
        )
        self.current_shutter = replacement
        self.entity._handle_coordinator_update()
        self.assertTrue(self.entity.available)
        self.assertFalse(self.entity.is_on)
        self.assertEqual(self.entity.device_info["name"], "Renamed")
        self.assertEqual(self.entity.device_info["sw_version"], "new")
        self.assertEqual(self.entity.extra_state_attributes["room_temperature_name"], "Lounge")
        await self.entity.async_turn_on()
        replacement.set_respect_seasonal_comfort.assert_awaited_with(True)
        await self.entity.async_turn_off()
        replacement.set_respect_seasonal_comfort.assert_awaited_with(False)
        self.shutter.set_respect_seasonal_comfort.assert_not_awaited()
        self.assertEqual(self.data.async_refresh.await_count, 2)

    async def test_hub_failure_makes_present_shutter_unavailable(self):
        self.data.last_update_success = False
        self.assertFalse(self.entity.available)


class WiserSeasonalSetupTest(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls):
        cls.module = _load_switch_module()

    async def _setup(self, generation, *, has_shutters=True, supports_seasonal=True):
        shutter = SimpleNamespace(
            id=12, name="Bedroom", product_type="Shutter", firmware_version="test",
            away_mode_action="Close", respect_summer_comfort=False,
        )
        if supports_seasonal:
            shutter.respect_seasonal_comfort = False
            shutter.set_respect_seasonal_comfort = AsyncMock()
        system = SimpleNamespace(name="WiserHeat123456")
        if generation >= 2:
            system.seasonal_comfort_enabled = False
        shutters = [shutter] if has_shutters else []
        data = SimpleNamespace(
            hub_version=generation, last_update_success=True,
            passive_mode_enabled=True, enable_hw_climate=False,
            hw_climate_experimental_mode=False,
            wiserhub=SimpleNamespace(
                system=system, hotwater=None,
                rooms=SimpleNamespace(all=[]),
                devices=SimpleNamespace(
                    all=shutters, get_by_id=lambda _: shutter,
                    shutters=SimpleNamespace(all=shutters),
                    lights=SimpleNamespace(all=[]), smartplugs=SimpleNamespace(all=[]),
                    power_tags_c=SimpleNamespace(all=[]), evse=None,
                ),
            ),
        )
        hass = SimpleNamespace(data={"wiser": {"entry": {"data": data}}})
        add_entities = Mock()
        await self.module.async_setup_entry(
            hass, SimpleNamespace(entry_id="entry"), add_entities
        )
        return [entity for entity in add_entities.call_args.args[0]
                if isinstance(entity, self.module.WiserShutterSeasonalComfortSwitch)]

    async def test_supported_shutters_on_generation_two_and_later(self):
        for generation in (1, 2, 3):
            with self.subTest(generation=generation):
                entities = await self._setup(generation)
                self.assertEqual(len(entities), 1 if generation >= 2 else 0)
                if entities:
                    self.assertFalse(entities[0].is_on)
                    self.assertEqual(
                        entities[0]._attr_translation_key, "respect_seasonal_comfort"
                    )

    async def test_absent_or_unsupported_shutters_do_not_create_switches(self):
        self.assertEqual(await self._setup(2, has_shutters=False), [])
        self.assertEqual(await self._setup(2, supports_seasonal=False), [])
