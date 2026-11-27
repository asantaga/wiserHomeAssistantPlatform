"""Check remove/re-add registry events against Home Assistant itself."""

import ast
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest

from homeassistant.config_entries import ConfigEntries
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr, entity_registry as er


class ExternalTemperatureDeltaLifecycleTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.hass = HomeAssistant(self.directory.name)
        self.hass.config_entries = ConfigEntries(self.hass, {})
        await self.hass.config_entries.async_initialize()
        dr.async_setup(self.hass)
        await dr.async_load(self.hass, load_empty=True)
        await er.async_load(self.hass, load_empty=True)
        self.registry = er.async_get(self.hass)
        self.unique_id = "room-1-external-temperature-delta"
        self.entry = self.registry.async_get_or_create(
            "sensor", "wiser", self.unique_id,
            suggested_object_id="test_external_temperature_delta",
            original_name="Temperature delta",
        )
        self.registry.async_update_entity(
            self.entry.entity_id, name="My delta", icon="mdi:delta"
        )
        self.assigned = True
        self.data = SimpleNamespace(external_room_control=SimpleNamespace(
            temperature_sensor_entity_id=lambda _room_id: (
                "sensor.external" if self.assigned else None
            ),
        ))
        source = Path(__file__).parents[2] / "custom_components/wiser/sensor.py"
        node = next(node for node in ast.parse(source.read_text()).body
                    if isinstance(node, ast.FunctionDef)
                    and node.name == "_external_temperature_delta_sensors")
        namespace = {
            "DOMAIN": "wiser",
            "active_wiser_rooms": lambda _data: [SimpleNamespace(id=1)],
            "get_room_entity_unique_id": lambda *_args: self.unique_id,
            "WiserExternalTemperatureDeltaSensor": lambda *_args: object(),
        }
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(source), "exec"), namespace)
        self.create_sensors = namespace[node.name]

    async def asyncTearDown(self):
        await self.hass.async_stop(force=True)

    async def test_unassignment_and_reassignment_never_delete_the_registry_entry(self):
        events = []

        @callback
        def record(event):
            events.append(event.data["action"])
            self.assertIsNotNone(self.registry.async_get(self.entry.entity_id))

        self.hass.bus.async_listen(er.EVENT_ENTITY_REGISTRY_UPDATED, record)
        # Simulate the restored state left by a normal platform unload.
        self.entry.write_unavailable_state(self.hass)
        config_entry = SimpleNamespace(entry_id=None)
        for _ in range(2):
            self.assigned = False
            self.assertEqual(self.create_sensors(self.hass, config_entry, self.data), [])
            disabled = self.registry.async_get(self.entry.entity_id)
            self.assertEqual(disabled.disabled_by, er.RegistryEntryDisabler.INTEGRATION)
            self.assertIsNone(self.hass.states.get(self.entry.entity_id))

            self.assigned = True
            self.assertEqual(len(self.create_sensors(self.hass, config_entry, self.data)), 1)
            restored = self.registry.async_get(self.entry.entity_id)
            self.assertIsNone(restored.disabled_by)
            self.assertEqual(restored.id, self.entry.id)
            self.assertEqual(restored.unique_id, self.unique_id)
            self.assertEqual(restored.name, "My delta")
            self.assertEqual(restored.icon, "mdi:delta")
            self.assertEqual(len(self.registry.entities), 1)
        self.assertTrue(events)
        self.assertEqual(set(events), {"update"})


if __name__ == "__main__":
    unittest.main()
