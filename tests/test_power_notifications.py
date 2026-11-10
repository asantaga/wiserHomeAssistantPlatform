"""Focused tests for native Wiser equipment power notification data."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from test_ui_options import load_functions


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
            isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in {
                "build_power_notification_data",
                "build_native_notification_data",
                "async_build_native_notification_data",
                "async_send_notification_write_result",
            }
        )
    ]
    namespace = {}
    exec(compile(ast.Module(body=selected, type_ignores=[]), SOURCE, "exec"), namespace)
    return namespace


HELPERS = _load_helpers()
build_power_notification_data = HELPERS["build_power_notification_data"]
build_native_notification_data = HELPERS["build_native_notification_data"]
async_build_native_notification_data = HELPERS[
    "async_build_native_notification_data"
]
async_send_notification_write_result = HELPERS["async_send_notification_write_result"]


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


class NotificationWriteResultTest(unittest.IsolatedAsyncioTestCase):
    async def test_power_notification_toggle_uses_the_enabled_only_setter(self):
        equipment = SimpleNamespace(
            set_under_power_notification_enabled=AsyncMock(return_value=True),
            set_under_power_notification=AsyncMock(),
        )
        data = SimpleNamespace(
            wiserhub=SimpleNamespace(
                devices=SimpleNamespace(
                    equipments=SimpleNamespace(get_by_id={12: equipment}.get, all=[])
                )
            ),
            async_refresh=AsyncMock(),
            last_update_status="Success",
        )
        connection = SimpleNamespace(send_result=Mock(), send_error=Mock())
        functions = load_functions(
            "websockets.py",
            {"websocket_set_power_notification_enabled"},
            {
                "get_api_for_hub": lambda _hub: data,
                "async_send_notification_write_result": async_send_notification_write_result,
            },
        )

        await functions.websocket_set_power_notification_enabled(
            None, connection, {"id": 4, "equipment_id": 12, "notification_type": "under", "enabled": False}
        )

        equipment.set_under_power_notification_enabled.assert_awaited_once_with(False)
        equipment.set_under_power_notification.assert_not_awaited()
        connection.send_result.assert_called_once_with(4, [])

    async def test_refresh_failure_does_not_return_a_successful_stale_result(self):
        data = SimpleNamespace(last_update_status="Failed", async_refresh=AsyncMock())
        connection = SimpleNamespace(send_result=Mock(), send_error=Mock())

        await async_send_notification_write_result(data, connection, 4, True)

        data.async_refresh.assert_awaited_once()
        connection.send_result.assert_not_called()
        connection.send_error.assert_called_once_with(
            4, "refresh_failed", "Wiser accepted the change, but the updated state could not be read"
        )

    async def test_rejected_write_does_not_refresh_or_return_success(self):
        data = SimpleNamespace(async_refresh=AsyncMock())
        connection = SimpleNamespace(send_result=Mock(), send_error=Mock())

        await async_send_notification_write_result(data, connection, 4, False)

        data.async_refresh.assert_not_awaited()
        connection.send_result.assert_not_called()
        connection.send_error.assert_called_once_with(
            4, "write_failed", "Wiser did not apply the change"
        )


class AutomationDetailsDataTest(unittest.IsolatedAsyncioTestCase):
    """Test serialization of the hub's detailed automation endpoint."""

    async def test_serializes_automation_details(self):
        async def get_details():
            return {
                "TriggerMode": "All",
                "Triggers": [
                    {"Domain": "SmartPlug", "Id": 1},
                    {"Domain": "BinarySensor", "Id": 2},
                ],
                "Actions": [{"Wait": 1}],
                "TimeConstraints": [],
            }

        api_automation = SimpleNamespace(
            set_enabled=lambda enabled: None,
            set_notification_enabled=lambda enabled: None,
            delete=lambda: None,
            get_details=get_details,
        )
        wiserhub = SimpleNamespace(
            devices=SimpleNamespace(
                equipments=SimpleNamespace(all=[]),
                smokealarms=SimpleNamespace(all=[]),
                binary_sensor=SimpleNamespace(all=[]),
                get_by_id=lambda device_id: SimpleNamespace(name="Front door")
                if device_id == 24
                else None,
            ),
            automations=SimpleNamespace(
                get_by_id=lambda automation_id: api_automation
            ),
            raw_hub_data={
                "Domain": {
                    "Automation": [
                        {"id": 3, "Name": "Test", "Enabled": True}
                    ],
                    "SmartPlug": [{"id": 1, "Name": "Kitchen plug"}],
                    "BinarySensor": [{"id": 2, "DeviceId": 24}],
                }
            },
        )

        automation = (await async_build_native_notification_data(wiserhub))[
            "automations"
        ][0]

        self.assertEqual(
            automation["details"],
            {
                "trigger_mode": "All",
                "triggers": [
                    {
                        "Domain": "SmartPlug",
                        "Id": 1,
                        "TargetName": "Kitchen plug",
                    },
                    {
                        "Domain": "BinarySensor",
                        "Id": 2,
                        "TargetName": "Front door",
                    },
                ],
                "actions": [{"Wait": 1}],
                "time_constraints": [],
            },
        )


if __name__ == "__main__":
    unittest.main()
