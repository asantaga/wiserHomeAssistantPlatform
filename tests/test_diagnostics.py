"""Tests for Wiser diagnostics."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


COMPONENT_PATH = Path(__file__).parents[1] / "custom_components/wiser"


def _module(name: str, **attributes: object) -> ModuleType:
    module = ModuleType(name)
    module.__dict__.update(attributes)
    return module


def _load_diagnostics(entity_entries):
    entity_registry = _module(
        "homeassistant.helpers.entity_registry",
        async_get=Mock(return_value="entity-registry"),
        async_entries_for_config_entry=Mock(return_value=entity_entries),
    )
    helpers = _module(
        "homeassistant.helpers", entity_registry=entity_registry
    )
    package = _module("wiser_diagnostics_test")
    package.__path__ = []
    modules = {
        "homeassistant": _module("homeassistant"),
        "homeassistant.config_entries": _module(
            "homeassistant.config_entries", ConfigEntry=object
        ),
        "homeassistant.core": _module(
            "homeassistant.core",
            HomeAssistant=object,
            callback=lambda function: function,
        ),
        "homeassistant.helpers": helpers,
        "homeassistant.helpers.device_registry": _module(
            "homeassistant.helpers.device_registry", DeviceEntry=object
        ),
        "homeassistant.helpers.entity_registry": entity_registry,
        "aioWiserHeatAPI": _module("aioWiserHeatAPI"),
        "aioWiserHeatAPI.cli": _module(
            "aioWiserHeatAPI.cli",
            anonymise_data=lambda value: {"anonymised": value},
        ),
        "wiser_diagnostics_test": package,
        "wiser_diagnostics_test.const": _module(
            "wiser_diagnostics_test.const", DOMAIN="wiser"
        ),
    }
    with patch.dict(sys.modules, modules):
        spec = importlib.util.spec_from_file_location(
            "wiser_diagnostics_test.diagnostics",
            COMPONENT_PATH / "diagnostics.py",
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return module, entity_registry


class DiagnosticsTest(unittest.TestCase):
    """Validate entity-registry diagnostics."""

    def test_includes_only_config_entry_registry_metadata(self) -> None:
        created_at = datetime(2026, 11, 3, tzinfo=timezone.utc)
        registry_entry = SimpleNamespace(
            entity_id="sensor.wiser_itrv_kitchen_battery_4",
            unique_id="stable-battery-id",
            device_id="device-row-four",
            domain="sensor",
            platform="wiser",
            original_name="Battery",
            disabled_by=None,
            created_at=created_at,
        )
        diagnostics, entity_registry = _load_diagnostics([registry_entry])
        hass = SimpleNamespace(
            data={
                "wiser": {
                    "entry-id": {
                        "data": SimpleNamespace(
                            wiserhub=SimpleNamespace(
                                raw_hub_data={"Room": "Kitchen"}
                            )
                        )
                    }
                }
            }
        )
        entry = SimpleNamespace(entry_id="entry-id")

        result = diagnostics._async_get_diagnostics(hass, entry)

        self.assertEqual(
            result,
            {
                "diagnostics_version": 2,
                "hub": {"anonymised": {"Room": "Kitchen"}},
                "entity_registry": [
                    {
                        "entity_id": "sensor.wiser_itrv_kitchen_battery_4",
                        "unique_id": "stable-battery-id",
                        "device_id": "device-row-four",
                        "domain": "sensor",
                        "platform": "wiser",
                        "original_name": "Battery",
                        "disabled_by": None,
                        "created_at": "2026-11-03T00:00:00+00:00",
                    }
                ],
            },
        )
        entity_registry.async_entries_for_config_entry.assert_called_once_with(
            "entity-registry", "entry-id"
        )


if __name__ == "__main__":
    unittest.main()
