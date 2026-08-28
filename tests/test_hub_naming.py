"""Regression tests for physical HeatHub naming."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest


SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/helpers.py"
ENTITY_SOURCE_PATH = Path(__file__).parents[1] / "custom_components/wiser/entity.py"


def _load_helpers_module() -> ModuleType:
    """Load helpers with lightweight dependency stubs."""
    wiserhub = ModuleType("aioWiserHeatAPI.wiserhub")
    wiserhub.WiserHubConnectionError = RuntimeError
    wiserhub.WiserHubAuthenticationError = RuntimeError
    wiserhub.WiserHubRESTError = RuntimeError
    sys.modules["aioWiserHeatAPI"] = ModuleType("aioWiserHeatAPI")
    sys.modules["aioWiserHeatAPI.wiserhub"] = wiserhub

    sys.modules["homeassistant"] = ModuleType("homeassistant")
    core = ModuleType("homeassistant.core")
    core.HomeAssistant = object
    sys.modules["homeassistant.core"] = core

    package = ModuleType("wiser_helpers_test")
    package.__path__ = []
    sys.modules[package.__name__] = package
    const = ModuleType("wiser_helpers_test.const")
    const.DOMAIN = "wiser"
    const.ENTITY_PREFIX = "Wiser"
    const.MANUFACTURER = "Drayton Wiser"
    sys.modules[const.__name__] = const

    spec = importlib.util.spec_from_file_location(
        "wiser_helpers_test.helpers", SOURCE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_entity_module() -> ModuleType:
    """Load the shared entity mixin against the helper test package."""
    spec = importlib.util.spec_from_file_location(
        "wiser_helpers_test.entity", ENTITY_SOURCE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class HubNamingTest(unittest.TestCase):
    """Ensure display names and object IDs use the physical hub MAC."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.helpers = _load_helpers_module()
        cls.entity = _load_entity_module()

    def setUp(self) -> None:
        system = SimpleNamespace(
            name="WiserHeatNOTUSED",
            network=SimpleNamespace(mac_address="FC:FE:C2:05:8A:52"),
            model="CCTFR6311G2",
            firmware_version="4.48.2",
        )
        self.data = SimpleNamespace(wiserhub=SimpleNamespace(system=system))

    def test_single_hub_has_concise_device_name(self) -> None:
        self.assertEqual(self.helpers.get_hub_device_name(self.data), "Wiser HeatHub")

    def test_multiple_hubs_add_mac_suffix_to_device_name(self) -> None:
        self.data._wiser_show_hub_suffix = True
        self.assertEqual(
            self.helpers.get_hub_device_name(self.data), "Wiser HeatHub (058A52)"
        )

    def test_hub_entity_object_id_uses_mac_suffix(self) -> None:
        self.assertEqual(
            self.helpers.get_hub_entity_object_id(self.data, "Away Mode"),
            "058a52_away_mode",
        )

    def test_hub_entity_mixin_suggests_mac_derived_object_id(self) -> None:
        class DefaultEntity:
            @property
            def suggested_object_id(self):
                return "default"

        class HubEntity(self.entity.WiserEntityMixin, DefaultEntity):
            name = "Away Mode"

            def __init__(entity_self, data) -> None:
                entity_self._data = data

            @property
            def device_info(entity_self):
                return {
                    "identifiers": {
                        ("wiser", entity_self._data.wiserhub.system.name)
                    }
                }

        self.assertEqual(
            HubEntity(self.data).suggested_object_id,
            "058a52_away_mode",
        )

    def test_hub_entity_object_id_does_not_repeat_device_name(self) -> None:
        object_id = self.helpers.get_hub_entity_object_id(self.data, "Away Mode")
        self.assertNotIn("wiser_heathub", object_id)

    def test_legacy_identifier_remains_stable(self) -> None:
        self.assertEqual(
            self.helpers.get_identifier(self.data, 0),
            "WiserHeatNOTUSED Wiser HeatHub (WiserHeatNOTUSED)",
        )


if __name__ == "__main__":
    unittest.main()
