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
            and node.name in {
                "build_power_notification_data",
                "build_native_notification_data",
            }
        )
    ]
    namespace = {}
    exec(compile(ast.Module(body=selected, type_ignores=[]), SOURCE, "exec"), namespace)
    return namespace


HELPERS = _load_helpers()
build_power_notification_data = HELPERS["build_power_notification_data"]
build_native_notification_data = HELPERS["build_native_notification_data"]


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

    def test_serializes_supported_device_notification_categories(self):
        """Smoke alarms, sensors and automations are grouped for panel tabs."""
        smoke_alarm = SimpleNamespace(
            id=11,
            name="Landing alarm",
            device_type="SmokeAlarm",
            notification_supported=True,
            notification_enabled=True,
            supervision_notify=True,
            restore_notify=False,
        )
        sensor = SimpleNamespace(
            id=8,
            name="Patio door",
            device_type="BinarySensor",
            type="WindowDoor",
            enable_notification="None",
            notification_enabled=False,
        )
        wiserhub = SimpleNamespace(
            devices=SimpleNamespace(
                equipments=SimpleNamespace(all=[]),
                smokealarms=SimpleNamespace(all=[smoke_alarm]),
                binary_sensor=SimpleNamespace(all=[sensor]),
            ),
            automations=SimpleNamespace(
                get_by_id=lambda automation_id: SimpleNamespace(
                    set_enabled=lambda enabled: None,
                    set_notification_enabled=lambda enabled: None,
                    delete=lambda: None,
                )
                if automation_id == 3
                else None
            ),
            raw_hub_data={
                "Domain": {
                    "Automation": [
                        {
                            "id": 3,
                            "Name": "Door left open",
                            "Enabled": True,
                            "EnableNotification": False,
                        }
                    ]
                }
            },
        )

        self.assertEqual(
            build_native_notification_data(wiserhub),
            {
                "equipment": [],
                "smoke_alarms": [
                    {
                        "device_id": 11,
                        "name": "Landing alarm",
                        "device_type": "SmokeAlarm",
                        "enabled": True,
                        "supervision_notify": True,
                        "restore_notify": False,
                    }
                ],
                "sensors": [
                    {
                        "device_id": 8,
                        "name": "Patio door",
                        "device_type": "BinarySensor",
                        "sensor_type": "WindowDoor",
                        "enabled": False,
                    }
                ],
                "automations": [
                    {
                        "automation_id": 3,
                        "name": "Door left open",
                        "enabled": True,
                        "notification_enabled": False,
                        "writable": True,
                        "notification_writable": True,
                        "deletable": True,
                    }
                ],
            },
        )

    def test_omits_devices_without_notification_capability(self):
        """Tabs only contain devices that report notification support."""
        wiserhub = SimpleNamespace(
            devices=SimpleNamespace(
                equipments=SimpleNamespace(all=[]),
                smokealarms=SimpleNamespace(
                    all=[SimpleNamespace(notification_supported=False)]
                ),
                binary_sensor=SimpleNamespace(
                    all=[SimpleNamespace(enable_notification=None)]
                ),
            ),
            raw_hub_data={"Domain": {"Automation": [{"id": 1}]}},
        )

        self.assertEqual(
            build_native_notification_data(wiserhub),
            {
                "equipment": [],
                "smoke_alarms": [],
                "sensors": [],
                "automations": [],
            },
        )

    def test_automation_is_read_only_without_api_setter(self):
        wiserhub = SimpleNamespace(
            devices=SimpleNamespace(
                equipments=SimpleNamespace(all=[]),
                smokealarms=SimpleNamespace(all=[]),
                binary_sensor=SimpleNamespace(all=[]),
            ),
            raw_hub_data={
                "Domain": {
                    "Automation": [{
                        "id": 3,
                        "Name": "Door left open",
                        "Enabled": True,
                    }]
                }
            },
        )

        automation = build_native_notification_data(wiserhub)["automations"][0]
        self.assertFalse(automation["writable"])
        self.assertFalse(automation["notification_writable"])
        self.assertFalse(automation["deletable"])


if __name__ == "__main__":
    unittest.main()
