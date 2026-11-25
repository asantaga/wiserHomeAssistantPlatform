"""Tests for inferred assignments on Wiser Smart schedules."""

import ast
from pathlib import Path
from types import SimpleNamespace
import unittest


SOURCE = (
    Path(__file__).resolve().parents[1]
    / "custom_components/wiser/websockets.py"
)


def _load_smart_schedule_assignments():
    """Load the pure schedule assignment helper without Home Assistant."""
    tree = ast.parse(SOURCE.read_text())
    helper = next(
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and node.name == "smart_schedule_assignments"
    )
    namespace = {}
    exec(compile(ast.Module(body=[helper], type_ignores=[]), SOURCE, "exec"), namespace)
    return namespace["smart_schedule_assignments"]


smart_schedule_assignments = _load_smart_schedule_assignments()


class SmartScheduleAssignmentsTest(unittest.TestCase):
    """Smart schedules are associated through equipment overview IDs."""

    def test_returns_linked_smartplugs_and_evses(self):
        wiserhub = SimpleNamespace(
            devices=SimpleNamespace(
                equipments=SimpleNamespace(
                    all=[
                        SimpleNamespace(
                            device_type="SmartPlug",
                            overview_schedule_id=12,
                            device_id=101,
                            equipment_name="Office plug",
                        ),
                        SimpleNamespace(
                            device_type="EVSE",
                            overview_schedule_id="12",
                            device_id=202,
                            equipment_name="Car charger",
                        ),
                        SimpleNamespace(
                            device_type="SmartPlug",
                            overview_schedule_id=13,
                            device_id=303,
                            equipment_name="Other plug",
                        ),
                        SimpleNamespace(
                            device_type="PowerTag",
                            overview_schedule_id=12,
                            device_id=404,
                            equipment_name="Meter",
                        ),
                    ]
                )
            )
        )

        self.assertEqual(
            smart_schedule_assignments(wiserhub, 12),
            [
                {"id": 101, "name": "Office plug"},
                {"id": 202, "name": "Car charger"},
            ],
        )

    def test_ignores_missing_and_duplicate_device_ids(self):
        wiserhub = SimpleNamespace(
            devices=SimpleNamespace(
                equipments=SimpleNamespace(
                    all=[
                        SimpleNamespace(
                            device_type="EVSE",
                            overview_schedule_id=12,
                            device_id=None,
                            equipment_name="Unknown charger",
                        ),
                        SimpleNamespace(
                            device_type="EVSE",
                            overview_schedule_id=12,
                            device_id=202,
                            equipment_name="Car charger",
                        ),
                        SimpleNamespace(
                            device_type="EVSE",
                            overview_schedule_id=12,
                            device_id=202,
                            equipment_name="Duplicate charger",
                        ),
                    ]
                )
            )
        )

        self.assertEqual(
            smart_schedule_assignments(wiserhub, 12),
            [{"id": 202, "name": "Car charger"}],
        )

    def test_missing_equipment_collection_returns_empty(self):
        self.assertEqual(smart_schedule_assignments(SimpleNamespace(), 12), [])


if __name__ == "__main__":
    unittest.main()
