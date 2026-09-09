"""Regression tests for Wiser entity unique-ID migration."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from uuid import UUID, uuid5


COMPONENT_PATH = Path(__file__).parents[1] / "custom_components/wiser"
NAMESPACE = UUID("8d42a4e1-b77b-4dda-a964-137b67c6257f")


class FakeRegistry:
    """Minimal entity registry used by the migration tests."""

    def __init__(self, entries):
        self.entries = entries
        self.updates = []

    def async_get_entity_id(self, domain, platform, unique_id):
        return next(
            (
                entry.entity_id
                for entry in self.entries
                if entry.domain == domain
                and entry.platform == platform
                and entry.unique_id == unique_id
            ),
            None,
        )

    def async_update_entity(self, entity_id, *, new_unique_id):
        entry = next(
            entry for entry in self.entries if entry.entity_id == entity_id
        )
        entry.unique_id = new_unique_id
        self.updates.append((entity_id, new_unique_id))


def _entry(entity_id, unique_id, *, platform="wiser", domain="sensor"):
    return SimpleNamespace(
        entity_id=entity_id,
        unique_id=unique_id,
        platform=platform,
        domain=domain,
        config_entry_id="entry-1",
    )


def _load_migration_module(registry):
    package = ModuleType("wiser_unique_id_test")
    package.__path__ = []
    sys.modules[package.__name__] = package

    const = ModuleType("wiser_unique_id_test.const")
    const.DOMAIN = "wiser"
    sys.modules[const.__name__] = const

    helpers = ModuleType("wiser_unique_id_test.helpers")
    helpers.get_uuid_unique_id = lambda value: str(uuid5(NAMESPACE, value))
    sys.modules[helpers.__name__] = helpers

    entity_registry = ModuleType("homeassistant.helpers.entity_registry")
    entity_registry.async_get = lambda _hass: registry
    entity_registry.async_entries_for_config_entry = (
        lambda current_registry, config_entry_id: [
            entry
            for entry in current_registry.entries
            if entry.config_entry_id == config_entry_id
        ]
    )
    helpers_package = sys.modules.setdefault(
        "homeassistant.helpers", ModuleType("homeassistant.helpers")
    )
    helpers_package.entity_registry = entity_registry
    sys.modules["homeassistant.helpers.entity_registry"] = entity_registry

    spec = importlib.util.spec_from_file_location(
        "wiser_unique_id_test.entity_migration",
        COMPONENT_PATH / "entity_migration.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class EntityUniqueIdMigrationTest(unittest.TestCase):
    """Ensure registry migration preserves entries and is restart-safe."""

    def test_migrates_in_place_and_is_idempotent(self) -> None:
        old_unique_id = "WiserHeat058A52-sensor-LTS Temperature Bedroom-7"
        entry = _entry("sensor.bedroom_temperature", old_unique_id)
        registry = FakeRegistry([entry])
        migration = _load_migration_module(registry)

        self.assertEqual(
            migration.migrate_entity_unique_ids(object(), "entry-1"), 1
        )
        self.assertEqual(entry.entity_id, "sensor.bedroom_temperature")
        self.assertEqual(UUID(entry.unique_id).version, 5)
        self.assertEqual(
            migration.migrate_entity_unique_ids(object(), "entry-1"), 0
        )
        self.assertEqual(len(registry.updates), 1)

    def test_preflight_collision_does_not_partially_migrate(self) -> None:
        first_old_id = "WiserHeat058A52-sensor-Temperature-7"
        second_old_id = "WiserHeat058A52-sensor-Humidity-7"
        first_target = str(uuid5(NAMESPACE, first_old_id))
        entries = [
            _entry("sensor.temperature", first_old_id),
            _entry("sensor.humidity", second_old_id),
            _entry("sensor.existing", first_target),
        ]
        registry = FakeRegistry(entries)
        migration = _load_migration_module(registry)

        with self.assertRaisesRegex(ValueError, "already used"):
            migration.migrate_entity_unique_ids(object(), "entry-1")

        self.assertEqual(entries[0].unique_id, first_old_id)
        self.assertEqual(entries[1].unique_id, second_old_id)
        self.assertEqual(registry.updates, [])

    def test_ignores_entities_from_other_integrations(self) -> None:
        entry = _entry(
            "sensor.other", "other-unique-id", platform="other_integration"
        )
        registry = FakeRegistry([entry])
        migration = _load_migration_module(registry)

        self.assertEqual(
            migration.migrate_entity_unique_ids(object(), "entry-1"), 0
        )
        self.assertEqual(entry.unique_id, "other-unique-id")

    def test_invalid_unique_id_does_not_partially_migrate(self) -> None:
        valid_entry = _entry("sensor.temperature", "legacy-temperature")
        invalid_entry = _entry("sensor.invalid", None)
        registry = FakeRegistry([valid_entry, invalid_entry])
        migration = _load_migration_module(registry)

        with self.assertRaisesRegex(ValueError, "has no valid unique ID"):
            migration.migrate_entity_unique_ids(object(), "entry-1")

        self.assertEqual(valid_entry.unique_id, "legacy-temperature")
        self.assertIsNone(invalid_entry.unique_id)
        self.assertEqual(registry.updates, [])
