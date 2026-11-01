"""Focused tests for native Wiser equipment power notification data."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "custom_components/wiser/websockets.py"


def _load_helpers():
    """Load the pure notification serializer without Home Assistant imports."""
    tree = ast.parse(SOURCE.read_text())
    selected = [
        node
        for node in tree.body
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "POWER_NOTIFICATION_TYPES"
                for target in node.targets
            )
        )
        or (
            isinstance(node, ast.FunctionDef)
            and node.name == "build_power_notification_data"
        )
    ]
    namespace = {}
    exec(compile(ast.Module(body=selected, type_ignores=[]), SOURCE, "exec"), namespace)
    return namespace


HELPERS = _load_helpers()
build_power_notification_data = HELPERS["build_power_notification_data"]


class PowerNotificationDataTest(unittest.TestCase):
    """Test the frontend representation of native hub notifications."""

    def test_serializes_configured_and_missing_notifications(self):
        """Each equipment includes both supported notification slots."""
        equipment = SimpleNamespace(
            id=1,
            device_id=8,
            device_type="SmartPlug",
            equipment_name="Smart Plug",
            equipment_family="ElectricalPlug",
            monitored=True,
            smart_supported=True,
            under_power_notification=SimpleNamespace(
                period_mins=5,
                limit=0,
                enabled=True,
            ),
            over_power_notification=None,
        )
        wiserhub = SimpleNamespace(
            devices=SimpleNamespace(equipments=SimpleNamespace(all=[equipment]))
        )

        self.assertEqual(
            build_power_notification_data(wiserhub),
            [
                {
                    "equipment_id": 1,
                    "device_id": 8,
                    "device_type": "SmartPlug",
                    "name": "Smart Plug",
                    "family": "ElectricalPlug",
                    "monitored": True,
                    "smart_supported": True,
                    "notifications": {
                        "under": {
                            "period_mins": 5,
                            "limit": 0,
                            "enabled": True,
                        },
                        "over": None,
                    },
                }
            ],
        )

    def test_missing_equipment_collection_is_empty(self):
        """Older hubs without equipment return an empty list."""
        wiserhub = SimpleNamespace(devices=SimpleNamespace())

        self.assertEqual(build_power_notification_data(wiserhub), [])


if __name__ == "__main__":
    unittest.main()
